"""Protótipo do experimento `preregistro-previsao-fisica.json`: compara a soma observada com a soma PREVISTA por
hipóteses físicas. Lê SOMENTE arrays de caso (f, hA, hB, hS, banda). Não importa nem lê rótulos. Não é o Jarvis.
Uso: python diagnostico_previsao.py <dir-casos> <saida-previsoes.json>
"""
import json, sys
from pathlib import Path
import numpy as np

C_ADM, MARGEM = 1.0, 0.2          # fixados no pré-registro
TAUS = np.round(np.arange(-3.0, 3.0001, 0.01), 2)
TAUS = TAUS[np.abs(TAUS) > 1e-9]


def _erros(pred, hS, m):
    el = np.abs(20 * np.log10(np.abs(pred[m]) / np.abs(hS[m])))
    ef = np.abs((np.rad2deg(np.angle(pred[m] / hS[m])) + 180) % 360 - 180)
    return float(np.median(el) + np.median(ef) / 10.0)


def diagnosticar(f, hA, hB, hS, banda_hz, margem=MARGEM):
    lo, hi = banda_hz
    faixa = (f >= lo) & (f <= hi)
    m = faixa.copy()
    for h in (hA, hB, hS):
        n = 20 * np.log10(np.maximum(np.abs(h), 1e-30))
        m &= n >= n[faixa].max() - 30.0
    if m.sum() < 5:
        return {"decisao": "nao_conclui", "motivo": "pontos insuficientes", "tau_ms": None, "custos": {}}
    c0 = _erros(hA + hB, hS, m)
    ci = _erros(hA - hB, hS, m)
    cs = [_erros(hA + hB * np.exp(-2j * np.pi * f * t / 1000.0), hS, m) for t in TAUS]
    j = int(np.argmin(cs)); ct, tau = cs[j], float(TAUS[j])
    custos = {"normal": c0, "inversao": ci, "atraso": ct}
    if min(custos.values()) > C_ADM:
        dec = "nao_conclui"
    elif c0 - min(ci, ct) < margem:
        dec = "normal"
    else:
        dec = "inversao" if ci <= ct else "atraso"
    return {"decisao": dec, "tau_ms": tau if dec == "atraso" else None, "tau_melhor_ms": tau, "custos": custos, "pontos": int(m.sum())}


def main():
    dcasos, saida = Path(sys.argv[1]), Path(sys.argv[2])
    out = {}
    for p in sorted(dcasos.glob("*.npz")):
        d = np.load(p)
        f, hA, hB, hS, banda = d["f"], d["hA"], d["hB"], d["hS"], d["banda"]
        out[p.stem] = {"banda_operacional": diagnosticar(f, hA, hB, hS, tuple(banda)),
                       "banda_cheia": diagnosticar(f, hA, hB, hS, (20.0, 20000.0))}
        out[p.stem]["sensibilidade_margem"] = {str(mg): diagnosticar(f, hA, hB, hS, tuple(banda), mg)["decisao"] for mg in (0.1, 0.2, 0.5, 1.0)}
    saida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(out), "casos diagnosticados")


if __name__ == "__main__":
    main()
