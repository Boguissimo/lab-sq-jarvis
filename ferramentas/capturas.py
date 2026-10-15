"""Gera capturas de tela do percurso do JV-V01 (uso do desenvolvimento; não faz parte do programa).

Uso: QT_QPA_PLATFORM=offscreen python ferramentas/capturas.py docs/capturas
"""

import sys
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication

from jarvis.interface.janela import JanelaPrincipal
from jarvis.persistencia import Banco
from jarvis.sessao import Servico


def main(destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication(sys.argv)
    with tempfile.TemporaryDirectory() as tmp:
        janela = JanelaPrincipal(Servico(Banco(Path(tmp))))
        janela.resize(1280, 900)
        janela.show()

        def foto(nome: str) -> None:
            for _ in range(3):
                app.processEvents()
            janela.grab().save(str(destino / f"{nome}.png"))

        foto("1-percepcao")
        janela.botao_comecar.click()
        janela.botao_importar.click()
        foto("2-medicoes")
        janela.botao_analisar.click()
        foto("3-dados-sugerem")
        pagina = janela.paginas[2]
        pagina.verticalScrollBar().setValue(pagina.verticalScrollBar().maximum())
        foto("3b-indicios-e-hipoteses")
        janela.botao_propor.click()
        foto("4-teste-proposto")
        pagina = janela.paginas[3]
        pagina.verticalScrollBar().setValue(pagina.verticalScrollBar().maximum())
        foto("4b-receita-e-reversao")
        janela.botao_aplicar.click()
        janela.botao_depois.click()
        janela.botao_concluir.click()
        foto("5-veredito")
        janela.botao_manter.click()
        janela._ir_para(5)
        janela.lista.setCurrentRow(5)
        foto("6-historico")
        janela.servico.b.fechar()


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "docs/capturas"))
