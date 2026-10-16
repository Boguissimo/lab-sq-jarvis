"""Modelo físico e camada de aquisição (JV-T210; ADR-201, INV-208)."""

import numpy as np
import pytest

from jarvis.referencia import modelo, ref001

VIA_A = {"alto_falante": {"tipo": "ressonante", "fs_hz": 60.0, "q": 0.8, "rolagem_hz": 9000.0},
         "filtros": [{"tipo": "lr4_pb", "fc_hz": 2800.0}], "distancia_m": 1.02, "nivel_db": 85.0}
VIA_B = {"filtros": [{"tipo": "lr4_pa", "fc_hz": 2800.0}, {"tipo": "peq", "f0_hz": 5000.0, "ganho_db": -2.0, "q": 2.0}],
         "polaridade_fiacao": -1, "distancia_m": 0.98, "atraso_dsp_ms": 0.05,
         "reflexoes": [{"g": 0.3, "tau_ms": 0.6}], "nivel_db": 86.0}


def test_coerencia_fisica():
    f = modelo.grade_log()
    ha, hb = modelo.resposta_via(VIA_A, f), modelo.resposta_via(VIA_B, f)
    s = modelo.soma(ha, hb)
    assert np.max(np.abs(s - (ha + hb))) < 1e-9 * np.max(np.abs(s))
    # nível e fase de cada arquivo saem do mesmo H (sem ruído nem quantização)
    for h in (ha, hb, s):
        r = modelo.adquirir(h, f, quantizar=False)
        x = 10 ** (r.nivel_db / 20.0) * np.exp(1j * np.deg2rad(r.fase_graus))
        assert np.max(np.abs(x - h) / np.abs(h)) < 1e-9


def test_reproduz_ref001a():
    """O modelo reconstrói o REF-001-A, que continua gerado por ref001.py (INV-213)."""
    f = ref001.grade_frequencias()
    assert np.allclose(f, modelo.grade_log())
    medio = {"filtros": [{"tipo": "lr4_pb", "fc_hz": 3000.0}], "distancia_m": 1.0}
    tweeter = {"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}], "distancia_m": 1.0, "polaridade_fiacao": -1}
    ref = ref001.respostas()
    hm, ht = modelo.resposta_via(medio, f), modelo.resposta_via(tweeter, f)
    for nome, h in (("medio", hm), ("tweeter", ht), ("soma-antes", hm + ht)):
        r = modelo.adquirir(h, f, quantizar=False)
        assert np.allclose(r.nivel_db, ref[nome].nivel_db, atol=1e-9)


def test_polaridade_dsp_compensa_fiacao():
    f = modelo.grade_log()
    base = {"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}]}
    h1 = modelo.resposta_via({**base, "polaridade_fiacao": -1, "polaridade_dsp_graus": 180}, f)
    assert np.allclose(h1, modelo.resposta_via(base, f))


def test_peq_ganho_no_centro():
    h = modelo.peq(np.array([1000.0]), 1000.0, 3.0, 4.0)
    assert 20 * np.log10(abs(h[0])) == pytest.approx(3.0, abs=1e-9)


def test_ruido_deterministico_e_com_sigma():
    f = modelo.grade_log()
    h = modelo.resposta_via(VIA_A, f)
    aq = {"ruido_sigma_db": 1.0}
    r1 = modelo.adquirir(h, f, aq, semente=7, quantizar=False)
    r2 = modelo.adquirir(h, f, aq, semente=7, quantizar=False)
    r3 = modelo.adquirir(h, f, aq, semente=8, quantizar=False)
    assert np.array_equal(r1.nivel_db, r2.nivel_db) and not np.array_equal(r1.nivel_db, r3.nivel_db)
    erro = r1.nivel_db - modelo.adquirir(h, f, quantizar=False).nivel_db
    assert np.std(erro) == pytest.approx(1.0, rel=0.1)
    with pytest.raises(ValueError, match="semente"):
        modelo.adquirir(h, f, aq)


def test_aquisicao_nao_altera_modelo():
    f = modelo.grade_log()
    h = modelo.resposta_via(VIA_B, f)
    copia = h.copy()
    r = modelo.adquirir(h, f, {"ganho_entrada_db": 2.0, "posicao": {"delta_distancia_m": 0.1,
                                                                     "reflexoes": [{"g": 0.5, "tau_ms": 1.0}]}},
                        quantizar=False)
    assert np.array_equal(h, copia)
    sem = modelo.adquirir(h, f, quantizar=False)
    assert not np.allclose(r.nivel_db, sem.nivel_db)
    so_ganho = modelo.adquirir(h, f, {"ganho_entrada_db": 2.0}, quantizar=False)
    assert np.allclose(so_ganho.nivel_db - sem.nivel_db, 2.0, atol=1e-9)
