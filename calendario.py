import sys
import json
import os
import winreg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCalendarWidget,
    QPushButton, QTextEdit, QMessageBox, QLabel, QListWidget, QMenuBar, QMenu
)
from PyQt6.QtCore import QDate, Qt, QTimer
from PyQt6.QtGui import QTextCharFormat, QColor, QPixmap, QIcon, QAction

# Configuração para suporte a High DPI
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

# Nome do arquivo JSON para salvar eventos
EVENTS_FILE = "eventos.json"

# Feriados nacionais e estaduais do Rio de Janeiro em 2025
FERIADOS = {
    "2025-01-01": "Confraternização Universal",
    "2025-01-20": "Dia de São Sebastião (RJ)",
    "2025-03-04": "Carnaval",
    "2025-04-18": "Sexta-feira Santa",
    "2025-04-21": "Tiradentes",
    "2025-05-01": "Dia do Trabalhador",
    "2025-06-19": "Corpus Christi",
    "2025-07-23": "Dia do Estado do Rio de Janeiro (RJ)",
    "2025-09-07": "Independência do Brasil",
    "2025-10-12": "Nossa Senhora Aparecida",
    "2025-11-02": "Finados",
    "2025-11-15": "Proclamação da República",
    "2025-12-25": "Natal"
}

# Estilos CSS para Dark e Light Mode
# Estilos CSS para Dark e Light Mode
DARK_STYLE = """
    QWidget {
        background-color: #2E3440;
        color: #ECEFF4;
    }
    QCalendarWidget {
        background-color: #3B4252;
        color: #ECEFF4;
    }
    QCalendarWidget QWidget {
        alternate-background-color: #3B4252;
    }
    QCalendarWidget QToolButton {
        background-color: #4C566A;
        color: #ECEFF4;
        font-size: 14px;
        padding: 5px;
    }
    QCalendarWidget QMenu {
        background-color: #4C566A;
        color: #ECEFF4;
    }
    QCalendarWidget QSpinBox {
        background-color: #4C566A;
        color: #ECEFF4;
    }
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #3B4252;
        color: #ECEFF4;
        selection-background-color: #5E81AC;
        selection-color: #ECEFF4;
    }
    QCalendarWidget QAbstractItemView:disabled {
        background-color: #3B4252;
        color: #4C566A;
    }
    QTextEdit {
        background-color: #4C566A;
        color: #ECEFF4;
    }
    QPushButton {
        background-color: #5E81AC;
        color: #ECEFF4;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #81A1C1;
    }
    QListWidget {
        background-color: #4C566A;
        color: #ECEFF4;
    }
    QLabel {
        color: #ECEFF4;
    }
"""

LIGHT_STYLE = """
    QWidget {
        background-color: #F5F5F5;
        color: #000000;
    }
    QCalendarWidget {
        background-color: #FFFFFF;
        color: #000000;
    }
    QCalendarWidget QWidget {
        alternate-background-color: #FFFFFF;
    }
    QCalendarWidget QToolButton {
        background-color: #E0E0E0;
        color: #000000;
        font-size: 14px;
        padding: 5px;
    }
    QCalendarWidget QMenu {
        background-color: #E0E0E0;
        color: #000000;
    }
    QCalendarWidget QSpinBox {
        background-color: #E0E0E0;
        color: #000000;
    }
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #FFFFFF;
        color: #000000;
        selection-background-color: #BDBDBD;
        selection-color: #000000;
    }
    QCalendarWidget QAbstractItemView:disabled {
        background-color: #FFFFFF;
        color: #E0E0E0;
    }
    QTextEdit {
        background-color: #FFFFFF;
        color: #000000;
    }
    QPushButton {
        background-color: #E0E0E0;
        color: #000000;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #BDBDBD;
    }
    QListWidget {
        background-color: #FFFFFF;
        color: #000000;
    }
    QLabel {
        color: #000000;
    }
"""

class CalendarioEventos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendário de Eventos")
        self.setGeometry(100, 100, 600, 700)

        # Definir ícone da janela
        self.setWindowIcon(QIcon("icone.ico"))  # Substitua "icone.ico" pelo caminho do seu arquivo .ico

        # Layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Menu para alternar entre Dark e Light Mode
        self.criar_menu()

        # Adicionar logo
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap("logo.png").scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.logo)

        # Widget do Calendário
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)  # Remove números da semana
        self.calendario.clicked.connect(self.mostrar_evento)
        self.layout.addWidget(self.calendario)

        # Caixa de texto para eventos
        self.texto_evento = QTextEdit()
        self.layout.addWidget(self.texto_evento)

        # Botão para salvar evento
        self.botao_salvar = QPushButton("Salvar Evento")
        self.botao_salvar.clicked.connect(self.salvar_evento)
        self.layout.addWidget(self.botao_salvar)

        # Botão para apagar evento
        self.botao_apagar = QPushButton("Apagar Evento")
        self.botao_apagar.clicked.connect(self.apagar_evento)
        self.layout.addWidget(self.botao_apagar)

        # Lista de feriados
        self.lista_feriados = QListWidget()
        self.lista_feriados.setFixedHeight(150)
        self.layout.addWidget(QLabel("Feriados em 2025:"))
        self.layout.addWidget(self.lista_feriados)

        # Carregar eventos salvos
        self.eventos = self.carregar_eventos()

        # Destacar feriados e eventos
        self.destacar_dias()

        # Exibir feriados na lista
        self.exibir_feriados()

        # Verificar eventos ao iniciar
        self.verificar_eventos_hoje()

        # Configurar inicialização automática com o Windows
        self.configurar_inicializacao_automatica()

        # Definir tema padrão (Light Mode)
        self.definir_tema("Light")

    def criar_menu(self):
        """Cria um menu para alternar entre Dark e Light Mode."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        menu_tema = QMenu("Tema", self)
        menu_bar.addMenu(menu_tema)

        acao_dark = QAction("Dark Mode", self)
        acao_dark.triggered.connect(lambda: self.definir_tema("Dark"))
        menu_tema.addAction(acao_dark)

        acao_light = QAction("Light Mode", self)
        acao_light.triggered.connect(lambda: self.definir_tema("Light"))
        menu_tema.addAction(acao_light)

    def definir_tema(self, tema):
        """Aplica o tema selecionado (Dark ou Light)."""
        if tema == "Dark":
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def carregar_eventos(self):
        """Carrega eventos do arquivo JSON."""
        try:
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def salvar_eventos(self):
        """Salva eventos no arquivo JSON."""
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.eventos, f, indent=4, ensure_ascii=False)

    def mostrar_evento(self):
        """Exibe o evento do dia selecionado."""
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        evento = self.eventos.get(data_selecionada, "")
        self.texto_evento.setText(evento)

    def salvar_evento(self):
        """Salva um evento na data selecionada."""
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        evento_texto = self.texto_evento.toPlainText().strip()

        if evento_texto:
            self.eventos[data_selecionada] = evento_texto
        else:
            # Se o evento estiver em branco, remove a data do dicionário
            self.eventos.pop(data_selecionada, None)

        self.salvar_eventos()
        self.destacar_dias()
        QMessageBox.information(self, "Sucesso", f"Evento salvo para {data_selecionada}!")

    def apagar_evento(self):
        """Apaga o evento da data selecionada."""
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        if data_selecionada in self.eventos:
            self.eventos.pop(data_selecionada)
            self.salvar_eventos()
            self.destacar_dias()
            self.texto_evento.clear()
            QMessageBox.information(self, "Sucesso", f"Evento apagado para {data_selecionada}!")
        else:
            QMessageBox.warning(self, "Aviso", "Nenhum evento encontrado para esta data.")

    def destacar_dias(self):
        """Destaca os dias com eventos e feriados."""
        formato_evento = QTextCharFormat()
        formato_evento.setBackground(QColor(173, 216, 230))  # Azul claro para eventos

        formato_feriado = QTextCharFormat()
        formato_feriado.setBackground(QColor(144, 238, 144))  # Verde claro para feriados

        # Limpa formatações anteriores
        for ano in range(2025, 2026):
            for mes in range(1, 13):
                for dia in range(1, QDate(ano, mes, 1).daysInMonth() + 1):
                    data = QDate(ano, mes, dia)
                    self.calendario.setDateTextFormat(data, QTextCharFormat())

        # Destaca feriados
        for data_str in FERIADOS:
            data = QDate.fromString(data_str, "yyyy-MM-dd")
            self.calendario.setDateTextFormat(data, formato_feriado)

        # Destaca dias com eventos
        for data_str in self.eventos:
            data = QDate.fromString(data_str, "yyyy-MM-dd")
            self.calendario.setDateTextFormat(data, formato_evento)

    def exibir_feriados(self):
        """Exibe os feriados na lista."""
        self.lista_feriados.clear()
        for data_str, descricao in FERIADOS.items():
            data = QDate.fromString(data_str, "yyyy-MM-dd")
            self.lista_feriados.addItem(f"{data.toString('dd/MM/yyyy')}: {descricao}")

    def verificar_eventos_hoje(self):
        """Verifica se há eventos no dia atual e exibe um alerta."""
        hoje = QDate.currentDate().toString("yyyy-MM-dd")
        if hoje in self.eventos:
            QMessageBox.information(self, "Evento Hoje", f"Lembrete: {self.eventos[hoje]}")

    def configurar_inicializacao_automatica(self):
        """Configura o programa para iniciar automaticamente com o Windows."""
        chave = r"Software\Microsoft\Windows\CurrentVersion\Run"
        nome_programa = "dist/calendario.exe"
        caminho_programa = os.path.abspath(sys.argv[0])

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave, 0, winreg.KEY_WRITE) as reg_key:
                winreg.SetValueEx(reg_key, nome_programa, 0, winreg.REG_SZ, caminho_programa)
        except Exception as e:
            print(f"Erro ao configurar inicialização automática: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = CalendarioEventos()
    janela.show()
    sys.exit(app.exec())