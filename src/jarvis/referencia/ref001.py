"""Gerador determinístico do caso de referência REF-001-A (JV-D016; spec do JV-V01, FR-001).

Cenário simulado e ideal: médio e tweeter do lado esquerdo, crossover Linkwitz-Riley de 4ª ordem
em 3 000 Hz, alto-falantes de resposta plana, ambos a 1,00 m do microfone, mesma referência temporal
(loopback simulado). A falha injetada é a **fiação do tweeter invertida**; no DSP, as duas vias
estão declaradas com polaridade 0°. Por isso a soma tem um vale profundo no cruzamento, e inverter a
polaridade do tweeter no DSP (0° → 180°) compensa a fiação.

Uso: ``python -m jarvis.referencia.ref001 [pasta]`` (padrão: pasta de dados do pacote).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from jarvis.rew_texto import RespostaFrequencia, escrever

CASO = "REF-001-A"
FREQ_CRUZAMENTO_HZ = 3000.0
DISTANCIA_M = 1.00
VELOCIDADE_SOM_M_S = 343.0
NIVEL_REFERENCIA_DB = 85.0
PONTOS_POR_OITAVA = 48
FAIXA_HZ = (20.0, 20_000.0)

PASTA_PADRAO = Path(__file__).resolve().parent / "dados" / CASO


def grade_frequencias() -> np.ndarray:
    oitavas = np.log2(FAIXA_HZ[1] / FAIXA_HZ[0])
    n = int(round(oitavas * PONTOS_POR_OITAVA)) + 1
    return FAIXA_HZ[0] * 2.0 ** (np.arange(n) / PONTOS_POR_OITAVA)


def linkwitz_riley_4(f: np.ndarray, fc: float) -> tuple[np.ndarray, np.ndarray]:
    """Passa-baixas e passa-altas LR4 (Butterworth de 2ª ordem ao quadrado)."""
    s = 1j * f / fc
    denominador = (s ** 2 + np.sqrt(2.0) * s + 1.0) ** 2
    return 1.0 / denominador, s ** 4 / denominador


def _resposta(f: np.ndarray, h: np.ndarray) -> RespostaFrequencia:
    atraso_s = DISTANCIA_M / VELOCIDADE_SOM_M_S
    h = h * np.exp(-2j * np.pi * f * atraso_s) * 10 ** (NIVEL_REFERENCIA_DB / 20.0)
    fase = np.rad2deg(np.angle(h))
    return RespostaFrequencia(freq_hz=f, nivel_db=20.0 * np.log10(np.maximum(np.abs(h), 1e-12)),
                              fase_graus=fase)


def respostas() -> dict[str, RespostaFrequencia]:
    f = grade_frequencias()
    passa_baixas, passa_altas = linkwitz_riley_4(f, FREQ_CRUZAMENTO_HZ)
    tweeter_com_fiacao_invertida = -passa_altas
    return {
        "medio": _resposta(f, passa_baixas),
        "tweeter": _resposta(f, tweeter_com_fiacao_invertida),
        "soma-antes": _resposta(f, passa_baixas + tweeter_com_fiacao_invertida),
        # depois de inverter o tweeter no DSP (0° → 180°), a fiação invertida fica compensada
        "soma-depois": _resposta(f, passa_baixas - tweeter_com_fiacao_invertida),
    }


def _manifesto() -> dict:
    referencia = {"tipo": "loopback", "id": f"{CASO}-loopback-simulado"}
    comum = {
        "referencia_temporal": referencia,
        "taxa_amostragem": 48000,
        "posicao_microfone": "P1 — posição de escuta do motorista (simulada)",
        "simulado": True,
    }
    return {
        "caso": CASO,
        "simulado": True,
        "descricao": (
            "Caso simulado e ideal: médio e tweeter com crossover Linkwitz-Riley de 4ª ordem em "
            "3 000 Hz, alto-falantes planos, mesma distância. Serve para verificar cálculos e o "
            "percurso do programa; não representa o carro."
        ),
        "configuracao_declarada": {
            "nome": "Ajuste inicial do caso REF-001-A (declarado)",
            "parametros": [
                {"canal": "medio_esq", "parametro": "polaridade", "valor": "0°"},
                {"canal": "tweeter_esq", "parametro": "polaridade", "valor": "0°"},
                {"canal": "medio_esq", "parametro": "passa-baixas", "valor": "LR 24 dB/oit em 3000 Hz"},
                {"canal": "tweeter_esq", "parametro": "passa-altas", "valor": "LR 24 dB/oit em 3000 Hz"},
            ],
        },
        "medicoes": [
            {"arquivo": "medio.txt", "momento": "antes", "papel": "via_a", "canal": "medio_esq",
             "descricao": "Médio esquerdo sozinho", **comum},
            {"arquivo": "tweeter.txt", "momento": "antes", "papel": "via_b", "canal": "tweeter_esq",
             "descricao": "Tweeter esquerdo sozinho", **comum},
            {"arquivo": "soma-antes.txt", "momento": "antes", "papel": "soma",
             "canal": "medio_esq+tweeter_esq", "descricao": "Médio e tweeter juntos", **comum},
            {"arquivo": "soma-depois.txt", "momento": "depois", "papel": "soma",
             "canal": "medio_esq+tweeter_esq",
             "descricao": "Médio e tweeter juntos, depois de inverter o tweeter no DSP", **comum},
        ],
    }


def gerar(pasta: str | Path = PASTA_PADRAO) -> Path:
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    cabecalho = [
        f"Lab SQ Jarvis — caso de referência {CASO} (DADOS SIMULADOS, não é medição real)",
        "Formato: frequência (Hz), nível (dB), fase (graus), no estilo da exportação em texto do REW",
    ]
    for nome, r in respostas().items():
        escrever(pasta / f"{nome}.txt", r, cabecalho + [f"Medição simulada: {nome}"])
    (pasta / "manifesto.json").write_text(
        json.dumps(_manifesto(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pasta


if __name__ == "__main__":
    destino = gerar(sys.argv[1] if len(sys.argv) > 1 else PASTA_PADRAO)
    print(f"Caso {CASO} gerado em {destino}")
