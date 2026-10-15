import numpy as np
import pytest

from jarvis import calculos
from jarvis.referencia import ref001
from jarvis.rew_texto import RespostaFrequencia


def _vias():
    f = ref001.grade_frequencias()
    lp, hp = ref001.linkwitz_riley_4(f, 3000.0)
    return f, lp, hp


def _resp(f, h, atraso_s=0.0):
    h = h * np.exp(-2j * np.pi * f * atraso_s)
    return RespostaFrequencia(f, 20 * np.log10(np.abs(h) + 1e-15), np.rad2deg(np.angle(h)))


def test_lr4_vale_menos_6_db_no_cruzamento():
    lp, hp = ref001.linkwitz_riley_4(np.array([3000.0]), 3000.0)
    assert 20 * np.log10(abs(lp[0])) == pytest.approx(-6.0206, abs=1e-3)
    assert 20 * np.log10(abs(hp[0])) == pytest.approx(-6.0206, abs=1e-3)


def test_soma_lr4_correta_e_plana():
    f, lp, hp = _vias()
    s = calculos.soma_complexa(_resp(f, lp), _resp(f, hp))
    assert np.max(np.abs(s["nivel_db"])) <= 0.01


def test_soma_lr4_invertida_tem_vale_profundo():
    f, lp, hp = _vias()
    s = calculos.soma_complexa(_resp(f, lp), _resp(f, hp), inverter_b=True)
    assert min(s["nivel_db"]) <= -30


def test_diferenca_fase_polaridade_constante():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, -hp)
    sob = calculos.sobreposicao(a, b, 6.0)
    d = calculos.diferenca_fase(a, b, sob["indices"])
    assert abs(d["media_graus"]) == pytest.approx(180.0, abs=0.01)
    assert d["dispersao_graus"] < 0.01
    assert abs(d["atraso_equivalente_ms"]) < 1e-6


def test_atraso_aparece_como_inclinacao():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, hp, atraso_s=0.0002)  # tweeter 0,2 ms atrasado
    sob = calculos.sobreposicao(a, b, 6.0)
    d = calculos.diferenca_fase(a, b, sob["indices"])
    assert d["atraso_equivalente_ms"] == pytest.approx(0.2, abs=0.005)
    assert d["dispersao_graus"] > 15  # diferença não é constante


def test_soma_potencias_e_vale_relativo():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, -hp)
    soma = calculos.soma_complexa(a, b)
    pot = calculos.soma_potencias(a, b)
    sob = calculos.sobreposicao(a, b, 6.0)
    v = calculos.vale_relativo(soma["nivel_db"], pot["nivel_db"], soma["freq_hz"], sob["indices"])
    assert v["min_relativo_db"] < -30
    assert v["freq_hz"] == pytest.approx(3000, rel=0.01)


def test_referencia_temporal():
    ok = {"referencia_temporal": {"tipo": "loopback", "id": "x"}, "taxa_amostragem": 48000,
          "posicao_microfone": "P1"}
    assert calculos.referencia_temporal([ok, ok])["compativel"]
    sem = {**ok, "referencia_temporal": {"tipo": "nenhuma"}}
    r = calculos.referencia_temporal([ok, sem])
    assert not r["compativel"] and r["motivos"]
    outra_pos = {**ok, "posicao_microfone": "P2"}
    assert not calculos.referencia_temporal([ok, outra_pos])["compativel"]


def test_qualidade_basica():
    f, lp, _ = _vias()
    assert calculos.qualidade_basica(_resp(f, lp))["aprovada"]
    estreita = RespostaFrequencia(f[200:260], np.zeros(60), np.zeros(60))
    assert not calculos.qualidade_basica(estreita)["aprovada"]


def test_comparacao_interpola_grades_diferentes():
    f, lp, hp = _vias()
    prev = calculos.soma_complexa(_resp(f, lp), _resp(f, hp))
    f2 = np.geomspace(20, 20000, 300)
    plano = RespostaFrequencia(f2, np.zeros(300), np.zeros(300))
    c = calculos.comparacao(prev, plano, (1000.0, 10000.0))
    assert c["rms_db"] < 0.02 and c["pontos"] > 0


def test_reprodutivel():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, -hp)
    assert calculos.soma_complexa(a, b) == calculos.soma_complexa(a, b)
