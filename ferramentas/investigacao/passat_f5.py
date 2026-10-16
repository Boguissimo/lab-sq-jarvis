"""F-5 em carro real (VW Passat B8): repetibilidade, janelas, grades, coerência e RTA espacial. Sem diagnóstico.

Usa o `calculos.irregularidade` do produto por chamada direta; não altera estimador nem limiares.
Uso: python passat_f5.py <pasta-clone-ayukhno> <saida.json>
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, RAIZ
from passat_comum import *
from jarvis import calculos, limiares
from jarvis.rew_texto import RespostaFrequencia

PRE = json.loads((Path(__file__).resolve().parent / "preregistro-passat.json").read_text(encoding="utf-8"))
BANDAS = {k: tuple(v) for k, v in PRE["F5_carro"]["bandas_uteis_hz"].items()}
AV, RP = limiares.valor("irregularidade_aviso_db"), limiares.valor("irregularidade_reprovada_db")
CONJ = PRE["F5_carro"]["conjuntos_de_repeticao"]


def classe(s):
    return None if s is None else ("reprovada" if s > RP else ("aviso" if s >= AV else "aprovada"))


def sig_prod(g, n):
    r = calculos.irregularidade(RespostaFrequencia(g, np.asarray(n, float), np.zeros_like(g)), "nenhuma")
    return r["sigma_db"]


def sig_formula(g, n, lo, hi):
    m = (g >= lo) & (g <= hi)
    d2 = np.diff(np.asarray(n)[m], n=2)
    return float(1.4826 * np.median(np.abs(d2 - np.median(d2))) / np.sqrt(6.0))


def curva(fonte, nome, jan, ppo):
    h, ini, _ = ler_ir(fonte, nome)
    X, f = espectro(h, jan, ini)
    g = grade_log(ppo)
    Xg = amostrar_bins(X, f, g)
    return g, 20 * np.log10(np.maximum(np.abs(Xg), 1e-30))


def canal_de(nome):
    return nome.split("-")[0]


def ruido_coerencia(fonte, arquivo, lo, hi, n=4):
    d = np.loadtxt(fonte / SET02 / "coherence" / f"{arquivo}.txt", comments="*")
    f, g2 = d[:, 0], np.clip(d[:, 1], 1e-3, 0.999999)
    m = (f >= lo) & (f <= hi)
    s = 8.686 * np.sqrt((1 - g2[m]) / (2 * g2[m] * n))
    return float(np.median(s)), float(np.median(g2[m]))


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    out = {"preregistro": "preregistro-passat.json", "capturas": {}, "repetibilidade": {}, "rta_mmm": {}}
    # --- σ̂ do produto por captura, janela e grade
    nomes = sorted({n for c in CONJ.values() for n in c} | set(CANAIS))
    for nome in nomes:
        ch = canal_de(nome)
        lo, hi = BANDAS[ch]
        e = {}
        for jan in ("W30", "Wfull"):
            for ppo in (48, 96):
                g, n = curva(fonte, nome, jan, ppo)
                sp = sig_prod(g, n)
                e[f"{jan}-{ppo}"] = {"sigma_produto_200_10k": None if sp is None else round(sp, 3), "classe": classe(sp),
                                     "sigma_banda_util": round(sig_formula(g, n, lo, hi), 3)}
        out["capturas"][nome] = e
    # --- repetibilidade
    for rotulo, membros in CONJ.items():
        ch = canal_de(membros[0])
        lo, hi = BANDAS[ch]
        r = {}
        for jan in ("W30", "Wfull"):
            for ppo in (48, 96):
                curvas = np.array([curva(fonte, m, jan, ppo)[1] for m in membros])
                g = grade_log(ppo)
                k = len(membros)
                med = curvas.mean(axis=0)
                res = np.array([(curvas[i] - np.delete(curvas, i, axis=0).mean(axis=0)) / np.sqrt(1 + 1 / (k - 1)) for i in range(k)])
                b = (g >= lo) & (g <= hi)
                b2 = (g >= 200) & (g <= 10000)
                dp = np.std(curvas, axis=0, ddof=1)
                r[f"{jan}-{ppo}"] = {
                    "sigma_banda_util": {"x": [round(sig_formula(g, c, lo, hi), 3) for c in curvas], "media": round(sig_formula(g, med, lo, hi), 3),
                                         "residuo": [round(sig_formula(g, c, lo, hi), 3) for c in res]},
                    "sigma_produto_200_10k": {"x": [None if (s := sig_prod(g, c)) is None else round(s, 3) for c in curvas],
                                              "media": None if (s := sig_prod(g, med)) is None else round(s, 3),
                                              "residuo": [None if (s := sig_prod(g, c)) is None else round(s, 3) for c in res]},
                    "desvio_entre_capturas_mediana_banda_util_db": round(float(np.median(dp[b])), 3),
                    "desvio_entre_capturas_mediana_200_10k_db": round(float(np.median(dp[b2])), 3),
                    "deslocamento_de_nivel_db": [round(float(np.mean(c[b] - med[b])), 3) for c in curvas],
                }
        out["repetibilidade"][rotulo] = {"membros": membros, "banda_util_hz": [lo, hi], "resultados": r}
    # --- coerência (bloco A) como referência de ruído
    coh = {}
    for ch in CANAIS:
        arq = "m_L-ctl2" if ch == "m_L" else ch
        lo, hi = BANDAS[ch]
        s, g2 = ruido_coerencia(fonte, arq, lo, hi)
        coh[ch] = {"banda_util_hz": [lo, hi], "ruido_esperado_db_mediana": round(s, 3), "coerencia_mediana": round(g2, 3)}
    out["coerencia_bloco_A"] = coh
    # --- RTA espacial (04-24)
    for arq in sorted((fonte / RTA).glob("*.txt")):
        d = np.loadtxt(arq, comments="#")
        g, n = d[:, 0], d[:, 1]
        sp = sig_prod(g, n)
        r = calculos.irregularidade(RespostaFrequencia(g, n, np.zeros_like(g)), "nenhuma")
        out["rta_mmm"][arq.stem] = {"pontos_por_oitava": r["condicoes"]["pontos_por_oitava"], "sigma_produto_200_10k": None if sp is None else round(sp, 3),
                                    "classe": classe(sp), "motivos": r["motivos"]}
    Path(saida).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("capturas:", len(out["capturas"]), "| RTA:", {k: (v["sigma_produto_200_10k"], v["classe"]) for k, v in out["rta_mmm"].items()})


if __name__ == "__main__":
    main()
