"""Utilitários do harness da investigação de desempenho (exploratório; não faz parte do produto)."""
import hashlib, json, os, re
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
ADMISSAO = RAIZ / "docs/revisoes/investigacao-desempenho/admissao-joeglondon.json"


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verificar_origem(fonte: Path, admissao: Path = ADMISSAO) -> dict:
    """Confere o SHA-256 de todos os arquivos do manifesto; aborta se algo divergir."""
    adm = json.loads(Path(admissao).read_text(encoding="utf-8"))
    ruins = [a for a, m in adm["arquivos"].items() if sha256(fonte / a) != m["sha256"]]
    if ruins:
        raise SystemExit(f"Arquivos que não conferem com o manifesto: {ruins[:5]}")
    return adm


def ler_spl(p):
    """Leitor independente do produto (numpy): devolve freq, nível dB, fase graus e o cabeçalho."""
    cab, dados = [], []
    for linha in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
        if linha.startswith("*"):
            cab.append(linha)
        elif linha.strip():
            campos = linha.split()
            # Fato do formato verificado nos arquivos: o REW (en-US) escreve a frequência com separador de
            # milhar ("1,000.1222"); a vírgula só aparece no 1º campo. Aqui é removida; o produto NÃO faz isso.
            assert all("," not in c for c in campos[1:]), "vírgula fora do campo de frequência"
            dados.append([float(campos[0].replace(",", "")), float(campos[1]), float(campos[2])])
    d = np.array(dados)
    return d[:, 0], d[:, 1], d[:, 2], cab


def complexo(nivel_db, fase_graus):
    return 10 ** (np.asarray(nivel_db) / 20.0) * np.exp(1j * np.deg2rad(fase_graus))
