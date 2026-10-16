"""Medições complementares da emenda E4 (SC-208 revisto) — JV-V02.

Domínio simulado apenas; não ajusta limiares (P8). Gera `08-qa/validacao-limiares-e4.md`, que **complementa** (não substitui)
`08-qa/validacao-limiares.md`. Uso: `python ferramentas/medir_e4.py` (a partir da raiz do repositório).
"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jarvis import calculos, limiares
from jarvis.referencia import modelo

F = modelo.grade_log()
TW = {"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}]}
base = modelo.resposta_via(TW, F)


def sig(h, s, seed):
    r = modelo.adquirir(h, F, {"ruido_sigma_db": s}, semente=seed if s else None, quantizar=True)
    return calculos.irregularidade(r, "nenhuma")


out = {}
cen = {"via plana LR4": base,
       "reflexão g=0,9": modelo.resposta_via({**TW, "reflexoes": [{"g": 0.9, "tau_ms": 0.4}]}, F),
       "reflexões múltiplas": modelo.resposta_via({**TW, "reflexoes": [{"g": 0.6, "tau_ms": 0.3}, {"g": 0.5, "tau_ms": 0.9}]}, F),
       "cancelamento": base + modelo.resposta_via({"filtros": [{"tipo": "lr4_pb", "fc_hz": 3000.0}], "polaridade_fiacao": -1}, F)}
SIG = (0.3, 0.45, 0.55, 1.0, 1.4, 1.6, 2.0)
A, fora = [], []
for n, h in cen.items():
    for s in SIG:
        e = np.array([sig(h, s, k)["sigma_db"] - s for k in range(50)])
        A.append((n, s, e))
        for x in e:
            if abs(x) > 0.15 * s + 0.05:
                fora.append((n, s, round(float(x), 3)))
rel = np.concatenate([e / s for _, s, e in A])
ab = np.concatenate([e for _, _, e in A])
out["a_global"] = {"N": int(ab.size), "vies_db": float(ab.mean()), "eam_db": float(np.abs(ab).mean()),
                   "dp_db": float(ab.std(ddof=1)), "vies_rel": float(rel.mean()), "dp_rel": float(rel.std(ddof=1)),
                   "pct_rel": {str(p): float(np.percentile(rel, p)) for p in (1, 5, 25, 50, 75, 95, 99)},
                   "fora": len(fora)}
out["a_por_sigma"] = {}
for s in SIG:
    e = np.concatenate([e for n, ss, e in A if ss == s])
    f = [x for n, ss, x in fora if ss == s]
    out["a_por_sigma"][str(s)] = {"N": int(e.size), "vies": float(e.mean()), "eam": float(np.abs(e).mean()),
                                  "dp": float(e.std(ddof=1)), "p5": float(np.percentile(e, 5)),
                                  "p95": float(np.percentile(e, 95)), "fora": len(f),
                                  "pos": sum(1 for x in f if x > 0), "neg": sum(1 for x in f if x < 0)}
out["a_por_cenario"] = {n: {"vies_rel": float(np.concatenate([e / s for nn, s, e in A if nn == n]).mean()),
                            "fora": sum(1 for a in fora if a[0] == n),
                            "pos": sum(1 for a in fora if a[0] == n and a[2] > 0)} for n in cen}
lim = {}
for n in ("via plana LR4", "reflexões múltiplas"):
    for s in (0.40, 0.45, 0.48, 0.50, 0.52, 0.55, 0.60, 1.30, 1.40, 1.45, 1.50, 1.55, 1.60, 1.70):
        cl = [sig(cen[n], s, k)["classificacao"] for k in range(200)]
        lim[f"{n}|{s}"] = {"aprov": cl.count("aprovada"), "aviso": cl.count("aviso"), "reprov": cl.count("reprovada")}
out["limites"] = lim

lb = limiares.valor("detector_banda_db")


def det(h_a, h_d, s, ka, kd):
    a = modelo.adquirir(h_a, F, {"ruido_sigma_db": s}, semente=ka if s else None)
    d = modelo.adquirir(h_d, F, {"ruido_sigma_db": s}, semente=kd if s else None)
    sa, sd = (calculos.irregularidade(x, "nenhuma")["sigma_db"] for x in (a, d))
    return calculos.detector_mudanca_via(a, d, sa, sd, calculos.faixa_util(a))


def rep(d1, d2, freq=False):
    x1 = d1["pior_banda"]["delta_db"] if d1["pior_banda"] else d1["media_db"]
    x2 = d2["pior_banda"]["delta_db"] if d2["pior_banda"] else d2["media_db"]
    tol = max(d1["limiar_bandas_db"] or 0, d2["limiar_bandas_db"] or 0, lb)
    ok = (x1 * x2 > 0) and abs(x1 - x2) <= tol
    if ok and freq:
        f1, f2 = d1["faixa_mudanca_hz"], d2["faixa_mudanca_hz"]
        ok = f1 is not None and f2 is not None and max(f1[0], f2[0]) <= min(f1[1], f2[1])
    return ok


def bateria(nome, h, s, N):
    ind = conf = conf_f = 0
    for k in range(N):
        d0 = det(base, h, s, k, k + 50000)
        d1 = det(base, h, s, k, k + 100000)  # mesmo "antes"; segunda aquisição "depois" independente
        ind += d0["resultado"] == "mudanca_detectada"
        if d0["resultado"] == d1["resultado"] == "mudanca_detectada":
            conf += rep(d0, d1)
            conf_f += rep(d0, d1, True)
    return {"cenario": nome, "sigma": s, "N": N, "indicativas": ind, "confirmadas": conf, "confirmadas_com_faixa": conf_f}


out["fp"] = [bateria("só polaridade", -base, s, 1000) for s in (0.5, 1.0, 1.5, 2.0)]


def g(extra):
    return modelo.resposta_via({**TW, "filtros": TW["filtros"] + extra}, F)


out["fn"] = [bateria(n, h, s, 300) for n, h, s in (
    ("N3 ganho +3 dB", -g([{"tipo": "ganho", "ganho_db": 3.0}]), 1.5),
    ("ganho +1,5 dB", g([{"tipo": "ganho", "ganho_db": 1.5}]), 0.5),
    ("ganho +1,5 dB", g([{"tipo": "ganho", "ganho_db": 1.5}]), 1.5),
    ("ganho −1,5 dB", g([{"tipo": "ganho", "ganho_db": -1.5}]), 1.5),
    ("PEQ −3 dB Q4 6 kHz", g([{"tipo": "peq", "f0_hz": 6000.0, "ganho_db": -3.0, "q": 4.0}]), 0.5),
    ("PEQ −3 dB Q4 6 kHz", g([{"tipo": "peq", "f0_hz": 6000.0, "ganho_db": -3.0, "q": 4.0}]), 1.5),
    ("PEQ +3 dB Q2 6 kHz", g([{"tipo": "peq", "f0_hz": 6000.0, "ganho_db": 3.0, "q": 2.0}]), 1.5))]

# ---------------------------------------------------------------- relatório
RAIZ = Path(__file__).resolve().parents[1]
SAIDA = (RAIZ / ".arkan" / "features" / "lab-sq-jarvis" / "003-000-jv-v02-honestidade-e-seguranca"
         / "08-qa" / "validacao-limiares-e4.md")
pc = lambda x: f"{100 * x:.1f} %"
L = ["# Validação dos limiares provisórios — complemento da emenda E4 (SC-208)", "",
     "> **Domínio simulado apenas.** Complementa `validacao-limiares.md`, que **permanece como foi gerado** (inclui os "
     "22/1 400 resultados fora da tolerância e os falsos positivos indicativos originais). Nenhum limiar foi ajustado (P8). "
     "Gerado por `ferramentas/medir_e4.py` (sementes fixas).", "",
     "## (a) σ̂ — viés, dispersão e distribuição do erro", "",
     "Mesma bateria de `validacao-limiares.md` (4 cenários × 7 níveis de σ × 50 sementes = 1 400 realizações). "
     "Erro = σ̂ − σ injetado.", ""]
g = out["a_global"]
L += [f"- **Global (N = {g['N']}):** viés médio assinado {g['vies_db']:+.3f} dB ({pc(g['vies_rel'])} de σ); erro absoluto médio "
      f"{g['eam_db']:.3f} dB; desvio-padrão {g['dp_db']:.3f} dB. Erro relativo (erro/σ), percentis 1/5/25/50/75/95/99: "
      + " / ".join(f"{100 * g['pct_rel'][str(p)]:+.1f} %" for p in (1, 5, 25, 50, 75, 95, 99)) + ".",
      f"- **Fora da tolerância original** (|σ̂ − σ| > 15 % de σ + 0,05 dB): **{g['fora']} de {g['N']}** ({pc(g['fora'] / g['N'])}). "
      "Mantida a tolerância original; nada foi ampliado.", "",
      "| σ injetado | N | viés (dB) | erro abs. médio | desvio-padrão | p5 | p95 | fora da tolerância (+/−) |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for s, v in out["a_por_sigma"].items():
    L.append(f"| {float(s):.2f} | {v['N']} | {v['vies']:+.3f} | {v['eam']:.3f} | {v['dp']:.3f} | {v['p5']:+.3f} | {v['p95']:+.3f} | "
             f"{v['fora']} ({v['pos']}+/{v['neg']}−) |")
L += ["", "| cenário | viés relativo | fora da tolerância | dos quais positivos |", "| --- | --- | --- | --- |"]
for n, v in out["a_por_cenario"].items():
    L.append(f"| {n} | {pc(v['vies_rel'])} | {v['fora']}/350 | {v['pos']} |")
L += ["", "**Leitura (sem ajuste):** o desvio-padrão do erro cresce com σ (o erro relativo é aproximadamente constante), de "
      "modo que as realizações fora da tolerância se concentram nos σ altos (19 das 22 em σ ≥ 1,4 dB). Há um viés positivo "
      "pequeno (≈ +2 % de σ no conjunto) que vem sobretudo dos cenários com estrutura espectral real "
      "(reflexões múltiplas: viés relativo maior e 6 de 9 fora da tolerância positivas); na via plana o viés é ≈ 0. "
      "Isso é um erro **sistemático leve** do estimador na presença de estrutura, coerente com o limite declarado na E1 "
      "(σ̂ é irregularidade fina, não ruído direto).", "",
      "### Classificação perto de 0,5 dB e 1,5 dB (200 sementes por linha)", "",
      "Classe teórica pelo σ injetado: aprovada (< 0,5), aviso (0,5 a 1,5), reprovada (> 1,5). "
      "**Falsa aprovação** = classificada menos grave que a teórica; **falsa reprovação** = mais grave.", "",
      "| cenário | σ injetado | classe teórica | aprovada | aviso | reprovada | falsas aprovações | falsas reprovações |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for k, v in out["limites"].items():
    n, s = k.split("|")
    s = float(s)
    teor = "aprovada" if s < 0.5 else ("aviso" if s < 1.5 else "reprovada")
    if s in (0.5, 1.5):
        teor = "no limite"
    fa = fr = 0
    if teor == "aviso":
        fa, fr = v["aprov"], v["reprov"]
    elif teor == "aprovada":
        fr = v["aviso"] + v["reprov"]
    elif teor == "reprovada":
        fa = v["aprov"] + v["aviso"]
    L.append(f"| {n} | {s:.2f} | {teor} | {v['aprov']} | {v['aviso']} | {v['reprov']} | "
             f"{fa if teor != 'no limite' else '—'} | {fr if teor != 'no limite' else '—'} |")
L += ["", "**Leitura:** a transição entre classes é gradual, com largura de cerca de ±0,1 a ±0,15 dB em torno de cada limite; "
      "a classificação nessa vizinhança é **probabilística**, não determinística. Nenhuma realização com σ ≥ 1,0 dB foi "
      "classificada `aprovada` nas duas famílias testadas. Com a reflexão múltipla, σ̂ tende a ficar acima de σ e a "
      "classificação antecipa o aviso (σ = 0,45: 45 % `aviso`).", "",
      "## (b) Detector — indicativas, confirmadas e falsos negativos", "",
      "Fluxo fiel ao serviço: **um** \"antes\" (semente k) e duas aquisições \"depois\" independentes (sementes k + 50 000 e "
      "k + 100 000). *Indicativa* = a primeira aquisição \"depois\" dá `mudança detectada`. *Confirmada (regra atual)* = as duas "
      "dão `mudança detectada`, mesmo sentido e concordância dentro do limiar das bandas (`sessao.py`). *Confirmada com faixa "
      "compatível (E4)* = a regra atual **e** interseção não vazia das faixas de frequência da mudança.", "",
      "### Falsos positivos (só polaridade, sem mudança de magnitude; N = 1 000 por linha)", "",
      "| σ | indicativas | confirmadas (regra atual) | confirmadas com faixa compatível (E4) | limite superior ≈95 % se 0 (regra dos três) |",
      "| --- | --- | --- | --- | --- |"]
for x in out["fp"]:
    ls = f"{100 * 3 / x['N']:.1f} %" if x["confirmadas_com_faixa"] == 0 else "—"
    L.append(f"| {x['sigma']:.1f} | {x['indicativas']} ({pc(x['indicativas'] / x['N'])}) | {x['confirmadas']} "
             f"({pc(x['confirmadas'] / x['N'])}) | {x['confirmadas_com_faixa']} ({pc(x['confirmadas_com_faixa'] / x['N'])}) | {ls} |")
L += ["", "**Leitura:** com σ ≤ 1,0 dB não houve alarme algum em 1 000 sementes. Com σ = 1,5 dB há alarmes indicativos e **também "
      "confirmações falsas**: a repetição reduz muito a taxa, mas **não a zera**, porque as duas comparações \"depois × antes\" "
      "compartilham o mesmo \"antes\" (o ruído do \"antes\" é comum às duas e não é repetido). A exigência de faixa compatível "
      "elimina só parte delas. O critério \"zero falso positivo confirmado até σ = 1,5 dB\" **não é atendido** pelo detector atual "
      "nesta bateria. É uma **limitação conhecida, não resolvida**: o detector não está validado quanto a falsos positivos confirmados, e qualquer limite futuro deve ser justificado e testado de forma independente. A região σ ≥ 1,5 dB coincide com o limite de reprovação da qualidade "
      "(`aviso`/`reprovada`).", "",
      "**Custo operacional.** Com duas vias independentes e σ = 1,5 dB, a chance de pelo menos um alarme indicativo numa sessão é "
      f"≈ {pc(1 - (1 - out['fp'][2]['indicativas'] / out['fp'][2]['N']) ** 2)} (cada alarme pede uma repetição). Com σ ≤ 1,0 dB foi 0 na bateria. "
      "Medir, no G3 e nas sessões reais, quantas repetições o detector pede em condições normais; se forem frequentes, "
      "revisar o detector em incremento posterior.", "",
      "### Falsos negativos (mudança real; N = 300 por linha)", "",
      "| cenário | σ | indicativas | confirmadas (regra atual) | confirmadas com faixa compatível (E4) |", "| --- | --- | --- | --- | --- |"]
for x in out["fn"]:
    L.append(f"| {x['cenario']} | {x['sigma']:.1f} | {x['indicativas']}/{x['N']} | {x['confirmadas']}/{x['N']} | "
             f"{x['confirmadas_com_faixa']}/{x['N']} |")
L += ["", "**Leitura:** a exigência de repetição não reduziu a detecção nos cenários de ganho (±1,5 e ±3 dB) nem no N3; a perda "
      "aparece no filtro estreito com ruído alto (PEQ −3 dB Q 4 em 6 kHz, σ = 1,5: 293/300 confirmadas). A faixa compatível "
      "não custou detecção em nenhum cenário medido.", "",
      "## Reconciliação com `test_detector_validacao_200_sementes`", "",
      "Esse teste codifica o critério **original** do SC-208(b) (zero alarme em 'só polaridade' a σ = 1,5 dB em 200 sementes) e está marcado "
      "`xfail` estrito: ele **falha de propósito**, o que coincide com este relatório e não o contradiz. Não há divergência de algoritmo "
      "nem de dados: o detector é o mesmo. Diferem só (i) as sementes do \"depois\" (teste: semente + 10 000; validação: + 50 000), o que dá "
      "16/200 contra 20/200 — variação amostral da mesma taxa; com 1 000 sementes ambos dão 87/1 000; (ii) o critério de contagem (o teste para no "
      "primeiro alarme e também exige N3 detectado; a validação conta todos); (iii) a quantização não altera o resultado. "
      "A asserção e os limiares não foram alterados; só o texto do motivo do `xfail`, que estava desatualizado.", "",
      "## Limitações estatísticas", "",
      "- Domínio simulado; ruído gaussiano independente entre pontos (a mesma hipótese do estimador).",
      "- N = 1 000 (falsos positivos) e 300 (falsos negativos) sementes por linha: taxas abaixo de ≈ 0,3 % não são resolvidas; "
      "\"0 em 1 000\" não é \"zero\".",
      "- Poucas famílias de cenário; não há ruído correlacionado nem reposicionamento nesta bateria.",
      "- A bateria varia σ de modo uniforme entre antes e depois; diferenças de σ entre aquisições não foram varridas.", ""]
SAIDA.write_text("\n".join(L), encoding="utf-8")
print("relatório:", SAIDA)
