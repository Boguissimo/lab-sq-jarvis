"""Avaliação da rodada 2 (`preregistro-previsao-fisica-r2.json`). Só aqui os rótulos entram.
Uso: python avaliar_previsao2.py <previsoes.json> <rotulos.json> <saida.json>"""
import hashlib, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from avaliar_previsao import wilson

TAUS = ("atraso_0.05_ms", "atraso_0.10_ms", "atraso_0.25_ms", "atraso_1.00_ms")


def classe(f):
    return "controle" if f == "controle" else ("polaridade" if f == "polaridade" else ("fora_do_espaco" if f.startswith("ganho") else f))


def veredito(d, r):
    """(resultado, tipo): resultado ∈ certa|errada|nao_concluiu|inadmissivel; tipo do erro: omissao|identificacao|falso_alarme|falsa_confianca."""
    dec, falha = d["decisao"], r["falha"]
    if dec == "inadmissivel":
        return "inadmissivel", None
    if falha.startswith("ganho"):
        return ("nao_concluiu", None) if dec == "nao_conclui" else ("errada", "falsa_confianca")
    if dec == "nao_conclui":
        return "nao_concluiu", None
    if falha == "controle":
        return ("certa", None) if dec == "normal" else ("errada", "falso_alarme")
    if dec == "normal":
        return "errada", "omissao"
    if falha == "polaridade":
        return ("certa", None) if dec == "inversao" else ("errada", "identificacao")
    tau = r["tau_ms"]
    ok = dec == "atraso" and abs(d["tau_ms"] - tau) <= max(0.05, 0.2 * tau)
    return ("certa", None) if ok else ("errada", "identificacao")


def main():
    prev_p, rot_p, saida = map(Path, sys.argv[1:4])
    prev, rot = json.loads(prev_p.read_text()), json.loads(rot_p.read_text())
    res = {"previsoes_sha256": hashlib.sha256(prev_p.read_bytes()).hexdigest(), "casos": len(prev), "matriz": {}, "aceitacao_sala_N1s": {}, "piso_por_construcao": {}, "admissibilidade": {}}
    # matriz: (conjunto, nivel, margem) × classe
    for margem in ("M_A", "M_B", "M_C"):
        for i, r in rot.items():
            if r["nivel"] == "adm_neg" or margem not in prev[i]["decisoes"]:
                continue
            res_v, tipo = veredito(prev[i]["decisoes"][margem], r)
            for cl in (classe(r["falha"]), "TODAS_atraso" if r["falha"].startswith("atraso") else None, "TODAS"):
                if cl is None:
                    continue
                chave = f"{r['conjunto']}|{r['nivel']}|{margem}|{cl}"
                c = res["matriz"].setdefault(chave, {"n": 0, "certa": 0, "errada": 0, "nao_concluiu": 0, "inadmissivel": 0, "omissao": 0, "identificacao": 0, "falso_alarme": 0, "falsa_confianca": 0})
                c["n"] += 1; c[res_v] += 1
                if tipo:
                    c[tipo] += 1
    for c in res["matriz"].values():
        concl = c["certa"] + c["errada"]
        c["cobertura_de_conclusoes"] = round(concl / c["n"], 3) if c["n"] else None
        # 'certa' em ganho conta só abstenção; aqui certa = decisão correta
        c["wilson95_certa_sobre_n"] = wilson(c["certa"], c["n"])
    # critério fixado: sala N1s por margem (grupo = lado oposto já aplicado dentro do protótipo)
    for margem in ("M_A", "M_B", "M_C"):
        fp = sum(1 for i, r in rot.items() if r["conjunto"] == "sala" and r["nivel"] == "N1s" and r["falha"] == "controle" and prev[i]["decisoes"][margem]["decisao"] in ("inversao", "atraso"))
        pol = sum(1 for i, r in rot.items() if r["conjunto"] == "sala" and r["nivel"] == "N1s" and r["falha"] == "polaridade" and prev[i]["decisoes"][margem]["decisao"] == "inversao")
        fe = sum(1 for i, r in rot.items() if r["conjunto"] == "sala" and r["nivel"] == "N1s" and r["falha"].startswith("ganho") and prev[i]["decisoes"][margem]["decisao"] == "nao_conclui")
        det = {}
        for t in TAUS:
            certos = sum(1 for i, r in rot.items() if r["conjunto"] == "sala" and r["nivel"] == "N1s" and r["falha"] == t and veredito(prev[i]["decisoes"][margem], r)[0] == "certa")
            det[t] = {"certas": certos, "n": 40, "fracao": round(certos / 40, 3)}
        ok = fp <= 2 and pol >= 36 and fe >= 36
        menor = next((t for t in TAUS if det[t]["fracao"] >= 0.9), None)
        res["aceitacao_sala_N1s"][margem] = {"falsos_alarmes_em_controles": f"{fp}/40", "polaridade_correta": f"{pol}/40", "fora_do_espaco_nao_conclui": f"{fe}/40",
                                              "deteccao_de_atraso": det, "aceitavel_pelo_criterio_fixado": ok, "menor_atraso_com_90pct": menor if ok else None}
    # piso por construção: custo da hipótese verdadeira
    d = defaultdict(list)
    for i, r in rot.items():
        if r["falha"].startswith("ganho") or r["nivel"] == "adm_neg":
            continue
        c = prev[i]["custos"]
        d[f"{r['conjunto']}|{r['nivel']}|{r['grupo'] if r['conjunto']=='sala' else r['par']}"].append(c["normal"] if r["falha"] == "controle" else (c["inversao"] if r["falha"] == "polaridade" else c["atraso"]))
    for k, v in sorted(d.items()):
        res["piso_por_construcao"][k] = {"n": len(v), "mediana": round(float(np.median(v)), 3), "P90": round(float(np.percentile(v, 90)), 3), "max": round(float(max(v)), 3)}
    # admissibilidade
    neg = [i for i, r in rot.items() if r["nivel"] == "adm_neg"]
    res["admissibilidade"] = {"casos_fora_da_banda": len(neg), "inadmissivel": sum(1 for i in neg if prev[i]["decisoes"]["M_A"]["decisao"] == "inadmissivel")}
    for margem in ("M_A", "M_B", "M_C"):
        res["admissibilidade"]["se_ignorasse_o_portao_" + margem] = {"controles_acusados_de_falha": sum(1 for i in neg if prev[i]["sem_portao"][margem]["decisao"] in ("inversao", "atraso")), "de": len(neg),
                                                                     "nao_conclui": sum(1 for i in neg if prev[i]["sem_portao"][margem]["decisao"] == "nao_conclui")}
    saida.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("aceitacao_sala_N1s", "piso_por_construcao", "admissibilidade")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
