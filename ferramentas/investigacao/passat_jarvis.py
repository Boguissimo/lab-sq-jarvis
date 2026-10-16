"""D-real e H: Jarvis (Servico, sem interface) sobre vias reais do VW Passat B8 com SOMA CALCULADA e falhas injetadas na via B.

Parâmetros e regras de pontuação: `preregistro-passat.json`. Desempate fixado ANTES de ver os resultados: se há hipóteses, vale a
hipótese 1 (certa = acerto; outra = erro, mesmo com sugestão solicitar_dados); sem hipóteses, sugestão solicitar_dados ou
nao_da_para_concluir = abstenção; nada_a_alterar = erro. O controle não é pontuado como falso positivo.
Uso: python passat_jarvis.py <pasta-clone-ayukhno> <pasta-trabalho> <saida.json>
"""
import json, shutil, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, sha256, RAIZ
from passat_comum import *
import braco_a as ba
import bracos_bc as bc
from jarvis import rew_texto

PRE = json.loads((Path(__file__).resolve().parent / "preregistro-passat.json").read_text(encoding="utf-8"))
PARES = PRE["D_real_e_H"]["pares"]
INJ = {"controle": None, "polaridade": ("pol", 0), "atraso_0.25ms": ("atr", 24), "atraso_1.0ms": ("atr", 96)}
SUAV = {"W30": "janela temporal de 30 ms (harness)", "Wfull": "nenhuma"}
META = PRE["D_real_e_H"]["metadados_do_caso"]


def injetar(h, inj):
    if inj is None:
        return h
    if inj[0] == "pol":
        return -h
    n = inj[1]
    out = np.zeros_like(h)
    out[n:] = h[:-n]
    return out


def montar(fonte, a, b, jan, ppo, inj_nome, destino):
    destino.mkdir(parents=True)
    ha, ia, da = ler_ir(fonte, a)
    hb, ib, db = ler_ir(fonte, b)
    ini = min(ia, ib)  # janela pelo MENOR início do par; a mesma nas duas vias
    hb = injetar(hb, INJ[inj_nome])
    Xa, f = espectro(ha, jan, ini)
    Xb, _ = espectro(hb, jan, ini)
    g = grade_log(ppo)
    A, B = amostrar_bins(Xa, f, g), amostrar_bins(Xb, f, g)
    cab = [f"[HARNESS] derivado de ayukhno/autosound-measurements@7725d42 (CC BY 4.0), IR v7 {a}/{b}; janela {jan}; {ppo} ppo; "
           f"bin FFT mais próximo; injeção na via B: {inj_nome}", "[HARNESS] soma = adição complexa calculada (não medida)"]
    meds = []
    for nome, papel, X, desc in (("via_a", "via_a", A, f"{a} sozinho"), ("via_b", "via_b", B, f"{b} sozinho ({inj_nome})"), ("soma", "soma", A + B, f"{a}+{b} (soma calculada)")):
        rew_texto.escrever(destino / f"{nome}.txt", para_resposta(X, g), cab)
        meds.append({"arquivo": f"{nome}.txt", "momento": "antes", "papel": papel, "canal": {"via_a": a, "via_b": b, "soma": f"{a}+{b}"}[papel],
                     "descricao": desc, "referencia_temporal": META["referencia_temporal"], "taxa_amostragem": META["taxa_amostragem"],
                     "posicao_microfone": META["posicao_microfone"], "suavizacao": SUAV[jan], "simulado": False})
    conf = [{"canal": c, "parametro": p, "valor": v} for c in (a, b) for p, v in (("polaridade", "0°"), ("atraso", "0 ms"), ("ganho", "0 dB"))]
    man = {"caso": f"PASSAT-{a}-{b}-{jan}-{ppo}-{inj_nome}", "simulado": False, "tipo_sessao": "investigacao",
           "descricao": "Vias reais; soma calculada; injeção declarada no nome.",
           "configuracao_declarada": {"nome": "dsp-state.json (zerado)", "parametros": conf}, "medicoes": meds}
    (destino / "manifesto.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    return destino


def pontuar(inj_nome, r):
    if inj_nome == "controle":
        pol = any("Polaridade invertida" in h[0] for h in r.get("hipoteses", [])[:1])
        return "sem pontuação" + (" (hipótese 1 = polaridade invertida: contradiz o DSP declarado 'normal')" if pol else "")
    alvo = "Polaridade invertida" if inj_nome == "polaridade" else "Diferença de tempo"
    hip = r.get("hipoteses", [])
    if r["resultado"] != "analisou":
        return "recusa"
    if hip:
        return "acerto" if alvo in hip[0][0] and (inj_nome != "polaridade" or r["sugestao"] == "teste_polaridade") else "erro"
    return "abstenção" if r["sugestao"] in ("solicitar_dados", "nao_da_para_concluir") else "erro"


def main():
    fonte, trab, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    verificar_origem(fonte, RAIZ / "docs/revisoes/investigacao-desempenho/admissao-ayukhno.json")
    if trab.exists():
        shutil.rmtree(trab)
    res = {"preregistro": "preregistro-passat.json", "casos": []}
    for a, b in PARES:
        for jan in ("W30", "Wfull"):
            for ppo in (48, 96):
                for inj in INJ:
                    pasta = montar(fonte, a, b, jan, ppo, inj, trab / f"{a}-{b}-{jan}-{ppo}-{inj}")
                    r = ba.rodar(pasta, trab / f"banco-{a}-{b}-{jan}-{ppo}-{inj}")
                    rs = bc.resumo(r)
                    rs.update({"par": [a, b], "janela": jan, "ppo": ppo, "injecao": inj})
                    rs["pontuacao"] = pontuar(inj, rs)
                    res["casos"].append(rs)
        print(a, b, "ok")
    Path(saida).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
