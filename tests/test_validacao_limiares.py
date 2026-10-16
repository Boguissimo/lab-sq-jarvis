"""Validação dos limiares provisórios por varredura (SC-208; ADR-211; JV-T221).

Alcance (E3): **só o domínio simulado** — não é validação acústica para o carro. Os limiares não são
ajustados para os casos passarem; falsos positivos e negativos ficam registrados em
``08-qa/validacao-limiares.md`` (gerado por este teste). Mudar um limiar exige `JV-D` (P8).
"""

from pathlib import Path

import numpy as np

from jarvis import calculos, limiares
from jarvis.referencia import modelo

RELATORIO = (Path(__file__).resolve().parents[1] / ".arkan" / "features" / "lab-sq-jarvis"
             / "003-000-jv-v02-honestidade-e-seguranca" / "08-qa" / "validacao-limiares.md")
F = modelo.grade_log()
TW = {"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}]}
SEMENTES = 200
_secoes: dict[str, list[str]] = {}


def _registrar(secao: str, linhas: list[str]) -> None:
    _secoes[secao] = linhas
    corpo = ["# Validação dos limiares provisórios — JV-V02 (SC-208)", "",
             "> **Domínio simulado apenas** (E3): estes números saem do gerador e de oráculos analíticos; "
             "não validam nada no carro. Limiares não foram ajustados (P8). Gerado por "
             "`tests/test_validacao_limiares.py`.", ""]
    for nome in sorted(_secoes):
        corpo += [f"## {nome}", "", *_secoes[nome], ""]
    RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    RELATORIO.write_text("\n".join(corpo), encoding="utf-8")


def _sigma(h, sigma, semente, suav="nenhuma", correlacao=0):
    r = modelo.adquirir(h, F, {"ruido_sigma_db": sigma}, semente=semente if sigma else None, quantizar=True)
    if correlacao:
        k = np.ones(correlacao) / correlacao
        ruido = r.nivel_db - modelo.adquirir(h, F, quantizar=True).nivel_db
        ruido = np.convolve(ruido, k, mode="same") * np.sqrt(correlacao)
        r = type(r)(r.freq_hz, modelo.adquirir(h, F, quantizar=True).nivel_db + ruido, r.fase_graus)
    return calculos.irregularidade(r, suav)


def test_a_sigma():
    """(a) σ̂: sem ruído, ruído conhecido, vizinhança dos limites, ruído correlacionado e suavização."""
    cenarios = {"via plana LR4": modelo.resposta_via(TW, F),
                "reflexão g=0,9": modelo.resposta_via({**TW, "reflexoes": [{"g": 0.9, "tau_ms": 0.4}]}, F),
                "reflexões múltiplas": modelo.resposta_via({**TW, "reflexoes": [{"g": 0.6, "tau_ms": 0.3},
                                                                                   {"g": 0.5, "tau_ms": 0.9}]}, F),
                "cancelamento": modelo.resposta_via(TW, F) + modelo.resposta_via(
                    {"filtros": [{"tipo": "lr4_pb", "fc_hz": 3000.0}], "polaridade_fiacao": -1}, F)}
    linhas = ["| cenário | σ injetado | σ̂ médio | erro máx. | fora de 15 % σ + 0,05 | classificações (aprov/aviso/reprov) |",
              "| --- | --- | --- | --- | --- | --- |"]
    total_fora = 0
    for nome, h in cenarios.items():
        assert _sigma(h, 0.0, 0)["sigma_db"] <= 0.05, nome
        for sigma in (0.3, 0.45, 0.55, 1.0, 1.4, 1.6, 2.0):
            res = [_sigma(h, sigma, s) for s in range(50)]
            est = np.array([r["sigma_db"] for r in res])
            cls = [r["classificacao"] for r in res]
            fora = int(np.sum(np.abs(est - sigma) > 0.15 * sigma + 0.05))
            total_fora += fora
            assert abs(est.mean() - sigma) <= 0.15 * sigma + 0.05, (nome, sigma)  # o estimador não é viesado
            linhas.append(f"| {nome} | {sigma:.2f} | {est.mean():.3f} | {np.max(np.abs(est - sigma)):.3f} | "
                          f"{fora}/50 | {cls.count('aprovada')}/{cls.count('aviso')}/{cls.count('reprovada')} |")
    h = cenarios["via plana LR4"]
    corr = np.mean([_sigma(h, 1.0, s, correlacao=8)["sigma_db"] for s in range(50)])
    suav = _sigma(h, 1.0, 1, suav="1/6 oitava")
    assert suav["classificacao"] == "nao_estimavel"
    linhas += ["", f"- **Critério por realização** (|σ̂ − σ| ≤ 15 % de σ + 0,05 dB): {total_fora} de "
                   f"{len(cenarios) * 7 * 50} realizações fora. A média fica dentro em todos os cenários; a "
                   "dispersão de uma realização isolada pode passar do critério com σ alto. Registrado para decisão "
                   "(o SC-208 não diz se o critério é por realização ou típico).",
               f"- Fora do domínio: ruído correlacionado (janela de 8 pontos, σ = 1,0 dB) dá σ̂ médio "
                   f"**{corr:.3f} dB** — o estimador subestima ruído correlacionado (limite declarado E1).",
               "- Suavização declarada: `nao_estimavel`, nunca aprovada."]
    _registrar("(a) Irregularidade σ̂", linhas)


def _det(h_antes, h_depois, sigma, s, comparaveis=None):
    a = modelo.adquirir(h_antes, F, {"ruido_sigma_db": sigma}, semente=s if sigma else None)
    d = modelo.adquirir(h_depois, F, {"ruido_sigma_db": sigma}, semente=s + 50_000 if sigma else None)
    sa, sd = (calculos.irregularidade(x, "nenhuma")["sigma_db"] for x in (a, d))
    return calculos.detector_mudanca_via(a, d, sa, sd, calculos.faixa_util(a), comparaveis)["resultado"]


def test_b_detector():
    """(b) Detector: falsos positivos em "só polaridade", detecção de mudanças globais e estreitas."""
    base = modelo.resposta_via(TW, F)
    linhas = ["| cenário | σ | detectada | não detectada | inconclusiva |", "| --- | --- | --- | --- | --- |"]

    def linha(nome, h, sigma):
        res = [_det(base, h, sigma, s) for s in range(SEMENTES)]
        linhas.append(f"| {nome} | {sigma:.1f} | {res.count('mudanca_detectada')} | {res.count('nao_detectada')} | "
                      f"{res.count('inconclusiva')} |")
        return res

    fp = {}
    for sigma in (0.5, 1.0, 1.5):
        fp[sigma] = linha("só polaridade (sem mudança de magnitude)", -base, sigma).count("mudanca_detectada")
    n3 = linha("N3: ganho +3 dB", -modelo.resposta_via({**TW, "filtros": TW["filtros"] + [{"tipo": "ganho", "ganho_db": 3.0}]}, F), 1.5)
    assert n3.count("mudanca_detectada") == SEMENTES
    for nome, extra in (("ganho +1,5 dB", [{"tipo": "ganho", "ganho_db": 1.5}]),
                        ("ganho −1,5 dB", [{"tipo": "ganho", "ganho_db": -1.5}]),
                        ("ganho +3 dB", [{"tipo": "ganho", "ganho_db": 3.0}]),
                        ("PEQ +3 dB Q 2 em 6 kHz", [{"tipo": "peq", "f0_hz": 6000.0, "ganho_db": 3.0, "q": 2.0}]),
                        ("PEQ −3 dB Q 4 em 6 kHz", [{"tipo": "peq", "f0_hz": 6000.0, "ganho_db": -3.0, "q": 4.0}])):
        h = modelo.resposta_via({**TW, "filtros": TW["filtros"] + extra}, F)
        assert _det(base, h, 0.0, 0) == "mudanca_detectada", nome
        linha(nome, h, 0.5)
    corte = modelo.resposta_via({"filtros": [{"tipo": "lr4_pa", "fc_hz": 3500.0}]}, F)
    assert _det(base, corte, 0.0, 0) == "mudanca_detectada"
    linha("corte 3,0 → 3,5 kHz", corte, 0.5)
    nc = calculos.condicoes_comparaveis({"posicao_microfone": "P1", "ganho_entrada_db": 0, "referencia_nivel": "x"},
                                        {"posicao_microfone": "P2", "ganho_entrada_db": 0, "referencia_nivel": "x"})
    assert _det(base, -base, 0.5, 1, nc) == "inconclusiva"
    linhas += ["", "- Posição de microfone diferente: `inconclusiva` (nenhuma diferença atribuída ao DSP).",
               f"- **Falsos positivos em “só polaridade”**: σ 0,5 → {fp[0.5]}/{SEMENTES}; σ 1,0 → {fp[1.0]}/{SEMENTES}; "
               f"σ 1,5 → {fp[1.5]}/{SEMENTES}. O SC-208(b) pede zero até σ = 1,5 dB: **divergência aberta**, "
               "aguardando decisão `JV-D` (limiar não ajustado, P8).",
               f"- Limiares usados: média {limiares.valor('detector_media_db')} dB; bandas max("
               f"{limiares.valor('detector_banda_db')} dB; {limiares.valor('detector_fator_sigma')}·σΔ)."]
    _registrar("(b) Detector de mudança", linhas)
