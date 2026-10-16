"""Migração do banco legado do V01 (ADR-207; critério 1 do plano)."""

import shutil
import sqlite3
from pathlib import Path

import pytest

from jarvis import migracao
from jarvis.persistencia import sha256_de

FIXTURE = Path(__file__).parent / "dados" / "banco-v01"
TABELAS_V01 = ["arquivo_original", "sessao", "configuracao", "parametro_config", "registro", "derivacao", "diario"]


@pytest.fixture
def banco_v01(tmp_path):
    destino = tmp_path / "dados"
    shutil.copytree(FIXTURE, destino)
    for p in destino.rglob("*"):
        p.chmod(0o644 if p.is_file() else 0o755)
    return destino / "jarvis.db"


def _dump(caminho, tabelas=TABELAS_V01):
    con = sqlite3.connect(caminho)
    try:
        return {t: con.execute(f"SELECT * FROM {t} ORDER BY rowid").fetchall() for t in tabelas}
    finally:
        con.close()


def _uv(caminho):
    con = sqlite3.connect(caminho)
    try:
        return con.execute("PRAGMA user_version").fetchone()[0]
    finally:
        con.close()


def test_detecta_fixture_como_v01(banco_v01):
    antes = sha256_de(banco_v01)
    assert migracao.detectar(banco_v01).estado == "v01"
    assert sha256_de(banco_v01) == antes  # detecção não escreve


def test_banco_novo_nasce_v2(tmp_path):
    caminho = tmp_path / "jarvis.db"
    assert migracao.detectar(caminho).estado == "novo"
    assert migracao.preparar(caminho) is None
    assert _uv(caminho) == 2
    assert migracao.detectar(caminho).estado == "v02"


def test_v01_real_migra_preservando(banco_v01):
    antes = _dump(banco_v01)
    cofre_antes = {p.name: sha256_de(p) for p in (banco_v01.parent / "cofre").rglob("*") if p.is_file()}
    backup = migracao.preparar(banco_v01)
    assert backup is not None and backup.exists()
    assert _uv(banco_v01) == 2
    assert migracao.detectar(banco_v01).estado == "v02"
    assert _dump(banco_v01) == antes
    assert {p.name: sha256_de(p) for p in (banco_v01.parent / "cofre").rglob("*") if p.is_file()} == cofre_antes


def test_backup_consistente(banco_v01):
    antes = _dump(banco_v01)
    backup = migracao.migrar_0_para_2(banco_v01)
    assert backup.name.startswith("jarvis.antes-v02-")
    con = sqlite3.connect(backup)
    try:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("PRAGMA user_version").fetchone()[0] == 0
    finally:
        con.close()
    assert _dump(backup) == antes


def test_idempotente(banco_v01):
    migracao.preparar(banco_v01)
    pasta = banco_v01.parent
    backups = sorted(pasta.glob("*.antes-v02-*.db"))
    sha = sha256_de(banco_v01)
    assert migracao.preparar(banco_v01) is None
    assert sorted(pasta.glob("*.antes-v02-*.db")) == backups
    assert sha256_de(banco_v01) == sha


def test_falha_no_meio_reverte(banco_v01, monkeypatch):
    comandos = list(migracao.COMANDOS_0_PARA_2)
    monkeypatch.setattr(migracao, "COMANDOS_0_PARA_2", [comandos[0], "CREATE TABLE quebra (", *comandos[1:]])
    with pytest.raises(migracao.ErroMigracao, match="desfeita"):
        migracao.migrar_0_para_2(banco_v01)
    assert _uv(banco_v01) == 0
    con = sqlite3.connect(banco_v01)
    try:
        assert con.execute("SELECT name FROM sqlite_master WHERE name = 'aprovacao'").fetchone() is None
    finally:
        con.close()
    assert list(banco_v01.parent.glob("*.antes-v02-*.db"))
    assert migracao.detectar(banco_v01).estado == "v01"


def test_versao_desconhecida_recusada(banco_v01):
    con = sqlite3.connect(banco_v01)
    con.execute("PRAGMA user_version = 99")
    con.close()
    sha = sha256_de(banco_v01)
    with pytest.raises(migracao.ErroVersaoBanco, match="não foi alterado"):
        migracao.preparar(banco_v01)
    assert sha256_de(banco_v01) == sha
    assert not list(banco_v01.parent.glob("*.antes-v02-*.db"))


def test_impressao_desconhecida_recusada(banco_v01):
    con = sqlite3.connect(banco_v01)
    con.execute("CREATE TABLE estranha (x)")
    con.commit()
    con.close()
    sha = sha256_de(banco_v01)
    with pytest.raises(migracao.ErroVersaoBanco, match="estranha"):
        migracao.preparar(banco_v01)
    assert sha256_de(banco_v01) == sha


def test_gatilhos_v2(tmp_path):
    caminho = tmp_path / "jarvis.db"
    migracao.criar_v2(caminho)
    con = sqlite3.connect(caminho)
    try:
        con.execute("INSERT INTO sessao (modo, criada_em) VALUES ('investigacao', 'x')")
        con.execute("INSERT INTO configuracao (sessao, nome, nivel, criada_em) VALUES (1, 'c', 'declarada', 'x')")
        with pytest.raises(sqlite3.DatabaseError, match="Configuração"):
            con.execute("UPDATE configuracao SET nome = 'y'")
        with pytest.raises(sqlite3.DatabaseError, match="recomendação existente"):
            con.execute("INSERT INTO aprovacao (sessao, recomendacao, nivel, escopo, momento) "
                        "VALUES (1, 'R-0001', 'B', '{}', 'x')")
    finally:
        con.close()
