"""Admissibilidade da soma complexa (L|R)+Sub como previsão de (L|R)+Sub medido — critérios pré-registrados.

Uso: python ferramentas/investigacao/admissibilidade.py <pasta-clone-joeglondon> <saida.json>
Não usa o produto (Jarvis). Dados lidos como texto; nada é executado do repositório externo.
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl, complexo, sha256, RAIZ

PRE = Path(__file__).resolve().parent / "preregistro-braco-a.json"
CRIT = json.loads(PRE.read_text(encoding="utf-8"))["admissibilidade_da_soma_complexa"]
F0, F1 = CRIT["faixa_hz"]
LIM = CRIT["admissivel_se"]


def erro_fase(a, b):
    return np.abs((np.rad2deg(np.angle(a / b)) + 180) % 360 - 180)


def avaliar(lado, k, fonte):
    fl, nl, pl, _ = ler_spl(fonte / "SPL" / f"{lado} {k}.txt")
    fs, ns, ps, _ = ler_spl(fonte / "SPL" / f"Sub Only {k}.txt")
    fm, nm, pm, _ = ler_spl(fonte / "SPL" / f"{lado} + Sub {k}.txt")
    assert np.array_equal(fl, fs) and np.array_equal(fl, fm), "grades diferentes"
    f = fl
    faixa = (f >= F0) & (f <= F1)
    mask = faixa
    for n in (nl, ns, nm):
        mask = mask & (n >= n[faixa].max() - 30.0)
    hl, hs, hm = complexo(nl, pl), complexo(ns, ps), complexo(nm, pm)

    def metr(pred):
        el = np.abs(20 * np.log10(np.abs(pred[mask]) / np.abs(hm[mask])))
        ef = erro_fase(pred[mask], hm[mask])
        return {"mediana_erro_nivel_db": float(np.median(el)), "p95_erro_nivel_db": float(np.percentile(el, 95)),
                "mediana_erro_fase_graus": float(np.median(ef)), "pontos": int(mask.sum())}

    base = metr(hl + hs)
    admiss = (base["mediana_erro_nivel_db"] <= LIM["mediana_erro_nivel_db_max"]
              and base["p95_erro_nivel_db"] <= LIM["p95_erro_nivel_db_max"]
              and base["mediana_erro_fase_graus"] <= LIM["mediana_erro_fase_graus_max"])
    # diagnóstico (não critério): polaridade invertida e varredura do atraso do Sub
    inv = metr(hl - hs)
    melhor = None
    for dt in np.arange(-3.0, 3.0001, 0.01):
        pred = hl + hs * np.exp(-2j * np.pi * f * dt / 1000.0)
        m = metr(pred)
        if melhor is None or m["mediana_erro_nivel_db"] < melhor[1]["mediana_erro_nivel_db"]:
            melhor = (float(dt), m)
    # faixa de nível relativa entre as vias na faixa (informativa, nível "compatível"?)
    dif = float(np.median(nl[mask] - ns[mask]))
    return {"lado": lado, "k": k, "admissivel": bool(admiss), "base": base, "polaridade_invertida": inv,
            "melhor_atraso_sub_ms": melhor[0], "com_melhor_atraso": melhor[1],
            "mediana_L_menos_Sub_db": dif}


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte)
    res = [avaliar(l, k, fonte) for l in ("L", "R") for k in range(1, 6)]
    # repetibilidade da via L (variação entre repetições na faixa), informativa para o braço B
    rep = {}
    for nome in ("L", "R", "Sub Only", "L + Sub", "R + Sub"):
        curvas = np.array([ler_spl(fonte / "SPL" / f"{nome} {k}.txt")[1] for k in range(1, 6)])
        f = ler_spl(fonte / "SPL" / f"{nome} 1.txt")[0]
        fx = (f >= F0) & (f <= F1)
        rep[nome] = {"desvio_padrao_medio_db_30_150Hz": float(np.mean(np.std(curvas[:, fx], axis=0)))}
    out = {"preregistro_sha256": sha256(PRE), "resultados": res, "repetibilidade": rep}
    saida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in res:
        b = r["base"]
        print(f"{r['lado']}{r['k']} admissível={r['admissivel']} med_nivel={b['mediana_erro_nivel_db']:.2f} dB "
              f"p95={b['p95_erro_nivel_db']:.2f} med_fase={b['mediana_erro_fase_graus']:.1f}° pts={b['pontos']} | "
              f"inv_med={r['polaridade_invertida']['mediana_erro_nivel_db']:.2f} | melhor_atraso={r['melhor_atraso_sub_ms']:.2f} ms "
              f"(med={r['com_melhor_atraso']['mediana_erro_nivel_db']:.2f})")
    print(json.dumps(rep, ensure_ascii=False))


if __name__ == "__main__":
    main()
