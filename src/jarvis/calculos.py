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
    "referencia_temporal": "1.0",
    "soma_complexa": "1.0",
    "soma_potencias": "1.0",
    "sobreposicao": "1.1",    # JV-T202: pontos e largura em oitavas
    "diferenca_fase": "1.1",  # JV-T202: amostras mínimas (ADR-212, A04)
    "vale_relativo": "1.0",
    "comparacao": "1.0",
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


def referencia_temporal(metadados: list[dict]) -> dict:
    """Compatibilidade de referência temporal entre medições (JV-D023).

    Compatível quando todas têm o mesmo tipo e identificador de referência (diferente de
    “nenhuma”), a mesma taxa de amostragem e a mesma posição de microfone.
    """
    motivos = []
    refs = [m.get("referencia_temporal") or {} for m in metadados]
    tipos = {r.get("tipo", "nenhuma") for r in refs}
    if "nenhuma" in tipos or not tipos:
        motivos.append("há medição sem referência temporal")
    if len(tipos) > 1:
        motivos.append("tipos de referência temporal diferentes")
    if len({r.get("id") for r in refs}) > 1:
        motivos.append("referências temporais de sessões de medição diferentes")
    if len({m.get("taxa_amostragem") for m in metadados}) > 1:
        motivos.append("taxas de amostragem diferentes")
    if len({m.get("posicao_microfone") for m in metadados}) > 1:
        motivos.append("posições de microfone diferentes")
    return {"compativel": not motivos, "motivos": motivos}


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
