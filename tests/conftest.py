import pytest

from jarvis.persistencia import Banco
from jarvis.referencia.ref001 import PASTA_PADRAO
from jarvis.sessao import Servico


@pytest.fixture
def banco(tmp_path):
    b = Banco(tmp_path / "dados")
    yield b
    b.fechar()


@pytest.fixture
def servico(banco):
    return Servico(banco)


@pytest.fixture
def pasta_caso():
    return PASTA_PADRAO
