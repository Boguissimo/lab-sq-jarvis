"""F-5: o que o σ̂ do produto mede em dado real? (exploratório; não altera estimador nem limiares)

Para cada tipo de curva (L, R, Sub Only, L+Sub, R+Sub), com as 5 repetições reamostradas por `bracos_bc.reamostrar`:
  x_k  = repetição k;  m = média das 5 (componente estável + ruído/√5);
  r_k  = (x_k − média das outras 4)/√1,25  (resíduo de variabilidade entre aquisições, escalonado para ter o desvio
         do ruído por aquisição se o ruído for independente entre repetições).
σ̂ é sempre o `calculos.irregularidade` do PRODUTO (chamada direta, "nenhuma" suavização). A variabilidade entre
repetições inclui qualquer mudança de posição/condição: é limite superior do ruído de aquisição.
Uso: python sigma_f5.py <pasta-clone> <saida.json>
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl
from bracos_bc import reamostrar
from jarvis import calculos, limiares
from jarvis.rew_texto import RespostaFrequencia

TIPOS = ("L", "R", "Sub Only", "L + Sub", "R + Sub")
PPOS = (24, 48, 96, 192)
BANDAS = [(200, 400), (400, 800), (800, 1600), (1600, 3200), (3200, 6400), (6400, 10000)]
AVISO, REPROV = limiares.valor("irregularidade_aviso_db"), limiares.valor("irregularidade_reprovada_db")


def sig_produto(g, n):
    return calculos.irregularidade(RespostaFrequencia(g, np.asarray(n, float), np.zeros_like(g)), "nenhuma")["sigma_db"]


sig_produto_orig = sig_produto


def sig_formula_grade(g, n):
    return sig_formula(g, n)


def sig_formula(f, n, lo=200, hi=10000):
    """Mesma fórmula do produto (1,4826·MAD(Δ²L)/√6) numa faixa/grade arbitrária (réplica; checada contra o produto)."""
    m = (f >= lo) & (f <= hi)
    d2 = np.diff(np.asarray(n)[m], n=2)
    return float(1.4826 * np.median(np.abs(d2 - np.median(d2))) / np.sqrt(6.0))


def classe(s):
    return "reprovada" if s > REPROV else ("aviso" if s >= AVISO else "aprovada")


def conjunto(fonte, tipo, ppo, metodo):
    X = []
    for k in range(1, 6):
        f, n, p, _ = ler_spl(fonte / "SPL" / f"{tipo} {k}.txt")
        X.append((f, n, p))
    if ppo is None:  # grade nativa (linear)
        return X[0][0], np.array([x[1] for x in X])
    cs = [reamostrar(f, n, p, ppo, metodo) for f, n, p in X]
    return cs[0][0], np.array([c[1] for c in cs])


def decompor(X):
    m = X.mean(axis=0)
    r = np.array([(X[k] - np.delete(X, k, axis=0).mean(axis=0)) / np.sqrt(1.25) for k in range(5)])
    return m, r


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte)
    out = {"limiares_produto": {"aviso_db": AVISO, "reprovada_db": REPROV}, "tipos": {}}
    for tipo in TIPOS:
        t = {}
        g, X = conjunto(fonte, tipo, 48, "pontual")
        faixa = (g >= 200) & (g <= 10000)
        m, r = decompor(X)
        # 2. compatibilidade de nível e estrutura da variabilidade
        offs = [float(np.mean(X[k][faixa] - m[faixa])) for k in range(5)]
        t["offset_medio_por_repeticao_db_200_10k"] = [round(o, 3) for o in offs]
        bandas = {}
        for lo, hi in BANDAS:
            b = (g >= lo) & (g < hi)
            bandas[f"{lo}-{hi}"] = {"desvio_entre_rep_mediana_db": round(float(np.median(np.std(X[:, b], axis=0, ddof=1))), 3),
                                    "sigma_hat_x_db": round(float(np.median([sig_formula(g, X[k], lo, hi) for k in range(5)])), 3),
                                    "sigma_hat_m_db": round(sig_formula(g, m, lo, hi), 3),
                                    "sigma_hat_residuo_db": round(float(np.median([sig_formula(g, r[k], lo, hi) for k in range(5)])), 3)}
        t["por_banda_48ppo_pontual"] = bandas
        # 3. componente estável × variabilidade (produto)
        sx = [sig_produto(g, X[k]) for k in range(5)]
        sm = sig_produto(g, m)
        sr = [sig_produto(g, r[k]) for k in range(5)]
        t["sigma_hat_produto_48ppo_pontual"] = {"x_por_repeticao": [round(s, 3) for s in sx], "m_estavel": round(sm, 3),
                                                "residuo_entre_aquisicoes": [round(s, 3) for s in sr]}
        assert abs(sig_formula(g, X[0]) - sx[0]) < 1e-9  # réplica confere com o produto
        t["desvio_entre_repeticoes_mediana_db"] = round(float(np.median(np.std(X[:, faixa], axis=0, ddof=1))), 3)
        # autocorrelação lag-1 do resíduo (ruído branco ≈ 0)
        ac = []
        for k in range(5):
            z = r[k][faixa] - r[k][faixa].mean()
            ac.append(float(np.sum(z[1:] * z[:-1]) / np.sum(z * z)))
        t["autocorr_lag1_residuo"] = [round(a, 3) for a in ac]
        # 5. o portão rejeita medição repetível?
        t["classe_produto_x"] = [classe(s) for s in sx]
        t["classe_se_so_ruido"] = [classe(s) for s in sr]
        # piso de estrutura: m + ruído branco conhecido
        rng = np.random.default_rng(20261016)
        piso = {}
        for s in (0.25, 0.5, 1.0, 1.5, 2.0):
            piso[str(s)] = round(sig_produto(g, m + rng.normal(0, s, m.size)), 3)
        t["sigma_hat_de_m_mais_ruido_branco_conhecido"] = piso
        # 4. sensibilidade à grade e à interpolação
        sens = {}
        for ppo in PPOS:
            for metodo in ("pontual", "janela"):
                gg, XX = conjunto(fonte, tipo, ppo, metodo)
                mm, rr = decompor(XX)
                # Em 24,0 ppo exatos o produto devolve "densidade insuficiente" (comparação de ponto flutuante com o
                # mínimo 24: 23,9999…); nesse caso usa-se a réplica da fórmula (rótulo no relatório).
                sp = sig_formula_grade if ppo == 24 else sig_produto_orig
                fx = (gg >= 200) & (gg <= 10000)
                sens[f"{ppo}-{metodo}"] = {"x": round(float(np.median([sp(gg, XX[k]) for k in range(5)])), 3),
                                           "m": round(sp(gg, mm), 3),
                                           "residuo": round(float(np.median([sp(gg, rr[k]) for k in range(5)])), 3),
                                           "desvio_entre_rep": round(float(np.median(np.std(XX[:, fx], axis=0, ddof=1))), 3)}
        gn, XN = conjunto(fonte, tipo, None, None)
        mn, rn = decompor(XN)
        sens["nativa-linear (réplica da fórmula)"] = {"x": round(float(np.median([sig_formula(gn, XN[k]) for k in range(5)])), 3),
                                                      "m": round(sig_formula(gn, mn), 3),
                                                      "residuo": round(float(np.median([sig_formula(gn, rn[k]) for k in range(5)])), 3),
                                                      "desvio_entre_rep": round(float(np.median(np.std(XN[:, (gn >= 200) & (gn <= 10000)], axis=0, ddof=1))), 3)}
        t["sensibilidade_grade"] = sens
        out["tipos"][tipo] = t
        print(tipo, "x", t["sigma_hat_produto_48ppo_pontual"]["x_por_repeticao"], "m", sm, "resíduo", t["sigma_hat_produto_48ppo_pontual"]["residuo_entre_aquisicoes"],
              "desvio", t["desvio_entre_repeticoes_mediana_db"], "ac1", t["autocorr_lag1_residuo"][:2], "piso", piso)
    Path(saida).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
