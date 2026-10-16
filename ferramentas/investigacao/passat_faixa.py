"""POST HOC e exploratório: o que a métrica de fase do produto (`calculos.diferenca_fase`) vê se a análise for restrita a uma
faixa operacional do par? Chamada direta da função do produto com índices restritos; nada é alterado no produto.
Faixas candidatas (escolhidas olhando as faixas úteis dos canais, não ajustadas aos resultados): w+m 150–400 Hz, m+tw 2–4 kHz, sw+w 60–150 Hz.
Uso: python passat_faixa.py <pasta-clone-ayukhno> <saida.json>"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, RAIZ
from passat_comum import *
from passat_jarvis import injetar, INJ
from jarvis import calculos

FAIXAS = {("w_L", "m_L"): (150, 400), ("w_R", "m_R"): (150, 400), ("m_L", "tw_L"): (2000, 4000), ("m_R", "tw_R"): (2000, 4000), ("sw", "w_L"): (60, 150)}


def complexo_de(r):
    return 10 ** (r.nivel_db / 20.0) * np.exp(1j * np.deg2rad(r.fase_graus))


def main():
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    verificar_origem(fonte, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    out = []
    for (a, b), (lo, hi) in FAIXAS.items():
        for jan in ("W30", "Wfull"):
            ha, ia, _ = ler_ir(fonte, a)
            hb0, ib, _ = ler_ir(fonte, b)
            for inj in INJ:
                hb = injetar(hb0, INJ[inj])
                Xa, f = espectro(ha, jan, min(ia, ib)); Xb, _ = espectro(hb, jan, min(ia, ib))
                g = grade_log(48)
                A, B = para_resposta(amostrar_bins(Xa, f, g), g), para_resposta(amostrar_bins(Xb, f, g), g)
                idx = [int(i) for i in np.where((g >= lo) & (g <= hi))[0]]
                d = calculos.diferenca_fase(A, B, idx)
                ca, cb = complexo_de(A), complexo_de(B)
                ganho_inv = float(np.median(20 * np.log10(np.abs(ca[idx] - cb[idx]) / np.abs(ca[idx] + cb[idx]))))
                out.append({"par": [a, b], "faixa_hz": [lo, hi], "janela": jan, "injecao": inj,
                            "calculavel": d["calculavel"], "media_graus": d.get("media_graus"), "dispersao_graus": d.get("dispersao_graus"),
                            "atraso_equivalente_ms": d.get("atraso_equivalente_ms"), "ganho_previsto_da_inversao_db": ganho_inv})
    Path(saida).write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    for o in out:
        if o["janela"] == "W30":
            r = lambda x: None if x is None else round(x, 2)
            print(o["par"], o["faixa_hz"], f'{o["injecao"]:14s} média={r(o["media_graus"])} disp={r(o["dispersao_graus"])} atraso_eq={r(o["atraso_equivalente_ms"])} ganho_inversão={r(o["ganho_previsto_da_inversao_db"])} dB')


if __name__ == "__main__":
    main()
