"""Oráculos analíticos independentes do gerador (SC-208, E3; JV-T221).

Vetores calculados à mão, sem passar por ``referencia/modelo.py``: identidade de quadratura, LR4 no
cruzamento e atraso puro. Valem só no domínio simulado.
"""

import numpy as np
import pytest

from jarvis import calculos
from jarvis.rew_texto import RespostaFrequencia

F = 1000.0 * 2.0 ** (np.arange(-96, 97) / 48.0)  # 250 Hz a 4 kHz, 48 pontos por oitava


def _resp(nivel_db, fase_graus):
    return RespostaFrequencia(F, np.full(F.size, float(nivel_db)) if np.isscalar(nivel_db) else nivel_db,
                              np.full(F.size, float(fase_graus)) if np.isscalar(fase_graus) else fase_graus)


def test_quadratura_soma_igual_a_potencias():
    """Duas vias iguais a 90° somam exatamente a soma de potências: deficit 0, sem alinhamento em fase."""
    a, b = _resp(80.0, 0.0), _resp(80.0, 90.0)
    soma = np.array(calculos.soma_complexa(a, b)["nivel_db"])
    pot = np.array(calculos.soma_potencias(a, b)["nivel_db"])
    assert np.allclose(soma, pot, atol=1e-9)
    assert np.allclose(pot, 80.0 + 10 * np.log10(2), atol=1e-9)
    em_fase = np.array(calculos.soma_complexa(a, _resp(80.0, 0.0))["nivel_db"])
    assert np.allclose(em_fase - soma, 10 * np.log10(2), atol=1e-9)  # quadratura não é soma em fase


def test_lr4_no_cruzamento():
    """No cruzamento, LR4: cada via a −6,02 dB e em fase; a soma fica em 0 dB."""
    a, b = _resp(-20 * np.log10(2), 0.0), _resp(-20 * np.log10(2), 0.0)
    assert np.allclose(calculos.soma_complexa(a, b)["nivel_db"], 0.0, atol=1e-9)
    invertida = calculos.soma_complexa(a, b, inverter_b=True)["nivel_db"]
    assert max(invertida) < -200  # cancelamento completo


@pytest.mark.parametrize("atraso_ms", [0.05, 0.1, -0.08])
def test_atraso_puro(atraso_ms):
    """Atraso puro de B: diferença de fase linear, atraso equivalente igual ao injetado."""
    fase_b = -360.0 * F * atraso_ms / 1000.0
    a, b = _resp(80.0, 0.0), _resp(80.0, ((fase_b + 180) % 360) - 180)
    d = calculos.diferenca_fase(a, b, list(range(F.size)))
    assert d["calculavel"] and d["atraso_equivalente_ms"] == pytest.approx(atraso_ms, abs=1e-6)
