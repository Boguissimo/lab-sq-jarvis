"""Testes metamórficos (SC-208, E3; JV-T221): transformações que não podem mudar o resultado.

- ganho global aplicado às duas medições não muda σ̂ nem o detector de mudança;
- trocar as vias não muda soma, soma de potências nem o vale relativo.
(O deficit no cruzamento entra com a JV-T232.)
"""

import numpy as np
import pytest

from jarvis import calculos
from jarvis.referencia import modelo
from jarvis.rew_texto import RespostaFrequencia

F = modelo.grade_log()
H = modelo.resposta_via({"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}], "reflexoes": [{"g": 0.5, "tau_ms": 0.3}]}, F)


def _ganho(r, g):
    return RespostaFrequencia(r.freq_hz, r.nivel_db + g, r.fase_graus)


@pytest.mark.parametrize("g", [-12.0, 6.0, 20.0])
def test_ganho_global_nao_muda_sigma(g):
    r = modelo.adquirir(H, F, {"ruido_sigma_db": 0.7}, semente=3, quantizar=False)
    assert calculos.irregularidade(_ganho(r, g), "nenhuma")["sigma_db"] == pytest.approx(
        calculos.irregularidade(r, "nenhuma")["sigma_db"], abs=1e-9)


@pytest.mark.parametrize("g", [-12.0, 6.0])
def test_ganho_global_nao_muda_detector(g):
    a = modelo.adquirir(H, F, {"ruido_sigma_db": 0.5}, semente=4, quantizar=False)
    d = modelo.adquirir(H * 10 ** (2.0 / 20), F, {"ruido_sigma_db": 0.5}, semente=5, quantizar=False)
    sa, sd = (calculos.irregularidade(x, "nenhuma")["sigma_db"] for x in (a, d))
    base = calculos.detector_mudanca_via(a, d, sa, sd, calculos.faixa_util(a))
    ga, gd = _ganho(a, g), _ganho(d, g)
    trans = calculos.detector_mudanca_via(ga, gd, sa, sd, calculos.faixa_util(ga))
    assert trans["resultado"] == base["resultado"] == "mudanca_detectada"
    assert trans["media_db"] == pytest.approx(base["media_db"], abs=1e-9)


def test_trocar_vias_nao_muda_soma_nem_potencias():
    ha = modelo.resposta_via({"filtros": [{"tipo": "lr4_pb", "fc_hz": 3000.0}]}, F)
    hb = modelo.resposta_via({"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}], "atraso_dsp_ms": 0.12}, F)
    a, b = modelo.adquirir(ha, F, quantizar=False), modelo.adquirir(hb, F, quantizar=False)
    assert np.allclose(calculos.soma_complexa(a, b)["nivel_db"], calculos.soma_complexa(b, a)["nivel_db"])
    assert np.allclose(calculos.soma_potencias(a, b)["nivel_db"], calculos.soma_potencias(b, a)["nivel_db"])
    assert calculos.sobreposicao(a, b, 6.0)["indices"] == calculos.sobreposicao(b, a, 6.0)["indices"]
