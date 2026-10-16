"""Regras de segurança e admissibilidade (ADR-204; FR-210, FR-211; critério 4 do plano)."""

import pytest

from jarvis import seguranca as seg

EQUIP = [{"canal": "tweeter_esq", "estado": "confirmado", "potencia_rms_w": 30, "fs_hz": 900.0},
         {"canal": "medio_esq", "estado": "informado", "potencia_rms_w": 60, "fs_hz": 70.0}]


@pytest.mark.parametrize("alteracao,classe", [
    ({"tipo": "polaridade"}, seg.NAO_SENSIVEL),
    ({"tipo": "atraso"}, seg.NAO_SENSIVEL),
    ({"tipo": "reforco_eq", "ganho_db": 1.0}, seg.CRESCENTE),
    ({"tipo": "corte_eq", "ganho_db": -2.0}, seg.DECRESCENTE),
    ({"tipo": "ganho", "ganho_db": 1.0}, seg.CRESCENTE),
    ({"tipo": "ganho", "ganho_db": -1.0}, seg.DECRESCENTE),
    ({"tipo": "ganho"}, seg.CRESCENTE),  # direção desconhecida: conservador
    ({"tipo": "passa_altas", "de_hz": 2000, "para_hz": 1800}, seg.CRESCENTE),
    ({"tipo": "passa_altas", "de_hz": 2000, "para_hz": 2500}, seg.DECRESCENTE),
    ({"tipo": "inclinacao", "de_db_oit": 24, "para_db_oit": 12}, seg.CRESCENTE),
    ({"tipo": "inclinacao", "de_db_oit": 12, "para_db_oit": 24}, seg.DECRESCENTE),
])
def test_classificacao(alteracao, classe):
    assert seg.classificar(alteracao) == classe


def test_classificacao_recusa_tipo_desconhecido():
    with pytest.raises(seg.AlteracaoInvalida):
        seg.classificar({"tipo": "volume"})


def test_avaliar_estrutura():
    res = seg.avaliar({"canal": "tweeter_esq", "tipo": "reforco_eq", "ganho_db": 1.0}, EQUIP)
    assert [r["regra"] for r in res] == list(seg.REGRAS)
    for r in res:
        assert set(r) >= {"regra", "resultado", "motivo", "provisorio"}
        assert r["resultado"] in (seg.APROVADA, seg.BLOQUEADA, seg.NAO_VERIFICAVEL, seg.NAO_SE_APLICA)


def _admissibilidade(alteracao, equip=EQUIP):
    return seg.admissibilidade(seg.classificar(alteracao), seg.avaliar(alteracao, equip))


def test_admissibilidade():
    # 1. risco crescente sem dado confirmado: bloqueada, sem aprovação disponível
    a = _admissibilidade({"canal": "tweeter_esq", "tipo": "reforco_eq", "ganho_db": 1.0}, [])
    assert a["admissivel"] is False and a["estado"] == "bloqueada" and not a["exige_aprovacao_b"]
    assert "não recomendada" in a["motivo"] and a["falta"]
    # 2. risco decrescente com "não verificável": admitida com lista e aviso
    d = _admissibilidade({"canal": "medio_esq", "tipo": "corte_eq", "ganho_db": -2.0})
    assert d["admissivel"] is True and d["exige_aprovacao_b"]
    assert "SEG-12" in d["nao_verificadas"] and d["aviso"] == seg.AVISO_EFEITOS_COLATERAIS
    # 3. não sensível: admitida com SEG-08 e SEG-11
    p = seg.avaliar({"canal": "tweeter_esq", "tipo": "polaridade"})
    estados = {r["regra"]: r["resultado"] for r in p}
    assert estados["SEG-08"] == estados["SEG-11"] == seg.APROVADA
    assert all(v == seg.NAO_SE_APLICA for k, v in estados.items() if k not in ("SEG-08", "SEG-11"))
    n = seg.admissibilidade(seg.NAO_SENSIVEL, p)
    assert n["admissivel"] and not n["exige_aprovacao_b"] and not n["nao_verificadas"]
    # 4. regra bloqueada bloqueia mesmo no risco decrescente
    bloq = [seg.resultado("SEG-01", seg.BLOQUEADA, "abaixo do mínimo", falta="x")]
    assert seg.admissibilidade(seg.DECRESCENTE, bloq)["admissivel"] is False


def test_seg12_planejado_nao_alimenta_regra():
    for estado in ("planejado", "informado"):
        res = seg.avaliar({"canal": "tweeter_esq", "tipo": "reforco_eq", "ganho_db": 1.0},
                          [{"canal": "tweeter_esq", "estado": estado}])
        seg12 = next(r for r in res if r["regra"] == "SEG-12")
        assert seg12["resultado"] == seg.NAO_VERIFICAVEL and seg12["falta"]


def test_funcoes_puras():
    alt = {"canal": "tweeter_esq", "tipo": "reforco_eq", "ganho_db": 1.0}
    copia = dict(alt)
    assert seg.avaliar(alt, EQUIP) == seg.avaliar(alt, EQUIP)
    assert alt == copia
    assert seg.VERSAO == "0.4.0"
