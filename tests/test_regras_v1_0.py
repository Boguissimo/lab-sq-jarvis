"""Regras 1.0 congeladas (JV-T208; ADR-210, INV-211).

A referência é o que o próprio V01 gravou na fixture do banco, não o `regras.py` atual, que vai mudar.
"""

import json
import sqlite3
from pathlib import Path

from jarvis import regras_v1_0

FIXTURE = Path(__file__).parent / "dados" / "banco-v01" / "jarvis.db"


def _registros(con, sessao, tipo):
    return [json.loads(r[0]) for r in con.execute(
        "SELECT dados FROM registro WHERE sessao = ? AND tipo = ? ORDER BY id", (sessao, tipo))]


def test_versao_congelada():
    assert regras_v1_0.VERSAO == "1.0"
    assert regras_v1_0.LIMIARES["cancelamento_min_db"] == 6.0


def test_reproduz_o_que_o_v01_gravou():
    con = sqlite3.connect(f"file:{FIXTURE}?mode=ro", uri=True)
    try:
        for sessao in (1, 2):
            calcs = {c["nome"]: c for c in _registros(con, sessao, "calculo")}
            ids = {r[1]: r[0] for r in con.execute(
                "SELECT id, json_extract(dados, '$.nome') FROM registro WHERE sessao = ? AND tipo = 'calculo'",
                (sessao,))}
            ids_regras = {"vale": ids["vale_relativo"], "fase": ids["diferenca_fase"],
                          "potencias": ids["soma_potencias"], "sobreposicao": ids["sobreposicao"]}
            r = regras_v1_0.avaliar(calcs["sobreposicao"]["resultado"], calcs["vale_relativo"]["resultado"],
                                    calcs["diferenca_fase"]["resultado"], ids_regras)
            gravados = _registros(con, sessao, "indicio")
            assert [i["titulo"] for i in r["indicios"]] == [g["titulo"] for g in gravados]
            assert [i["explicacao"] for i in r["indicios"]] == [g["explicacao"] for g in gravados]
            assert [h["enunciado"] for h in r["hipoteses"]] == [
                h["enunciado"] for h in _registros(con, sessao, "hipotese")]
            assert r["sugestao"] == "teste_polaridade"
    finally:
        con.close()
