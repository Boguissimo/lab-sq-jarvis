"""Braços B, C e D do ensaio com os dados de joeglondon/speakers-2026-filters (exploratório; sem alterar o produto).

  B = A2 (separador de milhar removido) + metadados HIPOTÉTICOS (posição constante e id temporal por repetição:
      ambos presumidos, o id é SINTÉTICO do harness e NÃO vem dos arquivos REW);
  C = A2 reamostrado para grade logarítmica no harness (sem metadados hipotéticos);
  D = C + B (contrafactual completo).
Uso: python ferramentas/investigacao/bracos_bc.py <pasta-clone> <pasta-trabalho> <saida.json>
Os arquivos reamostrados são derivados; NÃO são novas medições independentes e não vão para o repositório.
"""
import json, shutil, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import braco_a as ba
from comum import verificar_origem, ler_spl, complexo, sha256
from jarvis import calculos, rew_texto
from jarvis.rew_texto import RespostaFrequencia

PPOS = (24, 48, 96, 192)
METODOS = ("pontual", "janela")
F_MIN, F_MAX = 20.0, 20000.0


def reamostrar(f, n, ph, ppo, metodo):
    """Grade log de F_MIN a F_MAX com `ppo` pontos/oitava.
    pontual: nível (dB) e fase DESENROLADA interpolados linearmente em log(f) (decimação; mantém a rugosidade);
    janela: média de potência e fase da média complexa em cada janela de ±½ passo (suaviza)."""
    k = int(round(np.log2(F_MAX / F_MIN) * ppo)) + 1
    g = F_MIN * 2.0 ** (np.arange(k) / ppo)
    if metodo == "pontual":
        lf = np.log(f[1:])  # descarta f=0 se existir
        nn = np.interp(np.log(g), lf, n[1:])
        pu = np.interp(np.log(g), lf, np.unwrap(np.deg2rad(ph[1:])))
        return g, nn, (np.rad2deg(pu) + 180) % 360 - 180
    h = complexo(n, ph)
    lo, hi = g * 2.0 ** (-0.5 / ppo), g * 2.0 ** (0.5 / ppo)
    nn, pp = np.empty(k), np.empty(k)
    for i in range(k):
        m = (f >= lo[i]) & (f < hi[i])
        if m.sum() == 0:  # janela mais fina que a grade original: usa interpolação do vizinho
            j = np.argmin(np.abs(f - g[i]))
            m = np.zeros_like(f, bool); m[j] = True
        z = h[m]
        nn[i] = 10 * np.log10(np.mean(np.abs(z) ** 2))
        pp[i] = np.rad2deg(np.angle(np.mean(z)))
    return g, nn, pp


def montar(fonte, lado, k, destino, ppo=None, metodo=None, hipotetico=False):
    destino.mkdir(parents=True)
    itens = [(f"{lado} {k}", "via_a", lado, f"{lado} sozinho (repetição {k})"),
             (f"Sub Only {k}", "via_b", "Sub", f"Subwoofer sozinho (repetição {k})"),
             (f"{lado} + Sub {k}", "soma", f"{lado}+Sub", f"{lado} e Sub juntos (repetição {k})")]
    meds, trans = [], []
    for nome, papel, canal, desc in itens:
        f, n, p, cab = ler_spl(fonte / "SPL" / f"{nome}.txt")
        m = ba.meta(fonte, nome, papel, canal, desc)
        cabecalho = [c.lstrip("* ").rstrip() for c in cab if c.startswith("*") and c.strip("* ")][:12]
        if ppo:
            g, n2, p2 = reamostrar(f, n, p, ppo, metodo)
            cabecalho += [f"[HARNESS] derivado de {nome}.txt (sha256 {sha256(fonte / 'SPL' / (nome + '.txt'))[:16]}…) por reamostragem "
                          f"logarítmica {ppo} pontos/oitava, método {metodo}, {F_MIN:.0f}–{F_MAX:.0f} Hz; NÃO é nova medição"]
            rf = RespostaFrequencia(g, np.round(n2, 4), np.round(p2, 3))
            m["suavizacao"] = "nenhuma" if metodo == "pontual" else f"média em janela de 1/{ppo} de oitava (harness)"
        else:
            rf = RespostaFrequencia(f, n, p)
        rew_texto.escrever(destino / f"{nome}.txt", rf, cabecalho)
        trans.append({"arquivo": nome, "sha256_derivado": sha256(destino / f"{nome}.txt")})
        if hipotetico:
            m["referencia_temporal"] = {**m["referencia_temporal"], "id": f"HARNESS-PRESUMIDO-{lado}-{k}",
                                        "origem_do_id": "sintético do harness; NÃO vem dos arquivos REW; sincronização não verificada"}
            m["posicao_microfone"] = "PRESUMIDA constante (não verificada)"
        meds.append(m)
    man = {"caso": f"JOEGLONDON-{lado}-{k}", "simulado": False,
           "descricao": "Medições reais de terceiros; ver transformação no cabeçalho.", "tipo_sessao": "investigacao",
           "configuracao_declarada": {"nome": "Sem configuração declarada (dados de terceiros)", "parametros": []},
           "medicoes": meds}
    (destino / "manifesto.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    return destino, trans


def resumo(r, sigma_diag=None):
    """Extrai de uma execução do braço só os números necessários (nada dos dados de terceiros)."""
    out = {"resultado": r["resultado"]}
    if r["resultado"] != "analisou":
        out["mensagem"] = r.get("mensagem_recusa", "")[:160]
        return out
    c = {x["titulo"]: x["dados"] for x in r["calculos"]}
    g = lambda t: c[t].get("resultado", c[t])
    a = r["analise"]
    out["sugestao"] = a["sugestao"]
    out["portao"] = a["portao"]["classificacao"]
    sig = [g(t).get("sigma_db") for t in c if t.startswith("Irregularidade")]
    out["sigma_db"] = [None if s is None else round(s, 3) for s in sig]
    out["ref_temporal_compativel"] = g("Compatibilidade de referência temporal")["compativel"]
    s, v = g("Faixa de sobreposição das vias"), g("Soma medida contra soma de energias")
    out["jarvis_cruzamento_hz"], out["jarvis_vale_hz"] = s.get("cruzamento_hz"), v["freq_hz"]
    out["jarvis_vale_abaixo_db"] = round(-v["min_relativo_db"], 1)
    fase = a.get("fase")
    if fase:
        out["fase"] = {k: (round(fase[k], 2) if isinstance(fase.get(k), (int, float)) else fase.get(k))
                       for k in ("media_graus", "dispersao_graus", "atraso_equivalente_ms", "faixa_hz") if k in fase}
    out["fase_calculada"] = bool(fase)
    vi = [g(t) for t in c if t.startswith("Vales na via")]
    out["vales_via_a"], out["vales_via_b_sub"] = len(vi[0]["vales"]), len(vi[1]["vales"])
    out["indicios"] = [i["dados"]["regra"].split(" — ")[0] for i in r["indicios"]]
    out["hipoteses"] = [(h["dados"]["enunciado"][:60], h["dados"]["avaliacao"]) for h in r["hipoteses"]]
    return out


def efeito_da_conversao(fonte, lado, k, ppo, metodo):
    """Efeito da reamostragem (independente do Jarvis): profundidade/posição do cancelamento da soma em 30–150 Hz
    e consistência soma complexa × medida, antes e depois."""
    d = {}
    dados = {}
    for nome in (f"{lado} {k}", f"Sub Only {k}", f"{lado} + Sub {k}"):
        f, n, p, _ = ler_spl(fonte / "SPL" / f"{nome}.txt")
        dados[nome] = (f, n, p)
    def met(f, nl, ns, nm, pl, ps, pm):
        faixa = (f >= 30) & (f <= 150)
        pot = 10 * np.log10(10 ** (nl / 10) + 10 ** (ns / 10))
        rel = nm - pot
        idx = np.where(faixa)[0]; i = idx[np.argmin(rel[idx])]
        hl, hs, hm = complexo(nl, pl), complexo(ns, ps), complexo(nm, pm)
        mask = faixa
        for x in (nl, ns, nm):
            mask = mask & (x >= x[faixa].max() - 30)
        el = np.abs(20 * np.log10(np.abs(hl + hs) / np.abs(hm)))[mask]
        ef = np.abs((np.rad2deg(np.angle((hl + hs) / hm)) + 180) % 360 - 180)[mask]
        return {"freq_min_hz": float(f[i]), "min_rel_db": float(rel[i]), "med_erro_nivel_db": float(np.median(el)),
                "med_erro_fase_graus": float(np.median(ef)), "pontos": int(mask.sum())}
    (f, nl, pl), (_, ns, ps), (_, nm, pm) = [dados[x] for x in dados]
    d["original"] = met(f, nl, ns, nm, pl, ps, pm)
    rs = {x: reamostrar(*dados[x], ppo, metodo) for x in dados}
    g = rs[f"{lado} {k}"][0]
    d["reamostrado"] = met(g, rs[f"{lado} {k}"][1], rs[f"Sub Only {k}"][1], rs[f"{lado} + Sub {k}"][1],
                           rs[f"{lado} {k}"][2], rs[f"Sub Only {k}"][2], rs[f"{lado} + Sub {k}"][2])
    # σ̂ direto (diagnóstico; independe da suavização declarada) nas três curvas
    d["sigma_diag"] = {nome: round(calculos.irregularidade(RespostaFrequencia(*rs[nome][:1], rs[nome][1], rs[nome][2]), "nenhuma")["sigma_db"] or float("nan"), 3)
                       for nome in rs}
    return d


def main():
    fonte, trab, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    adm = verificar_origem(fonte)
    if trab.exists():
        shutil.rmtree(trab)
    configs = [("B", None, None, True)] + [("C", p, m, False) for p in PPOS for m in METODOS] + \
              [("D", p, m, True) for p in PPOS for m in METODOS]
    res = {"fonte_commit": adm["commit"], "configs": []}
    for braco, ppo, metodo, hip in configs:
        rot = f"{braco}" + (f"-{ppo}ppo-{metodo}" if ppo else "")
        item = {"config": rot, "braco": braco, "ppo": ppo, "metodo": metodo, "metadados_hipoteticos": hip, "pares": []}
        for lado in ("L", "R"):
            for k in range(1, 6):
                pasta, trans = montar(fonte, lado, k, trab / rot / f"{lado}-{k}", ppo, metodo, hip)
                r = ba.rodar(pasta, trab / rot / f"banco-{lado}-{k}")
                par = {"par": f"{lado}-{k}", **resumo(r)}
                if ppo and lado == "L" and k <= 2 or (ppo and lado == "R" and k == 1):
                    par["efeito_conversao"] = efeito_da_conversao(fonte, lado, k, ppo, metodo)
                item["pares"].append(par)
        res["configs"].append(item)
        print(rot, {p["resultado"] for p in item["pares"]}, {p.get("sugestao") for p in item["pares"]})
    Path(saida).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
