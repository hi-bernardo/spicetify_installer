import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QProgressBar
from PyQt5.QtGui import QFontDatabase, QFont, QPalette, QColor, QCursor, QIcon
from PyQt5.QtCore import Qt, QTimer

class CustomButton(QPushButton):
    def __init__(self, texto, cor, fonte, parent=None):
        super().__init__(texto, parent)
        self.setFont(fonte)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor};
                color: white;
                border-radius: 5px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_brightness(cor, 1.4)};
                font-weight: bold;
            }}
        """)

    def adjust_brightness(self, color_hex, factor):
        color = QColor(color_hex)
        r = min(int(color.red() * factor), 255)
        g = min(int(color.green() * factor), 255)
        b = min(int(color.blue() * factor), 255)
        return f"rgb({r}, {g}, {b})"


class SpicetifyInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalador Spicetify")
        self.setFixedSize(400, 240)
        self.setWindowIcon(QIcon("src/icon.ico"))

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#212327"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.load_fonts()
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0

    def load_fonts(self):
        QFontDatabase.addApplicationFont("src/font/Inter-Variable.ttf")
        QFontDatabase.addApplicationFont("src/font/Montserrat-Bold.ttf")
        self.font_regular = QFont("Inter", 10)
        self.font_bold = QFont("Montserrat", 10, QFont.Bold)

    def init_ui(self):
        padding = 10
        full_width = self.width() - 2 * padding
        half_width = (self.width() - 3 * padding) // 2

        self.label_desinstalar = QLabel("DESINSTALAR", self)
        self.label_desinstalar.setFont(self.font_bold)
        self.label_desinstalar.setStyleSheet("color: white; font-size: 18px;")
        self.label_desinstalar.setGeometry(padding, 90, full_width, 30)
        self.label_desinstalar.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(padding, 180, full_width, 30)
        self.progress.setValue(0)
        self.progress.setFont(self.font_bold)
        self.progress.setVisible(False)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #363636;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background-color: #00c853;
                margin: 0px;
            }
        """)

        self.label_autor = QLabel("by oBrazoo", self)
        self.label_autor.setGeometry(8, self.height() - 20, 100, 15)
        self.label_autor.setStyleSheet("color: gray; font-size: 10px;")

        self.btn_instalar = CustomButton("INSTALAR SPICETIFY", "#0085eb", self.font_bold, self)
        self.btn_instalar.setGeometry(padding, 20, full_width, 40)
        self.btn_instalar.clicked.connect(self.simular_instalacao)

        self.btn_desinst_spicetify = CustomButton("SPICETIFY", "#D32F2F", self.font_regular, self)
        self.btn_desinst_spicetify.setGeometry(padding, 120, half_width, 40)
        self.btn_desinst_spicetify.clicked.connect(lambda: self.simular_acao("SPICETIFY"))

        self.btn_desinst_spotify = CustomButton("SPOTIFY", "#D32F2F", self.font_regular, self)
        self.btn_desinst_spotify.setGeometry(padding * 2 + half_width, 120, half_width, 40)
        self.btn_desinst_spotify.clicked.connect(lambda: self.simular_acao("SPOTIFY"))

    def simular_instalacao(self):
        self.acao = "INSTALANDO"
        self.start_progress_animation()

    # def simular_acao(self, nome):
    #     self.acao = f"DESINSTALANDO {nome}"
    #     self.start_progress_animation()

    def start_progress_animation(self):
        self.progress.setValue(0)
        self.progress.setVisible(True)

        self.progress_value = 0
        self.timer.start(30)

    def update_progress(self):
        if self.progress_value >= 100:
            self.timer.stop()
            self.progress.setVisible(False)
        else:
            self.progress_value += 1
            self.progress.setValue(self.progress_value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpicetifyInstaller()
    window.show()
    sys.exit(app.exec_())
