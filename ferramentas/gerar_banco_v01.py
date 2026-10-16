"""Gera a fixture do banco do JV-V01 usada pelos testes de migração (ADR-207, JV-T205).

Roda o percurso completo do REF-001-A com o **código original do V01** (commit ``389e580``), num
checkout temporário (``git worktree``), e grava banco e cofre em ``tests/dados/banco-v01/``.

A fixture contém só dados sintéticos (sessões do REF-001-A), é versionada e **não deve ser
regenerada sem uma decisão `JV-D`**: ela é o teste de regressão permanente da migração (E2).

Uso (na raiz do repositório):
    python ferramentas/gerar_banco_v01.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COMMIT_V01 = "389e580"
RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "tests" / "dados" / "banco-v01"

# Executado com o código do V01 no PYTHONPATH. Duas sessões: uma completa (teste de polaridade,
# veredito, decisão "manter") e outra aberta depois da análise, para a migração preservar também
# sessões em andamento.
PERCURSO = r'''
import sys
from pathlib import Path
from jarvis.persistencia import Banco
from jarvis.referencia.ref001 import PASTA_PADRAO
from jarvis.sessao import Servico

b = Banco(Path(sys.argv[1]))
s = Servico(b)
s.nova_sessao("investigacao")
s.registrar_percepcao("antes", "não aplicável")
s.importar_caso(PASTA_PADRAO)
s.analisar()
s.propor_teste()
s.registrar_aplicacao()
s.importar_depois()
s.registrar_percepcao("depois", "não aplicável")
s.concluir()
s.decidir("manter")

s.nova_sessao("investigacao")
s.registrar_percepcao("antes", "não aplicável")
s.importar_caso(PASTA_PADRAO)
s.analisar()
assert b.integridade() == [], b.integridade()
b.fechar()
print("ok")
'''


def main() -> int:
    if DESTINO.exists() and "--forcar" not in sys.argv:
        print(f"{DESTINO} já existe. A fixture é permanente; regenere só com uma decisão JV-D (--forcar).")
        return 1
    with tempfile.TemporaryDirectory(prefix="jv-v01-") as tmp:
        checkout = Path(tmp) / "v01"
        saida = Path(tmp) / "dados"
        subprocess.run(["git", "-C", str(RAIZ), "worktree", "add", "--detach", str(checkout), COMMIT_V01],
                       check=True)
        try:
            env = {**os.environ, "PYTHONPATH": str(checkout / "src")}
            env.pop("JARVIS_DADOS", None)
            subprocess.run([sys.executable, "-c", PERCURSO, str(saida)], check=True, env=env, cwd=tmp)
        finally:
            subprocess.run(["git", "-C", str(RAIZ), "worktree", "remove", "--force", str(checkout)], check=True)
        if DESTINO.exists():
            shutil.rmtree(DESTINO, onerror=lambda f, p, e: (os.chmod(p, 0o644), f(p)))
        shutil.copytree(saida, DESTINO)
    for extra in DESTINO.rglob("*-wal"):
        extra.unlink()
    print(f"Fixture gravada em {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
