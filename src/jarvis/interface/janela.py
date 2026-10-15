"""Janela principal do JV-V01: sessão guiada em cinco passos e histórico.

A interface não calcula nada (ADR-03): mostra o que ``Servico`` devolve. O aviso de demonstração com
dados simulados fica sempre visível.
"""

from __future__ import annotations

import html
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QSizePolicy, QAbstractItemView, QButtonGroup, QDialog, QFileDialog, QGroupBox, QHBoxLayout, QHeaderView,
    QInputDialog, QLabel, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit,
    QPushButton, QRadioButton, QScrollArea, QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem,
    QTextBrowser, QVBoxLayout, QWidget,
)

from jarvis import INCREMENTO, VERSAO, regras
from jarvis.referencia.ref001 import PASTA_PADRAO
from jarvis.rew_texto import FormatoInvalido
from jarvis.sessao import AVISO_SIMULADO, CRITERIO_ACEITE, ErroDoPercurso, Servico

pg.setConfigOptions(background="w", foreground="#222222", antialias=True)

CORES = {
    "via_a_antes": "#1f5fbf",      # médio
    "via_b_antes": "#d9822b",      # tweeter
    "soma_antes": "#b3261e",       # soma medida
    "previsao": "#2e7d32",         # previsão
    "soma_depois": "#00796b",      # depois
}
PASSOS = [
    "1. O que estou percebendo",
    "2. O que preciso medir",
    "3. O que os dados sugerem",
    "4. Qual passo dar",
    "5. O que mudou",
    "Histórico",
]


MARCAS_HZ = [(20, "20"), (50, "50"), (100, "100"), (200, "200"), (500, "500"), (1000, "1 k"),
             (2000, "2 k"), (3000, "3 k"), (5000, "5 k"), (10000, "10 k"), (20000, "20 k")]


def _fmt(x: float, casas: int = 1) -> str:
    if abs(x) < 0.5 * 10 ** -casas:
        x = 0.0
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def _titulo(texto: str) -> QLabel:
    rotulo = QLabel(texto)
    fonte = QFont()
    fonte.setPointSize(15)
    fonte.setBold(True)
    rotulo.setFont(fonte)
    return rotulo


def _texto(texto: str) -> QLabel:
    rotulo = QLabel(texto)
    rotulo.setWordWrap(True)
    rotulo.setTextFormat(Qt.RichText)
    return rotulo


def _caixa(texto: str, fundo: str, borda: str) -> QLabel:
    """Texto em uma caixa contínua, com cores que combinam com o tema escuro."""
    rotulo = _texto(texto)
    rotulo.setStyleSheet(f"background:{fundo}; border-left:4px solid {borda}; "
                         "border-radius:4px; padding:10px 14px;")
    return rotulo


def _grafico(titulo: str, rotulo_y: str, log_x: bool = True) -> pg.PlotWidget:
    g = pg.PlotWidget(title=titulo)
    g.setLogMode(x=log_x, y=False)
    g.showGrid(x=True, y=True, alpha=0.25)
    g.setLabel("bottom", "Frequência (Hz)")
    if log_x:
        g.getAxis("bottom").setTicks([[(float(np.log10(f)), t) for f, t in MARCAS_HZ], []])
    g.setLabel("left", rotulo_y)
    g.addLegend(offset=(10, -10))  # canto inferior esquerdo, livre nestes gráficos
    g.setMinimumHeight(260)
    return g


def _curva(grafico: pg.PlotWidget, curva: dict, cor: str, tracejada: bool = False, largura: int = 2) -> None:
    caneta = pg.mkPen(cor, width=largura, style=Qt.DashLine if tracejada else Qt.SolidLine)
    grafico.plot(curva["freq_hz"], curva["nivel_db"], pen=caneta, name=curva["rotulo"])


class Pagina(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.conteudo = QWidget()
        self.layout_ = QVBoxLayout(self.conteudo)
        self.layout_.setContentsMargins(24, 18, 24, 18)
        self.layout_.setSpacing(12)
        self.setWidget(self.conteudo)

    def limpar(self) -> None:
        def esvaziar(layout) -> None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    widget.deleteLater()  # seguro mesmo para o botão que disparou a ação
                elif item.layout():
                    esvaziar(item.layout())
                    item.layout().deleteLater()
        esvaziar(self.layout_)


class JanelaPrincipal(QMainWindow):
    def __init__(self, servico: Servico):
        super().__init__()
        self.servico = servico
        self.setWindowTitle(f"Lab SQ Jarvis — {INCREMENTO} (demonstração com dados simulados)")
        self.resize(1280, 860)
        # funções substituíveis nos testes automatizados
        self.pedir_texto = lambda titulo, rotulo: QInputDialog.getMultiLineText(self, titulo, rotulo)
        self.escolher_pasta = lambda: QFileDialog.getExistingDirectory(self, "Pasta do caso de referência")
        self.mostrar_erro = lambda msg: QMessageBox.warning(self, "Lab SQ Jarvis", msg)

        central = QWidget()
        raiz = QVBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        self.aviso = QLabel(f"⚠  {AVISO_SIMULADO}")
        self.aviso.setWordWrap(True)
        self.aviso.setStyleSheet("background:#fff3c4; color:#4a3b00; padding:10px 16px; "
                                 "font-weight:bold; border-bottom:1px solid #e0c96b;")
        self.aviso.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        raiz.addWidget(self.aviso)

        divisor = QSplitter()
        self.lista = QListWidget()
        self.lista.setMaximumWidth(260)
        self.lista.setStyleSheet("QListWidget{font-size:13px;} QListWidget::item{padding:10px;}")
        for nome in PASSOS:
            self.lista.addItem(QListWidgetItem(nome))
        self.lista.currentRowChanged.connect(self._ir_para)
        self.pilha = QStackedWidget()
        self.paginas = [Pagina() for _ in PASSOS]
        for p in self.paginas:
            self.pilha.addWidget(p)
        divisor.addWidget(self.lista)
        divisor.addWidget(self.pilha)
        divisor.setStretchFactor(1, 1)
        raiz.addWidget(divisor, 1)
        self.setCentralWidget(central)
        self.statusBar().showMessage(
            f"Versão {VERSAO} · {INCREMENTO} · dados guardados em {self.servico.b.pasta}")
        self.atualizar(ir_para=5 if self.servico.listar_sessoes() else 0)

    # ------------------------------------------------------------ navegação
    def _estado(self) -> dict | None:
        return self.servico.estado() if self.servico.sessao_id is not None else None

    def _passo_maximo(self, e: dict | None) -> int:
        if e is None:
            return 0
        if e["experimento"]:
            return 4
        if e["analise"]:
            return 3
        if e["medicoes"]:
            return 2
        return 1

    def _ir_para(self, linha: int) -> None:
        if linha < 0:
            return
        self.pilha.setCurrentIndex(linha)

    def atualizar(self, ir_para: int | None = None) -> None:
        e = self._estado()
        maximo = self._passo_maximo(e)
        for i in range(5):
            item = self.lista.item(i)
            habilitado = i <= maximo
            item.setFlags((Qt.ItemIsEnabled | Qt.ItemIsSelectable) if habilitado else Qt.NoItemFlags)
        self._montar_percepcao(e)
        self._montar_medir(e)
        self._montar_dados(e)
        self._montar_passo(e)
        self._montar_mudou(e)
        self._montar_historico()
        destino = maximo if ir_para is None else ir_para
        self.lista.setCurrentRow(destino)
        self.pilha.setCurrentIndex(destino)

    def _executar(self, acao, ir_para: int | None = None) -> bool:
        try:
            acao()
        except (ErroDoPercurso, FormatoInvalido) as erro:
            self.mostrar_erro(str(erro))
            return False
        self.atualizar(ir_para)
        return True

    def _encerrada(self, e: dict | None) -> bool:
        return bool(e) and e["sessao"]["estado"] == "encerrada"

    # ------------------------------------------------------------ passo 1
    def _montar_percepcao(self, e: dict | None) -> None:
        p = self.paginas[0]
        p.limpar()
        L = p.layout_
        L.addWidget(_titulo("1. O que estou percebendo"))
        L.addWidget(_texto(
            "Escolha o tipo de sessão e registre o que você percebe. Neste incremento só existe o caso "
            "<b>simulado</b> REF-001-A: não há escuta real, por isso a percepção vem marcada como "
            "<b>não aplicável</b>. Se quiser exercitar o registro, use “simulada” — ela fica rotulada como tal."))
        if e:
            L.addWidget(_texto(f"<b>Sessão {e['sessao']['id']}</b> em andamento "
                               f"(modo: investigação; criada em {e['sessao']['criada_em'][:16]})."))
            for pr in e["percepcoes"]:
                L.addWidget(_texto(f"Percepção {pr['dados']['momento']} — <i>{pr['dados']['origem']}</i>: "
                                   f"{html.escape(pr['dados']['descricao'])} [{pr['id']}]"))
            L.addStretch()
            return

        caixa = QGroupBox("Tipo de sessão")
        cl = QVBoxLayout(caixa)
        self.modo_queixa = QRadioButton("Investigação de uma queixa")
        self.modo_queixa.setChecked(True)
        modo_cal = QRadioButton("Calibração do sistema — disponível a partir do incremento JV-V04")
        modo_cal.setEnabled(False)
        cl.addWidget(self.modo_queixa)
        cl.addWidget(modo_cal)
        L.addWidget(caixa)

        caixa2 = QGroupBox("Percepção antes")
        c2 = QVBoxLayout(caixa2)
        grupo = QButtonGroup(caixa2)
        self.perc_na = QRadioButton("Não aplicável — caso simulado, sem escuta (recomendado)")
        self.perc_sim = QRadioButton("Simulada — exercício de registro, marcada como simulada")
        self.perc_na.setChecked(True)
        grupo.addButton(self.perc_na)
        grupo.addButton(self.perc_sim)
        self.perc_texto = QPlainTextEdit()
        self.perc_texto.setPlaceholderText("Ex.: vozes sem corpo na região dos médios-agudos (exercício)")
        self.perc_texto.setMaximumHeight(80)
        c2.addWidget(self.perc_na)
        c2.addWidget(self.perc_sim)
        c2.addWidget(self.perc_texto)
        L.addWidget(caixa2)

        self.botao_comecar = QPushButton("Começar a sessão")
        self.botao_comecar.setMinimumHeight(36)
        self.botao_comecar.clicked.connect(self._comecar)
        L.addWidget(self.botao_comecar)
        L.addStretch()

    def _comecar(self) -> None:
        def acao():
            self.servico.nova_sessao("investigacao")
            if self.perc_sim.isChecked():
                self.servico.registrar_percepcao("antes", "simulada", self.perc_texto.toPlainText())
            else:
                self.servico.registrar_percepcao("antes", "não aplicável")
        self._executar(acao, ir_para=1)

    # ------------------------------------------------------------ passo 2
    def _montar_medir(self, e: dict | None) -> None:
        p = self.paginas[1]
        p.limpar()
        L = p.layout_
        L.addWidget(_titulo("2. O que preciso medir"))
        L.addWidget(_texto(
            "Para investigar o cruzamento entre médio e tweeter são necessárias três medições, na mesma "
            "posição de microfone e com a <b>mesma referência temporal</b>: o médio sozinho, o tweeter "
            "sozinho e os dois juntos. Sem referência temporal comum, a fase entre as vias não pode ser "
            "comparada. O caso REF-001-A traz essas três medições, <b>simuladas</b>."))
        if e and not e["medicoes"] and not self._encerrada(e):
            linha = QHBoxLayout()
            self.botao_importar = QPushButton("Importar o caso REF-001-A (dados simulados)")
            self.botao_importar.setMinimumHeight(36)
            self.botao_importar.clicked.connect(
                lambda: self._executar(lambda: self.servico.importar_caso(PASTA_PADRAO), ir_para=1))
            outra = QPushButton("Escolher outra pasta de caso…")
            outra.clicked.connect(self._importar_outra)
            linha.addWidget(self.botao_importar)
            linha.addWidget(outra)
            L.addLayout(linha)
        if e and e["medicoes"]:
            tabela = QTableWidget(len(e["medicoes"]), 4)
            tabela.setHorizontalHeaderLabels(["Registro", "Medição", "Arquivo", "Verificação de qualidade"])
            tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for i, m in enumerate(e["medicoes"]):
                q = m.get("qualidade") or {}
                lista = q.get("itens", [])
                detalhe = "\n".join(("✓ " if it["ok"] else "✗ ") + it["item"] for it in lista)
                resumo = (("✓ aprovada" if q.get("aprovada") else "✗ reprovada")
                          + f" — {sum(it['ok'] for it in lista)} de {len(lista)} itens (passe o mouse)")
                valores = [m["id"], m["dados"].get("descricao", ""), m["dados"]["arquivo"]
                           + (" (simulada)" if m["dados"].get("simulado") else ""), resumo]
                for j, v in enumerate(valores):
                    celula = QTableWidgetItem(v)
                    if j == 3:
                        celula.setToolTip(detalhe)
                    tabela.setItem(i, j, celula)
            tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            tabela.horizontalHeader().setStretchLastSection(True)
            tabela.setMinimumHeight(170)
            L.addWidget(tabela)
            conf = e["configuracoes"][0] if e["configuracoes"] else None
            if conf:
                linhas = "".join(f"<li>{html.escape(pp['canal'])} — {html.escape(pp['parametro'])}: "
                                 f"{html.escape(pp['valor'])} <i>(origem: {pp['origem']})</i></li>"
                                 for pp in conf["parametros"])
                L.addWidget(_texto(f"<b>Configuração do DSP — {html.escape(conf['nome'])}</b> "
                                   f"(nível de confiança: <b>{conf['nivel']}</b>)<ul>{linhas}</ul>"))
            if not e["analise"] and not self._encerrada(e):
                self.botao_analisar = QPushButton("Analisar as medições")
                self.botao_analisar.setMinimumHeight(36)
                self.botao_analisar.clicked.connect(lambda: self._executar(self.servico.analisar, ir_para=2))
                L.addWidget(self.botao_analisar)
        L.addStretch()

    def _importar_outra(self) -> None:
        pasta = self.escolher_pasta()
        if pasta:
            self._executar(lambda: self.servico.importar_caso(Path(pasta)), ir_para=1)

    # ------------------------------------------------------------ passo 3
    def _montar_dados(self, e: dict | None) -> None:
        p = self.paginas[2]
        p.limpar()
        L = p.layout_
        L.addWidget(_titulo("3. O que os dados sugerem"))
        if not e or not e["analise"]:
            L.addWidget(_texto("A análise aparece depois de importar as medições."))
            L.addStretch()
            return
        a = e["analise"]
        g = _grafico("Resposta em frequência (dados simulados)", "Nível (dB)")
        for chave in ("via_a_antes", "via_b_antes", "soma_antes"):
            if chave in e["curvas"]:
                _curva(g, e["curvas"][chave], CORES[chave], largura=3 if chave == "soma_antes" else 2)
        g.setYRange(10, 92)
        L.addWidget(g)
        if a["fase"]:
            gf = _grafico("Diferença de fase médio − tweeter na sobreposição", "Graus")
            gf.plot(a["fase"]["freq_hz"], a["fase"]["diferenca_graus"],
                    pen=pg.mkPen("#6a1b9a", width=2), name=f"diferença de fase [{a['ids']['fase']}]")
            gf.setYRange(-200, 200)
            gf.setMinimumHeight(200)
            L.addWidget(gf)

        partes = ["<p><b>Como esta explicação foi feita:</b> por "
                  "regras implementadas no programa, a partir dos cálculos indicados entre colchetes — "
                  "não por IA. Os limiares das regras são <b>provisórios</b> e só foram testados em casos "
                  "simulados.</p>"]
        ref = a["referencia"]
        partes.append("<p><b>Referência temporal:</b> " + (
            "compatível entre as três medições — a fase pode ser comparada."
            if ref["compativel"] else html.escape(a.get("aviso_referencia", ""))) + "</p>")
        if e["indicios"]:
            partes.append("<h3>Indícios</h3>")
            for ind in e["indicios"]:
                partes.append(f"<p><b>{html.escape(ind['titulo'])}</b> <i>({ind['dados']['regra']}; "
                              f"registro {ind['id']})</i><br>{html.escape(ind['dados']['explicacao'])}</p>")
        if e["hipoteses"]:
            partes.append("<h3>Hipóteses, em ordem</h3><ol>")
            for h in e["hipoteses"]:
                d = h["dados"]
                partes.append(f"<li><b>{html.escape(d['enunciado'])}</b> — {d['avaliacao']} "
                              f"<i>[{h['id']}]</i><br>{html.escape(d['por_que'])}<br>"
                              f"<i>Confirmaria:</i> {html.escape(d['confirmaria'])}<br>"
                              f"<i>Refutaria:</i> {html.escape(d['refutaria'])}</li>")
            partes.append("</ol>")
        partes.append(f"<p><b>Próximo passo sugerido pelas regras:</b> {html.escape(a['motivo'])}</p>")
        lim = regras.LIMIARES
        partes.append(
            "<p style='color:#9a9a9a'><small>Limiares provisórios: vias a até "
            f"{_fmt(lim['sobreposicao_max_diferenca_db'], 0)} dB uma da outra; cancelamento quando a soma fica "
            f"{_fmt(lim['cancelamento_min_db'], 0)} dB ou mais abaixo da soma de energias; oposição quando a média "
            f"da diferença de fase passa de {_fmt(lim['oposicao_media_min_graus'], 0)}° com variação de até "
            f"{_fmt(lim['oposicao_dispersao_max_graus'], 0)}°.</small></p>")
        caixa = QTextBrowser()
        caixa.setHtml("".join(partes))
        caixa.setMinimumHeight(380)
        L.addWidget(caixa)
        detalhes = QPushButton("Ver a cadeia por trás desta análise")
        detalhes.clicked.connect(self._mostrar_cadeia)
        L.addWidget(detalhes)

    def _mostrar_cadeia(self) -> None:
        sid = self.servico.sessao_id
        b = self.servico.b
        linhas = []
        for tipo in ("percepcao", "medicao", "calculo", "indicio", "hipotese", "recomendacao",
                     "experimento", "conclusao", "decisao"):
            for r in b.registros(sid, tipo):
                origens = ", ".join(f"{o['origem']} ({o['papel']})" for o in b.origens_de(r["id"]))
                linhas.append(f"<tr><td>{r['id']}</td><td>{tipo}</td><td>{html.escape(r['titulo'])}</td>"
                              f"<td>{origens or '—'}</td><td>{r['autor']}</td></tr>")
        problemas = b.integridade()
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Cadeia de conhecimento da sessão")
        dialogo.resize(980, 600)
        lay = QVBoxLayout(dialogo)
        t = QTextBrowser()
        t.setHtml("<p>Cada registro aponta para os registros de que deriva. Rotina de integridade: "
                  + ("<b>sem problemas</b>." if not problemas else "<b>" + html.escape("; ".join(problemas)) + "</b>")
                  + "</p><table border='1' cellpadding='4' cellspacing='0'><tr><th>Registro</th><th>Tipo</th>"
                  "<th>Título</th><th>Deriva de</th><th>Autor</th></tr>" + "".join(linhas) + "</table>")
        lay.addWidget(t)
        dialogo.show()
        self._dialogo_cadeia = dialogo

    # ------------------------------------------------------------ passo 4
    def _montar_passo(self, e: dict | None) -> None:
        p = self.paginas[3]
        p.limpar()
        L = p.layout_
        L.addWidget(_titulo("4. Qual passo dar"))
        if not e or not e["analise"]:
            L.addWidget(_texto("O próximo passo aparece depois da análise."))
            L.addStretch()
            return
        a = e["analise"]
        rec = e["recomendacao"]
        encerrada = self._encerrada(e)
        if a["sugestao"] == "teste_polaridade" and rec is None and not encerrada:
            L.addWidget(_texto("As regras sugerem um <b>teste de diagnóstico</b>: uma única alteração, "
                               "reversível, com o resultado previsto antes de aplicar."))
            self.botao_propor = QPushButton("Ver o teste proposto")
            self.botao_propor.setMinimumHeight(36)
            self.botao_propor.clicked.connect(lambda: self._executar(self.servico.propor_teste, ir_para=3))
            L.addWidget(self.botao_propor)
        if rec:
            d = rec["dados"]
            g = _grafico("Soma medida e soma prevista após o teste", "Nível (dB)")
            _curva(g, e["curvas"]["soma_antes"], CORES["soma_antes"], largura=3)
            _curva(g, e["curvas"]["previsao"], CORES["previsao"], tracejada=True, largura=3)
            g.setYRange(10, 92)
            L.addWidget(g)
            seg = d["seguranca"]
            receita = "".join(f"<li>{html.escape(r)}</li>" for r in d["receita"])
            rev = d["reversao"]
            c = d["criterio"]
            L.addWidget(_texto(
                f"<h3>{html.escape(rec['titulo'])}</h3>"
                f"<p><b>Tipo:</b> teste de diagnóstico — uma variável. <b>Hipótese testada:</b> {d['hipotese']}.</p>"
                f"<p><b>Previsão (calculada antes):</b> {html.escape(d['previsao_resumo'])}</p>"
                f"<p><b>Critério de aceite (provisório):</b> diferença RMS até {_fmt(c['rms_max_db'])} dB e máxima "
                f"até {_fmt(c['max_abs_db'])} dB entre {_fmt(c['faixa_hz'][0] / 1000, 0)} e "
                f"{_fmt(c['faixa_hz'][1] / 1000, 0)} kHz, e o nível no vale subir pelo menos "
                f"{_fmt(c['aumento_vale_min_db'], 0)} dB.</p>"
                f"<p><b>Segurança:</b> classe <b>{seg['classe']}</b>. {html.escape(seg['motivo'])} "
                + " ".join(f"{r['regra']}: {html.escape(r['resultado'])}." for r in seg["regras"]) + "</p>"
                f"<p><b>Receita:</b></p><ol>{receita}</ol>"
                f"<p><b>Reversão:</b> {'garantida' if rev['garantida'] else 'NÃO garantida'} — "
                f"{html.escape(rev['base'])}.</p>"))
            if e["experimento"] is None and not encerrada:
                self.botao_aplicar = QPushButton(
                    "Registrar: apliquei o teste (no caso simulado, considere aplicado)")
                self.botao_aplicar.setMinimumHeight(36)
                self.botao_aplicar.clicked.connect(
                    lambda: self._executar(self.servico.registrar_aplicacao, ir_para=4))
                L.addWidget(self.botao_aplicar)
            elif e["experimento"]:
                L.addWidget(_texto(f"<b>Teste registrado</b> em {e['experimento']['dados']['aplicado_em'][:16]} "
                                   f"[{e['experimento']['id']}]. Siga para “5. O que mudou”."))
        if not encerrada and e["experimento"] is None:
            caixa = QGroupBox("Decidir sem intervir")
            cl = QVBoxLayout(caixa)
            cl.addWidget(_texto("Se os dados e a sua percepção não justificam mudar nada, ou se falta "
                                "informação, registre a decisão com a sua justificativa. Ela não cria "
                                "experimento e não é uma conclusão experimental."))
            linha = QHBoxLayout()
            self.botao_nada = QPushButton("Nada a alterar")
            self.botao_dados = QPushButton("Solicitar dados adicionais")
            self.botao_nada.clicked.connect(lambda: self._sem_intervencao("nada_a_alterar"))
            self.botao_dados.clicked.connect(lambda: self._sem_intervencao("solicitar_dados"))
            linha.addWidget(self.botao_nada)
            linha.addWidget(self.botao_dados)
            cl.addLayout(linha)
            L.addWidget(caixa)
        for dec in e["decisoes"]:
            if dec["dados"].get("sem_intervencao"):
                L.addWidget(_texto(f"<b>Decisão registrada: {html.escape(dec['titulo'])}</b> [{dec['id']}] — "
                                   f"{html.escape(dec['dados']['fundamentacao'])}"))
        L.addStretch()

    def _sem_intervencao(self, tipo: str) -> None:
        titulo = "Nada a alterar" if tipo == "nada_a_alterar" else "Solicitar dados adicionais"
        texto, ok = self.pedir_texto(titulo, "Fundamentação (obrigatória):")
        if ok:
            self._executar(lambda: self.servico.decidir_sem_intervencao(tipo, texto), ir_para=3)

    # ------------------------------------------------------------ passo 5
    def _montar_mudou(self, e: dict | None) -> None:
        p = self.paginas[4]
        p.limpar()
        L = p.layout_
        L.addWidget(_titulo("5. O que mudou"))
        if not e or not e["experimento"]:
            L.addWidget(_texto("Esta etapa aparece depois de registrar o teste."))
            L.addStretch()
            return
        encerrada = self._encerrada(e)
        if e["comparacao"] is None:
            L.addWidget(_texto("Meça de novo nas mesmas condições e importe a medição “depois”. "
                               "No caso simulado, ela já vem pronta."))
            self.botao_depois = QPushButton("Importar a medição “depois” do caso REF-001-A")
            self.botao_depois.setMinimumHeight(36)
            self.botao_depois.clicked.connect(lambda: self._executar(self.servico.importar_depois, ir_para=4))
            L.addWidget(self.botao_depois)
            L.addStretch()
            return
        g = _grafico("Antes, previsto e depois (dados simulados)", "Nível (dB)")
        _curva(g, e["curvas"]["soma_antes"], CORES["soma_antes"], largura=2)
        _curva(g, e["curvas"]["previsao"], CORES["previsao"], tracejada=True, largura=3)
        _curva(g, e["curvas"]["soma_depois"], CORES["soma_depois"], largura=2)
        g.setYRange(10, 92)
        L.addWidget(g)
        r = e["comparacao"]["dados"]["resultado"]
        L.addWidget(_texto(
            f"<p><b>Comparação [{e['comparacao']['id']}]:</b> entre 1 e 10 kHz, a medição depois ficou a "
            f"{_fmt(r['rms_db'], 3)} dB (RMS) da previsão, máximo {_fmt(r['max_abs_db'], 3)} dB. Em "
            f"{_fmt(r['vale_freq_hz'], 0)} Hz o nível passou de {_fmt(r['nivel_vale_antes_db'])} dB para "
            f"{_fmt(r['nivel_vale_depois_db'])} dB.</p>"))
        if e["conclusao"] is None and not encerrada:
            caixa = QGroupBox("Percepção depois")
            cl = QVBoxLayout(caixa)
            grupo = QButtonGroup(caixa)
            self.depois_na = QRadioButton("Não aplicável — caso simulado, sem escuta (recomendado)")
            self.depois_sim = QRadioButton("Simulada — exercício de registro")
            self.depois_na.setChecked(True)
            grupo.addButton(self.depois_na)
            grupo.addButton(self.depois_sim)
            self.depois_texto = QPlainTextEdit()
            self.depois_texto.setMaximumHeight(70)
            cl.addWidget(self.depois_na)
            cl.addWidget(self.depois_sim)
            cl.addWidget(self.depois_texto)
            self.botao_concluir = QPushButton("Registrar a percepção e ver o veredito")
            self.botao_concluir.setMinimumHeight(36)
            self.botao_concluir.clicked.connect(self._concluir)
            cl.addWidget(self.botao_concluir)
            L.addWidget(caixa)
        if e["conclusao"]:
            d = e["conclusao"]["dados"]
            fundo, borda = {"confirmada": ("#1e3326", "#4caf50"),
                            "refutada": ("#3a2121", "#e57373")}.get(d["veredito"], ("#2c2c2c", "#9e9e9e"))
            L.addWidget(_caixa(
                f"<h3 style='margin:0 0 6px 0'>Veredito: hipótese {d['veredito']}</h3>"
                f"<p>{html.escape(d['motivo'])}</p><p><b>Incerteza:</b> {html.escape(d['incerteza'])}</p>"
                f"<p style='margin-bottom:0'><b>Limite:</b> {html.escape(d['limite'])}</p>", fundo, borda))
            decisoes = [x for x in e["decisoes"] if not x["dados"].get("sem_intervencao")]
            if not decisoes and not encerrada:
                linha = QHBoxLayout()
                self.botao_manter = QPushButton("Manter a alteração")
                self.botao_reverter = QPushButton("Reverter a alteração")
                self.botao_manter.clicked.connect(lambda: self._executar(lambda: self.servico.decidir("manter"), ir_para=4))
                self.botao_reverter.clicked.connect(lambda: self._executar(lambda: self.servico.decidir("reverter"), ir_para=4))
                linha.addWidget(self.botao_manter)
                linha.addWidget(self.botao_reverter)
                L.addLayout(linha)
            for dec in decisoes:
                texto = f"<b>Decisão: {html.escape(dec['titulo'])}</b> [{dec['id']}]"
                rev = dec["dados"].get("reversao")
                if rev:
                    if rev["garantida"]:
                        texto += "<p>Receita para reverter:</p><ol>" + "".join(
                            f"<li>{html.escape(x)}</li>" for x in rev["receita_inversa"]) + "</ol>"
                    else:
                        texto += f"<p><b>{html.escape(rev['base'])}</b></p>"
                L.addWidget(_texto(texto))
        if encerrada:
            L.addWidget(_caixa(f"<b>Resumo da sessão:</b> {html.escape(e['sessao']['resumo'] or '')}",
                               "#2c2c2c", "#9e9e9e"))
        L.addStretch()

    def _concluir(self) -> None:
        def acao():
            if self.depois_sim.isChecked():
                self.servico.registrar_percepcao("depois", "simulada", self.depois_texto.toPlainText())
            else:
                self.servico.registrar_percepcao("depois", "não aplicável")
            self.servico.concluir()
        self._executar(acao, ir_para=4)

    # ------------------------------------------------------------ histórico
    def _montar_historico(self) -> None:
        p = self.paginas[5]
        p.limpar()
        L = p.layout_
        L.addWidget(_titulo("Histórico"))
        sessoes = self.servico.listar_sessoes()
        L.addWidget(_texto("Sessões guardadas neste computador. Abra uma para ver tudo o que foi feito "
                           "ou continuar de onde parou."))
        self.tabela_hist = QTableWidget(len(sessoes), 5)
        self.tabela_hist.setHorizontalHeaderLabels(["Sessão", "Criada em", "Caso", "Estado", "Encerramento"])
        self.tabela_hist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela_hist.setSelectionBehavior(QAbstractItemView.SelectRows)
        for i, s in enumerate(sessoes):
            for j, v in enumerate([str(s["id"]), s["criada_em"][:16].replace("T", " "), s["caso"] or "—",
                                   s["estado"], s["encerramento"] or "—"]):
                self.tabela_hist.setItem(i, j, QTableWidgetItem(v))
        self.tabela_hist.horizontalHeader().setStretchLastSection(True)
        self.tabela_hist.setMinimumHeight(260)
        if sessoes:
            self.tabela_hist.selectRow(0)
        L.addWidget(self.tabela_hist)
        linha = QHBoxLayout()
        self.botao_abrir = QPushButton("Abrir a sessão selecionada")
        self.botao_abrir.clicked.connect(self._abrir_selecionada)
        self.botao_nova = QPushButton("Começar uma nova sessão")
        self.botao_nova.clicked.connect(self._nova)
        linha.addWidget(self.botao_abrir)
        linha.addWidget(self.botao_nova)
        L.addLayout(linha)
        L.addStretch()

    def _abrir_selecionada(self) -> None:
        linha = self.tabela_hist.currentRow()
        if linha < 0:
            return
        sid = int(self.tabela_hist.item(linha, 0).text())
        self._executar(lambda: self.servico.abrir_sessao(sid), ir_para=None)

    def _nova(self) -> None:
        self.servico.sessao_id = None
        self.atualizar(ir_para=0)
