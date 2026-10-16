"""Regras de diagnóstico (V01 e V02): indícios e hipóteses sobre o cruzamento entre duas vias.

As explicações são geradas por estas regras — não por IA. Os limiares são **provisórios**: foram
escolhidos pelo agente e só foram exercitados em casos simulados; não são critérios validados para o
carro (JV-D025, JV-D042).
"""

from __future__ import annotations

VERSAO = "1.1"  # JV-V02: portão de qualidade, I-3 e reordenação (as 1.0 ficam em regras_v1_0.py)

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


def _avaliar_cruzamento(sobreposicao: dict, vale: dict | None, fase: dict | None, ids: dict[str, str]) -> dict:
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


# ----------------------------------------------------------------- regras 1.1 (JV-V02)

ORDEM_QUALIDADE = ("aprovada", "aviso", "nao_estimavel", "reprovada")


# @@T216 [FR-203] [INV-201] [INV-212] Portão de qualidade (ADR-203)
def portao(qualidade: dict | None) -> dict:
    """Decide o que a qualidade das medições permite concluir.

    ``qualidade``: ``{"medicoes": {id: resultado de calculos.irregularidade}}``. Sem qualidade
    informada (chamadas do V01), o portão não limita nada.
    - ``reprovada`` (σ̂ acima do limite em alguma medição) ⇒ “não dá para concluir”: sem hipóteses
      ordenadas e sem teste proposto (INV-201);
    - ``nao_estimavel`` ⇒ a análise descritiva segue, a incerteza fica “não quantificada” e nenhuma
      hipótese é apresentada como confirmada (INV-212);
    - ``aviso`` ⇒ segue, com incerteza declarada maior.
    """
    if not qualidade:
        return {"classificacao": None, "conclui": True, "motivo": None, "falta": [], "sigma_max_db": None}
    meds = qualidade.get("medicoes", {})
    pior = max((m["classificacao"] for m in meds.values()), key=ORDEM_QUALIDADE.index, default="aprovada")
    sigmas = [m["sigma_db"] for m in meds.values() if m.get("sigma_db") is not None]
    sigma_max = max(sigmas) if sigmas else None
    if pior == "reprovada":
        ruins = [mid for mid, m in meds.items() if m["classificacao"] == "reprovada"]
        lim = meds[ruins[0]]["limiares"]["limiares"]["irregularidade_reprovada_db"]["valor"]
        return {"classificacao": pior, "conclui": False, "sigma_max_db": sigma_max,
                "motivo": (f"A irregularidade ponto a ponto (σ̂ = {_fmt(sigma_max, 2)} dB) passa do limite provisório "
                           f"de {_fmt(lim)} dB em {', '.join(ruins)}: com este ruído, a medição não permite concluir."),
                "falta": ["nova medição com menos ruído (mais média, microfone fixo, ambiente mais silencioso)"]}
    if pior == "nao_estimavel":
        sem = [mid for mid, m in meds.items() if m["classificacao"] == "nao_estimavel"]
        motivos = sorted({mt for mid in sem for mt in meds[mid].get("motivos", [])})
        return {"classificacao": pior, "conclui": True, "sigma_max_db": sigma_max,
                "motivo": ("Ruído não estimável em " + ", ".join(sem) + " (" + "; ".join(motivos) + "). "
                           "As observações descritivas continuam; a incerteza fica não quantificada e nenhuma "
                           "hipótese pode ser confirmada."),
                "falta": ["medição sem suavização, em grade logarítmica com pelo menos 24 pontos por oitava"]}
    return {"classificacao": pior, "conclui": True, "sigma_max_db": sigma_max, "falta": [],
            "motivo": ("Irregularidade entre os limites de aviso: a análise segue com incerteza declarada maior."
                       if pior == "aviso" else None)}


def _indicio_vale_individual(vales_individuais: dict, ids: dict[str, str]) -> dict | None:
    rotulos = {"via_a": "médio", "via_b": "tweeter"}
    partes, calcs, valores = [], [], []
    for via, res in (vales_individuais or {}).items():
        if not res or not res.get("vales"):
            continue
        freqs = ", ".join(f"{_fmt(v['freq_hz'], 0)} Hz" for v in res["vales"])
        cid = ids.get(f"vales_individuais_{via}")
        partes.append(f"no {rotulos.get(via, via)} sozinho, em {freqs}" + (f" [{cid}]" if cid else ""))
        calcs += [cid] if cid else []
        valores += [{"via": via, **v} for v in res["vales"]]
    if not partes:
        return None
    return {
        "regra": "Regra 3 — vale numa via isolada",
        "titulo": "Há vale estreito numa via medida sozinha",
        "explicacao": ("A medição individual já mostra vale estreito " + "; ".join(partes) + ". Um vale que existe "
                       "com a via tocando sozinha não vem da soma entre as vias: costuma ser interferência ou "
                       "reflexão no caminho até o microfone, que muda com a posição e não se corrige com reforço de EQ."),
        "valores": {"vales": valores},
        "calculos": calcs,
    }


# @@T216 [FR-203] [FR-204] [FR-206] Regras 1.1: portão, I-3 e reordenação (ADR-210)
def avaliar(sobreposicao: dict, vale: dict | None, fase: dict | None, ids: dict[str, str],
            vales_individuais: dict | None = None, qualidade: dict | None = None) -> dict:
    """Aplica as regras 1.1. As chamadas do V01 (sem ``vales_individuais`` nem ``qualidade``) dão o mesmo
    resultado das regras 1.0, acrescido do campo ``portao``.
    """
    p = portao(qualidade)
    if not p["conclui"]:
        return {"indicios": [], "hipoteses": [], "sugestao": "nao_da_para_concluir",
                "motivo": p["motivo"], "falta": p["falta"], "portao": p}
    r = _avaliar_cruzamento(sobreposicao, vale, fase, ids)
    i3 = _indicio_vale_individual(vales_individuais, ids) if sobreposicao.get("existe") else None
    if i3:
        r["indicios"].append(i3)
        oposicao = any(i["regra"].startswith("Regra 2") for i in r["indicios"])
        cancelamento = any(i["regra"].startswith("Regra 1") for i in r["indicios"])
        if not oposicao:
            hip = [{
                "posicao": 1, "avaliacao": "mais provável",
                "enunciado": "Interferência ou reflexão no caminho de uma via (vale presente na via isolada)",
                "por_que": "O vale aparece na medição individual, sem oposição de fase constante entre as vias.",
                "confirmaria": "O vale mudar de frequência ou profundidade ao medir em outras posições.",
                "refutaria": "O vale continuar igual em várias posições de microfone.",
                "apoio": ["Regra 3"],
            }]
            if cancelamento:
                hip.append({
                    "posicao": 2, "avaliacao": "pouco provável",
                    "enunciado": "Polaridade invertida em uma das vias (médio ou tweeter)",
                    "por_que": "Há cancelamento na soma, mas sem a oposição de 180° constante que a polaridade daria.",
                    "confirmaria": "Diferença de fase constante perto de 180° na sobreposição.",
                    "refutaria": "Diferença de fase variável, como a observada.",
                    "apoio": ["Regra 1"],
                })
            r["hipoteses"] = hip
            r["sugestao"] = "solicitar_dados"
            r["motivo"] = ("O vale já existe numa via medida sozinha: antes de qualquer alteração, meça em outras "
                           "posições para saber se é interferência. Não reforce a EQ para preencher o vale "
                           "(não equalizável).")
    if p["classificacao"] == "nao_estimavel":
        for i in r["indicios"]:
            i["qualidade"] = "não estimada"
        r["aviso_qualidade"] = p["motivo"]
    elif p["classificacao"] == "aviso":
        r["aviso_qualidade"] = p["motivo"]
    r["portao"] = p
    return r
