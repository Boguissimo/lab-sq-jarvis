"""Persistência local: banco SQLite, cofre de originais e rotina de integridade.

- Originais (arquivos importados) ficam no cofre com o nome igual ao hash SHA-256 e nunca são
  alterados nem substituídos (constituição, P2).
- Registros da cadeia, arquivos originais e o diário só aceitam inserção: gatilhos do SQLite
  recusam UPDATE e DELETE.
- A rotina de integridade confere tipos, derivações permitidas (P1, JV-D038) e hashes do cofre.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import stat
from datetime import datetime
from pathlib import Path

PREFIXOS = {
    "medicao": "M", "calculo": "C", "indicio": "I", "hipotese": "H", "recomendacao": "R",
    "experimento": "X", "conclusao": "A", "decisao": "D", "percepcao": "P", "estimativa": "E",
}

# destino ← origens permitidas (P1; decisão sem intervenção em JV-D038)
DERIVACOES_PERMITIDAS = {
    "calculo": {"medicao", "calculo"},
    "indicio": {"calculo"},
    "hipotese": {"indicio"},
    "recomendacao": {"hipotese", "calculo"},
    "experimento": {"recomendacao", "medicao", "percepcao"},
    "conclusao": {"experimento", "calculo", "medicao", "percepcao"},
    "decisao": {"conclusao", "experimento", "calculo", "indicio", "hipotese"},
}

ESQUEMA = """
CREATE TABLE IF NOT EXISTS arquivo_original (
    sha256 TEXT PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL,
    tamanho INTEGER NOT NULL, importado_em TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sessao (
    id INTEGER PRIMARY KEY AUTOINCREMENT, modo TEXT NOT NULL, caso TEXT,
    criada_em TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'aberta',
    passo_atual INTEGER NOT NULL DEFAULT 1, encerramento TEXT, resumo TEXT);
CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sessao INTEGER NOT NULL REFERENCES sessao(id),
    nome TEXT NOT NULL, nivel TEXT NOT NULL, criada_em TEXT NOT NULL,
    anterior INTEGER REFERENCES configuracao(id), arquivo_sha256 TEXT);
CREATE TABLE IF NOT EXISTS parametro_config (
    configuracao INTEGER NOT NULL REFERENCES configuracao(id), canal TEXT NOT NULL,
    parametro TEXT NOT NULL, valor TEXT NOT NULL, origem TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS registro (
    id TEXT PRIMARY KEY, sessao INTEGER NOT NULL REFERENCES sessao(id), tipo TEXT NOT NULL,
    autor TEXT NOT NULL, criado_em TEXT NOT NULL, titulo TEXT NOT NULL, dados TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS derivacao (
    origem TEXT NOT NULL REFERENCES registro(id), destino TEXT NOT NULL REFERENCES registro(id),
    papel TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT, momento TEXT NOT NULL, sessao INTEGER,
    evento TEXT NOT NULL, descricao TEXT NOT NULL);
"""

GATILHOS = [
    ("arquivo_original", "Arquivo original não pode ser alterado nem apagado"),
    ("registro", "Registro da cadeia não pode ser alterado nem apagado"),
    ("derivacao", "Derivação da cadeia não pode ser alterada nem apagada"),
    ("diario", "O diário só aceita novos eventos"),
    ("parametro_config", "Parâmetros de configuração registrados não podem ser alterados"),
]


class OriginalImutavel(Exception):
    """Tentativa de alterar ou substituir um original."""


def pasta_de_dados() -> Path:
    if os.environ.get("JARVIS_DADOS"):
        return Path(os.environ["JARVIS_DADOS"])
    base = os.environ.get("LOCALAPPDATA") or (Path.home() / ".local" / "share")
    return Path(base) / "LabSQJarvis"


def agora() -> str:
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def sha256_de(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as arq:
        for bloco in iter(lambda: arq.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


class Banco:
    def __init__(self, pasta: Path | None = None):
        self.pasta = Path(pasta) if pasta else pasta_de_dados()
        self.cofre = self.pasta / "cofre"
        self.cofre.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(self.pasta / "jarvis.db")
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.executescript(ESQUEMA)
        for tabela, mensagem in GATILHOS:
            for operacao in ("UPDATE", "DELETE"):
                self.con.execute(
                    f"CREATE TRIGGER IF NOT EXISTS so_insercao_{tabela}_{operacao.lower()} "
                    f"BEFORE {operacao} ON {tabela} BEGIN SELECT RAISE(ABORT, '{mensagem}'); END")
        self.con.commit()

    def fechar(self) -> None:
        self.con.close()

    # ---------------------------------------------------------------- originais
    def caminho_original(self, sha: str) -> Path:
        return self.cofre / sha[:2] / sha

    def guardar_original(self, origem: Path, tipo: str) -> str:
        origem = Path(origem)
        sha = sha256_de(origem)
        destino = self.caminho_original(sha)
        if destino.exists():
            if sha256_de(destino) != sha:
                raise OriginalImutavel(f"O original {sha[:12]}… no cofre foi alterado fora do programa.")
            return sha  # mesmo conteúdo já guardado: nada a fazer
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origem, destino)
        os.chmod(destino, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        self.con.execute(
            "INSERT OR IGNORE INTO arquivo_original VALUES (?, ?, ?, ?, ?)",
            (sha, origem.name, tipo, destino.stat().st_size, agora()))
        self.con.commit()
        return sha

    def substituir_original(self, sha: str, novo_conteudo: bytes) -> None:
        """Existe só para deixar explícito (e testável) que substituir é proibido."""
        self.diario(None, "recusa", f"Tentativa de substituir o original {sha[:12]}… recusada")
        raise OriginalImutavel("Arquivos originais não podem ser substituídos (constituição, P2).")

    def verificar_original(self, sha: str) -> bool:
        caminho = self.caminho_original(sha)
        return caminho.exists() and sha256_de(caminho) == sha

    # ---------------------------------------------------------------- sessões
    def nova_sessao(self, modo: str, caso: str | None) -> int:
        cur = self.con.execute("INSERT INTO sessao (modo, caso, criada_em) VALUES (?, ?, ?)",
                               (modo, caso, agora()))
        self.con.commit()
        return int(cur.lastrowid)

    def atualizar_sessao(self, sessao: int, **campos) -> None:
        nomes = ", ".join(f"{k} = ?" for k in campos)
        self.con.execute(f"UPDATE sessao SET {nomes} WHERE id = ?", (*campos.values(), sessao))
        self.con.commit()

    def sessao(self, sessao: int) -> sqlite3.Row:
        return self.con.execute("SELECT * FROM sessao WHERE id = ?", (sessao,)).fetchone()

    def sessoes(self) -> list[sqlite3.Row]:
        return self.con.execute("SELECT * FROM sessao ORDER BY id DESC").fetchall()

    # ---------------------------------------------------------------- configurações
    def nova_configuracao(self, sessao: int, nome: str, nivel: str, parametros: list[dict],
                          anterior: int | None = None, arquivo_sha256: str | None = None) -> int:
        cur = self.con.execute(
            "INSERT INTO configuracao (sessao, nome, nivel, criada_em, anterior, arquivo_sha256) "
            "VALUES (?, ?, ?, ?, ?, ?)", (sessao, nome, nivel, agora(), anterior, arquivo_sha256))
        cid = int(cur.lastrowid)
        self.con.executemany(
            "INSERT INTO parametro_config VALUES (?, ?, ?, ?, ?)",
            [(cid, p["canal"], p["parametro"], p["valor"], p["origem"]) for p in parametros])
        self.con.commit()
        return cid

    def configuracoes(self, sessao: int) -> list[dict]:
        saida = []
        for c in self.con.execute("SELECT * FROM configuracao WHERE sessao = ? ORDER BY id", (sessao,)):
            params = [dict(p) for p in self.con.execute(
                "SELECT canal, parametro, valor, origem FROM parametro_config WHERE configuracao = ?",
                (c["id"],))]
            saida.append({**dict(c), "parametros": params})
        return saida

    # ---------------------------------------------------------------- cadeia
    def novo_registro(self, sessao: int, tipo: str, titulo: str, dados: dict, autor: str = "sistema",
                      origens: list[tuple[str, str]] | None = None) -> str:
        prefixo = PREFIXOS[tipo]
        n = self.con.execute("SELECT COUNT(*) FROM registro WHERE tipo = ?", (tipo,)).fetchone()[0] + 1
        rid = f"{prefixo}-{n:04d}"
        self.con.execute("INSERT INTO registro VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (rid, sessao, tipo, autor, agora(), titulo,
                          json.dumps(dados, ensure_ascii=False)))
        self.con.executemany("INSERT INTO derivacao VALUES (?, ?, ?)",
                             [(o, rid, papel) for o, papel in (origens or [])])
        self.con.commit()
        return rid

    def registros(self, sessao: int, tipo: str | None = None) -> list[dict]:
        sql = "SELECT * FROM registro WHERE sessao = ?" + (" AND tipo = ?" if tipo else "") + " ORDER BY rowid"
        args = (sessao, tipo) if tipo else (sessao,)
        return [{**dict(r), "dados": json.loads(r["dados"])} for r in self.con.execute(sql, args)]

    def origens_de(self, rid: str) -> list[dict]:
        return [dict(r) for r in self.con.execute(
            "SELECT d.origem, d.papel, r.tipo FROM derivacao d JOIN registro r ON r.id = d.origem "
            "WHERE d.destino = ?", (rid,))]

    def diario(self, sessao: int | None, evento: str, descricao: str) -> None:
        self.con.execute("INSERT INTO diario (momento, sessao, evento, descricao) VALUES (?, ?, ?, ?)",
                         (agora(), sessao, evento, descricao))
        self.con.commit()

    def eventos(self, sessao: int) -> list[dict]:
        return [dict(r) for r in self.con.execute(
            "SELECT * FROM diario WHERE sessao = ? ORDER BY id", (sessao,))]

    # ---------------------------------------------------------------- integridade
    def integridade(self) -> list[str]:
        """Lista de problemas encontrados; vazia quando tudo confere."""
        problemas = []
        tipos = {r["id"]: r["tipo"] for r in self.con.execute("SELECT id, tipo FROM registro")}
        for rid, tipo in tipos.items():
            if tipo not in PREFIXOS:
                problemas.append(f"{rid}: tipo desconhecido “{tipo}”")
                continue
            origens = self.origens_de(rid)
            permitidas = DERIVACOES_PERMITIDAS.get(tipo)
            if permitidas is not None:
                if tipo not in ("decisao",) and not origens:
                    problemas.append(f"{rid}: {tipo} sem origem na cadeia")
                for o in origens:
                    if o["tipo"] not in permitidas:
                        problemas.append(f"{rid}: {tipo} não pode derivar de {o['tipo']} ({o['origem']})")
            dados = json.loads(self.con.execute("SELECT dados FROM registro WHERE id = ?", (rid,)).fetchone()[0])
            if tipo == "conclusao" and not any(o["tipo"] == "experimento" for o in origens):
                problemas.append(f"{rid}: conclusão experimental sem experimento")
            if tipo == "decisao" and not dados.get("sem_intervencao") and not origens:
                problemas.append(f"{rid}: decisão sobre o ajuste sem conclusão ou experimento de origem")
            if tipo == "decisao" and dados.get("sem_intervencao"):
                if not str(dados.get("fundamentacao", "")).strip():
                    problemas.append(f"{rid}: decisão sem intervenção sem fundamentação")
                if any(o["tipo"] == "experimento" for o in origens):
                    problemas.append(f"{rid}: decisão sem intervenção não pode apontar para experimento")
                if not origens and not dados.get("avaliacao"):
                    problemas.append(f"{rid}: decisão sem intervenção sem registros que a sustentem")
            if tipo == "medicao" and not self.verificar_original(dados.get("sha256", "")):
                problemas.append(f"{rid}: original da medição ausente ou alterado no cofre")
        return problemas
