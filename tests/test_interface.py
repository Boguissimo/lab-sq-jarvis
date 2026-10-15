"""Teste da interface com pytest-qt: o percurso completo pelos botões, fechando e reabrindo."""

from jarvis.interface.janela import JanelaPrincipal
from jarvis.persistencia import Banco
from jarvis.sessao import AVISO_SIMULADO, Servico


def _janela(qtbot, pasta):
    janela = JanelaPrincipal(Servico(Banco(pasta)))
    erros = []
    janela.mostrar_erro = erros.append
    qtbot.addWidget(janela)
    return janela, erros


def test_aviso_de_demonstracao_sempre_visivel(qtbot, tmp_path):
    janela, _ = _janela(qtbot, tmp_path / "d")
    janela.show()
    assert AVISO_SIMULADO in janela.aviso.text()
    assert "simulados" in janela.windowTitle()


def test_percurso_pela_interface_e_retomada(qtbot, tmp_path):
    pasta = tmp_path / "d"
    janela, erros = _janela(qtbot, pasta)
    janela.show()
    janela.botao_comecar.click()
    assert janela.pilha.currentIndex() == 1
    janela.botao_importar.click()
    janela.botao_analisar.click()
    assert janela.pilha.currentIndex() == 2
    janela.botao_propor.click()
    assert janela.pilha.currentIndex() == 3
    janela.botao_aplicar.click()
    assert janela.pilha.currentIndex() == 4
    janela.botao_depois.click()
    janela.botao_concluir.click()
    estado = janela.servico.estado()
    assert estado["conclusao"]["dados"]["veredito"] == "confirmada"
    janela.botao_manter.click()
    assert erros == []
    assert janela.servico.estado()["sessao"]["estado"] == "encerrada"
    sid = janela.servico.sessao_id
    janela.servico.b.fechar()
    janela.close()

    # programa reaberto: a sessão aparece no histórico e pode ser aberta
    janela2, erros2 = _janela(qtbot, pasta)
    janela2.show()
    assert janela2.pilha.currentIndex() == 5
    assert janela2.tabela_hist.item(0, 0).text() == str(sid)
    janela2.botao_abrir.click()
    assert janela2.servico.sessao_id == sid
    assert janela2.pilha.currentIndex() == 4
    assert erros2 == []
    janela2.servico.b.fechar()


def test_nada_a_alterar_pela_interface(qtbot, tmp_path):
    janela, erros = _janela(qtbot, tmp_path / "d")
    janela.pedir_texto = lambda titulo, rotulo: ("Sem queixa nesta região; manter como está.", True)
    janela.botao_comecar.click()
    janela.botao_importar.click()
    janela.botao_analisar.click()
    janela.botao_nada.click()
    e = janela.servico.estado()
    assert e["sessao"]["estado"] == "encerrada"
    assert e["decisoes"][0]["dados"]["sem_intervencao"]
    assert not e["experimento"]
    assert erros == []
    janela.servico.b.fechar()


def test_erro_aparece_em_linguagem_simples(qtbot, tmp_path):
    janela, erros = _janela(qtbot, tmp_path / "d")
    janela.escolher_pasta = lambda: str(tmp_path)  # pasta sem caso
    janela.botao_comecar.click()
    janela._importar_outra()
    assert erros and "manifesto" in erros[0]
    janela.servico.b.fechar()
