import sys
import requests
import os
import pyperclip
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QProgressBar, QMessageBox
)
from PyQt5.QtGui import QFontDatabase, QFont, QPalette, QColor, QCursor, QIcon
from PyQt5.QtCore import Qt, QTimer


class CustomButton(QPushButton):
    def __init__(self, texto, cor, fonte, parent=None):
        super().__init__(texto, parent)
        self.setFont(fonte)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(
            f"""
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
        """
            )

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
        self.setFixedSize(400, 260)
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
        self.progress.setStyleSheet(
            """
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
                    """
            )

        self.label_autor = QLabel("by oBrazoo", self)
        self.label_autor.setGeometry(8, self.height() - 20, 100, 15)
        self.label_autor.setStyleSheet("color: gray; font-size: 10px;")

        self.btn_instalar = CustomButton("INSTALAR SPICETIFY", "#0085eb", self.font_bold, self)
        self.btn_instalar.setGeometry(padding, 20, full_width, 40)
        self.btn_instalar.clicked.connect(self.instalar_spotify_spicetify)

        self.btn_uns_spicetify = CustomButton("SPICETIFY", "#D32F2F", self.font_regular, self)
        self.btn_uns_spicetify.setGeometry(padding, 120, half_width, 40)
        self.btn_uns_spicetify.clicked.connect(
            lambda: self.executar_powershell(
                "https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/uns_spicetify.ps1"
                )
            )

        self.btn_uns_spotify = CustomButton("SPOTIFY", "#D32F2F", self.font_regular, self)
        self.btn_uns_spotify.setGeometry(padding * 2 + half_width, 120, half_width, 40)
        self.btn_uns_spotify.clicked.connect(
            lambda: self.executar_powershell(
                "https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/uns_spotify.ps1"
                )
            )

        self.btn_copy_gist = QPushButton(self)
        self.btn_copy_gist.setGeometry(self.width() - 40, self.height() - 40, 28, 28)
        self.btn_copy_gist.setIcon(QIcon("src/icons/copy.ico"))
        self.btn_copy_gist.setStyleSheet("background-color: transparent;")
        self.btn_copy_gist.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_copy_gist.clicked.connect(self.copiar_gist)

    def executar_powershell(self, url):
        subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                 f"irm {url} | iex"], shell=True
                )

    def spotify_esta_instalado_winget(self):
        try:
            result = subprocess.run(
                    ["winget", "list", "--name", "Spotify"],
                    capture_output=True,
                    text=True,
                    shell=True
            )
            output = result.stdout.strip()

            if "Spotify" in output:
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao verificar Spotify: {e}")
            return False

    def instalar_spotify_spicetify(self):
        if self.spotify_esta_instalado_winget():
            QMessageBox.information(self, "Spotify", "Spotify já está instalado. Prosseguindo com o Spicetify...")
        else:
            QMessageBox.information(self, "Spotify", "Spotify não encontrado. Instalando agora...")
            self.executar_powershell("https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/ins_spotify.ps1")

        self.executar_powershell("https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/ins_spicetify.ps1")
        self.start_progress_animation()

    def copiar_gist(self):
        url = "https://gist.githubusercontent.com/hi-bernardo/5abd76c0f4f7dd366c6a22d90d5b59da/raw/spotify-backup.json"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                pyperclip.copy(resposta.text)
                QMessageBox.information(self, "Copiado", "Mensagem copiada para a área de transferência!")
            else:
                QMessageBox.warning(self, "Erro", "Falha ao acessar o conteúdo do Gist.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao copiar: {e}")

    # ANIMAÇÕES / BARRA DE PROGRESSO
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
