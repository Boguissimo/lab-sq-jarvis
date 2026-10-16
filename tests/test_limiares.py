"""Testes dos limiares centralizados do JV-V02 (ADR-211)."""

import pytest

from jarvis import limiares


def test_todo_limiar_tem_campos_e_origem():
    for nome, lim in limiares.LIMIARES.items():
        assert set(lim) == {"valor", "unidade", "provisorio", "origem"}, nome
        assert isinstance(lim["valor"], (int, float)), nome
        assert isinstance(lim["provisorio"], bool), nome
        assert lim["unidade"].strip(), nome
        assert lim["origem"].strip(), nome


def test_valores_da_spec():
    assert limiares.valor("irregularidade_aviso_db") == 0.5
    assert limiares.valor("irregularidade_reprovada_db") == 1.5
    assert limiares.valor("irregularidade_pontos_por_oitava_min") == 24
    assert limiares.valor("detector_media_db") == 1.0
    assert limiares.valor("detector_banda_db") == 1.5
    assert limiares.valor("detector_fator_sigma") == 3.0
    assert limiares.valor("etapa_deficit_objetivo_db") == 3.0
    assert limiares.valor("seg04_passo_max_db") == 1.5


@pytest.mark.parametrize("nome", ["irregularidade_reprovada_db", "detector_banda_db", "seg04_passo_max_db",
                                  "etapa_deficit_objetivo_db", "fase_pontos_min"])
def test_provisorios_marcados(nome):
    assert limiares.LIMIARES[nome]["provisorio"] is True


def test_rotulo_exibe_provisorio():
    assert limiares.rotulo("seg04_passo_max_db") == "limite provisório de 1,5 dB"
    assert limiares.rotulo("faixa_analise_min_hz", 0) == "limite de 200 Hz"


def test_snapshot_e_copia_independente():
    s = limiares.snapshot("detector_media_db")
    assert s["versao"] == limiares.VERSAO
    assert list(s["limiares"]) == ["detector_media_db"]
    s["limiares"]["detector_media_db"]["valor"] = 99
    assert limiares.valor("detector_media_db") == 1.0
    assert set(limiares.snapshot()["limiares"]) == set(limiares.LIMIARES)
