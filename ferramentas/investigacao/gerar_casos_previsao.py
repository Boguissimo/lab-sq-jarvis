"""Gera os casos do experimento `preregistro-previsao-fisica.json`. Separa ARRAYS (casos/) de RÓTULOS (rotulos/).
Uso: python gerar_casos_previsao.py <clone-joeglondon> <clone-ayukhno> <dir-casos> <dir-rotulos>
Os arquivos de caso são derivados de dados de terceiros e NÃO vão para o repositório.
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl, complexo, sha256, RAIZ
from bracos_bc import reamostrar
import passat_comum as pc

PRE = Path(__file__).resolve().parent / "preregistro-previsao-fisica.json"
SEMENTE = 20261016
FALHAS = [("controle", None), ("polaridade", None), ("atraso_0.05_ms", 0.05), ("atraso_0.10_ms", 0.10),
          ("atraso_0.25_ms", 0.25), ("atraso_1.00_ms", 1.00), ("ganho_+3dB_fora_do_espaco", 3.0)]


def aplicar(h, f_hz, falha, val):
    if falha == "controle":
        return h
    if falha == "polaridade":
        return -h
    if falha.startswith("atraso"):
        return h * np.exp(-2j * np.pi * f_hz * val / 1000.0)
    return h * 10 ** (val / 20.0)


def para_grade(f, h, ppo=48):
    n, ph = 20 * np.log10(np.abs(h)), np.rad2deg(np.angle(h))
    g, nn, pp = reamostrar(f, n, ph, ppo, "pontual")
    return g, complexo(nn, pp)


def main():
    sala, carro, dcasos, drot = map(Path, sys.argv[1:5])
    verificar_origem(sala)
    verificar_origem(carro, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    dcasos.mkdir(parents=True, exist_ok=True); drot.mkdir(parents=True, exist_ok=True)
    lista = []  # (arrays, rotulo)
    # ---- sala
    spl = {}
    for via in ("L", "R", "Sub Only", "L + Sub", "R + Sub"):
        for k in range(1, 6):
            f, n, p, _ = ler_spl(sala / "SPL" / f"{via} {k}.txt")
            spl[(via, k)] = complexo(n, p)
    for nivel in ("N1", "N0"):
        for lado in ("L", "R"):
            for k in range(1, 6):
                kp = (k % 5) + 1 if nivel == "N1" else k
                hs_k, hs_prev = spl[("Sub Only", k)], spl[("Sub Only", kp)]
                for falha, val in FALHAS:
                    hS = spl[(f"{lado} + Sub", k)] - hs_k + aplicar(hs_k, f, falha, val)
                    g, hSg = para_grade(f, hS)
                    _, hAg = para_grade(f, spl[(lado, k)])
                    _, hBg = para_grade(f, hs_prev)
                    lista.append(({"f": g, "hA": hAg, "hB": hBg, "hS": hSg, "banda": np.array([30.0, 150.0])},
                                  {"conjunto": "sala", "nivel": nivel + "-sala", "par": f"{lado}+Sub k={k}", "falha": falha, "tau_ms": val if falha.startswith("atraso") else None}))
    # ---- carro
    g = pc.grade_log(48)
    idx = np.clip(np.round(g / (pc.FS / pc.N)).astype(int), 1, pc.N // 2)
    fb = idx * pc.FS / pc.N  # frequência real do bin usada na fase da falha
    cache = {}

    def X(nome):
        if nome not in cache:
            h, ini, _ = pc.ler_ir(carro, nome)
            Xf, ff = pc.espectro(h, "W30", ini)
            cache[nome] = pc.amostrar_bins(Xf, ff, g)
        return cache[nome]
    P = json.loads(PRE.read_text(encoding="utf-8"))["casos"]["carro"]["pares"]
    cfg = [("P1", "w_L", "m_L", "m_L-ctl1", "B", (200, 500), "N1"), ("P1", "w_L", "m_L", "m_L-ctl3", "B", (200, 500), "N1"),
           ("P2", "m_L", "tw_L", "m_L-ctl1", "A", (2000, 10000), "N1"), ("P2", "m_L", "tw_L", "m_L-ctl3", "A", (2000, 10000), "N1"),
           ("P3", "w_R", "m_R", "w_R-retake", "A", (200, 500), "N1"),
           ("P4", "m_R", "tw_R", None, None, (2000, 10000), "N0"), ("P5", "sw", "w_L", None, None, (40, 150), "N0")]
    assert {c["id"] for c in P} == {c[0] for c in cfg}  # pares conforme o pré-registro
    for pid, a, b, alt, onde, banda, nivel in cfg:
        hA_pred, hB_pred = X(a), X(b)
        hA_soma = X(alt) if onde == "A" else hA_pred
        hB_soma = X(alt) if onde == "B" else hB_pred
        for falha, val in FALHAS:
            hS = hA_soma + aplicar(hB_soma, fb, falha, val)
            lista.append(({"f": g, "hA": hA_pred, "hB": hB_pred, "hS": hS, "banda": np.array(banda, float)},
                          {"conjunto": "carro", "nivel": nivel + "-carro", "par": f"{pid} {a}+{b}" + (f" (soma com {alt})" if alt else ""), "falha": falha,
                           "tau_ms": val if falha.startswith("atraso") else None}))
    rng = np.random.default_rng(SEMENTE)
    ordem = rng.permutation(len(lista))
    ids = [f"c{int(i):04d}" for i in rng.permutation(len(lista))]
    rot = {}
    for novo_id, o in zip(ids, ordem):
        arr, r = lista[o]
        np.savez(dcasos / f"{novo_id}.npz", **arr)
        rot[novo_id] = r
    (drot / "rotulos.json").write_text(json.dumps(rot, indent=1, ensure_ascii=False), encoding="utf-8")
    man = {"preregistro_sha256": sha256(PRE), "casos": len(lista),
           "sha256_dos_arquivos_de_caso": {p.name: sha256(p) for p in sorted(dcasos.glob("*.npz"))}}
    (drot / "manifesto-casos.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(len(lista), "casos;", sum(1 for r in rot.values() if r["conjunto"] == "sala"), "sala;", sum(1 for r in rot.values() if r["conjunto"] == "carro"), "carro")


if __name__ == "__main__":
    main()
