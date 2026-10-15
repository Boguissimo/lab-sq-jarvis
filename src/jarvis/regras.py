"""Regras de diagnóstico do JV-V01: indícios e hipóteses sobre o cruzamento entre duas vias.

As explicações são geradas por estas regras — não por IA. Os limiares são **provisórios**: foram
escolhidos pelo agente e só foram exercitados em casos simulados; não são critérios validados para o
carro (JV-D025, JV-D042).
"""

from __future__ import annotations

VERSAO = "1.0"

LIMIARES = {
    "sobreposicao_max_diferenca_db": 6.0,
    "cancelamento_min_db": 6.0,         # soma pelo menos 6 dB abaixo da soma de potências
    "oposicao_media_min_graus": 160.0,  # |média circular| da diferença de fase
    "oposicao_dispersao_max_graus": 15.0,
    "atraso_relevante_ms": 0.02,        # abaixo disso, o atraso equivalente é tratado como nulo
}
LIMIARES_PROVISORIOS = True


def _fmt(x: float, casas: int = 1) -> str:
    if abs(x) < 0.5 * 10 ** -casas:
        x = 0.0  # evita “−0,0”
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def avaliar(sobreposicao: dict, vale: dict | None, fase: dict | None, ids: dict[str, str]) -> dict:
    """Aplica as regras e devolve indícios, hipóteses e a sugestão de próximo passo.

    ``ids`` mapeia o nome de cada cálculo para o identificador do registro (por exemplo,
    ``{"vale": "C-0004"}``), para que cada número citado aponte para sua origem.
    """
    indicios: list[dict] = []
    hipoteses: list[dict] = []

    if not sobreposicao.get("existe"):
        return {
            "indicios": [],
            "hipoteses": [],
            "sugestao": "solicitar_dados",
            "motivo": "As duas vias não se sobrepõem em nenhuma faixa com níveis próximos; "
                      "não há cruzamento para analisar com estas medições.",
        }

    cancelamento = vale is not None and vale["min_relativo_db"] <= -LIMIARES["cancelamento_min_db"]
    if cancelamento:
        indicios.append({
            "regra": "Regra 1 — cancelamento entre as vias",
            "titulo": "A soma das vias fica muito abaixo do que deveria",
            "explicacao": (
                f"Em {_fmt(vale['freq_hz'], 0)} Hz, médio e tweeter juntos medem "
                f"{_fmt(vale['soma_no_vale_db'])} dB, mas só a soma das energias das duas vias daria "
                f"{_fmt(vale['potencias_no_vale_db'])} dB — a soma ficou {_fmt(-vale['min_relativo_db'])} dB "
                f"abaixo [{ids['vale']}]. Quando duas fontes somam menos que a energia de cada uma, elas "
                "estão se anulando nessa faixa."
            ),
            "valores": {"freq_hz": vale["freq_hz"], "abaixo_db": -vale["min_relativo_db"]},
            "calculos": [ids["vale"], ids["potencias"], ids["sobreposicao"]],
        })

    oposicao = (
        fase is not None
        and abs(fase["media_graus"]) >= LIMIARES["oposicao_media_min_graus"]
        and fase["dispersao_graus"] <= LIMIARES["oposicao_dispersao_max_graus"]
    )
    atraso_nulo = fase is not None and abs(fase["atraso_equivalente_ms"]) < LIMIARES["atraso_relevante_ms"]
    if oposicao:
        indicios.append({
            "regra": "Regra 2 — fases em oposição constante",
            "titulo": "As duas vias estão em oposição de fase, de forma constante",
            "explicacao": (
                f"Entre {_fmt(fase['faixa_hz'][0], 0)} Hz e {_fmt(fase['faixa_hz'][1], 0)} Hz, onde as vias "
                f"têm níveis próximos, a diferença de fase entre elas é em média {_fmt(abs(fase['media_graus']))}°, "
                f"com variação de só {_fmt(abs(fase['dispersao_graus']))}° [{ids['fase']}]. Uma diferença de "
                "180° que não muda com a frequência é a assinatura de uma inversão de polaridade."
            ),
            "valores": {"media_graus": fase["media_graus"], "dispersao_graus": fase["dispersao_graus"]},
            "calculos": [ids["fase"]],
        })

    if cancelamento and oposicao:
        hipoteses.append({
            "posicao": 1,
            "avaliacao": "mais provável",
            "enunciado": "Polaridade invertida em uma das vias (médio ou tweeter)",
            "por_que": "Os dois indícios juntos: as vias se anulam no cruzamento e estão a 180° de "
                       "forma constante.",
            "confirmaria": "Inverter a polaridade de uma das vias e a soma ficar plana no cruzamento, "
                           "como na previsão calculada.",
            "refutaria": "Inverter a polaridade e o vale continuar.",
            "apoio": ["Regra 1", "Regra 2"],
        })
        hipoteses.append({
            "posicao": 2,
            "avaliacao": "pouco provável" if atraso_nulo else "possível",
            "enunciado": "Diferença de tempo de chegada entre as vias",
            "por_que": (
                f"Um atraso faria a diferença de fase variar com a frequência; o atraso equivalente "
                f"calculado é {_fmt(fase['atraso_equivalente_ms'], 3)} ms [{ids['fase']}]."
            ),
            "confirmaria": "Diferença de fase que cresce de forma regular com a frequência.",
            "refutaria": "Diferença de fase constante, como a observada.",
            "apoio": [],
        })
        hipoteses.append({
            "posicao": 3,
            "avaliacao": "pouco provável",
            "enunciado": "Filtros de crossover diferentes entre as vias, defasando-as",
            "por_que": "Filtros diferentes também produziriam diferença de fase variável na sobreposição.",
            "confirmaria": "Diferença de fase variável e configuração de filtros diferente entre as vias.",
            "refutaria": "Configuração declarada com filtros iguais e diferença constante.",
            "apoio": [],
        })
        return {"indicios": indicios, "hipoteses": hipoteses, "sugestao": "teste_polaridade",
                "motivo": "A hipótese mais provável pode ser testada com uma única alteração reversível."}

    if not cancelamento:
        return {"indicios": indicios, "hipoteses": [], "sugestao": "nada_a_alterar",
                "motivo": "As vias não se anulam no cruzamento; por estas regras, não há motivo "
                          "para alterar a polaridade ou o cruzamento."}

    return {"indicios": indicios, "hipoteses": [], "sugestao": "solicitar_dados",
            "motivo": "Há cancelamento, mas a fase não permite apontar a causa com estas regras; "
                      "são necessárias outras medições."}
