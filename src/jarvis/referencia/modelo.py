"""Modelo físico único dos casos simulados do JV-V02 (ADR-201; FR-201, INV-208).

A resposta complexa de cada via no microfone é um **produto** de fatores, todos do mesmo H(f):

    H = alto-falante × filtros do DSP × polaridade (fiação e DSP) × atraso (distância + DSP) × acústica

e a soma é a **soma complexa** das vias. Magnitude, fase e soma saem do mesmo H, nunca de
perturbações independentes.

A **camada de aquisição** vem depois, arquivo por arquivo: ganho de entrada, mudança de posição
(atraso e reflexão extras), ruído relativo complexo com σ e semente registrados, e quantização do
arquivo. Ruído e erros nunca entram no modelo físico.

Os parâmetros são dicionários simples, para irem inteiros ao manifesto (auditoria).
"""

# @@T210 [FR-201] [INV-208] Modelo físico e camada de aquisição separados (ADR-201)

from __future__ import annotations

import numpy as np

from jarvis.rew_texto import RespostaFrequencia

VERSAO = "1.0"
VELOCIDADE_SOM_M_S = 343.0
DB_POR_NEPER = 20.0 / np.log(10.0)  # ≈ 8,686 dB por unidade de erro relativo de amplitude


def grade_log(f_min: float = 20.0, f_max: float = 20_000.0, pontos_por_oitava: int = 48) -> np.ndarray:
    """Grade logarítmica uniforme (a mesma construção do REF-001-A)."""
    n = int(round(np.log2(f_max / f_min) * pontos_por_oitava)) + 1
    return f_min * 2.0 ** (np.arange(n) / pontos_por_oitava)


# ----------------------------------------------------------------- fatores do modelo físico

def _alto_falante(p: dict, f: np.ndarray) -> np.ndarray:
    """Resposta do alto-falante: ``plano``, ou ``ressonante`` (passa-altas de 2ª ordem em ``fs_hz``
    com fator ``q``) com rolagem opcional de 1ª ordem em ``rolagem_hz``."""
    tipo = p.get("tipo", "plano")
    h = np.ones_like(f, dtype=complex)
    if tipo == "ressonante":
        s = 1j * f / p["fs_hz"]
        h = h * s ** 2 / (s ** 2 + s / p.get("q", 0.7) + 1.0)
    elif tipo != "plano":
        raise ValueError(f"alto-falante desconhecido: {tipo}")
    if p.get("rolagem_hz"):
        h = h / (1.0 + 1j * f / p["rolagem_hz"])
    return h


def lr4(f: np.ndarray, fc: float) -> tuple[np.ndarray, np.ndarray]:
    """Passa-baixas e passa-altas Linkwitz-Riley de 4ª ordem."""
    s = 1j * f / fc
    d = (s ** 2 + np.sqrt(2.0) * s + 1.0) ** 2
    return 1.0 / d, s ** 4 / d


def peq(f: np.ndarray, f0: float, ganho_db: float, q: float) -> np.ndarray:
    """Filtro paramétrico (pico/vale) analógico de 2ª ordem."""
    a = 10 ** (ganho_db / 40.0)
    s = 1j * f / f0
    return (s ** 2 + s * a / q + 1.0) / (s ** 2 + s / (a * q) + 1.0)


def _filtro(p: dict, f: np.ndarray) -> np.ndarray:
    tipo = p["tipo"]
    if tipo == "lr4_pb":
        return lr4(f, p["fc_hz"])[0]
    if tipo == "lr4_pa":
        return lr4(f, p["fc_hz"])[1]
    if tipo == "peq":
        return peq(f, p["f0_hz"], p["ganho_db"], p["q"])
    if tipo == "ganho":
        return np.full_like(f, 10 ** (p["ganho_db"] / 20.0), dtype=complex)
    raise ValueError(f"filtro desconhecido: {tipo}")


def _atraso(f: np.ndarray, segundos: float) -> np.ndarray:
    return np.exp(-2j * np.pi * f * segundos)


def _reflexao(f: np.ndarray, g: float, tau_ms: float) -> np.ndarray:
    return 1.0 + g * _atraso(f, tau_ms / 1000.0)


def resposta_via(params: dict, f: np.ndarray) -> np.ndarray:
    """H(f) complexo de uma via no microfone, sem nenhum efeito de aquisição.

    ``params``: ``alto_falante``, ``filtros`` (lista), ``polaridade_fiacao`` (+1/−1),
    ``polaridade_dsp_graus`` (0/180), ``distancia_m``, ``atraso_dsp_ms``, ``reflexoes``
    (lista de ``{g, tau_ms}``) e ``nivel_db`` (nível de referência).
    """
    h = _alto_falante(params.get("alto_falante", {}), f)
    for filtro in params.get("filtros", []):
        h = h * _filtro(filtro, f)
    h = h * float(params.get("polaridade_fiacao", 1))
    if params.get("polaridade_dsp_graus", 0) == 180:
        h = -h
    segundos = params.get("distancia_m", 1.0) / VELOCIDADE_SOM_M_S + params.get("atraso_dsp_ms", 0.0) / 1000.0
    h = h * _atraso(f, segundos)
    for r in params.get("reflexoes", []):
        h = h * _reflexao(f, r["g"], r["tau_ms"])
    return h * 10 ** (params.get("nivel_db", 85.0) / 20.0)


def soma(*hs: np.ndarray) -> np.ndarray:
    """Soma complexa das vias (o que o microfone recebe com as vias tocando juntas)."""
    return np.sum(np.vstack(hs), axis=0)


# ----------------------------------------------------------------- camada de aquisição

def adquirir(h: np.ndarray, f: np.ndarray, aquisicao: dict | None = None, semente: int | None = None,
             quantizar: bool = True) -> RespostaFrequencia:
    """Transforma H(f) num arquivo de medição, aplicando só efeitos de aquisição.

    ``aquisicao``: ``ganho_entrada_db``; ``posicao`` com ``delta_distancia_m`` e ``reflexoes``
    extras (o microfone noutro lugar muda atraso e interferências sem tocar no DSP);
    ``ruido_sigma_db`` (ruído relativo complexo independente por ponto, com a semente informada).
    ``quantizar`` arredonda como o arquivo de texto (nível 4 casas, fase 3 casas).
    """
    aq = aquisicao or {}
    x = np.asarray(h, dtype=complex).copy()
    x = x * 10 ** (aq.get("ganho_entrada_db", 0.0) / 20.0)
    pos = aq.get("posicao") or {}
    if pos.get("delta_distancia_m"):
        x = x * _atraso(f, pos["delta_distancia_m"] / VELOCIDADE_SOM_M_S)
    for r in pos.get("reflexoes", []):
        x = x * _reflexao(f, r["g"], r["tau_ms"])
    sigma_db = aq.get("ruido_sigma_db", 0.0)
    if sigma_db:
        if semente is None:
            raise ValueError("ruído exige semente registrada (INV-208)")
        rng = np.random.default_rng(semente)
        s = sigma_db / DB_POR_NEPER  # desvio relativo em amplitude e, igual, em fase (rad)
        x = x * np.exp(rng.normal(0.0, s, f.size) + 1j * rng.normal(0.0, s, f.size))
    nivel = 20.0 * np.log10(np.maximum(np.abs(x), 1e-12))
    fase = np.rad2deg(np.angle(x))
    if quantizar:
        nivel, fase = np.round(nivel, 4), np.round(fase, 3)
    return RespostaFrequencia(freq_hz=np.asarray(f, dtype=float), nivel_db=nivel, fase_graus=fase)
