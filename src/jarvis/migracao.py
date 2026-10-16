"""Detecção de versão e migração do banco local (ADR-207; data-model, "Versões do esquema").

O V01 não grava ``user_version``: o banco do desenvolvedor está em 0. Por isso a versão é decidida
por ``user_version`` **e** pela impressão digital do esquema (tipo, nome e SQL normalizado de tabelas
e gatilhos em ``sqlite_master``). A leitura é feita numa conexão somente leitura; nada é escrito
antes de a versão ser reconhecida.

- arquivo inexistente ou sem tabelas → ``criar_v2``;
- ``user_version`` 0 com a impressão do V01 → ``migrar_0_para_2`` (backup consistente, conferência
  do backup, transação única, ``user_version = 2``);
- ``user_version`` 2 com a impressão do V02 → abre sem alterar nada;
- qualquer outro caso → ``ErroVersaoBanco``, sem modificar o arquivo.

Nenhuma linha do V01 é alterada e o cofre não é tocado.
"""

# @@T206 [FR-222] [INV-210] Migração 0 → 2 com backup e recusa segura (ADR-207)

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

VERSAO_ATUAL = 2

# Cópia literal do esquema do V01 (main@389e580, persistencia.ESQUEMA e GATILHOS). Não editar:
# serve para reconhecer o banco legado.
_TABELAS_V01 = [
    """CREATE TABLE IF NOT EXISTS arquivo_original (
    sha256 TEXT PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL,
    tamanho INTEGER NOT NULL, importado_em TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS sessao (
    id INTEGER PRIMARY KEY AUTOINCREMENT, modo TEXT NOT NULL, caso TEXT,
    criada_em TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'aberta',
    passo_atual INTEGER NOT NULL DEFAULT 1, encerramento TEXT, resumo TEXT)""",
    """CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sessao INTEGER NOT NULL REFERENCES sessao(id),
    nome TEXT NOT NULL, nivel TEXT NOT NULL, criada_em TEXT NOT NULL,
    anterior INTEGER REFERENCES configuracao(id), arquivo_sha256 TEXT)""",
    """CREATE TABLE IF NOT EXISTS parametro_config (
    configuracao INTEGER NOT NULL REFERENCES configuracao(id), canal TEXT NOT NULL,
    parametro TEXT NOT NULL, valor TEXT NOT NULL, origem TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS registro (
    id TEXT PRIMARY KEY, sessao INTEGER NOT NULL REFERENCES sessao(id), tipo TEXT NOT NULL,
    autor TEXT NOT NULL, criado_em TEXT NOT NULL, titulo TEXT NOT NULL, dados TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS derivacao (
    origem TEXT NOT NULL REFERENCES registro(id), destino TEXT NOT NULL REFERENCES registro(id),
    papel TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT, momento TEXT NOT NULL, sessao INTEGER,
    evento TEXT NOT NULL, descricao TEXT NOT NULL)""",
]
_GATILHOS_V01 = [
    ("arquivo_original", "Arquivo original não pode ser alterado nem apagado"),
    ("registro", "Registro da cadeia não pode ser alterado nem apagado"),
    ("derivacao", "Derivação da cadeia não pode ser alterada nem apagada"),
    ("diario", "O diário só aceita novos eventos"),
    ("parametro_config", "Parâmetros de configuração registrados não podem ser alterados"),
]


def _so_insercao(tabela: str, mensagem: str) -> list[str]:
    return [f"CREATE TRIGGER IF NOT EXISTS so_insercao_{tabela}_{op.lower()} "
            f"BEFORE {op} ON {tabela} BEGIN SELECT RAISE(ABORT, '{mensagem}'); END"
            for op in ("UPDATE", "DELETE")]


ESQUEMA_V01: list[str] = _TABELAS_V01 + [c for t, m in _GATILHOS_V01 for c in _so_insercao(t, m)]

# O que a migração 0 → 2 acrescenta (data-model, "Tabelas"). Comandos individuais: nada de
# executescript, que faz commit implícito.
COMANDOS_0_PARA_2: list[str] = [
    """CREATE TABLE aprovacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sessao INTEGER NOT NULL REFERENCES sessao(id),
    recomendacao TEXT NOT NULL UNIQUE REFERENCES registro(id),
    nivel TEXT NOT NULL CHECK (nivel = 'B'), escopo TEXT NOT NULL, momento TEXT NOT NULL,
    autor TEXT NOT NULL DEFAULT 'usuário')""",
    *_so_insercao("aprovacao", "Aprovação registrada não pode ser alterada nem apagada"),
    *_so_insercao("configuracao", "Configuração registrada não pode ser alterada nem apagada"),
    """CREATE TRIGGER aprovacao_recomendacao_valida BEFORE INSERT ON aprovacao
    WHEN NOT EXISTS (SELECT 1 FROM registro WHERE id = NEW.recomendacao
                     AND tipo = 'recomendacao' AND sessao = NEW.sessao)
    BEGIN SELECT RAISE(ABORT, 'Aprovação só para recomendação existente da mesma sessão'); END""",
]

ESQUEMA_V02: list[str] = ESQUEMA_V01 + COMANDOS_0_PARA_2


class ErroVersaoBanco(Exception):
    """Banco com versão ou esquema não reconhecido; o arquivo não foi modificado."""


class ErroMigracao(Exception):
    """A migração falhou e foi revertida; o backup continua na pasta de dados."""


@dataclass
class Versao:
    estado: str  # "novo" | "v01" | "v02" | "desconhecida"
    user_version: int | None = None
    motivos: list[str] = field(default_factory=list)


def _normalizar(sql: str) -> str:
    sql = re.sub(r"\s+", " ", sql.strip())
    return re.sub(r"\bIF NOT EXISTS\b ", "", sql, flags=re.IGNORECASE)


def _impressao(con: sqlite3.Connection) -> frozenset:
    linhas = con.execute("SELECT type, name, sql FROM sqlite_master "
                         "WHERE type IN ('table', 'trigger') AND name NOT LIKE 'sqlite_%'")
    return frozenset((t, n, _normalizar(s or "")) for t, n, s in linhas)


def _impressao_de(comandos: list[str]) -> frozenset:
    con = sqlite3.connect(":memory:")
    try:
        for c in comandos:
            con.execute(c)
        return _impressao(con)
    finally:
        con.close()


IMPRESSAO_V01 = _impressao_de(ESQUEMA_V01)
IMPRESSAO_V02 = _impressao_de(ESQUEMA_V02)


def _conectar_ro(caminho: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{Path(caminho).resolve().as_uri()}?mode=ro", uri=True)


def detectar(caminho: Path) -> Versao:
    """Reconhece a versão do banco sem escrever nada."""
    caminho = Path(caminho)
    if not caminho.exists() or caminho.stat().st_size == 0:
        return Versao("novo", None)
    con = _conectar_ro(caminho)
    try:
        uv = con.execute("PRAGMA user_version").fetchone()[0]
        impressao = _impressao(con)
    finally:
        con.close()
    if not impressao and uv == 0:
        return Versao("novo", uv)
    if uv == 0 and impressao == IMPRESSAO_V01:
        return Versao("v01", uv)
    if uv == VERSAO_ATUAL and impressao == IMPRESSAO_V02:
        return Versao("v02", uv)
    motivos = []
    if uv not in (0, VERSAO_ATUAL):
        motivos.append(f"user_version {uv} não reconhecida")
    else:
        esperada = IMPRESSAO_V01 if uv == 0 else IMPRESSAO_V02
        sobra = sorted(n for _, n, _ in impressao - esperada)
        falta = sorted(n for _, n, _ in esperada - impressao)
        if sobra:
            motivos.append("objetos não reconhecidos: " + ", ".join(sobra))
        if falta:
            motivos.append("objetos ausentes ou diferentes: " + ", ".join(falta))
    return Versao("desconhecida", uv, motivos)


def _executar_em_transacao(con: sqlite3.Connection, comandos: list[str]) -> None:
    con.execute("BEGIN IMMEDIATE")
    try:
        for c in comandos:
            con.execute(c)
        con.execute(f"PRAGMA user_version = {VERSAO_ATUAL}")
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise


def criar_v2(caminho: Path) -> None:
    """Cria o esquema 2 num arquivo novo ou vazio, numa única transação."""
    con = sqlite3.connect(caminho, isolation_level=None)
    try:
        _executar_em_transacao(con, ESQUEMA_V02)
    finally:
        con.close()


def _contagens(con: sqlite3.Connection) -> dict[str, int]:
    tabelas = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    return {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tabelas}


def fazer_backup(caminho: Path) -> Path:
    """Backup consistente (API de backup do SQLite), conferido por ``integrity_check`` e contagens."""
    caminho = Path(caminho)
    destino = caminho.with_name(f"{caminho.stem}.antes-v02-{datetime.now():%Y%m%d-%H%M%S}.db")
    n = 1
    while destino.exists():
        destino = caminho.with_name(f"{caminho.stem}.antes-v02-{datetime.now():%Y%m%d-%H%M%S}-{n}.db")
        n += 1
    origem = _conectar_ro(caminho)
    copia = sqlite3.connect(destino)
    try:
        origem.backup(copia)
        if copia.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ErroMigracao(f"O backup {destino.name} não passou na verificação de integridade.")
        if _contagens(copia) != _contagens(origem):
            raise ErroMigracao(f"O backup {destino.name} não tem as mesmas linhas do banco original.")
    finally:
        copia.close()
        origem.close()
    return destino


def migrar_0_para_2(caminho: Path) -> Path:
    """Migra um banco do V01 para o esquema 2 e devolve o caminho do backup."""
    caminho = Path(caminho)
    versao = detectar(caminho)
    if versao.estado != "v01":
        raise ErroVersaoBanco(f"O banco não é um banco do JV-V01 reconhecido ({versao.estado}).")
    backup = fazer_backup(caminho)
    con = sqlite3.connect(caminho, isolation_level=None)
    try:
        _executar_em_transacao(con, COMANDOS_0_PARA_2)
    except sqlite3.Error as e:
        raise ErroMigracao(
            f"A atualização do banco falhou e foi desfeita ({e}). Nada foi alterado; "
            f"o backup ficou em {backup.name}.") from e
    finally:
        con.close()
    return backup


def preparar(caminho: Path) -> Path | None:
    """Deixa o banco no esquema 2 conforme a versão detectada. Devolve o backup, se houve migração."""
    versao = detectar(caminho)
    if versao.estado == "novo":
        criar_v2(caminho)
        return None
    if versao.estado == "v01":
        return migrar_0_para_2(caminho)
    if versao.estado == "v02":
        return None
    raise ErroVersaoBanco(
        "O banco de dados não foi reconhecido (" + "; ".join(versao.motivos) + "). "
        "Ele não foi alterado. Verifique se é o banco do Lab SQ Jarvis ou use outra pasta de dados.")
