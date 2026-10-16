"""Rodada 2 (`preregistro-previsao-fisica-r2.json`): gera casos com aquisições DISJUNTAS entre previsão e observação.
Uso: python gerar_casos_previsao2.py <clone-joeglondon> <clone-ayukhno> <dir-casos> <dir-rotulos>
Arquivos de caso são derivados de dados de terceiros e NÃO vão para o repositório."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl, complexo, sha256, RAIZ
from gerar_casos_previsao import aplicar, para_grade, FALHAS
import passat_comum as pc

PRE = Path(__file__).resolve().parent / "preregistro-previsao-fisica-r2.json"
SEMENTE = 20261017
OP_SALA = {"lado": (20.0, 20000.0), "Sub": (30.0, 150.0)}
OP_CARRO = {"sw": (30.0, 150.0), "w": (40.0, 500.0), "m": (200.0, 10000.0), "tw": (2000.0, 16000.0)}


def inter(a, b):
    return (max(a[0], b[0]), min(a[1], b[1]))


def carregar_sala(sala):
    spl = {}
    for via in ("L", "R", "Sub Only", "L + Sub", "R + Sub"):
        for k in range(1, 6):
            f, n, p, _ = ler_spl(sala / "SPL" / f"{via} {k}.txt")
            spl[(via, k)] = complexo(n, p)
    return f, spl


def main():
    sala, carro, dcasos, drot = map(Path, sys.argv[1:5])
    verificar_origem(sala)
    verificar_origem(carro, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    dcasos.mkdir(parents=True, exist_ok=True); drot.mkdir(parents=True, exist_ok=True)
    lista = []

    def add(arr, rot):
        lista.append((arr, rot))

    # ---- sala
    f, spl = carregar_sala(sala)
    banda_par = inter(OP_SALA["lado"], OP_SALA["Sub"])
    for lado in ("L", "R"):
        for ko in range(1, 6):
            for kp in range(1, 6):
                nivel = "N0" if ko == kp else "N1s"
                for falha, val in FALHAS:
                    hs_o = spl[("Sub Only", ko)]
                    hS = spl[(f"{lado} + Sub", ko)] - hs_o + aplicar(hs_o, f, falha, val)
                    g, hSg = para_grade(f, hS)
                    _, hAg = para_grade(f, spl[(lado, kp)])
                    _, hBg = para_grade(f, spl[("Sub Only", kp)])
                    base = {"f": g, "hA": hAg, "hB": hBg, "hS": hSg, "banda_decl": np.array(banda_par), "op_A": np.array(OP_SALA["lado"]),
                            "op_B": np.array(OP_SALA["Sub"]), "grupo": np.array("sala-" + lado)}
                    rot = {"conjunto": "sala", "grupo": "sala-" + lado, "nivel": nivel, "par": f"{lado}+Sub", "ko": ko, "kp": kp, "falha": falha,
                           "tau_ms": val if falha.startswith("atraso") else None}
                    add(base, rot)
                    if nivel == "N1s" and falha == "controle":   # controles negativos do portão de admissibilidade
                        for banda in ((200.0, 10000.0), (20.0, 20000.0)):
                            add({**base, "banda_decl": np.array(banda)}, {**rot, "nivel": "adm_neg", "banda_declarada": list(banda)})
    # ---- carro
    g = pc.grade_log(48)
    idx = np.clip(np.round(g / (pc.FS / pc.N)).astype(int), 1, pc.N // 2)
    fb = idx * pc.FS / pc.N
    cache = {}

    def X(nome):
        if nome not in cache:
            h, ini, _ = pc.ler_ir(carro, nome)
            Xf, ff = pc.espectro(h, "W30", ini)
            cache[nome] = pc.amostrar_bins(Xf, ff, g)
        return cache[nome]
    mL = ["m_L", "m_L-ctl1", "m_L-ctl3"]
    cfg = [("C1", "w_L", "w", "m_L", "m", mL), ("C2", "tw_L", "tw", "m_L", "m", mL), ("C3", "m_R", "m", "w_R", "w", ["w_R", "w_R-retake"]),
           ("P4", "m_R", "m", "tw_R", "tw", ["tw_R"]), ("P5", "sw", "sw", "w_L", "w", ["w_L"])]
    for pid, a, ta, b, tb, caps in cfg:
        banda = inter(OP_CARRO[ta], OP_CARRO[tb])
        for ko in caps:
            for kp in caps:
                nivel = "N0" if ko == kp else "N1s"
                if pid in ("P4", "P5") and nivel != "N0":
                    continue
                for falha, val in FALHAS:
                    hS = X(a) + aplicar(X(ko), fb, falha, val)
                    add({"f": g, "hA": X(a), "hB": X(kp), "hS": hS, "banda_decl": np.array(banda), "op_A": np.array(OP_CARRO[ta]),
                         "op_B": np.array(OP_CARRO[tb]), "grupo": np.array("carro")},
                        {"conjunto": "carro", "grupo": "carro", "nivel": nivel, "par": pid, "ko": ko, "kp": kp, "falha": falha,
                         "tau_ms": val if falha.startswith("atraso") else None})
    rng = np.random.default_rng(SEMENTE)
    ordem = rng.permutation(len(lista))
    ids = [f"d{int(i):04d}" for i in rng.permutation(len(lista))]
    rot = {}
    for novo_id, o in zip(ids, ordem):
        arr, r = lista[o]
        np.savez(dcasos / f"{novo_id}.npz", **arr)
        rot[novo_id] = r
    (drot / "rotulos.json").write_text(json.dumps(rot, indent=1, ensure_ascii=False), encoding="utf-8")
    man = {"preregistro_sha256": sha256(PRE), "casos": len(lista), "sha256_dos_arquivos_de_caso": {p.name: sha256(p) for p in sorted(dcasos.glob("*.npz"))}}
    (drot / "manifesto-casos.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    cont = {}
    for r in rot.values():
        cont[(r["conjunto"], r["nivel"])] = cont.get((r["conjunto"], r["nivel"]), 0) + 1
    print(len(lista), "casos", {f"{a}/{b}": n for (a, b), n in sorted(cont.items())})


if __name__ == "__main__":
    main()
