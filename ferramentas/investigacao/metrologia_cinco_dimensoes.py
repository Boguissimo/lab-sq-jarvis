"""Parte M do pré-registro `preregistro-metrologia-rigor.json`: integridade, repetibilidade, estrutura, incerteza e
admissibilidade por análise, sobre as 5 repetições da sala (joeglondon). Exploratório; não usa nem altera o produto,
exceto `calculos.irregularidade` por chamada direta.
Uso: python metrologia_cinco_dimensoes.py <pasta-clone> <saida.json>
"""
import json, sys
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
BANDAS = {k: tuple(v) for k, v in P["bandas_hz"].items()}
EF = P["parte_M_metrologia"]["admissibilidade_por_analise"]["efeitos"]


def desvio_fase(fases):  # fases: (reps, pontos) em graus; desvio circular em graus
    z = np.exp(1j * np.deg2rad(fases))
    R = np.abs(z.mean(axis=0))
    return np.rad2deg(np.sqrt(-2 * np.log(np.clip(R, 1e-12, 1.0))))


def classificar(u2, efeito):
    return "admissível" if u2 <= efeito / 2 else ("marginal" if u2 <= efeito else "não admissível")


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte)
    out = {"preregistro_sha256": sha256(PRE), "vias": {}}
    for via in P["vias"]:
        dados = [ler_spl(fonte / "SPL" / f"{via} {k}.txt") for k in range(1, 6)]
        f = dados[0][0]
        N = np.array([d[1] for d in dados]); PH = np.array([d[2] for d in dados])
        integ = {"pontos": int(f.size), "finito": bool(np.isfinite(N).all() and np.isfinite(PH).all()),
                 "frequencia_crescente": bool((np.diff(f) > 0).all()),
                 "mesma_grade_nas_5": bool(all(np.array_equal(d[0], f) for d in dados)),
                 "passo_hz": round(float(np.median(np.diff(f))), 4), "fmin": float(f[0]), "fmax": float(f[-1])}
        res = {"integridade": integ}
        for b, (a, c) in BANDAS.items():
            m = (f >= a) & (f <= c)
            dn = N[:, m].std(axis=0, ddof=1); dp = desvio_fase(PH[:, m])
            res[b] = {"rep_nivel_db": {"mediana": round(float(np.median(dn)), 3), "p90": round(float(np.percentile(dn, 90)), 3)},
                      "rep_fase_graus": {"mediana": round(float(np.median(dp)), 2), "p90": round(float(np.percentile(dp, 90)), 2)}}
        # decomposição suave × rápida a 48 ppo
        reamo = [reamostrar(d[0], d[1], d[2], 48, "janela") for d in dados]
        g = reamo[0][0]; Nr = np.array([r[1] for r in reamo])
        R = Nr - Nr.mean(axis=0)
        for b, (a, c) in BANDAS.items():
            m = (g >= a) & (g <= c)
            suave = np.array([np.convolve(r, np.ones(5) / 5, mode="same") for r in R])
            rap = R - suave
            res[b]["decomposicao_48ppo_rms_db"] = {"residuo": round(float(np.sqrt((R[:, m] ** 2).mean())), 3),
                                                   "suave": round(float(np.sqrt((suave[:, m] ** 2).mean())), 3),
                                                   "rapida": round(float(np.sqrt((rap[:, m] ** 2).mean())), 3)}
        # estrutura: σ̂ da média complexa / σ̂ médio por repetição (48 ppo pontual, banda V02)
        sig_rep, curvas = [], []
        for d in dados:
            gg, n2, p2 = reamostrar(d[0], d[1], d[2], 48, "pontual")
            curvas.append(complexo(n2, p2))
            sig_rep.append(calculos.irregularidade(RespostaFrequencia(gg, n2, p2), "nenhuma")["sigma_db"])
        zm = np.mean(curvas, axis=0)
        sig_med = calculos.irregularidade(RespostaFrequencia(gg, 20 * np.log10(np.abs(zm)), np.rad2deg(np.angle(zm))), "nenhuma")["sigma_db"]
        res["estrutura_sigma_hat_v02"] = {"por_repeticao_media": round(float(np.mean(sig_rep)), 3), "da_media_complexa": round(float(sig_med), 3),
                                          "razao_media_sobre_captura": round(float(sig_med / np.mean(sig_rep)), 3)}
        out["vias"][via] = res
    # incerteza tipo A e admissibilidade por análise (mediana entre as vias L, R, Sub Only)
    resumo = {}
    for b, (a, c) in BANDAS.items():
        fc = float(np.sqrt(a * c))
        sn = float(np.median([out["vias"][v][b]["rep_nivel_db"]["mediana"] for v in ("L", "R", "Sub Only")]))
        sf = float(np.median([out["vias"][v][b]["rep_fase_graus"]["mediana"] for v in ("L", "R", "Sub Only")]))
        tab = {}
        for n in (1, 3, 5):
            un, uf = sn / np.sqrt(n), sf / np.sqrt(n)
            # comparação entre duas vias independentes (diferença): u = √2·u
            ef_fase_tempo = 360.0 * fc * EF["tempo_relativo_ms"] / 1000.0
            tab[f"n={n}"] = {
                "u_nivel_db": round(un, 3), "U_k2_diferenca_nivel_db": round(2 * np.sqrt(2) * un, 3),
                "u_fase_graus": round(uf, 2), "U_k2_diferenca_fase_graus": round(2 * np.sqrt(2) * uf, 2),
                "efeito_fase_para_0.25ms_graus": round(ef_fase_tempo, 1),
                "nivel_entre_vias_1dB": classificar(2 * np.sqrt(2) * un, EF["nivel_entre_vias_ou_balanco_LR_db"]),
                "tempo_0.25ms": classificar(2 * np.sqrt(2) * uf, ef_fase_tempo),
                "polaridade_180": classificar(2 * np.sqrt(2) * uf, EF["polaridade_graus"])}
        resumo[b] = {"f_central_hz": round(fc, 1), "s_nivel_db": round(sn, 3), "s_fase_graus": round(sf, 2), "por_n": tab}
    out["incerteza_e_admissibilidade_por_analise"] = resumo
    saida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({v: {"rep": {b: out["vias"][v][b]["rep_nivel_db"] for b in BANDAS},
                          "decomp": {b: out["vias"][v][b]["decomposicao_48ppo_rms_db"] for b in BANDAS},
                          "estr": out["vias"][v]["estrutura_sigma_hat_v02"], "integ": out["vias"][v]["integridade"]}
                      for v in out["vias"]}, ensure_ascii=False, indent=0))
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
