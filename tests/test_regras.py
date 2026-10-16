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


def test_i3_reordena_hipoteses():
    """Com vale na via isolada e sem oposição constante, interferência vem antes de polaridade (FR-204)."""
    sob = {"existe": True, "faixa_hz": [2000, 4500], "indices": [1, 2, 3]}
    vale = {"min_relativo_db": -8.0, "freq_hz": 5000.0, "soma_no_vale_db": 70.0, "potencias_no_vale_db": 78.0}
    fase = {"media_graus": 40.0, "dispersao_graus": 30.0, "atraso_equivalente_ms": 0.0, "faixa_hz": [2000, 4500]}
    ids = {"vale": "C-1", "potencias": "C-2", "sobreposicao": "C-3", "fase": "C-4", "vales_individuais_via_b": "C-5"}
    vi = {"via_a": {"vales": []}, "via_b": {"vales": [{"freq_hz": 5000.0, "profundidade_db": 12, "largura_oitava": 0.02}]}}
    r = regras.avaliar(sob, vale, fase, ids, vales_individuais=vi)
    assert [h["enunciado"].split()[0] for h in r["hipoteses"]] == ["Interferência", "Polaridade"]
    assert r["sugestao"] == "solicitar_dados"
    # sem I-3 o resultado é o das regras 1.0
    from jarvis import regras_v1_0
    assert regras.avaliar(sob, vale, fase, ids)["sugestao"] == regras_v1_0.avaliar(sob, vale, fase, ids)["sugestao"]
