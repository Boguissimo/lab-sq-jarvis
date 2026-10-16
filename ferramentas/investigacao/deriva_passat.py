"""Ensaio pré-registrado em `preregistro-deriva-passat.json`: estabilidade de decisões de balanço L/R entre capturas
(deriva temporal / refazer) e utilidade do gatilho adaptativo. Exploratório; não usa o produto.
Uso: python deriva_passat.py <pasta-clone-ayukhno> <saida.json>
"""
import itertools, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, sha256, RAIZ
from passat_comum import *

PRE = Path(__file__).resolve().parent / "preregistro-deriva-passat.json"
P = json.loads(PRE.read_text(encoding="utf-8"))
TAU = 0.3  # dB, fixado em preregistro-deriva-passat.json (gatilho_adaptativo.regra)
PPO = P["grade_ppo"]


def resp(fonte, nome):
    h, ini, _ = ler_ir(fonte, nome)
    X, f = espectro(h, P["janela"], ini)
    g = grade_log(PPO)
    return g, amostrar_bins(X, f, g)


def mediana_nivel_dif(g, a, b, lo, hi):
    m = (g >= lo) & (g <= hi)
    return float(np.median(20 * np.log10(np.abs(a[m])) - 20 * np.log10(np.abs(b[m]))))


def gatilho(g, a, b, lo, hi):
    m = (g >= lo) & (g <= hi)
    return float(np.median(np.abs(20 * np.log10(np.abs(a[m]) / np.abs(b[m])))))


def classe(amp, ef):
    return "estável" if amp <= 0.5 * ef else ("instável" if amp > ef else "intermediária")


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    nomes = ["m_L", "m_L-ctl1", "m_L-ctl3", "m_R", "w_L", "w_R", "w_R-retake"]
    R = {n: resp(fonte, n) for n in nomes}
    g = R["m_L"][0]
    D = P["decisoes_D"]
    out = {"preregistro_sha256": sha256(PRE), "decisoes": {}, "gatilhos": {}}
    esp = {"D1": ("m_R", ["m_L", "m_L-ctl1", "m_L-ctl3"], 200, 10000, True),
           "D2": ("w_L", ["w_R", "w_R-retake"], 40, 500, False),
           "D3": ("w_L", ["w_R", "w_R-retake"], 500, 2000, False)}
    for chave, (fixa, caps, lo, hi, cap_primeiro) in esp.items():
        ef = [v for k, v in D.items() if k.startswith(chave)][0]["efeito_db"]
        vals = {}
        for c in caps:
            # D1: capturas são do lado L (m_L − m_R); D2/D3: w_L − w_R(k)
            vals[c] = mediana_nivel_dif(g, R[c][1], R[fixa][1], lo, hi) if cap_primeiro else mediana_nivel_dif(g, R[fixa][1], R[c][1], lo, hi)
        amp = max(vals.values()) - min(vals.values())
        out["decisoes"][chave] = {"valores_db": {k: round(v, 3) for k, v in vals.items()}, "amplitude_db": round(amp, 3),
                                  "efeito_db": ef, "estabilidade": classe(amp, ef)}
    bandas = P["gatilho_adaptativo"]["bandas_uteis_hz"]
    for a, b in (("m_L", "m_L-ctl1"), ("m_L", "m_L-ctl3"), ("m_L-ctl1", "m_L-ctl3"), ("w_R", "w_R-retake")):
        lo, hi = bandas["m_L" if a.startswith("m_L") else "w_R"]
        v = gatilho(g, R[a][1], R[b][1], lo, hi)
        out["gatilhos"][f"{a}×{b}"] = {"banda_util_hz": [lo, hi], "mediana_abs_dnivel_db": round(v, 3), "pediria_nova_captura": bool(v > TAU)}
    v = gatilho(g, R["w_R"][1], R["w_R-retake"][1], 500, 2000)
    out["gatilhos"]["w_R×w_R-retake@500-2000 (complemento rotulado)"] = {"banda_hz": [500, 2000], "mediana_abs_dnivel_db": round(v, 3), "pediria_nova_captura": bool(v > TAU)}
    # descritivo de fase entre capturas m_L (200–2000 Hz) × deriva do manifesto
    m = (g >= 200) & (g <= 2000)
    deriva = {"m_L-ctl1": 0.0, "m_L": -0.291, "m_L-ctl3": -0.636}
    fase = {}
    for a, b in (("m_L-ctl1", "m_L"), ("m_L", "m_L-ctl3"), ("m_L-ctl1", "m_L-ctl3")):
        dphi = np.abs(np.rad2deg(np.angle(R[b][1][m] / R[a][1][m])))
        dt = abs(deriva[b] - deriva[a]) / FS
        esperado = np.median(360.0 * g[m] * dt)
        fase[f"{a}×{b}"] = {"mediana_abs_dfase_graus": round(float(np.median(dphi)), 2), "esperado_pela_deriva_graus": round(float(esperado), 2)}
    out["descritivo_fase_200_2000"] = fase
    saida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
