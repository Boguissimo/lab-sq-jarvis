"""Estima as componentes da margem (rodada 2, `preregistro-previsao-fisica-r2.json`) SEM usar rótulos nem casos
injetados: parte de arquivos brutos. Sala: (a) variabilidade entre aquisições, (c) discrepância do modelo, (d) folga
empírica de controles disjuntos; (b) só descritivo. Carro: (a) e (b) descritivos; (c) e (d) NÃO estimáveis.
Uso: python estimar_margem_previsao.py <clone-joeglondon> <clone-ayukhno> <saida.json>"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, sha256, RAIZ
from gerar_casos_previsao import para_grade
from gerar_casos_previsao2 import carregar_sala, OP_CARRO, inter
from diagnostico_previsao2 import mascara, custo, custos_das_hipoteses
import passat_comum as pc

PRE = Path(__file__).resolve().parent / "preregistro-previsao-fisica-r2.json"
BANDA = (30.0, 150.0)


def c_xy(f, x, y, banda):
    m = mascara(f, (x, y), banda)
    return custo(x, y, m)


def main():
    sala, carro, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    verificar_origem(sala)
    verificar_origem(carro, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    f0, spl = carregar_sala(sala)
    out = {"preregistro_sha256": sha256(PRE), "sala": {}, "carro": {}, "margens": {"M_B": {}, "M_C": {}}}
    for lado in ("L", "R"):
        P, M, L_, S_ = {}, {}, {}, {}
        for k in range(1, 6):
            g, P[k] = para_grade(f0, spl[(lado, k)] + spl[("Sub Only", k)])
            _, M[k] = para_grade(f0, spl[(f"{lado} + Sub", k)])
            _, L_[k] = para_grade(f0, spl[(lado, k)])
            _, S_[k] = para_grade(f0, spl[("Sub Only", k)])
        rep = [c_xy(g, P[a], P[b], BANDA) for a in range(1, 6) for b in range(1, 6) if a != b]
        mod = [c_xy(g, P[k], M[k], BANDA) for k in range(1, 6)]
        gaps, taus = [], []
        for ko in range(1, 6):
            for kp in range(1, 6):
                if ko == kp:
                    continue
                c = custos_das_hipoteses(g, L_[kp], S_[kp], M[ko], BANDA)
                gaps.append(c["normal"] - min(c["inversao"], c["atraso"]))
                taus.append(c["tau_ms"])
        c_rep, c_mod = float(np.percentile(rep, 95)), float(np.percentile(mod, 95))
        m_b, m_c = float(np.percentile(gaps, 95)), float(np.sqrt(c_rep ** 2 + c_mod ** 2))
        out["sala"][lado] = {"n_pares_rep": len(rep), "c_rep_P95": round(c_rep, 4), "c_rep_mediana": round(float(np.median(rep)), 4),
                             "c_mod_P95": round(c_mod, 4), "c_mod_mediana": round(float(np.median(mod)), 4),
                             "folga_controle_P95": round(m_b, 4), "folga_controle_max": round(float(np.max(gaps)), 4), "n_controles": len(gaps),
                             "tau_melhor_nos_controles_ms": {"mediana": round(float(np.median(taus)), 3), "min": round(float(np.min(taus)), 3), "max": round(float(np.max(taus)), 3)},
                             "c_tim": "NAO_ESTIMAVEL_ABSOLUTO (sem id/loopback); só a dispersão relativa de τ* acima"}
        out["margens"]["M_B"][lado] = round(m_b, 4)
        out["margens"]["M_C"][lado] = round(m_c, 4)
    # ---- carro: componentes descritivas; nenhuma margem emitida
    gg = pc.grade_log(48)
    idx = np.clip(np.round(gg / (pc.FS / pc.N)).astype(int), 1, pc.N // 2)
    fb = idx * pc.FS / pc.N
    cache = {}

    def X(n):
        if n not in cache:
            h, ini, _ = pc.ler_ir(carro, n)
            Xf, ff = pc.espectro(h, "W30", ini)
            cache[n] = pc.amostrar_bins(Xf, ff, gg)
        return cache[n]
    deriva = {"m_L-ctl1": 0.0, "m_L": -0.291, "m_L-ctl3": -0.636}
    pares = {"C1 (w_L + m_L, 200–500)": ("w_L", "m_L", ["m_L", "m_L-ctl1", "m_L-ctl3"], inter(OP_CARRO["w"], OP_CARRO["m"])),
             "C2 (tw_L + m_L, 2000–10000)": ("tw_L", "m_L", ["m_L", "m_L-ctl1", "m_L-ctl3"], inter(OP_CARRO["tw"], OP_CARRO["m"])),
             "C3 (m_R + w_R, 200–500)": ("m_R", "w_R", ["w_R", "w_R-retake"], inter(OP_CARRO["w"], OP_CARRO["m"]))}
    for nome, (a, b, caps, banda) in pares.items():
        rep = [c_xy(gg, X(a) + X(p), X(a) + X(q), banda) for p in caps for q in caps if p != q]
        r = {"banda_hz": list(banda), "n_pares_rep": len(rep), "c_rep_max": round(float(max(rep)), 4), "c_rep_mediana": round(float(np.median(rep)), 4),
             "c_mod": "NAO_ESTIMAVEL (não há soma medida no conjunto)", "folga_efetiva": "NAO_ESTIMAVEL (n ≤ 6 e sem c_mod)"}
        if b == "m_L":   # efeito calculado da deriva medida pelo autor (amostras @96 kHz)
            efs = []
            for p in caps:
                for q in caps:
                    if p != q:
                        dt = (deriva[q] - deriva[p]) / pc.FS
                        efs.append(c_xy(gg, X(a) + X(b), X(a) + X(b) * np.exp(-2j * np.pi * fb * dt), banda))
            r["c_tim_deriva_conhecida_max"] = round(float(max(efs)), 4)
        out["carro"][nome] = r
    out["nota"] = "Nenhuma margem é emitida para o carro: componentes (c) e (d) não estimáveis."
    saida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
