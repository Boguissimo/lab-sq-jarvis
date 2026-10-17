"""Regras de segurança e admissibilidade (ADR-204; FR-210, FR-211; critério 4 do plano)."""

import random

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


# ---- JV-T224: regras por caso (permitido / limítrofe / proibido / dado ausente) ----------------------------

CONF = {"canal": "c", "estado": "confirmado", "potencia_rms_w": 50.0, "fs_hz": 80.0,
        "passa_altas_min_hz": 2500.0, "inclinacao_min_db_oit": 12.0}


def _r(regra, alteracao, equip=CONF):
    return next(x for x in seg.avaliar({"canal": "c", **alteracao}, [equip] if equip else []) if x["regra"] == regra)


def _estado(regra, alteracao, equip=CONF):
    return _r(regra, alteracao, equip)["resultado"]


@pytest.mark.parametrize("para,esperado", [(3000.0, seg.APROVADA), (2500.0, seg.APROVADA),
                                           (2499.0, seg.BLOQUEADA), (1000.0, seg.BLOQUEADA)])
def test_seg01(para, esperado):
    assert _estado("SEG-01", {"tipo": "passa_altas", "de_hz": 3200.0, "para_hz": para}) == esperado


@pytest.mark.parametrize("para,esperado", [(24.0, seg.APROVADA), (12.0, seg.APROVADA), (6.0, seg.BLOQUEADA)])
def test_seg01_inclinacao(para, esperado):
    assert _estado("SEG-01", {"tipo": "inclinacao", "de_db_oit": 24.0, "para_db_oit": para}) == esperado


def test_seg01_sem_dado_confirmado_nao_aprova():
    alt = {"tipo": "passa_altas", "de_hz": 3000.0, "para_hz": 2800.0}
    for equip in (None, {**CONF, "estado": "informado"}, {**CONF, "estado": "planejado"},
                  {k: v for k, v in CONF.items() if k != "passa_altas_min_hz"},
                  {**CONF, "passa_altas_min_hz": 0}, {**CONF, "passa_altas_min_hz": True}):
        r = _r("SEG-01", alt, equip)
        assert r["resultado"] == seg.NAO_VERIFICAVEL and r["falta"]
    a = seg.admissibilidade(seg.CRESCENTE, seg.avaliar({"canal": "c", **alt}, []))
    assert a["admissivel"] is False  # baixar o corte sem dado: bloqueado


def test_seg01_nao_se_aplica_a_ganho():
    assert _estado("SEG-01", {"tipo": "ganho", "ganho_db": 1.0}) == seg.NAO_SE_APLICA


@pytest.mark.parametrize("est,esperado", [(30.0, seg.APROVADA), (50.0, seg.APROVADA), (50.5, seg.BLOQUEADA)])
def test_seg03(est, esperado):
    assert _estado("SEG-03", {"tipo": "ganho", "ganho_db": 1.0, "potencia_estimada_w": est}) == esperado


def test_seg03_sem_dado_nao_aprova():
    alt = {"tipo": "ganho", "ganho_db": 1.0}
    assert _estado("SEG-03", alt) == seg.NAO_VERIFICAVEL  # sem potência estimada
    for equip in (None, {**CONF, "estado": "planejado"}, {**CONF, "potencia_rms_w": None}):
        assert _estado("SEG-03", {**alt, "potencia_estimada_w": 10.0}, equip) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-03", {**alt, "potencia_estimada_w": -1.0}) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-03", {"tipo": "passa_altas", "de_hz": 3000.0, "para_hz": 3500.0}) == seg.NAO_SE_APLICA


@pytest.mark.parametrize("tipo,g,esperado", [("ganho", 1.0, seg.APROVADA), ("ganho", 1.5, seg.APROVADA),
                                             ("ganho", 1.6, seg.BLOQUEADA), ("reforco_eq", 1.5, seg.APROVADA),
                                             ("reforco_eq", 1.51, seg.BLOQUEADA), ("ganho", -6.0, seg.NAO_SE_APLICA)])
def test_seg04(tipo, g, esperado):
    r = _r("SEG-04", {"tipo": tipo, "ganho_db": g})
    assert r["resultado"] == esperado and r["provisorio"] is True


def test_seg04_valor_ausente_nao_aprova():
    assert _estado("SEG-04", {"tipo": "reforco_eq"}) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-04", {"tipo": "ganho", "ganho_db": "1"}) == seg.NAO_VERIFICAVEL
    assert seg.classificar({"tipo": "ganho", "ganho_db": "1"}) == seg.CRESCENTE  # valor ilegível: conservador
    assert seg.classificar({"tipo": "passa_altas", "de_hz": "x", "para_hz": 1.0}) == seg.CRESCENTE


@pytest.mark.parametrize("g,banda,esperado", [(3.0, [3.0], seg.APROVADA), (3.0, [3.0, 0.0], seg.APROVADA),
                                              (3.0, [3.5], seg.BLOQUEADA), (3.1, [], seg.BLOQUEADA),
                                              (2.0, [], seg.APROVADA), (1.0, [-4.0], seg.APROVADA)])
def test_seg05(g, banda, esperado):
    r = _r("SEG-05", {"tipo": "reforco_eq", "ganho_db": g, "reforcos_na_banda_db": banda})
    assert r["resultado"] == esperado and r["provisorio"] is True


def test_seg05_banda_desconhecida_nao_aprova():
    assert _estado("SEG-05", {"tipo": "reforco_eq", "ganho_db": 1.0}) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-05", {"tipo": "reforco_eq", "ganho_db": 1.0, "reforcos_na_banda_db": ["x"]}) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-05", {"tipo": "ganho", "ganho_db": 1.0}) == seg.NAO_SE_APLICA


@pytest.mark.parametrize("classe", ["cancelamento", "interferencia", "variacao_espacial"])
def test_seg06(classe):
    assert _estado("SEG-06", {"tipo": "reforco_eq", "ganho_db": 1.0, "vale_classificacao": classe}) == seg.BLOQUEADA


def test_seg06_permitido_e_desconhecido():
    for c in ("equalizavel", "nao_e_vale"):
        assert _estado("SEG-06", {"tipo": "reforco_eq", "ganho_db": 1.0, "vale_classificacao": c}) == seg.APROVADA
    for c in (None, "", "talvez"):
        assert _estado("SEG-06", {"tipo": "reforco_eq", "ganho_db": 1.0, "vale_classificacao": c}) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-06", {"tipo": "corte_eq", "ganho_db": -2.0}) == seg.NAO_SE_APLICA


def test_seg13():
    base = {"tipo": "atraso", "etapa_automatizada": True}
    ok = [{"valor": 3.0, "origem": "declarado"}, {"valor": 1.0, "origem": "medição"}]
    assert _estado("SEG-13", {"tipo": "atraso"}) == seg.NAO_SE_APLICA
    assert _estado("SEG-13", base) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-13", {**base, "limites_informados": {"reforco_max_db": 3}}) == seg.NAO_VERIFICAVEL
    assert _estado("SEG-13", {**base, "limites_informados": {"x": 1}, "valores_conferencia": ok}) == seg.APROVADA
    sem = [{"valor": 1.0}]
    assert _estado("SEG-13", {**base, "limites_informados": {"x": 1}, "valores_conferencia": sem}) == seg.NAO_VERIFICAVEL
    pc = [{"valor": 1.0, "origem": "arquivo_pctool"}]
    r = _r("SEG-13", {**base, "limites_informados": {"x": 1}, "valores_conferencia": pc})
    assert r["resultado"] == seg.BLOQUEADA and "PC-Tool" in r["motivo"]


def test_seg13_bloqueada_bloqueia_alteracao_nao_sensivel():
    alt = {"canal": "c", "tipo": "atraso", "etapa_automatizada": True, "limites_informados": {"x": 1},
           "valores_conferencia": [{"valor": 1.0, "origem": "arquivo_pctool"}]}
    assert seg.admissibilidade(seg.classificar(alt), seg.avaliar(alt, [CONF]))["admissivel"] is False


def test_seg02_07_09_nao_verificaveis():
    for alt in ({"tipo": "reforco_eq", "ganho_db": 1.0}, {"tipo": "corte_eq", "ganho_db": -2.0},
                {"tipo": "passa_altas", "de_hz": 3000.0, "para_hz": 3500.0}):
        for regra in ("SEG-02", "SEG-07", "SEG-09"):
            r = _r(regra, alt)  # mesmo com equipamento confirmado e completo
            assert r["resultado"] == seg.NAO_VERIFICAVEL and r["falta"]
    assert _estado("SEG-07", {"tipo": "polaridade"}) == seg.NAO_SE_APLICA
    # qualquer reforço (risco crescente) fica bloqueado por depender delas, mesmo com tudo dentro dos limites
    alt = {"canal": "c", "tipo": "reforco_eq", "ganho_db": 1.0, "potencia_estimada_w": 10.0,
           "reforcos_na_banda_db": [], "vale_classificacao": "equalizavel"}
    res = seg.avaliar(alt, [CONF])
    assert {x["regra"] for x in res if x["resultado"] == seg.NAO_VERIFICAVEL} >= {"SEG-02", "SEG-07", "SEG-09"}
    a = seg.admissibilidade(seg.classificar(alt), res)
    assert a["admissivel"] is False and not a["exige_aprovacao_b"]


def test_seg12_planejado_nao_confirma():
    alt = {"canal": "c", "tipo": "reforco_eq", "ganho_db": 1.0, "potencia_estimada_w": 10.0,
           "reforcos_na_banda_db": [], "vale_classificacao": "equalizavel"}
    for estado in ("planejado", "informado"):
        res = seg.avaliar(alt, [{**CONF, "estado": estado}])
        por = {x["regra"]: x["resultado"] for x in res}
        assert por["SEG-12"] == por["SEG-03"] == seg.NAO_VERIFICAVEL
        assert seg.admissibilidade(seg.CRESCENTE, res)["admissivel"] is False


def test_decrescente_sem_dado_admite_com_lista_e_nao_presume_aprovacao():
    alt = {"canal": "c", "tipo": "corte_eq", "ganho_db": -2.0}
    res = seg.avaliar(alt, [])
    a = seg.admissibilidade(seg.classificar(alt), res)
    assert a["admissivel"] is True and a["exige_aprovacao_b"] and {"SEG-02", "SEG-07", "SEG-09", "SEG-12"} <= set(a["nao_verificadas"])
    assert not any(x["resultado"] == seg.APROVADA for x in res if x["regra"] in ("SEG-01", "SEG-03", "SEG-04", "SEG-05", "SEG-06"))
    # a violação de uma regra bloqueia mesmo o risco decrescente
    violacao = {"canal": "c", "tipo": "passa_altas", "de_hz": 2000.0, "para_hz": 2200.0}  # sobe, mas abaixo do mínimo
    assert seg.classificar(violacao) == seg.DECRESCENTE
    assert seg.admissibilidade(seg.DECRESCENTE, seg.avaliar(violacao, [CONF]))["admissivel"] is False


def test_provisorios_rotulados():
    por = {x["regra"]: x for x in seg.avaliar({"canal": "c", "tipo": "reforco_eq", "ganho_db": 1.0}, [CONF])}
    for regra in ("SEG-04", "SEG-05", "SEG-02", "SEG-07"):
        assert por[regra]["provisorio"] is True and "provisório" in por[regra]["limite"]
    assert "+1,5 dB" in por["SEG-04"]["limite"] and "+3 dB" in por["SEG-05"]["limite"] and "+6 dB" in por["SEG-05"]["limite"]
    for regra in ("SEG-01", "SEG-03", "SEG-06", "SEG-08", "SEG-10", "SEG-11", "SEG-12"):
        assert por[regra]["provisorio"] is False


def test_avaliar_nao_altera_entradas():
    alt = {"canal": "c", "tipo": "reforco_eq", "ganho_db": 1.0, "reforcos_na_banda_db": [1.0]}
    eq = [dict(CONF)]
    copia_alt, copia_eq = {**alt, "reforcos_na_banda_db": [1.0]}, [dict(CONF)]
    seg.avaliar(alt, eq)
    assert alt == copia_alt and eq == copia_eq


# ---- JV-T225: propriedade (SC-204, INV-203) — complementa, não substitui, os testes de limite acima --------

def _sorteia(rng):
    tipo = rng.choice(seg.TIPOS)
    alt = {"canal": "c", "tipo": tipo}
    campos = {"ganho_db": lambda: round(rng.uniform(-8, 8), 2), "de_hz": lambda: rng.choice([1500.0, 2500.0, 3500.0]),
              "para_hz": lambda: rng.choice([1000.0, 2400.0, 2500.0, 2600.0, 4000.0]),
              "de_db_oit": lambda: rng.choice([6.0, 12.0, 24.0]), "para_db_oit": lambda: rng.choice([6.0, 12.0, 24.0]),
              "potencia_estimada_w": lambda: rng.choice([5.0, 50.0, 80.0]),
              "reforcos_na_banda_db": lambda: [round(rng.uniform(-3, 5), 1) for _ in range(rng.randint(0, 3))],
              "vale_classificacao": lambda: rng.choice(["cancelamento", "equalizavel", "nao_e_vale", None])}
    for k, f in campos.items():
        if rng.random() < 0.8:
            alt[k] = f()
    equip = rng.choice([[], [CONF], [{**CONF, "estado": "planejado"}], [{**CONF, "estado": "informado"}],
                        [{k: v for k, v in CONF.items() if k != rng.choice(["potencia_rms_w", "passa_altas_min_hz"])}]])
    return alt, equip


def test_propriedade_sem_violacao():
    rng = random.Random(20261017)
    admitidas = {seg.CRESCENTE: 0, seg.DECRESCENTE: 0, seg.NAO_SENSIVEL: 0}
    for _ in range(1000):
        alt, equip = _sorteia(rng)
        classe = seg.classificar(alt)
        res = seg.avaliar(alt, equip)
        a = seg.admissibilidade(classe, res)
        estados = {x["regra"]: x["resultado"] for x in res}
        if seg.BLOQUEADA in estados.values():
            assert a["admissivel"] is False and not a["exige_aprovacao_b"], (alt, equip)  # bloqueada nunca vira admissível
        if classe == seg.CRESCENTE:
            assert a["admissivel"] is False, (alt, equip)  # SEG-02/07/09 não verificáveis (FR-212)
        if a["admissivel"]:
            admitidas[classe] += 1
            assert estados["SEG-08"] == estados["SEG-11"] == seg.APROVADA
            assert a["exige_aprovacao_b"] == (classe != seg.NAO_SENSIVEL)
        if equip and equip[0].get("estado") != "confirmado" and classe != seg.NAO_SENSIVEL:
            assert estados["SEG-12"] == seg.NAO_VERIFICAVEL
        assert all(x["resultado"] in (seg.APROVADA, seg.BLOQUEADA, seg.NAO_VERIFICAVEL, seg.NAO_SE_APLICA) for x in res)
    assert admitidas[seg.DECRESCENTE] > 0 and admitidas[seg.NAO_SENSIVEL] > 0  # o sorteio exercita o lado admissível
