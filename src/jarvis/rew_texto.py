"""Leitura e escrita de resposta em frequência em texto, no estilo da exportação do REW.

Estrutura assumida a partir de fontes secundárias (confirmação com arquivo real do REW prevista para o
JV-V04): linhas de comentário iniciadas por ``*``; uma linha de dados por frequência, com frequência
(Hz), nível (dB) e, opcionalmente, fase (graus). A leitura é tolerante a separadores (espaço,
tabulação, vírgula ou ponto e vírgula) e a vírgula decimal quando o separador é ponto e vírgula.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

MINIMO_DE_PONTOS = 10


class FormatoInvalido(Exception):
    """Arquivo que não pôde ser lido como resposta em frequência; a mensagem é para o usuário."""


@dataclass(frozen=True)
class RespostaFrequencia:
    freq_hz: np.ndarray
    nivel_db: np.ndarray
    fase_graus: np.ndarray | None  # None quando o arquivo não traz fase

    @property
    def tem_fase(self) -> bool:
        return self.fase_graus is not None


# Número en-US com separador de milhar e parte decimal, como o REW exporta ("1,000.1222"). A forma exige o ponto
# decimal para não confundir com vírgula decimal ("1,000" lido como 1,0), que continua tratada como antes.
_MILHAR_EN_US = re.compile(r"[+-]?\d{1,3}(?:,\d{3})+\.\d+")


def _campos(linha: str) -> list[str]:
    if ";" in linha:
        return [c.strip().replace(",", ".") for c in linha.split(";") if c.strip()]
    tokens = linha.split()
    if any(_MILHAR_EN_US.fullmatch(t) for t in tokens):
        return [t.replace(",", "") for t in tokens]  # vírgula dentro do número = milhar (REW, en-US)
    return [c for c in re.split(r"[\s,]+", linha.strip()) if c]


def ler_texto(texto: str, nome: str = "arquivo") -> RespostaFrequencia:
    linhas_dados: list[list[float]] = []
    for linha in texto.splitlines():
        limpa = linha.strip()
        if not limpa or limpa.startswith(("*", "#")):
            continue
        try:
            valores = [float(c) for c in _campos(limpa)]
        except ValueError:
            continue  # cabeçalho sem marcador de comentário
        if len(valores) >= 2:
            linhas_dados.append(valores[:3])

    if len(linhas_dados) < MINIMO_DE_PONTOS:
        raise FormatoInvalido(
            f"Não encontrei dados de resposta em frequência em “{nome}”. "
            "O arquivo precisa ter, em cada linha, a frequência em Hz e o nível em dB "
            "(e, de preferência, a fase em graus), como na exportação em texto do REW."
        )

    com_fase = all(len(v) >= 3 for v in linhas_dados)
    dados = np.array([v[:3] if com_fase else v[:2] for v in linhas_dados], dtype=float)
    return RespostaFrequencia(
        freq_hz=dados[:, 0],
        nivel_db=dados[:, 1],
        fase_graus=dados[:, 2] if com_fase else None,
    )


def motivo_do_sistema(erro: OSError) -> str:
    """Motivo, em português, de um erro de leitura de arquivo (o texto do sistema vem em inglês)."""
    if isinstance(erro, FileNotFoundError):
        return "o arquivo não existe (ou foi movido ou renomeado)"
    if isinstance(erro, IsADirectoryError):
        return "isto é uma pasta, não um arquivo"
    if isinstance(erro, PermissionError):
        return "sem permissão para ler o arquivo"
    return "o sistema não deixou ler o arquivo"


def ler(caminho: str | Path) -> RespostaFrequencia:
    caminho = Path(caminho)
    try:
        # No Windows, abrir uma pasta gera PermissionError (no Linux, IsADirectoryError); por isso a pasta é
        # identificada antes da leitura. A conferência fica DENTRO do tratamento de erros: em algumas versões do
        # Python (3.11) `Path.is_dir()` propaga erros de permissão em vez de devolver False.
        if caminho.is_dir():
            raise FormatoInvalido(f"Não consegui abrir “{caminho.name}”: isto é uma pasta, não um arquivo.")
        texto = caminho.read_text(encoding="utf-8", errors="replace")
    except OSError as erro:
        raise FormatoInvalido(f"Não consegui abrir “{caminho.name}”: {motivo_do_sistema(erro)}.") from erro
    return ler_texto(texto, caminho.name)


def escrever(caminho: str | Path, resposta: RespostaFrequencia, cabecalho: list[str]) -> None:
    Path(caminho).write_text(formatar(resposta, cabecalho), encoding="utf-8")


def formatar(resposta: RespostaFrequencia, cabecalho: list[str]) -> str:
    """Texto do arquivo com fim de linha LF (``escrever`` deixa o sistema convertê-lo, como no V01)."""
    linhas = [f"* {c}" for c in cabecalho]
    if resposta.tem_fase:
        linhas.append("* Freq(Hz) SPL(dB) Phase(degrees)")
        for f, n, p in zip(resposta.freq_hz, resposta.nivel_db, resposta.fase_graus):
            linhas.append(f"{f:.6f} {n:.4f} {p:.3f}")
    else:
        linhas.append("* Freq(Hz) SPL(dB)")
        for f, n in zip(resposta.freq_hz, resposta.nivel_db):
            linhas.append(f"{f:.6f} {n:.4f}")
    return "\n".join(linhas) + "\n"
