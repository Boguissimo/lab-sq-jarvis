"""Quanto da concordância previsão × observação é por construção? Para cada nível, o custo da hipótese VERDADEIRA
(rodada 1, arquivos já gravados). Custo ≈ 0 = a observação é algebricamente a previsão; custo > 0 = discrepância real
entre capturas/modelo. Análise post hoc, rotulada; usa rótulos só depois da execução.
Uso: python piso_construcao_previsao.py <previsoes.json> <rotulos.json>"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

prev, rot = json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text())
d = defaultdict(list)
for i, r in rot.items():
    if r["falha"].startswith("ganho"):
        continue
    custos = prev[i]["banda_operacional"]["custos"]
    chave = "normal" if r["falha"] == "controle" else ("inversao" if r["falha"] == "polaridade" else "atraso")
    d[(r["nivel"], r["par"].split(" (")[0] if r["conjunto"] == "carro" else r["par"].split()[0])].append(custos[chave])
print(f"{'nivel':10s} {'par/lado':16s} {'n':>3s} {'custo da hipótese verdadeira: mediana':>40s} {'P90':>7s} {'máx':>7s}")
for (nivel, par), v in sorted(d.items()):
    v = np.array(v)
    print(f"{nivel:10s} {par:16s} {v.size:3d} {np.median(v):40.3f} {np.percentile(v, 90):7.3f} {v.max():7.3f}")
