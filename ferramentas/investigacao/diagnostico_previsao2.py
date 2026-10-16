"""Protótipo da rodada 2 (`preregistro-previsao-fisica-r2.json`): previsão física com PORTÃO de admissibilidade por banda
e margem de decisão externa. Lê SOMENTE arrays de caso (f, hA, hB, hS, banda declarada, bandas operacionais das vias,
grupo) e `margens.json`. Não importa nem lê rótulos. Não é o Jarvis.
Uso: python diagnostico_previsao2.py <dir-casos> <margens.json> <saida.json>"""
import json, sys
from pathlib import Path
import numpy as np

C_ADM = 1.0
TAUS = np.round(np.arange(-3.0, 3.0001, 0.01), 2)
TAUS = TAUS[np.abs(TAUS) > 1e-9]


def mascara(f, curvas, banda):
    lo, hi = banda
    faixa = (f >= lo) & (f <= hi)
    m = faixa.copy()
    for h in curvas:
        n = 20 * np.log10(np.maximum(np.abs(h), 1e-30))
        if faixa.any():
            m &= n >= n[faixa].max() - 30.0
    return m


def custo(pred, hS, m):
    el = np.abs(20 * np.log10(np.abs(pred[m]) / np.abs(hS[m])))
    ef = np.abs((np.rad2deg(np.angle(pred[m] / hS[m])) + 180) % 360 - 180)
    return float(np.median(el) + np.median(ef) / 10.0)


def custos_das_hipoteses(f, hA, hB, hS, banda):
    m = mascara(f, (hA, hB, hS), banda)
    c0 = custo(hA + hB, hS, m)
    ci = custo(hA - hB, hS, m)
    cs = [custo(hA + hB * np.exp(-2j * np.pi * f * t / 1000.0), hS, m) for t in TAUS]
    j = int(np.argmin(cs))
    return {"normal": c0, "inversao": ci, "atraso": float(cs[j]), "tau_ms": float(TAUS[j]), "pontos": int(m.sum())}


def portao(banda_decl, op_A, op_B, pontos):
    inter = (max(op_A[0], op_B[0]), min(op_A[1], op_B[1]))
    if not np.allclose(banda_decl, inter):
        return "banda declarada diferente da interseção das bandas operacionais das vias"
    if inter[1] <= inter[0] or np.log2(inter[1] / inter[0]) < 1.0:
        return "banda menor que 1 oitava"
    if pontos < 20:
        return "menos de 20 pontos válidos na máscara"
    return None


def decidir(c, margem):
    if min(c["normal"], c["inversao"], c["atraso"]) > C_ADM:
        return {"decisao": "nao_conclui", "tau_ms": None}
    if c["normal"] - min(c["inversao"], c["atraso"]) < margem:
        return {"decisao": "normal", "tau_ms": None}
    if c["inversao"] <= c["atraso"]:
        return {"decisao": "inversao", "tau_ms": None}
    return {"decisao": "atraso", "tau_ms": c["tau_ms"]}


def margens_do_grupo(grupo, margens):
    """Calibração cruzada: sala-L usa margens estimadas em R e vice-versa; carro só tem a constante de referência."""
    if grupo == "sala-L":
        return {"M_A": 0.2, "M_B": margens["M_B"]["R"], "M_C": margens["M_C"]["R"]}
    if grupo == "sala-R":
        return {"M_A": 0.2, "M_B": margens["M_B"]["L"], "M_C": margens["M_C"]["L"]}
    return {"M_A": 0.2}


def main():
    dcasos, margens_p, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    margens = json.loads(margens_p.read_text(encoding="utf-8"))["margens"]
    out = {}
    for p in sorted(dcasos.glob("*.npz")):
        d = np.load(p)
        f, hA, hB, hS = d["f"], d["hA"], d["hB"], d["hS"]
        banda, opA, opB, grupo = tuple(d["banda_decl"]), tuple(d["op_A"]), tuple(d["op_B"]), str(d["grupo"])
        c = custos_das_hipoteses(f, hA, hB, hS, banda)
        motivo = portao(banda, opA, opB, c["pontos"])
        r = {"grupo": grupo, "custos": {k: v for k, v in c.items()}, "portao": motivo}
        if motivo:
            r["decisoes"] = {k: {"decisao": "inadmissivel", "tau_ms": None} for k in margens_do_grupo(grupo, margens)}
            r["sem_portao"] = {k: decidir(c, m) for k, m in margens_do_grupo(grupo, margens).items()}   # só para quantificar o risco de ignorar o portão
        else:
            r["decisoes"] = {k: decidir(c, m) for k, m in margens_do_grupo(grupo, margens).items()}
        out[p.stem] = r
    saida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(out), "casos diagnosticados")


if __name__ == "__main__":
    main()
