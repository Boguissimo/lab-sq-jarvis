"""Parte E do pré-registro `preregistro-metrologia-rigor.json`: custo (varreduras) × precisão da decisão para as
aquisições simplificada (S), repetida (R2, R3) e adaptativa (A), sobre as 5 repetições da sala (joeglondon).
Exploratório; não usa nem altera o produto, exceto `calculos.irregularidade` por chamada direta.
Uso: python rigor_usabilidade.py <pasta-clone> <saida.json>
"""
import itertools, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl, complexo, sha256
from bracos_bc import reamostrar
from jarvis import calculos
from jarvis.rew_texto import RespostaFrequencia

PRE = Path(__file__).resolve().parent / "preregistro-metrologia-rigor.json"
P = json.loads(PRE.read_text(encoding="utf-8"))
E = P["parte_E_experimento_rigor_usabilidade"]
TAU = E["tau_db"]
CRIT = json.loads((Path(__file__).resolve().parent / "preregistro-braco-a.json").read_text(encoding="utf-8"))["admissibilidade_da_soma_complexa"]
F0, F1 = CRIT["faixa_hz"]; LIM = CRIT["admissivel_se"]
V0, V1 = P["bandas_hz"]["v02"]
EFEITO = {"Q1": 1.0, "Q3": 0.25, "Q4": 1.0, "Q5": 1.0, "Q6": 0.5}
DT = np.arange(-3.0, 3.0001, 0.01)


def erro_fase(a, b):
    return np.abs((np.rad2deg(np.angle(a / b)) + 180) % 360 - 180)


def carregar(fonte):
    D = {}
    for via in ("L", "R", "Sub Only", "L + Sub", "R + Sub"):
        L = [ler_spl(fonte / "SPL" / f"{via} {k}.txt") for k in range(1, 6)]
        D[via] = np.array([complexo(x[1], x[2]) for x in L])
    D["f"] = L[0][0]
    return D


def media(D, via, idx):
    return D[via][list(idx)].mean(axis=0)


def quantidades(D, lado, idx):
    f = D["f"]
    hl, hs, hm = (media(D, v, idx) for v in (lado, "Sub Only", f"{lado} + Sub"))
    faixa = (f >= F0) & (f <= F1)
    mask = faixa.copy()
    for h in (hl, hs, hm):
        n = 20 * np.log10(np.abs(h))
        mask &= n >= n[faixa].max() - 30.0

    def m(pred):
        el = np.abs(20 * np.log10(np.abs(pred[mask]) / np.abs(hm[mask])))
        return np.median(el), np.percentile(el, 95), np.median(erro_fase(pred[mask], hm[mask]))
    base = m(hl + hs); inv = m(hl - hs)
    # varredura do atraso do Sub só nos pontos da máscara (equivalente a admissibilidade.py)
    erros = [np.median(np.abs(20 * np.log10(np.abs((hl + hs * np.exp(-2j * np.pi * f * dt / 1000.0))[mask]) / np.abs(hm[mask])))) for dt in DT]
    Q = {"Q1": base[0], "Q2": bool(base[0] <= LIM["mediana_erro_nivel_db_max"] and base[1] <= LIM["p95_erro_nivel_db_max"]
                                  and base[2] <= LIM["mediana_erro_fase_graus_max"]),
         "Q3": float(DT[int(np.argmin(erros))]), "Q4": inv[0] - base[0]}
    # Q5/Q6 na banda V02 (lado isolado); Q5 usa L − R, calculado fora desta função
    return Q


def q56(D, idx_l, idx_r):
    f = D["f"]
    m = (f >= V0) & (f <= V1)
    hl, hr = media(D, "L", idx_l), media(D, "R", idx_r)
    q5 = float(np.median(20 * np.log10(np.abs(hl[m]) / np.abs(hr[m]))))
    out = {"Q5": q5}
    for nome, h in (("L", hl), ("R", hr)):
        g, n2, p2 = reamostrar(f, 20 * np.log10(np.abs(h)), np.rad2deg(np.angle(h)), 48, "pontual")
        out["Q6_" + nome] = calculos.irregularidade(RespostaFrequencia(g, n2, p2), "nenhuma")["sigma_db"]
    return out


def tomadas_adaptativas(D, ordem):
    """Devolve quantas repetições o modo A usa para esta ordem (regra do pré-registro)."""
    f = D["f"]
    m = (f >= F0) & (f <= F1)
    vias = ("L", "R", "Sub Only", "L + Sub", "R + Sub")
    n = 2
    while n < 5:
        a, b = ordem[n - 2], ordem[n - 1]
        piores = max(np.median(np.abs(20 * np.log10(np.abs(D[v][a][m]) / np.abs(D[v][b][m])))) for v in vias)
        if piores <= TAU:
            break
        n += 1
    return n


def p(x, q):
    return float(np.percentile(x, q))


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte)
    D = carregar(fonte)
    todas = range(5)
    res = {"preregistro_sha256": sha256(PRE), "modos": {}}
    linhas = []  # (modo, lado, n_usado, Q-dict modo, Q-dict ref)
    for lado in ("L", "R"):
        other = "R" if lado == "L" else "L"
        for n, nome in ((1, "S"), (2, "R2"), (3, "R3")):
            for sub in itertools.combinations(todas, n):
                comp = [i for i in todas if i not in sub]
                qm, qr = quantidades(D, lado, sub), quantidades(D, lado, comp)
                q5m, q5r = q56(D, sub, sub), q56(D, comp, comp)
                linhas.append((nome, lado, n, {**qm, **{k: v for k, v in q5m.items()}}, {**qr, **q5r}))
        usos = []
        for ordem in itertools.permutations(todas):
            n = tomadas_adaptativas(D, ordem)
            usos.append(n)
            if n < 5:
                sub, comp = ordem[:n], ordem[n:]
                qm, qr = quantidades(D, lado, sub), quantidades(D, lado, comp)
                q5m, q5r = q56(D, sub, sub), q56(D, comp, comp)
                linhas.append(("A", lado, n, {**qm, **q5m}, {**qr, **q5r}))
        res.setdefault("adaptativo_usos", {})[lado] = {str(k): int(usos.count(k)) for k in (2, 3, 4, 5)}
    for modo in ("S", "R2", "R3", "A"):
        L = [l for l in linhas if l[0] == modo]
        nmed = float(np.mean([l[2] for l in L]))
        r = {"avaliacoes": len(L), "varreduras_por_via_media": round(nmed, 2)}
        for q, ef, chave in (("Q1", EFEITO["Q1"], "Q1"), ("Q3", EFEITO["Q3"], "Q3"), ("Q4", EFEITO["Q4"], "Q4"), ("Q5", EFEITO["Q5"], "Q5")):
            e = np.array([abs(l[3][chave] - l[4][chave]) for l in L])
            r[q] = {"P50": round(p(e, 50), 4), "P95": round(p(e, 95), 4), "suficiente": bool(p(e, 95) <= 0.5 * ef)}
        e6 = np.array([abs(l[3]["Q6_" + l[1]] - l[4]["Q6_" + l[1]]) for l in L])
        r["Q6"] = {"P50": round(p(e6, 50), 4), "P95": round(p(e6, 95), 4), "suficiente": bool(p(e6, 95) <= 0.5 * EFEITO["Q6"])}
        conc = np.array([l[3]["Q2"] == l[4]["Q2"] for l in L])
        r["Q2_concordancia"] = {"fracao": round(float(conc.mean()), 4), "suficiente": bool(conc.mean() >= 0.95)}
        res["modos"][modo] = r
    res["modo_A_sem_referencia_usou_5"] = {lado: res["adaptativo_usos"][lado]["5"] for lado in ("L", "R")}
    saida.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
