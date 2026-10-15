import numpy as np

from jarvis import calculos, regras
from jarvis.referencia import ref001
from jarvis.rew_texto import RespostaFrequencia

IDS = {"vale": "C-1", "fase": "C-2", "potencias": "C-3", "sobreposicao": "C-4"}


def _caso(inverter_tweeter: bool):
    f = ref001.grade_frequencias()
    lp, hp = ref001.linkwitz_riley_4(f, 3000.0)
    hp = -hp if inverter_tweeter else hp
    a = RespostaFrequencia(f, 20 * np.log10(np.abs(lp)), np.rad2deg(np.angle(lp)))
    b = RespostaFrequencia(f, 20 * np.log10(np.abs(hp)), np.rad2deg(np.angle(hp)))
    soma = lp + hp
    s = RespostaFrequencia(f, 20 * np.log10(np.abs(soma) + 1e-12), np.rad2deg(np.angle(soma)))
    sob = calculos.sobreposicao(a, b, regras.LIMIARES["sobreposicao_max_diferenca_db"])
    pot = calculos.soma_potencias(a, b)
    vale = calculos.vale_relativo(s.nivel_db.tolist(), pot["nivel_db"], s.freq_hz.tolist(), sob["indices"])
    fase = calculos.diferenca_fase(a, b, sob["indices"])
    return sob, vale, fase


def test_polaridade_invertida_vem_em_primeiro():
    r = regras.avaliar(*_caso(True), IDS)
    assert r["sugestao"] == "teste_polaridade"
    assert [i["regra"][:7] for i in r["indicios"]] == ["Regra 1", "Regra 2"]
    assert r["hipoteses"][0]["enunciado"].startswith("Polaridade invertida")
    assert r["hipoteses"][1]["avaliacao"] == "pouco provável"
    # cada indício cita os cálculos de origem
    assert "[C-1]" in r["indicios"][0]["explicacao"] and "[C-2]" in r["indicios"][1]["explicacao"]


def test_sem_cancelamento_nada_a_alterar():
    r = regras.avaliar(*_caso(False), IDS)
    assert r["sugestao"] == "nada_a_alterar" and not r["hipoteses"]


def test_sem_fase_pede_dados():
    sob, vale, _ = _caso(True)
    r = regras.avaliar(sob, vale, None, IDS)
    assert r["sugestao"] == "solicitar_dados"


def test_limiares_declarados_provisorios():
    assert regras.LIMIARES_PROVISORIOS is True
