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
                   "dispersão de uma realização isolada pode passar do critério com σ alto. Critério revisto pela E4 "
                   "(viés médio + dispersão declarada, sem ampliar a tolerância); as realizações fora ficam registradas "
                   "aqui e analisadas em `validacao-limiares-e4.md`.",
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
               f"σ 1,5 → {fp[1.5]}/{SEMENTES}. O critério original do SC-208(b) (zero até σ = 1,5 dB) **não é atendido**: "
               "limitação conhecida, registrada pela E4 (indicativa × confirmada; ensaio ampliado em "
               "`validacao-limiares-e4.md`). Limiar não ajustado (P8).",
               f"- Limiares usados: média {limiares.valor('detector_media_db')} dB; bandas max("
               f"{limiares.valor('detector_banda_db')} dB; {limiares.valor('detector_fator_sigma')}·σΔ)."]
    _registrar("(b) Detector de mudança", linhas)


# --------------------------------------------------------------------------------------------------
# (c) Limites SEG (JV-T229). Usa o módulo de segurança real; nenhum dado de equipamento é inventado
# além do necessário para exercitar a fronteira (valores de cadastro fictícios, estado "confirmado").
# Falso aprovado = limite violado e regra aprovada; falso bloqueado = limite respeitado e regra bloqueada.
# O registro fica nas asserções e em ``LINHAS_C`` (não regrava ``validacao-limiares.md``).
# --------------------------------------------------------------------------------------------------
from jarvis import seguranca as seg  # noqa: E402

LINHAS_C: list[str] = []
EQUIP = [{"canal": "C1", "estado": "confirmado", "potencia_rms_w": 50.0, "fs_hz": 60.0,
          "passa_altas_min_hz": 80.0, "inclinacao_min_db_oit": 12.0}]


def _res(alt: dict, regra: str, equip=EQUIP) -> dict:
    alt = {"canal": "C1", **alt}
    return next(r for r in seg.avaliar(alt, equip) if r["regra"] == regra)


def _varrer(nome: str, valores, gerar, regra: str, dentro, equip=EQUIP) -> None:
    """Varre ``valores``; ``dentro(v)`` diz se o limite é respeitado. Afirma zero falsos e registra a contagem."""
    fa = fb = 0
    for v in valores:
        est = _res(gerar(v), regra, equip)["resultado"]
        assert est in (seg.APROVADA, seg.BLOQUEADA), (nome, v, est)
        if dentro(v) and est == seg.BLOQUEADA:
            fb += 1
        if not dentro(v) and est == seg.APROVADA:
            fa += 1
    assert (fa, fb) == (0, 0), (nome, fa, fb)
    LINHAS_C.append(f"{nome}: {len(valores)} pontos, falsos aprovados {fa}, falsos bloqueados {fb}")


def _passos(ini: float, fim: float, passo: float) -> list[float]:
    n = round((fim - ini) / passo)
    return [round(ini + i * passo, 6) for i in range(n + 1)]


def test_c_seg01_minimo_do_fabricante():
    """SEG-01: passa-altas e inclinação nunca abaixo do mínimo (80 Hz; 12 dB/oit) — fronteira e passos finos."""
    _varrer("SEG-01 passa-altas 70–90 Hz, passo 0,5", _passos(70, 90, 0.5),
            lambda v: {"tipo": "passa_altas", "de_hz": 100.0, "para_hz": v}, "SEG-01", lambda v: v >= 80.0)
    _varrer("SEG-01 passa-altas 79,99–80,01, passo 0,001", _passos(79.99, 80.01, 0.001),
            lambda v: {"tipo": "passa_altas", "de_hz": 100.0, "para_hz": v}, "SEG-01", lambda v: v >= 80.0 - 1e-9)
    _varrer("SEG-01 inclinação 6–18 dB/oit, passo 0,25", _passos(6, 18, 0.25),
            lambda v: {"tipo": "inclinacao", "de_db_oit": 24.0, "para_db_oit": v}, "SEG-01", lambda v: v >= 12.0)
    _varrer("SEG-01 inclinação 11,99–12,01, passo 0,001", _passos(11.99, 12.01, 0.001),
            lambda v: {"tipo": "inclinacao", "de_db_oit": 24.0, "para_db_oit": v}, "SEG-01", lambda v: v >= 12.0 - 1e-9)
    # Bloqueia o destino abaixo do mínimo mesmo quando a alteração SOBE a frequência (20 → 30 Hz, mín. 80).
    assert _res({"tipo": "passa_altas", "de_hz": 20.0, "para_hz": 30.0}, "SEG-01")["resultado"] == seg.BLOQUEADA
    assert seg.classificar({"tipo": "passa_altas", "de_hz": 20.0, "para_hz": 30.0}) == seg.DECRESCENTE
    # Dado ausente/inválido/não confirmado nunca aprova, em qualquer ponto da vizinhança.
    equips = [None, [], [{**EQUIP[0], "estado": "estimado"}], [{**EQUIP[0], "estado": "informado"}]]
    equips += [[{**EQUIP[0], "passa_altas_min_hz": m}] for m in (0, -80.0, None, "80", float("nan"), True)]
    for equip in equips:
        for v in (70.0, 79.99, 80.0, 90.0):
            assert _res({"tipo": "passa_altas", "de_hz": 100.0, "para_hz": v}, "SEG-01", equip)["resultado"] \
                == seg.NAO_VERIFICAVEL, (equip, v)
    assert _res({"tipo": "passa_altas", "de_hz": 100.0}, "SEG-01")["resultado"] == seg.NAO_VERIFICAVEL
    LINHAS_C.append("SEG-01: sem cadastro confirmado, mínimo inválido ou destino ausente ⇒ nunca aprovada")


def test_c_seg03_rms():
    """SEG-03: potência estimada versus RMS confirmada (50 W) — abaixo, no limite, acima e passos finos."""
    for tipo in ("ganho", "reforco_eq"):
        _varrer(f"SEG-03 {tipo} 40–60 W, passo 0,5", _passos(40, 60, 0.5),
                lambda v, t=tipo: {"tipo": t, "ganho_db": 1.0, "potencia_estimada_w": v}, "SEG-03", lambda v: v <= 50.0)
    _varrer("SEG-03 49,999–50,001 W, passo 0,0005", _passos(49.999, 50.001, 0.0005),
            lambda v: {"tipo": "ganho", "ganho_db": 1.0, "potencia_estimada_w": v}, "SEG-03", lambda v: v <= 50.0 + 1e-9)
    # Tolerância absoluta (1e-9 W): 50 + 1e-10 W ainda aprova; 50 + 1e-6 W bloqueia.
    assert _res({"tipo": "ganho", "ganho_db": 1.0, "potencia_estimada_w": 50.0 + 1e-10}, "SEG-03")["resultado"] == seg.APROVADA
    assert _res({"tipo": "ganho", "ganho_db": 1.0, "potencia_estimada_w": 50.0 + 1e-6}, "SEG-03")["resultado"] == seg.BLOQUEADA
    for est in (None, -1.0, float("nan"), float("inf"), True, "50"):
        alt = {"tipo": "ganho", "ganho_db": 1.0, **({} if est is None else {"potencia_estimada_w": est})}
        assert _res(alt, "SEG-03")["resultado"] == seg.NAO_VERIFICAVEL, est
    for equip in (None, [{**EQUIP[0], "estado": "estimado"}], [{**EQUIP[0], "potencia_rms_w": 0}],
                  [{**EQUIP[0], "potencia_rms_w": -50.0}], [{**EQUIP[0], "potencia_rms_w": None}]):
        assert _res({"tipo": "ganho", "ganho_db": 1.0, "potencia_estimada_w": 10.0}, "SEG-03", equip)["resultado"] \
            == seg.NAO_VERIFICAVEL
    # Vale também para redução de ganho (SEG-03 se aplica ao tipo "ganho" de qualquer sinal).
    assert _res({"tipo": "ganho", "ganho_db": -1.0, "potencia_estimada_w": 60.0}, "SEG-03")["resultado"] == seg.BLOQUEADA
    LINHAS_C.append("SEG-03: fronteira em 50 W (tolerância absoluta 1e-9 W); dado ausente/inválido ⇒ não verificável")


def test_c_seg04_passo():
    """SEG-04: no máximo +1,5 dB por experimento — ganho e reforço, de −1 a +2 dB em passos de 0,05."""
    ganhos = _passos(-1.0, 2.0, 0.05)
    for v in ganhos:
        if v <= 0:
            assert _res({"tipo": "ganho", "ganho_db": v}, "SEG-04")["resultado"] == seg.NAO_SE_APLICA, v
    for tipo in ("ganho", "reforco_eq"):
        _varrer(f"SEG-04 {tipo} 0,05–2 dB, passo 0,05", [g for g in ganhos if g > 0],
                lambda v, t=tipo: {"tipo": t, "ganho_db": v}, "SEG-04", lambda v: v <= 1.5 + 1e-9)
    _varrer("SEG-04 vizinhança 1,499–1,501, passo 0,0005", _passos(1.499, 1.501, 0.0005),
            lambda v: {"tipo": "ganho", "ganho_db": v}, "SEG-04", lambda v: v <= 1.5 + 1e-9)
    # Reforço de EQ com ganho ≤ 0 não é bloqueado pelo passo (a classe segue crescente pelo tipo).
    assert _res({"tipo": "reforco_eq", "ganho_db": 0.0}, "SEG-04")["resultado"] == seg.APROVADA
    assert seg.classificar({"tipo": "reforco_eq", "ganho_db": -2.0}) == seg.CRESCENTE
    assert _res({"tipo": "ganho"}, "SEG-04")["resultado"] == seg.NAO_VERIFICAVEL
    for alt in ({"tipo": "corte_eq", "ganho_db": -3.0}, {"tipo": "passa_altas", "para_hz": 90.0},
                {"tipo": "polaridade"}, {"tipo": "atraso"}):
        assert _res(alt, "SEG-04")["resultado"] == seg.NAO_SE_APLICA, alt
    LINHAS_C.append("SEG-04: fronteira em +1,5 dB (provisório); redução e corte não se aplicam")


def test_c_seg05_filtro_e_banda():
    """SEG-05: +3 dB por filtro e +6 dB somados na banda — grade de filtro × reforço já presente."""
    _varrer("SEG-05 por filtro 2,5–3,5 dB, passo 0,05", _passos(2.5, 3.5, 0.05),
            lambda v: {"tipo": "reforco_eq", "ganho_db": v, "reforcos_na_banda_db": []}, "SEG-05", lambda v: v <= 3.0 + 1e-9)
    fa = fb = pts = 0
    for g in _passos(0.5, 3.0, 0.25):
        for outro in _passos(0.0, 4.0, 0.25):
            est = _res({"tipo": "reforco_eq", "ganho_db": g, "reforcos_na_banda_db": [outro]}, "SEG-05")["resultado"]
            dentro = g + outro <= 6.0 + 1e-9
            pts += 1
            fa += (not dentro) and est == seg.APROVADA
            fb += dentro and est == seg.BLOQUEADA
    assert (fa, fb) == (0, 0)
    LINHAS_C.append(f"SEG-05 grade filtro × banda: {pts} pontos, falsos aprovados {fa}, falsos bloqueados {fb}")
    base = {"tipo": "reforco_eq", "ganho_db": 3.0}
    assert _res({**base, "reforcos_na_banda_db": [3.0]}, "SEG-05")["resultado"] == seg.APROVADA
    assert _res({**base, "reforcos_na_banda_db": [3.01]}, "SEG-05")["resultado"] == seg.BLOQUEADA
    assert _res({**base, "reforcos_na_banda_db": [1.0, 1.0, 1.01]}, "SEG-05")["resultado"] == seg.BLOQUEADA
    assert _res({**base, "reforcos_na_banda_db": [3.0, -5.0]}, "SEG-05")["resultado"] == seg.APROVADA  # corte não abate
    assert _res({**base, "reforcos_na_banda_db": [3.0, 0.01, -5.0]}, "SEG-05")["resultado"] == seg.BLOQUEADA
    for banda in (None, "3", [float("nan")], [None], [True]):
        alt = {**base, **({} if banda is None else {"reforcos_na_banda_db": banda})}
        assert _res(alt, "SEG-05")["resultado"] == seg.NAO_VERIFICAVEL, banda
    assert _res({"tipo": "reforco_eq"}, "SEG-05")["resultado"] == seg.NAO_VERIFICAVEL
    assert _res({"tipo": "reforco_eq", "ganho_db": 3.01}, "SEG-05")["resultado"] == seg.BLOQUEADA
    for alt in ({"tipo": "ganho", "ganho_db": 5.0}, {"tipo": "corte_eq", "ganho_db": -4.0}):
        assert _res(alt, "SEG-05")["resultado"] == seg.NAO_SE_APLICA
    LINHAS_C.append("SEG-05: +3 dB por filtro e +6 dB na banda (provisório); banda não informada ⇒ não verificável")


def test_c_seg06_seg13_e_nao_confirmado():
    """SEG-06 e SEG-13 (limites categóricos) e equipamento não confirmado (SEG-12) sobre SEG-01/03."""
    for c in seg.CLASSES_VALE_NAO_EQUALIZAVEL:
        assert _res({"tipo": "reforco_eq", "ganho_db": 1.0, "vale_classificacao": c}, "SEG-06")["resultado"] == seg.BLOQUEADA
    for c in seg.CLASSES_SEM_VALE_NAO_EQUALIZAVEL:
        assert _res({"tipo": "reforco_eq", "ganho_db": 1.0, "vale_classificacao": c}, "SEG-06")["resultado"] == seg.APROVADA
    for c in (None, "", "desconhecida", 3):
        alt = {"tipo": "reforco_eq", "ganho_db": 1.0, **({} if c is None else {"vale_classificacao": c})}
        assert _res(alt, "SEG-06")["resultado"] == seg.NAO_VERIFICAVEL, c
    etapa = {"tipo": "ganho", "ganho_db": 1.0, "etapa_automatizada": True, "limites_informados": True}
    assert _res({**etapa, "valores_conferencia": [{"valor": 1, "origem": "declarado"}, {"valor": 2, "origem": "medição"}]},
                "SEG-13")["resultado"] == seg.APROVADA
    assert _res({**etapa, "valores_conferencia": [{"valor": 1, "origem": "arquivo"}]}, "SEG-13")["resultado"] == seg.BLOQUEADA
    assert _res({**etapa, "valores_conferencia": [{"valor": 1}]}, "SEG-13")["resultado"] == seg.NAO_VERIFICAVEL
    assert _res({**etapa, "valores_conferencia": []}, "SEG-13")["resultado"] == seg.NAO_VERIFICAVEL
    assert _res({**etapa, "limites_informados": False, "valores_conferencia": [{"valor": 1, "origem": "declarado"}]},
                "SEG-13")["resultado"] == seg.NAO_VERIFICAVEL
    for estado in ("estimado", "informado", "", None):
        eq = [{**EQUIP[0], "estado": estado}]
        for v in (60.0, 80.0, 100.0):
            assert _res({"tipo": "passa_altas", "de_hz": 120.0, "para_hz": v}, "SEG-01", eq)["resultado"] == seg.NAO_VERIFICAVEL
        for w in (10.0, 50.0, 90.0):
            assert _res({"tipo": "ganho", "ganho_db": 1.0, "potencia_estimada_w": w}, "SEG-03", eq)["resultado"] == seg.NAO_VERIFICAVEL
    LINHAS_C.append("SEG-06/13: categóricos; equipamento não confirmado nunca aprova SEG-01/03")


def test_c_admissibilidade_nas_fronteiras():
    """Admissibilidade nas fronteiras: risco crescente nunca é recomendado (SEG-02/07/09 sem método); decrescente
    só é bloqueado por regra bloqueada. Bloquear crescente dentro de todos os limites é falso bloqueio *por
    desenho* (FR-212), registrado e não corrigido."""
    crescentes = 0
    for g in _passos(0.0, 3.5, 0.1):
        alt = {"canal": "C1", "tipo": "reforco_eq", "ganho_db": g, "potencia_estimada_w": 20.0,
               "reforcos_na_banda_db": [], "vale_classificacao": "equalizavel"}
        adm = seg.admissibilidade(seg.classificar(alt), seg.avaliar(alt, EQUIP))
        assert adm["admissivel"] is False and adm["exige_aprovacao_b"] is False, g
        assert {"SEG-02", "SEG-07", "SEG-09"} <= set(adm["nao_verificadas"]), g
        crescentes += 1
    for alt in ({"tipo": "ganho", "ganho_db": -1.5, "potencia_estimada_w": 50.0},
                {"tipo": "passa_altas", "de_hz": 80.0, "para_hz": 90.0}):
        alt = {"canal": "C1", **alt}
        adm = seg.admissibilidade(seg.classificar(alt), seg.avaliar(alt, EQUIP))
        assert adm["admissivel"] is True and adm["exige_aprovacao_b"] is True and adm["aviso"], alt
    for alt, regra in (({"tipo": "ganho", "ganho_db": -1.5, "potencia_estimada_w": 50.01}, "SEG-03"),
                       ({"tipo": "passa_altas", "de_hz": 90.0, "para_hz": 79.99}, "SEG-01")):
        alt = {"canal": "C1", **alt}
        adm = seg.admissibilidade(seg.classificar(alt), seg.avaliar(alt, EQUIP))
        assert adm["admissivel"] is False and adm["estado"] == "bloqueada" and regra in adm["motivo"], alt
    for tipo in ("polaridade", "atraso"):
        alt = {"canal": "C1", "tipo": tipo}
        assert seg.admissibilidade(seg.classificar(alt), seg.avaliar(alt, EQUIP))["admissivel"] is True
    LINHAS_C.append(f"Admissibilidade: {crescentes} reforços de 0 a 3,5 dB, todos bloqueados por SEG-02/07/09 "
                    "(falso bloqueio por desenho); decrescentes dentro dos limites recomendados")
