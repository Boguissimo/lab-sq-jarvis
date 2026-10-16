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


# --- JV-T222 (FR-209): seletor de caso e textos dos resultados do bloco 1 ---

from PySide6.QtWidgets import QLabel, QTextBrowser  # noqa: E402


def _textos(janela, pagina):
    w = janela.paginas[pagina]
    return " ".join([x.toPlainText() for x in w.findChildren(QTextBrowser)]
                    + [x.text() for x in w.findChildren(QLabel)])


def _escolher(janela, nome):
    i = next(i for i in range(janela.seletor_caso.count()) if janela.seletor_caso.itemText(i).startswith(nome))
    janela.seletor_caso.setCurrentIndex(i)


def test_seletor_casos(qtbot, tmp_path):
    janela, erros = _janela(qtbot, tmp_path / "d")
    janela.botao_comecar.click()
    nomes = [janela.seletor_caso.itemText(i) for i in range(janela.seletor_caso.count())]
    assert nomes[0].startswith("REF-001-A")
    for caso in ("REF-001-B", "REF-001-N1", "REF-001-N2", "REF-001-N3", "REF-001-N4", "REF-001-N5"):
        assert any(n.startswith(caso) for n in nomes), caso
    assert all("simulado" in n for n in nomes)
    _escolher(janela, "REF-001-N2")
    assert "ruído alto" in janela.descricao_caso.text()
    janela.botao_importar.click()
    janela.botao_analisar.click()
    assert janela.servico.estado()["sessao"]["caso"] == "REF-001-N2"
    texto = _textos(janela, 2)
    assert "Não dá para concluir" in texto and "O que falta" in texto
    assert erros == []
    janela.servico.b.fechar()


def _analisar_pela_interface(qtbot, tmp_path, nome):
    janela, erros = _janela(qtbot, tmp_path / nome)
    janela.botao_comecar.click()
    _escolher(janela, nome)
    janela.botao_importar.click()
    janela.botao_analisar.click()
    return janela, erros


def test_textos_resultados(qtbot, tmp_path):
    j, erros = _analisar_pela_interface(qtbot, tmp_path, "REF-001-N1")
    t = _textos(j, 2)
    assert "vale numa via isolada" in t and "Interferência ou reflexão" in t and "aprovada" in t
    j.servico.b.fechar()

    j, erros = _analisar_pela_interface(qtbot, tmp_path, "REF-001-N4")
    assert "Sem referência temporal declarada compatível" in _textos(j, 2)
    j.servico.b.fechar()

    j, erros = _analisar_pela_interface(qtbot, tmp_path, "REF-001-N5")
    assert "Sem indício de problema no cruzamento" in _textos(j, 2)
    recebido = {}
    j.pedir_texto = lambda titulo, rotulo, inicial="": (recebido.setdefault("inicial", inicial) or inicial, True)
    j.botao_nada.click()
    assert recebido["inicial"].startswith("Sem indício de problema")
    assert j.servico.estado()["sessao"]["estado"] == "encerrada"
    j.servico.b.fechar()

    j, erros = _analisar_pela_interface(qtbot, tmp_path, "REF-001-N3")
    j.botao_propor.click()
    j.botao_aplicar.click()
    j.botao_depois.click()
    j.botao_concluir.click()
    t = _textos(j, 4)
    assert "comprometida" in t and "mudança detectada e reproduzida" in t
    assert "a medição não identifica a causa" in t
    assert "não comprova alteração no DSP" in t
    assert "Médio: não verificada" in t
    assert erros == []
    j._montar_historico()
    cab = [j.tabela_hist.horizontalHeaderItem(i).text() for i in range(j.tabela_hist.columnCount())]
    assert "Modo" in cab
    j.servico.b.fechar()


def test_mudanca_suspeita_sem_afirmar_dsp(qtbot, tmp_path, monkeypatch):
    """E4/FR-209: a mudança indicativa aparece como suspeita, pede repetição e não afirma alteração do DSP."""
    from jarvis import calculos
    real = calculos.repeticao_confirma
    monkeypatch.setattr(calculos, "repeticao_confirma", lambda d1, d2: {**real(d1, d2), "reproduzida": False,
                                                                        "faixa_compativel": False})
    j, erros = _analisar_pela_interface(qtbot, tmp_path, "REF-001-N3")
    j.botao_propor.click()
    j.botao_aplicar.click()
    j.botao_depois.click()
    j.botao_concluir.click()
    t = _textos(j, 4)
    assert "mudança suspeita; repetir a medição" in t
    assert "nenhuma alteração do DSP é afirmada" in t
    assert "mudança detectada e reproduzida" not in t
    assert erros == []
    j.servico.b.fechar()



# --- JV-T251: manifesto incompleto não derruba a interface ---

def test_manifesto_incompleto_mostra_mensagem_e_a_janela_continua(qtbot, tmp_path):
    import json
    import shutil
    from jarvis.referencia.ref001 import PASTA_PADRAO
    janela, erros = _janela(qtbot, tmp_path / "d")
    copia = tmp_path / "caso"
    shutil.copytree(PASTA_PADRAO, copia)
    m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
    m.pop("medicoes")
    (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    janela.escolher_pasta = lambda: str(copia)
    janela.botao_comecar.click()
    janela._importar_outra()
    assert erros and "incompleto ou inválido" in erros[0] and "medicoes" in erros[0]
    assert not janela.servico.b.registros(janela.servico.sessao_id, "medicao")
    janela.botao_importar.click()                       # a mesma sessão ainda aceita o caso certo
    assert janela.servico.b.registros(janela.servico.sessao_id, "medicao")
    janela.servico.b.fechar()
