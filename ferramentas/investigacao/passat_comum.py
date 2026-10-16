"""Conversão IR→resposta em frequência e utilitários do ensaio com ayukhno/autosound-measurements (VW Passat B8).

Parâmetros conforme `preregistro-passat.json`. Exploratório; não faz parte do produto.
"""
import json
from pathlib import Path
import numpy as np

FS = 96000
N = 262144
FIM_CAUSAL = 166395  # amostra a partir da qual o vetor guarda tempo negativo (pré-roll); descartado
SET02 = "cars/vw-passat-b8-sedan-lhd/2026-08-20_front-set-02"
RTA = "cars/vw-passat-b8-sedan-lhd/2026-08-24_mmm-rta-levels/rta-mmm"
CANAIS = ("sw", "w_L", "w_R", "m_L", "m_R", "tw_L", "tw_R", "c")


def ler_ir(fonte: Path, nome: str):
    d = json.loads((fonte / SET02 / "ir-v7" / f"{nome}.json").read_text(encoding="utf-8"))
    assert d["sampleRate"] == FS and len(d["transferRealSamples"]) == N, nome
    return np.asarray(d["transferRealSamples"], dtype=float), float(d["rewSource"]["rewTimeOfIrStartS"]), d


def janela(tipo: str, inicio_s: float):
    """Devolve (i0, i1, taper) em amostras; W30 e Wfull conforme o pré-registro."""
    if tipo == "W30":
        i0 = max(0, int(round((inicio_s - 0.0005) * FS)))
        i1 = i0 + int(round(0.030 * FS))
        n_fade = int(round(0.005 * FS))
    elif tipo == "Wfull":
        i0, i1 = 0, FIM_CAUSAL
        n_fade = int(round(0.100 * FS))
    else:
        raise ValueError(tipo)
    w = np.ones(i1 - i0)
    w[-n_fade:] = 0.5 * (1 + np.cos(np.pi * np.arange(n_fade) / n_fade))
    return i0, i1, w


def espectro(h: np.ndarray, tipo: str, inicio_s: float):
    """DFT do sinal janelado com a origem de tempo no índice 0 (fase relativa ao loopback preservada)."""
    i0, i1, w = janela(tipo, inicio_s)
    x = np.zeros(N)
    x[i0:i1] = h[i0:i1] * w
    return np.fft.rfft(x), np.fft.rfftfreq(N, 1.0 / FS)


def grade_log(ppo: int, f_min=20.0, f_max=20000.0):
    k = int(round(np.log2(f_max / f_min) * ppo)) + 1
    return f_min * 2.0 ** (np.arange(k) / ppo)


def amostrar_bins(X: np.ndarray, f: np.ndarray, g: np.ndarray):
    """Bin FFT mais próximo de cada frequência da grade (sem interpolar fase)."""
    idx = np.clip(np.round(g / (FS / N)).astype(int), 1, X.size - 1)
    return X[idx]


def para_resposta(Xg: np.ndarray, g: np.ndarray):
    from jarvis.rew_texto import RespostaFrequencia
    nivel = 20 * np.log10(np.maximum(np.abs(Xg), 1e-30))
    fase = np.rad2deg(np.angle(Xg))
    return RespostaFrequencia(g, np.round(nivel, 4), np.round(fase, 3))
