"""σ̂ do produto × variabilidade entre repetições (referência empírica independente de ruído), 200 Hz–10 kHz.

Para cada via (L, R, Sub Only, somas) reamostra as 5 repetições com o MESMO método (pontual, ppo dado), calcula σ̂ com
`calculos.irregularidade` (código do produto, chamada direta) e o desvio-padrão entre repetições por ponto da grade.
A variabilidade entre repetições inclui qualquer mudança real de posição/condição: é um limite SUPERIOR do ruído de
medição, não o ruído exato. Uso: python repetibilidade_sigma.py <pasta-clone> <saida.json> [ppo]
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl
from bracos_bc import reamostrar
from jarvis import calculos
from jarvis.rew_texto import RespostaFrequencia

fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
ppo = int(sys.argv[3]) if len(sys.argv) > 3 else 48
verificar_origem(fonte)
res = {}
for nome in ("L", "R", "Sub Only", "L + Sub", "R + Sub"):
    curvas, sig = [], []
    for k in range(1, 6):
        f, n, p, _ = ler_spl(fonte / "SPL" / f"{nome} {k}.txt")
        g, n2, p2 = reamostrar(f, n, p, ppo, "pontual")
        curvas.append(n2)
        s = calculos.irregularidade(RespostaFrequencia(g, n2, p2), "nenhuma")["sigma_db"]
        sig.append(s)
    c = np.array(curvas)
    faixa = (g >= 200) & (g <= 10000)
    dp = np.std(c[:, faixa], axis=0, ddof=1)
    res[nome] = {"sigma_hat_db_por_repeticao": [round(float(s), 2) for s in sig],
                 "desvio_entre_repeticoes_db": {"mediana": round(float(np.median(dp)), 2), "p90": round(float(np.percentile(dp, 90)), 2)}}
res["ppo"] = ppo
Path(saida).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False))
