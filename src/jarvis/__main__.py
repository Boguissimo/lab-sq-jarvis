"""Ponto de entrada: ``python -m jarvis``."""

import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)
    app.setApplicationName("Lab SQ Jarvis")
    try:
        from jarvis.interface.janela import JanelaPrincipal
        from jarvis.persistencia import Banco
        from jarvis.sessao import Servico

        janela = JanelaPrincipal(Servico(Banco()))
    except Exception as erro:  # mostrar em linguagem simples em vez de fechar sem aviso
        QMessageBox.critical(None, "Lab SQ Jarvis",
                             f"O programa não conseguiu abrir.\n\nDetalhe técnico: {erro}\n\n"
                             "Mostre esta mensagem ao Claude.")
        return 1
    janela.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
