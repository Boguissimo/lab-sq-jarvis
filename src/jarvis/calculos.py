"""Cálculos determinísticos do JV-V01 (constituição, P3).

Funções puras: mesmas entradas, mesmos resultados. Cada função tem uma versão em ``VERSOES``, que é
gravada junto com o resultado para rastrear qual algoritmo produziu cada número.

Convenções:
- nível em dB e fase em graus, como no arquivo de origem;
- “via A” e “via B” são as duas medições individuais (no REF-001, médio e tweeter);
- diferença de fase = fase(A) − fase(B), reduzida a (−180°, 180°].
"""

from __future__ import annotations

import numpy as np

from jarvis import limiares
from jarvis.rew_texto import RespostaFrequencia

VERSOES = {
    "qualidade_basica": "1.0",
    "referencia_temporal": "1.1",  # JV-T203: campos obrigatórios, declarada (A02)
    "soma_complexa": "1.0",
    "soma_potencias": "1.0",
    "sobreposicao": "1.1",    # JV-T202: pontos e largura em oitavas
    "diferenca_fase": "1.1",  # JV-T202: amostras mínimas (ADR-212, A04)
    "vale_relativo": "1.0",
    "comparacao": "1.0",
    "irregularidade": "1.0",  # JV-T212 (E1)
    "vales_individuais": "1.0",  # JV-T214
    "faixa_util": "1.0",  # JV-T214
    "condicoes_comparaveis": "1.0",  # JV-T215
    "detector_mudanca_via": "1.0",  # JV-T215
}

FAIXA_MINIMA_HZ = (200.0, 10_000.0)  # faixa que a análise do cruzamento precisa cobrir


def _complexa(r: RespostaFrequencia) -> np.ndarray:
    return 10 ** (r.nivel_db / 20.0) * np.exp(1j * np.deg2rad(r.fase_graus))


def _em_db(x: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-12))


def _reduzir_graus(g: np.ndarray) -> np.ndarray:
    r = (g + 180.0) % 360.0 - 180.0
    return np.where(r == -180.0, 180.0, r)


def mesma_grade(a: RespostaFrequencia, b: RespostaFrequencia, tolerancia_relativa: float = 1e-6) -> bool:
    return a.freq_hz.shape == b.freq_hz.shape and bool(
        np.all(np.abs(a.freq_hz - b.freq_hz) <= tolerancia_relativa * b.freq_hz)
    )


def qualidade_basica(r: RespostaFrequencia) -> dict:
    """Verificação mínima: valores finitos, frequências crescentes e faixa coberta."""
    itens = []
    finitos = bool(np.all(np.isfinite(r.freq_hz)) and np.all(np.isfinite(r.nivel_db))
                   and (r.fase_graus is None or np.all(np.isfinite(r.fase_graus))))
    itens.append({"item": "valores numéricos válidos", "ok": finitos})
    crescente = bool(np.all(np.diff(r.freq_hz) > 0))
    itens.append({"item": "frequências em ordem crescente", "ok": crescente})
    cobre = bool(r.freq_hz.min() <= FAIXA_MINIMA_HZ[0] and r.freq_hz.max() >= FAIXA_MINIMA_HZ[1])
    itens.append({"item": f"cobre {FAIXA_MINIMA_HZ[0]:.0f} Hz a {FAIXA_MINIMA_HZ[1]:.0f} Hz", "ok": cobre})
    itens.append({"item": "contém fase", "ok": r.tem_fase})
    aprovada = finitos and crescente and cobre
    return {
        "aprovada": aprovada,
        "itens": itens,
        "pontos": int(r.freq_hz.size),
        "faixa_hz": [float(r.freq_hz.min()), float(r.freq_hz.max())],
    }


# @@T203 [FR-205] Referência temporal declarada com campos obrigatórios (ADR-212, A02)
def referencia_temporal(metadados: list[dict]) -> dict:
    """Compatibilidade **declarada** de referência temporal entre medições (JV-D023; spec E3).

    Compatível quando todas as medições têm ``referencia_temporal.tipo`` diferente de “nenhuma”,
    ``referencia_temporal.id``, ``taxa_amostragem`` e ``posicao_microfone`` presentes, não vazios e
    iguais entre si. Campo ausente ⇒ incompatível. É igualdade declarada no manifesto, não verificação
    física: a interface diz “declarada compatível”, nunca “verificada”.
    """
    def _vazio(v) -> bool:
        return v is None or (isinstance(v, str) and not v.strip())

    motivos = []
    if not metadados:
        motivos.append("nenhuma medição informada")
    refs = [m.get("referencia_temporal") or {} for m in metadados]
    tipos = [r.get("tipo") for r in refs]
    if any(_vazio(t) or t == "nenhuma" for t in tipos):
        motivos.append("há medição sem referência temporal declarada")
    if any(_vazio(r.get("id")) for r in refs):
        motivos.append("há medição sem identificador da referência temporal")
    if any(_vazio(m.get("taxa_amostragem")) for m in metadados):
        motivos.append("há medição sem taxa de amostragem declarada")
    if any(_vazio(m.get("posicao_microfone")) for m in metadados):
        motivos.append("há medição sem posição de microfone declarada")
    if len({t for t in tipos if not _vazio(t) and t != "nenhuma"}) > 1:
        motivos.append("tipos de referência temporal diferentes")
    if len({r.get("id") for r in refs if not _vazio(r.get("id"))}) > 1:
        motivos.append("referências temporais de sessões de medição diferentes")
    if len({m.get("taxa_amostragem") for m in metadados if not _vazio(m.get("taxa_amostragem"))}) > 1:
        motivos.append("taxas de amostragem diferentes")
    if len({m.get("posicao_microfone") for m in metadados if not _vazio(m.get("posicao_microfone"))}) > 1:
        motivos.append("posições de microfone diferentes")
    return {"compativel": not motivos, "declarada": True, "motivos": motivos}


def soma_complexa(a: RespostaFrequencia, b: RespostaFrequencia, inverter_b: bool = False) -> dict:
    """Soma das duas vias como se tocassem juntas; com ``inverter_b``, simula a via B invertida."""
    soma = _complexa(a) + (-1.0 if inverter_b else 1.0) * _complexa(b)
    return {
        "freq_hz": a.freq_hz.tolist(),
        "nivel_db": _em_db(soma).tolist(),
        "fase_graus": _reduzir_graus(np.rad2deg(np.angle(soma))).tolist(),
        "inverter_b": inverter_b,
    }


def soma_potencias(a: RespostaFrequencia, b: RespostaFrequencia) -> dict:
    """Soma sem interferência (energia): referência para dizer se as vias se reforçam ou se anulam."""
    pot = 10 ** (a.nivel_db / 10.0) + 10 ** (b.nivel_db / 10.0)
    return {"freq_hz": a.freq_hz.tolist(), "nivel_db": (10.0 * np.log10(pot)).tolist()}


def sobreposicao(a: RespostaFrequencia, b: RespostaFrequencia, max_diferenca_db: float) -> dict:
    """Faixa em que as duas vias têm níveis próximos — onde a fase entre elas decide a soma."""
    mascara = np.abs(a.nivel_db - b.nivel_db) <= max_diferenca_db
    if not mascara.any():
        return {"existe": False, "max_diferenca_db": max_diferenca_db}
    f = a.freq_hz[mascara]
    i_cruz = int(np.argmin(np.abs(a.nivel_db - b.nivel_db)))
    return {
        "existe": True,
        "max_diferenca_db": max_diferenca_db,
        "faixa_hz": [float(f.min()), float(f.max())],
        "cruzamento_hz": float(a.freq_hz[i_cruz]),
        "nivel_a_no_cruzamento_db": float(a.nivel_db[i_cruz]),
        "nivel_b_no_cruzamento_db": float(b.nivel_db[i_cruz]),
        "indices": np.flatnonzero(mascara).tolist(),
        "pontos": int(mascara.sum()),
        "largura_oitavas": float(np.log2(f.max() / f.min())),
    }


# @@T202 [FR-205] Amostras mínimas para fase e atraso (ADR-212, A04)
def amostras_fase_suficientes(a: RespostaFrequencia, indices: list[int]) -> dict:
    """Confere se a sobreposição tem pontos e largura suficientes para estimar fase e atraso.

    Abaixo do mínimo, a regressão do atraso é degenerada (um ponto dá atraso 0); fase e atraso
    ficam “não calculáveis” em vez de produzir um número sem sentido.
    """
    pontos_min = int(limiares.valor("fase_pontos_min"))
    largura_min = limiares.valor("sobreposicao_largura_min_oitava")
    idx = np.asarray(indices, dtype=int)
    pontos = int(idx.size)
    largura = float(np.log2(a.freq_hz[idx].max() / a.freq_hz[idx].min())) if pontos else 0.0
    motivos = []
    if pontos < pontos_min:
        motivos.append(f"a sobreposição tem {pontos} ponto(s); são necessários pelo menos {pontos_min}")
    if largura < largura_min - 1e-9:
        motivos.append(f"a sobreposição cobre {largura:.2f} oitava; é necessário pelo menos 1/3 de oitava")
    return {"suficiente": not motivos, "pontos": pontos, "largura_oitavas": largura, "motivos": motivos,
            "limiares": limiares.snapshot("fase_pontos_min", "sobreposicao_largura_min_oitava")}


def diferenca_fase(a: RespostaFrequencia, b: RespostaFrequencia, indices: list[int]) -> dict:
    """Diferença de fase A − B na sobreposição: média e dispersão circulares e atraso equivalente.

    Uma diferença constante (≈ 180°) indica inversão de polaridade; um atraso entre as vias faz a
    diferença crescer com a frequência (360° × f × atraso). O atraso equivalente é a inclinação da
    diferença desdobrada em função da frequência.
    """
    amostras = amostras_fase_suficientes(a, indices)
    if not amostras["suficiente"]:
        return {"calculavel": False, "motivos": amostras["motivos"], "amostras": amostras}
    idx = np.asarray(indices, dtype=int)
    d = _reduzir_graus(a.fase_graus[idx] - b.fase_graus[idx])
    vetor = np.exp(1j * np.deg2rad(d))
    media = vetor.mean()
    resultante = float(np.abs(media))
    dispersao = float(np.rad2deg(np.sqrt(-2.0 * np.log(max(resultante, 1e-12)))))
    desdobrada = np.unwrap(np.deg2rad(d))
    inclinacao = np.polyfit(a.freq_hz[idx], desdobrada, 1)[0]  # rad por Hz
    atraso_ms = float(inclinacao / (2.0 * np.pi) * 1000.0)  # positivo: B chega depois de A
    return {
        "calculavel": True,
        "media_graus": float(_reduzir_graus(np.array([np.rad2deg(np.angle(media))]))[0]),
        "dispersao_graus": dispersao,
        "atraso_equivalente_ms": atraso_ms,
        "faixa_hz": [float(a.freq_hz[idx].min()), float(a.freq_hz[idx].max())],
        "diferenca_graus": d.tolist(),
        "freq_hz": a.freq_hz[idx].tolist(),
    }


def vale_relativo(soma_db: list[float], potencias_db: list[float], freq_hz: list[float],
                  indices: list[int]) -> dict:
    """Quanto a soma medida fica abaixo da soma de potências na sobreposição (cancelamento)."""
    s = np.asarray(soma_db)
    p = np.asarray(potencias_db)
    idx = np.asarray(indices, dtype=int)
    rel = s[idx] - p[idx]
    k = int(np.argmin(rel))
    return {
        "min_relativo_db": float(rel[k]),
        "freq_hz": float(np.asarray(freq_hz)[idx][k]),
        "soma_no_vale_db": float(s[idx][k]),
        "potencias_no_vale_db": float(p[idx][k]),
    }


def nivel_em(freq_hz: list[float], nivel_db: list[float], f: float) -> float:
    """Nível interpolado em escala logarítmica de frequência."""
    return float(np.interp(np.log10(f), np.log10(np.asarray(freq_hz)), np.asarray(nivel_db)))


def comparacao(previsto: dict, medido: RespostaFrequencia, faixa_hz: tuple[float, float]) -> dict:
    """Diferença medido − previsto na faixa; o medido é interpolado na grade do previsto se preciso."""
    fp = np.asarray(previsto["freq_hz"])
    np_db = np.asarray(previsto["nivel_db"])
    med = np.interp(np.log10(fp), np.log10(medido.freq_hz), medido.nivel_db)
    banda = (fp >= faixa_hz[0]) & (fp <= faixa_hz[1])
    dif = med[banda] - np_db[banda]
    return {
        "faixa_hz": list(faixa_hz),
        "rms_db": float(np.sqrt(np.mean(dif ** 2))),
        "max_abs_db": float(np.max(np.abs(dif))),
        "pontos": int(banda.sum()),
        "medido_na_grade_db": med.tolist(),
    }


# @@T212 [FR-202] [INV-212] Irregularidade ponto a ponto σ̂ (ADR-202; spec E1)
def irregularidade(r: RespostaFrequencia, suavizacao: str | None) -> dict:
    """σ̂ = 1,4826 · MAD(Δ²L) / √6 entre 200 Hz e 10 kHz, com as condições de aplicação.

    σ̂ é uma estimativa normalizada de irregularidade fina, **não** uma medição direta de ruído:
    supõe ruído independente entre pontos e não enxerga ruído correlacionado ou removido por
    suavização. Com qualquer condição falhando, o resultado é ``nao_estimavel``, que **não** é
    qualidade aprovada (INV-212) e preserva as observações descritivas (E2).

    ``suavizacao``: ``"nenhuma"``, o texto da suavização declarada, ou ``None`` (desconhecida).
    """
    tol = limiares.valor("irregularidade_tolerancia_grade")
    ppo_min = limiares.valor("irregularidade_pontos_por_oitava_min")
    f_min, f_max = limiares.valor("faixa_analise_min_hz"), limiares.valor("faixa_analise_max_hz")
    f = r.freq_hz
    razoes = f[1:] / f[:-1] if f.size > 1 else np.array([1.0])
    razao = float(np.median(razoes))
    grade_log = bool(razao > 1.0 and np.all(np.abs(razoes / razao - 1.0) <= tol))
    ppo = float(1.0 / np.log2(razao)) if razao > 1.0 else 0.0
    if suavizacao is None or not str(suavizacao).strip():
        estado_suav = "desconhecida"
    elif str(suavizacao).strip().lower() == "nenhuma":
        estado_suav = "nenhuma"
    else:
        estado_suav = "declarada"
    condicoes = {"grade_log_uniforme": grade_log, "pontos_por_oitava": round(ppo, 3),
                 "densidade_suficiente": ppo >= ppo_min, "suavizacao": estado_suav}
    aplicavel = grade_log and ppo >= ppo_min and estado_suav == "nenhuma"
    faixa = (f >= f_min) & (f <= f_max)
    snapshot = limiares.snapshot("irregularidade_aviso_db", "irregularidade_reprovada_db",
                                 "irregularidade_pontos_por_oitava_min", "irregularidade_tolerancia_grade")
    if not aplicavel or faixa.sum() < 3:
        motivos = []
        if not grade_log:
            motivos.append("a grade de frequências não é logarítmica uniforme")
        if ppo < ppo_min:
            motivos.append(f"densidade de {ppo:.1f} pontos por oitava (mínimo {ppo_min})")
        if estado_suav != "nenhuma":
            motivos.append("suavização " + ("declarada" if estado_suav == "declarada" else "desconhecida"))
        if aplicavel:
            motivos.append("pontos insuficientes entre 200 Hz e 10 kHz")
        return {"sigma_db": None, "aplicavel": False, "condicoes": condicoes,
                "classificacao": "nao_estimavel", "motivos": motivos, "limiares": snapshot}
    d2 = np.diff(r.nivel_db[faixa], n=2)
    mad = float(np.median(np.abs(d2 - np.median(d2))))
    sigma = 1.4826 * mad / np.sqrt(6.0)
    if sigma > limiares.valor("irregularidade_reprovada_db"):
        classe = "reprovada"
    elif sigma >= limiares.valor("irregularidade_aviso_db"):
        classe = "aviso"
    else:
        classe = "aprovada"
    return {"sigma_db": float(sigma), "aplicavel": True, "condicoes": condicoes,
            "classificacao": classe, "motivos": [], "limiares": snapshot}


def _janela_pontos(f: np.ndarray, oitavas: float) -> int:
    """Número de pontos de uma janela de ``oitavas`` numa grade logarítmica (ímpar, ≥ 3)."""
    razao = float(np.median(f[1:] / f[:-1]))
    n = int(round(oitavas / np.log2(razao))) if razao > 1.0 else 3
    return max(3, n | 1)


# @@T214 [FR-204] Vale individual por via (spec, definição "Vale individual")
def vales_individuais(r: RespostaFrequencia) -> dict:
    """Vales estreitos de uma via entre 200 Hz e 10 kHz.

    Vale individual: nível ≥ 10 dB abaixo da média móvel de 1/3 de oitava (em dB, centrada), com
    largura ≤ 1/3 de oitava; a largura é a extensão contínua em que o nível fica ≥ 10 dB abaixo da média.
    Um vale presente na via isolada não vem da soma entre as vias (I-3).
    """
    prof = limiares.valor("vale_individual_profundidade_db")
    larg_max = limiares.valor("vale_individual_largura_max_oitava")
    f_min, f_max = limiares.valor("faixa_analise_min_hz"), limiares.valor("faixa_analise_max_hz")
    f, nivel = r.freq_hz, r.nivel_db
    n = _janela_pontos(f, 1.0 / 3.0)
    meio = n // 2
    padded = np.pad(nivel, meio, mode="edge")
    media = np.convolve(padded, np.ones(n) / n, mode="valid")
    abaixo = (nivel - media <= -prof) & (f >= f_min) & (f <= f_max)
    vales = []
    i = 0
    while i < f.size:
        if not abaixo[i]:
            i += 1
            continue
        j = i
        while j + 1 < f.size and abaixo[j + 1]:
            j += 1
        k = i + int(np.argmin(nivel[i:j + 1] - media[i:j + 1]))
        largura = float(np.log2(f[j] / f[i])) if j > i else float(np.log2(f[min(i + 1, f.size - 1)] / f[i]))
        if largura <= larg_max + 1e-9:
            vales.append({"freq_hz": float(f[k]), "profundidade_db": float(media[k] - nivel[k]),
                          "largura_oitava": largura})
        i = j + 1
    return {"vales": vales, "existe": bool(vales),
            "limiares": limiares.snapshot("vale_individual_profundidade_db", "vale_individual_largura_max_oitava")}


# @@T214 [FR-207] Faixa útil da via (spec E1)
def faixa_util(r: RespostaFrequencia) -> list[int]:
    """Índices entre 200 Hz e 10 kHz em que o nível “antes” da via está a até 20 dB do seu máximo ali."""
    f_min, f_max = limiares.valor("faixa_analise_min_hz"), limiares.valor("faixa_analise_max_hz")
    dentro = (r.freq_hz >= f_min) & (r.freq_hz <= f_max)
    if not dentro.any():
        return []
    teto = float(r.nivel_db[dentro].max())
    return np.flatnonzero(dentro & (r.nivel_db >= teto - limiares.valor("faixa_util_abaixo_max_db"))).tolist()


CAMPOS_AQUISICAO = ("posicao_microfone", "ganho_entrada_db", "referencia_nivel")


def _vazio(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


# @@T215 [FR-207] [INV-214] Condições de aquisição comparáveis declaradas (spec E1/E3)
def condicoes_comparaveis(meta_antes: dict, meta_depois: dict, catalogo: bool = False) -> dict:
    """Igualdade **declarada** de posição, ganho de entrada e referência de nível.

    Campo ausente ⇒ não comparáveis, exceto num caso do catálogo interno com proveniência verificada
    (``catalogo=True``), em que o ausente vale "idêntico por construção". Não é verificação física.
    """
    diferencas, ausentes = [], []
    for campo in CAMPOS_AQUISICAO:
        a, d = meta_antes.get(campo), meta_depois.get(campo)
        if _vazio(a) or _vazio(d):
            if not catalogo:
                ausentes.append(campo)
            continue
        if a != d:
            diferencas.append({"campo": campo, "antes": a, "depois": d})
    return {"ok": not diferencas and not ausentes, "declarada": True, "diferencas": diferencas,
            "ausentes": ausentes, "presumido_catalogo": bool(catalogo)}


# @@T215 [FR-207] Detector de mudança da via (spec E1; ADR-208)
def detector_mudanca_via(antes: RespostaFrequencia, depois: RespostaFrequencia, sigma_antes: float | None,
                         sigma_depois: float | None, faixa: list[int], comparaveis: dict | None = None) -> dict:
    """Δ = depois − antes na faixa útil: mudança geral (|média| > 1,0 dB) ou localizada (banda de
    1/3 de oitava com |média| > max(1,5 dB; 3·σΔ), σΔ = √(σ̂²antes + σ̂²depois)/√n).

    Resultados: ``mudanca_detectada``; ``nao_detectada`` (com a resolução declarada); ``inconclusiva``
    (condições não comparáveis, ou σ̂ não estimável sem mudança geral). Sem comparabilidade, nenhuma
    diferença é atribuída ao DSP. O detector só prova ausência de mudança acima da resolução e nunca
    identifica qual parâmetro mudou.
    """
    lim_media = limiares.valor("detector_media_db")
    lim_banda = limiares.valor("detector_banda_db")
    fator = limiares.valor("detector_fator_sigma")
    snapshot = limiares.snapshot("detector_media_db", "detector_banda_db", "detector_fator_sigma",
                                 "detector_largura_banda_oitava", "faixa_util_abaixo_max_db")
    comparaveis = comparaveis or {"ok": True, "declarada": True, "diferencas": [], "ausentes": []}
    idx = np.asarray(faixa, dtype=int)
    faixa_hz = [float(antes.freq_hz[idx].min()), float(antes.freq_hz[idx].max())] if idx.size else None
    base = {"condicoes_comparaveis": comparaveis, "limiares": snapshot, "parametro_identificado": False,
            "faixa_util_hz": faixa_hz, "media_db": None, "pior_banda": None, "limiar_bandas_db": None,
            "faixa_mudanca_hz": None, "resolucao": None}
    if not comparaveis.get("ok"):
        return {**base, "resultado": "inconclusiva",
                "motivo": "condições de aquisição não comparáveis: nenhuma diferença é atribuída ao DSP"}
    if idx.size < 3 or not mesma_grade(antes, depois):
        return {**base, "resultado": "inconclusiva", "motivo": "faixa útil insuficiente ou grades diferentes"}
    delta = depois.nivel_db[idx] - antes.nivel_db[idx]
    media = float(delta.mean())
    geral = abs(media) > lim_media
    estimavel = sigma_antes is not None and sigma_depois is not None
    pior, faixa_mudanca, limiar_ef, localizada = None, None, None, False
    if estimavel:
        n = min(_janela_pontos(antes.freq_hz, limiares.valor("detector_largura_banda_oitava")), idx.size)
        sigma_d = float(np.sqrt(sigma_antes ** 2 + sigma_depois ** 2) / np.sqrt(n))
        limiar_ef = max(lim_banda, fator * sigma_d)
        medias = np.convolve(delta, np.ones(n) / n, mode="valid")
        k = int(np.argmax(np.abs(medias)))
        pior = {"freq_hz": float(antes.freq_hz[idx[k + n // 2]]), "delta_db": float(medias[k])}
        acima = np.flatnonzero(np.abs(medias) > limiar_ef)
        if acima.size:
            localizada = True
            faixa_mudanca = [float(antes.freq_hz[idx[acima.min()]]),
                             float(antes.freq_hz[idx[acima.max() + n - 1]])]
    if geral or localizada:
        res, motivo = "mudanca_detectada", "mudança geral" if geral else "mudança localizada"
        faixa_mudanca = faixa_mudanca or faixa_hz
    elif estimavel:
        res, motivo = "nao_detectada", "nenhuma mudança acima da resolução declarada"
    else:
        res, motivo = "inconclusiva", "irregularidade não estimável e sem mudança geral detectada"
    return {**base, "resultado": res, "motivo": motivo, "media_db": media, "pior_banda": pior,
            "limiar_bandas_db": limiar_ef, "faixa_mudanca_hz": faixa_mudanca,
            "resolucao": {"media_db": lim_media, "bandas_db": limiar_ef}}
