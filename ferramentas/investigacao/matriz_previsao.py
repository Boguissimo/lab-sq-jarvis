"""Matriz de resultados do experimento de previsão física (rodada 1): casos por classe, acertos, erros, abstenções e
COBERTURA das conclusões. Só lê arquivos já gravados (previsoes, rótulos); não recalcula nada.
Uso: python matriz_previsao.py <previsoes.json> <rotulos.json> [variante]"""
import json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from avaliar_previsao import veredito, wilson

prev, rot = json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text())
variante = sys.argv[3] if len(sys.argv) > 3 else "banda_operacional"
CLASSE = lambda f: "controle" if f == "controle" else ("polaridade" if f == "polaridade" else ("fora_do_espaco(ganho)" if f.startswith("ganho") else "atraso"))
linhas = defaultdict(lambda: {"n": 0, "concluiu": 0, "concl_certa": 0, "concl_errada": 0, "nao_concluiu": 0, "nao_concluiu_correto": 0})
for i, r in rot.items():
    d = prev[i][variante]
    v = veredito(d, r)
    concluiu = d["decisao"] != "nao_conclui"
    for chave in ((r["nivel"], CLASSE(r["falha"])), ("TOTAL", CLASSE(r["falha"])), (r["nivel"], "TODAS"), ("TOTAL", "TODAS")):
        c = linhas[chave]; c["n"] += 1
        if concluiu:
            c["concluiu"] += 1
            c["concl_certa" if v == "acerto" else "concl_errada"] += 1
        else:
            c["nao_concluiu"] += 1
            c["nao_concluiu_correto"] += v == "acerto"   # só a classe fora do espaço: abster-se é a resposta certa
print(f"{'nivel':10s} {'classe':22s} {'n':>4s} {'concluiu':>8s} {'certas':>6s} {'erradas':>7s} {'nao_concl':>9s} {'(corretas)':>10s} {'cobertura':>9s} {'certas/concl.':>13s}")
saida = []
for (nivel, cl), c in sorted(linhas.items(), key=lambda kv: (kv[0][0] == "TOTAL", kv[0])):
    cob = c["concluiu"] / c["n"]
    prec = c["concl_certa"] / c["concluiu"] if c["concluiu"] else None
    print(f"{nivel:10s} {cl:22s} {c['n']:4d} {c['concluiu']:8d} {c['concl_certa']:6d} {c['concl_errada']:7d} {c['nao_concluiu']:9d} {c['nao_concluiu_correto']:10d} {cob:9.0%} {('%.0f%%' % (100*prec)) if prec is not None else '—':>13s}")
    saida.append({"nivel": nivel, "classe": cl, **c, "cobertura": round(cob, 3), "certas_entre_conclusoes": None if prec is None else round(prec, 3),
                  "wilson95_certas_entre_conclusoes": wilson(c["concl_certa"], c["concluiu"])})
Path(sys.argv[2]).with_name(f"previsao-fisica-matriz-{variante}.json").write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
