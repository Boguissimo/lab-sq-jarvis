"""Limiares do JV-V02, centralizados (ADR-211).

Cada limiar traz valor, unidade, se é provisório e a origem na spec ou nas regras de segurança.
Provisório quer dizer: escolhido pelo agente ou candidato, exercitado só em casos simulados, **não**
validado para o carro (JV-D025, JV-D042). Mudar um valor exige uma decisão `JV-D` e reexecutar a
varredura de validação (SC-208, P8).

Os limiares do V01 (`regras.LIMIARES`, `sessao.CRITERIO_ACEITE`) continuam onde estão, para não
alterar as asserções do V01 (INV-210).
"""

# @@T201 [FR-202] [FR-207] [FR-217] Limiares centralizados com origem e rótulo provisório

from __future__ import annotations

import copy

VERSAO = "1.0"

LIMIARES: dict[str, dict] = {
    # --- Irregularidade ponto a ponto σ̂ (FR-202; ADR-202) ---
    "irregularidade_aviso_db": {
        "valor": 0.5, "unidade": "dB", "provisorio": True,
        "origem": "spec E1, definição 'Aviso de irregularidade' / FR-202 (limite candidato, SC-208)",
    },
    "irregularidade_reprovada_db": {
        "valor": 1.5, "unidade": "dB", "provisorio": True,
        "origem": "spec E1, definição 'Qualidade reprovada por irregularidade' / FR-202 (limite candidato, SC-208)",
    },
    "irregularidade_pontos_por_oitava_min": {
        "valor": 24, "unidade": "pontos/oitava", "provisorio": True,
        "origem": "spec E1, 'Condições de aplicação do estimador' (ii) / FR-202",
    },
    "irregularidade_tolerancia_grade": {
        "valor": 0.005, "unidade": "fração", "provisorio": False,
        "origem": "spec E1, 'Condições de aplicação do estimador' (i) / FR-202",
    },
    "faixa_analise_min_hz": {
        "valor": 200.0, "unidade": "Hz", "provisorio": False,
        "origem": "spec E1, definição de σ̂, vale individual e faixa útil",
    },
    "faixa_analise_max_hz": {
        "valor": 10000.0, "unidade": "Hz", "provisorio": False,
        "origem": "spec E1, definição de σ̂, vale individual e faixa útil",
    },
    # --- Vale individual (FR-204) ---
    "vale_individual_profundidade_db": {
        "valor": 10.0, "unidade": "dB", "provisorio": True,
        "origem": "spec, definição 'Vale individual' / FR-204",
    },
    "vale_individual_largura_max_oitava": {
        "valor": 1.0 / 3.0, "unidade": "oitava", "provisorio": True,
        "origem": "spec, definição 'Vale individual' / FR-204",
    },
    # --- Detector de mudança por via (FR-207; ADR-208) ---
    "faixa_util_abaixo_max_db": {
        "valor": 20.0, "unidade": "dB", "provisorio": True,
        "origem": "spec E1, definição 'Faixa útil da via' / FR-207",
    },
    "detector_media_db": {
        "valor": 1.0, "unidade": "dB", "provisorio": True,
        "origem": "spec E1, definição 'Detector de mudança da via' (mudança geral) / FR-207",
    },
    "detector_banda_db": {
        "valor": 1.5, "unidade": "dB", "provisorio": True,
        "origem": "spec E1, definição 'Detector de mudança da via' (mudança localizada) / FR-207",
    },
    "detector_fator_sigma": {
        "valor": 3.0, "unidade": "adimensional", "provisorio": True,
        "origem": "spec E1, definição 'Detector de mudança da via' (fator de σΔ) / FR-207",
    },
    "detector_largura_banda_oitava": {
        "valor": 1.0 / 3.0, "unidade": "oitava", "provisorio": False,
        "origem": "spec E1, definição 'Detector de mudança da via' (janela deslizante) / FR-207",
    },
    # --- Amostras mínimas para fase e atraso (ADR-212, A04) ---
    "fase_pontos_min": {
        "valor": 8, "unidade": "pontos", "provisorio": True,
        "origem": "plano R1.2, ADR-212 (A04) / FR-205",
    },
    "sobreposicao_largura_min_oitava": {
        "valor": 1.0 / 3.0, "unidade": "oitava", "provisorio": True,
        "origem": "plano R1.2, ADR-212 (A04) / FR-205",
    },
    # --- Etapa de calibração (FR-217) ---
    "etapa_deficit_objetivo_db": {
        "valor": 3.0, "unidade": "dB", "provisorio": True,
        "origem": "spec E1/E3, 'Objetivo da etapa de calibração' / FR-217",
    },
    "etapa_reducao_parcial": {
        "valor": 0.5, "unidade": "fração", "provisorio": True,
        "origem": "spec E1, 'Resultado da etapa' (3. parcial) / FR-217",
    },
    # --- Regras de segurança v0.4.0 (FR-211, FR-214) ---
    "seg02_fator_fs": {
        "valor": 2.0, "unidade": "× Fs", "provisorio": True,
        "origem": "regras de segurança v0.4.0, SEG-02 / FR-212",
    },
    "seg04_passo_max_db": {
        "valor": 1.5, "unidade": "dB", "provisorio": True,
        "origem": "regras de segurança v0.4.0, SEG-04 / FR-211, FR-214",
    },
    "seg05_reforco_filtro_max_db": {
        "valor": 3.0, "unidade": "dB", "provisorio": True,
        "origem": "regras de segurança v0.4.0, SEG-05 / FR-211",
    },
    "seg05_reforco_banda_max_db": {
        "valor": 6.0, "unidade": "dB", "provisorio": True,
        "origem": "regras de segurança v0.4.0, SEG-05 / FR-211",
    },
}


def valor(nome: str) -> float:
    """Valor numérico do limiar ``nome``."""
    return LIMIARES[nome]["valor"]


def rotulo(nome: str, casas: int = 1) -> str:
    """Texto do limiar para exibição, com o rótulo de provisório quando for o caso (FR-214)."""
    lim = LIMIARES[nome]
    v = f"{lim['valor']:.{casas}f}".replace(".", ",")
    unidade = f" {lim['unidade']}" if lim["unidade"] not in ("fração", "adimensional") else ""
    return f"limite provisório de {v}{unidade}" if lim["provisorio"] else f"limite de {v}{unidade}"


def snapshot(*nomes: str) -> dict:
    """Cópia dos limiares usados num cálculo, para gravar junto do registro (ADR-210, ADR-211)."""
    escolhidos = nomes or tuple(LIMIARES)
    return {"versao": VERSAO, "limiares": {n: copy.deepcopy(LIMIARES[n]) for n in escolhidos}}
