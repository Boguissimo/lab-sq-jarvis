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


@pytest.fixture
def cria_recomendacao():
    """Fábrica de ``recomendacao`` para testar a aprovação (T227).

    A alteração passa pelo módulo de segurança real (``classificar``/``avaliar``/``admissibilidade``), sem dado
    de equipamento inventado. O produto só gera recomendação sensível a partir da T228; até lá o registro é
    montado aqui, no mesmo formato que ``propor_teste`` grava.
    """
    from jarvis import seguranca as seg
    from jarvis.persistencia import agora

    def _f(servico, **campos):
        b, sid = servico.b, servico.sessao_id
        alt = {"canal": "medio_esq", "parametro": "EQ 1 kHz", "de": "0 dB", "para": "−2 dB",
               "tipo": "corte_eq", "freq_hz": 1000.0, "q": 2.0, "ganho_db": -2.0}
        alt.update(campos)
        classe = seg.classificar(alt)
        regras = seg.avaliar(alt, None)
        adm = seg.admissibilidade(classe, regras)
        h = b.novo_registro(sid, "hipotese", "hipótese sintética", {})
        c = b.novo_registro(sid, "calculo", "previsão sintética", {})
        dados = {"variavel": {k: alt[k] for k in ("canal", "parametro", "de", "para")},
                 "seguranca": {"versao_regras_seg": seg.VERSAO, "classe": classe, "motivo": adm["motivo"],
                               "regras": regras, "admissibilidade": adm, "limitacoes": list(seg.LIMITACOES)},
                 "receita": ["passo sintético"] if adm["admissivel"] else None,
                 "reversao": {"garantida": False, "receita_inversa": None, "base": "sintético"},
                 "previsao_registrada_em": agora()}
        return b.novo_registro(sid, "recomendacao", "Recomendação sintética", dados,
                               origens=[(h, "hipótese testada"), (c, "previsão")])
    return _f
