"""Compatibilidade de posição/tempo em ALTA frequência: acima de ~2 kHz o Sub não contribui, então (L|R)+Sub k deve igualar (L|R) k
se a posição do microfone e a referência temporal forem as mesmas (10 kHz: 5° ≈ 0,5 mm de caminho). Teste físico, sem o Jarvis.
Uso: python compat_hf.py <pasta-clone> <saida.json>"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl, complexo

fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
verificar_origem(fonte)
res = []
for lado in ("L", "R"):
    for k in range(1, 6):
        f, nl, pl, _ = ler_spl(fonte / "SPL" / f"{lado} {k}.txt")
        _, ns, ps, _ = ler_spl(fonte / "SPL" / f"Sub Only {k}.txt")
        _, nm, pm, _ = ler_spl(fonte / "SPL" / f"{lado} + Sub {k}.txt")
        out = {"par": f"{lado}-{k}"}
        for lo, hi in ((2000, 4000), (4000, 7000), (7000, 10000)):
            b = (f >= lo) & (f < hi)
            r = complexo(nm[b], pm[b]) / complexo(nl[b], pl[b])
            out[f"{lo}-{hi}"] = {"med_erro_nivel_db": round(float(np.median(np.abs(20 * np.log10(np.abs(r))))), 3),
                                 "med_erro_fase_graus": round(float(np.median(np.abs(np.rad2deg(np.angle(r))))), 2),
                                 "sub_menos_L_db_mediana": round(float(np.median(ns[b] - nl[b])), 1)}
        res.append(out)
Path(saida).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
for o in res:
    print(o["par"], {k: (v["med_erro_nivel_db"], v["med_erro_fase_graus"], v["sub_menos_L_db_mediana"]) for k, v in o.items() if k != "par"})
