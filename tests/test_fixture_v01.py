"""Conferência da fixture do banco do V01 (JV-T205; ADR-207, emenda E2)."""

import sqlite3
from pathlib import Path

from jarvis.persistencia import sha256_de
from jarvis.referencia.ref001 import PASTA_PADRAO

FIXTURE = Path(__file__).parent / "dados" / "banco-v01"


def _normalizado(caminho: Path) -> bytes:
    return caminho.read_bytes().replace(b"\r\n", b"\n")


def test_fixture_e_banco_v01_versao_0():
    con = sqlite3.connect(f"file:{FIXTURE / 'jarvis.db'}?mode=ro", uri=True)
    try:
        assert con.execute("PRAGMA user_version").fetchone()[0] == 0
        assert con.execute("SELECT COUNT(*) FROM sessao").fetchone()[0] == 2
        assert con.execute("SELECT name FROM sqlite_master WHERE name = 'aprovacao'").fetchone() is None
        inventario = {r[0] for r in con.execute("SELECT sha256 FROM arquivo_original")}
    finally:
        con.close()
    no_cofre = {p.name for p in (FIXTURE / "cofre").rglob("*") if p.is_file()}
    assert inventario == no_cofre and len(no_cofre) == 4


def test_originais_do_cofre_sao_os_arquivos_do_ref001a():
    ref = {_normalizado(PASTA_PADRAO / n) for n in ("medio.txt", "tweeter.txt", "soma-antes.txt", "soma-depois.txt")}
    for arq in (FIXTURE / "cofre").rglob("*"):
        if arq.is_file():
            assert sha256_de(arq) == arq.name  # bytes preservados
            assert _normalizado(arq) in ref    # conteúdo do REF-001-A (fim de linha à parte)
