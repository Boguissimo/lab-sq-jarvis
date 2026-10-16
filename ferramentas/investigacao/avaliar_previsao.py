"""Avaliação do experimento `preregistro-previsao-fisica.json`: cruza previsoes.json com rotulos.json (só aqui os rótulos
entram). Uso: python avaliar_previsao.py <previsoes.json> <rotulos.json> <saida.json>"""
import hashlib, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(float(max(0, c - h)), 3), round(float(min(1, c + h)), 3)]


def veredito(dec, rot):
    """Devolve 'acerto', 'abstencao' ou 'erro' conforme o pré-registro."""
    falha = rot["falha"]
    if falha == "controle":
        return "acerto" if dec["decisao"] == "normal" else ("abstencao" if dec["decisao"] == "nao_conclui" else "erro")
    if falha.startswith("ganho"):
        return "acerto" if dec["decisao"] == "nao_conclui" else "erro"
    if dec["decisao"] == "nao_conclui":
        return "abstencao"
    if falha == "polaridade":
        return "acerto" if dec["decisao"] == "inversao" else "erro"
    tau = rot["tau_ms"]
    ok = dec["decisao"] == "atraso" and abs(dec["tau_ms"] - tau) <= max(0.05, 0.2 * tau)
    return "acerto" if ok else "erro"


def main():
    prev_p, rot_p, saida = map(Path, sys.argv[1:4])
    prev, rot = json.loads(prev_p.read_text()), json.loads(rot_p.read_text())
    res = {"previsoes_sha256": hashlib.sha256(prev_p.read_bytes()).hexdigest(), "casos": len(prev)}
    for variante in ("banda_operacional", "banda_cheia"):
        tab = defaultdict(lambda: defaultdict(lambda: {"acerto": 0, "abstencao": 0, "erro": 0, "n": 0}))
        for i, r in rot.items():
            v = veredito(prev[i][variante], r)
            c = tab[r["nivel"]][r["falha"]]
            c[v] += 1; c["n"] += 1
        res[variante] = {n: {f: {**c, "acerto_wilson95": wilson(c["acerto"], c["n"])} for f, c in d.items()} for n, d in tab.items()}
        # falsa confiança: decisão ≠ nao_conclui em falha fora do espaço, ou atraso/inversão em controle
        fc = [i for i, r in rot.items() if (r["falha"].startswith("ganho") and prev[i][variante]["decisao"] != "nao_conclui")
              or (r["falha"] == "controle" and prev[i][variante]["decisao"] in ("atraso", "inversao"))]
        res[variante + "_falsa_confianca"] = len(fc)
        # detectabilidade de atraso por nível
        det = {}
        for n in tab:
            det[n] = {f: tab[n][f]["acerto"] / tab[n][f]["n"] for f in tab[n] if f.startswith("atraso")}
        res[variante + "_deteccao_atraso_fracao_acerto"] = det
    sens = {}
    for mg in ("0.1", "0.2", "0.5", "1.0"):
        a = n = 0
        for i, r in rot.items():
            if r["falha"].startswith("ganho"):
                continue
            n += 1
            dec = {"decisao": prev[i]["sensibilidade_margem"][mg], "tau_ms": prev[i]["banda_operacional"]["tau_ms"]}
            if mg == "0.2":
                dec = prev[i]["banda_operacional"]
            # atraso: sem τ por margem alternativa, só tipo de decisão
            tipo = {"controle": "normal", "polaridade": "inversao"}.get(r["falha"], "atraso")
            a += dec["decisao"] == tipo
        sens[mg] = {"acertos_de_tipo": a, "n": n}
    res["sensibilidade_margem_tipo_da_decisao_banda_operacional"] = sens
    saida.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
