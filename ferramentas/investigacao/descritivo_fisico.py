"""Descritivo físico POST HOC (calculado depois de ver a saída do Jarvis; não é cego e não é referência independente).

Uso: python ferramentas/investigacao/descritivo_fisico.py <pasta-clone> <saida.json>
Para cada par: onde (30–150 Hz) a soma medida fica mais abaixo da soma de potências das vias, quanto, e a
diferença de fase L–Sub nessa frequência e na faixa. Só descreve os dados; não diz qual ajuste é melhor.
"""
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
        faixa = (f >= 30) & (f <= 150)
        pot = 10 * np.log10(10 ** (nl / 10) + 10 ** (ns / 10))
        rel = nm - pot
        idx = np.where(faixa)[0]
        i = idx[np.argmin(rel[idx])]
        dfase = (pl - ps + 180) % 360 - 180
        b = (f >= 60) & (f <= 120)
        z = np.exp(1j * np.deg2rad(dfase[b]))
        cruz = idx[np.argmin(np.abs(nl[idx] - ns[idx]))]
        res.append({"par": f"{lado}-{k}", "freq_minimo_relativo_hz": float(f[i]), "min_relativo_db": float(rel[i]),
                    "dif_fase_nesse_ponto_graus": float(dfase[i]),
                    "dif_fase_circular_media_60_120hz": float(np.rad2deg(np.angle(z.mean()))),
                    "dispersao_fase_60_120hz": float(np.rad2deg(np.sqrt(-2 * np.log(max(np.abs(z.mean()), 1e-9))))),
                    "freq_niveis_iguais_30_150hz": float(f[cruz])})
Path(saida).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
for r in res:
    print(r["par"], f"mín. rel. {r['min_relativo_db']:.1f} dB @ {r['freq_minimo_relativo_hz']:.1f} Hz | Δfase no ponto {r['dif_fase_nesse_ponto_graus']:.0f}° | "
          f"Δfase 60–120 Hz média {r['dif_fase_circular_media_60_120hz']:.0f}° disp {r['dispersao_fase_60_120hz']:.0f}° | níveis iguais @ {r['freq_niveis_iguais_30_150hz']:.1f} Hz")
