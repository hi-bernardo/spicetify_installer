import os
import sys
import requests
import pyperclip
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFontDatabase, QFont, QPalette, QColor, QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QByteArray

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class VerificadorSpotify(QThread):
    resultado = pyqtSignal(bool)

    def run(self):
        try:
            output = subprocess.check_output(
                    ["powershell", "-Command", "winget list --id Spotify.Spotify"],
                    stderr=subprocess.DEVNULL,
                    shell=True
            )
            instalado = bool(output.strip())
            self.resultado.emit(instalado)
        except subprocess.CalledProcessError:
            self.resultado.emit(False)


class ScriptRunner(QThread):
    finished = pyqtSignal(str)

    def __init__(self, url, apos=None):
        super().__init__()
        self.url = url
        self.apos = apos

    def run(self):
        subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", f"irm {self.url} | iex"],
                shell=True
        )
        self.finished.emit(self.apos)


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
        r = min(int(color.red() * factor), 200)
        g = min(int(color.green() * factor), 200)
        b = min(int(color.blue() * factor), 200)
        return f"rgb({r}, {g}, {b})"


class SpicetifyInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spicetify Installer")
        self.setFixedSize(400, 275)
        self.setWindowIcon(QIcon(resource_path("src/icons/app.ico")))

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#242424"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.load_fonts()
        self.init_ui()

        self.dot_timer = QTimer(self)
        self.dot_timer.timeout.connect(self.update_dots)
        self.dot_phase = 0
        self.status_base_text = ""
        self.mouse_sobre_botao = False

    def load_fonts(self):
        QFontDatabase.addApplicationFont(resource_path("src/font/Inter-Variable.ttf"))
        QFontDatabase.addApplicationFont(resource_path("src/font/Montserrat-Bold.ttf"))
        self.font_regular = QFont("Inter", 10)
        self.font_bold = QFont("Montserrat", 10, QFont.Bold)

    def verificar_spotify(self):
        self.start_status_animation("Verificando se o Spotify está instalado")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.verificador = VerificadorSpotify()
        self.verificador.resultado.connect(self.depois_de_verificar_spotify)
        self.verificador.start()

    def depois_de_verificar_spotify(self, instalado):
        self.stop_status_animation()
        QApplication.restoreOverrideCursor()

        if instalado:
            self.label_status.setText("Spotify já instalado!\nFaça login para instalar o Spicetify!")
            self.label_status.setVisible(True)
        else:
            self.executar_com_status(
                    "Instalando Spotify",
                    "https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/ins_spotify.ps1",
                    apos="spotify_install"
            )

    def init_ui(self):
        padding = 10
        full_width = self.width() - 2 * padding
        half_width = (self.width() - 3 * padding) // 2

        self.label_msg_temporaria = QLabel("", self)
        self.label_msg_temporaria.setStyleSheet(
                """
                background-color: #2D2D2D;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
            """
        )
        self.label_msg_temporaria.setFont(self.font_regular)
        self.label_msg_temporaria.setVisible(False)
        self.label_msg_temporaria.setAlignment(Qt.AlignCenter)
        self.label_msg_temporaria.setFixedWidth(350)
        self.label_msg_temporaria.move((self.width() - 350) // 2, self.height() - 90)

        self.tooltip_custom = QLabel("COPIAR BACKUP", self)
        self.tooltip_custom.setStyleSheet(
                """
                background-color: #353535;
                color: #FFFFFF;
                padding: 3px 7px;
                border-radius: 6px;
                font-size: 10px;
            """
        )
        self.tooltip_custom.setFont(self.font_regular)
        self.tooltip_custom.setVisible(False)
        self.tooltip_custom.adjustSize()
        # Efeito de opacidade para animar
        self.opacity_effect = QGraphicsOpacityEffect(self.tooltip_custom)
        self.tooltip_custom.setGraphicsEffect(self.opacity_effect)
        self.tooltip_custom.setVisible(False)

        # Animação de opacidade
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # RESPONSÁVEL PELAS MENSAGENS DE STATUS
        self.label_status = QLabel("", self)
        self.label_status.setGeometry(padding, 185, full_width, 60)
        self.label_status.setFont(self.font_bold)
        self.label_status.setStyleSheet("color: white; font-size: 12px;")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setVisible(False)

        # --- TÍTULO SPOTIFY ---
        self.icon_spotify = QLabel(self)
        self.icon_spotify.setPixmap(
            QPixmap(resource_path("src/icons/spotify.ico")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        self.icon_spotify.setGeometry(padding, 10, 30, 30)

        self.label_spotify = QLabel("SPOTIFY", self)
        self.label_spotify.setFont(self.font_bold)
        self.label_spotify.setStyleSheet("color: white; font-size: 18px;")
        self.label_spotify.setGeometry(padding + 30, 10, full_width - 30, 30)

        # --- BOTÕES SPOTIFY ---
        self.btn_ins_spotify = CustomButton("INSTALAR", "#1ED760", self.font_regular, self)
        self.btn_ins_spotify.setGeometry(padding, 45, half_width, 40)
        self.btn_ins_spotify.clicked.connect(self.verificar_spotify)

        self.btn_uns_spotify = CustomButton("DESINSTALAR", "#C33F3F", self.font_regular, self)
        self.btn_uns_spotify.setGeometry(padding * 2 + half_width, 45, half_width, 40)
        self.btn_uns_spotify.clicked.connect(
                lambda: self.executar_com_status(
                        "Desinstalando Spotify",
                        "https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/uns_spotify.ps1",
                        apos="spotify_uninstall"
                )
        )

        # --- TÍTULO SPICETIFY ---
        self.icon_spicetify = QLabel(self)
        self.icon_spicetify.setPixmap(
            QPixmap(resource_path("src/icons/spicetify.ico")).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        self.icon_spicetify.setGeometry(padding, 100, 30, 30)

        self.label_spicetify = QLabel("SPICETIFY", self)
        self.label_spicetify.setFont(self.font_bold)
        self.label_spicetify.setStyleSheet("color: white; font-size: 18px;")
        self.label_spicetify.setGeometry(padding + 30, 100, full_width - 30, 30)

        # --- BOTÕES SPICETIFY ---
        self.btn_ins_spicetify = CustomButton("INSTALAR", "#1ED760", self.font_regular, self)
        self.btn_ins_spicetify.setGeometry(padding, 135, half_width, 40)
        self.btn_ins_spicetify.clicked.connect(
                lambda: self.executar_com_status(
                        "Instalando Spicetify",
                        "https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/ins_spicetify.ps1",
                        apos="spicetify_install"
                )
        )
        # DESINSTALAR SPICETIFY
        self.btn_uns_spicetify = CustomButton("DESINSTALAR", "#C33F3F", self.font_regular, self)
        self.btn_uns_spicetify.setGeometry(padding * 2 + half_width, 135, half_width, 40)
        self.btn_uns_spicetify.clicked.connect(
                lambda: self.executar_com_status(
                        "Desinstalando Spicetify",
                        "https://raw.githubusercontent.com/hi-bernardo/spicetify_installer/master/src/scripts/uns_spicetify.ps1",
                        apos="spicetify_uninstall"
                )
        )

        # --- SESSÃO BACKUP
        self.btn_copy_gist = QPushButton(self)
        self.btn_copy_gist.enterEvent = self.mostrar_tooltip_custom
        self.btn_copy_gist.leaveEvent = self.esconder_tooltip_custom
        self.btn_copy_gist.setGeometry(self.width() - 35, self.height() - 35, 28, 28)
        self.btn_copy_gist.setIcon(QIcon(resource_path("src/icons/copy.ico")))
        self.btn_copy_gist.setStyleSheet(
                """
                QPushButton {
                    background-color: #202020;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #353535;
                }
            """
        )
        self.btn_copy_gist.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_copy_gist.clicked.connect(self.copiar_gist)

        # ASSINATURA
        self.label_autor = QLabel("by oBrazoo", self)
        self.label_autor.setGeometry(8, self.height() - 20, 100, 15)
        self.label_autor.setStyleSheet("color: gray; font-size: 10px;")

    def mostrar_tooltip_custom(self, event):
        self.mouse_sobre_botao = True

        btn = self.btn_copy_gist
        tooltip = self.tooltip_custom

        tooltip.move(
                btn.x() + tooltip.width() - 205,
                btn.y() + (btn.height() - tooltip.height()) // 2
        )
        tooltip.setVisible(True)
        self.fade_animation.stop()
        self.fade_animation.setStartValue(self.opacity_effect.opacity())
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def esconder_tooltip_custom(self, event):
        self.mouse_sobre_botao = False

        self.fade_animation.stop()
        self.fade_animation.setStartValue(self.opacity_effect.opacity())
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

        def esconder_se_necessario():
            if not self.mouse_sobre_botao:
                self.tooltip_custom.setVisible(False)

        self.fade_animation.finished.connect(esconder_se_necessario)

    # FUNÇÃO MOSTRAR MENSAGEM BACKUP
    def mostrar_mensagem_estilizada(self, texto):
        self.label_msg_temporaria.setText(texto)
        self.label_msg_temporaria.setVisible(True)
        QTimer.singleShot(5000, lambda: self.label_msg_temporaria.setVisible(False))

    def executar_com_status(self, status_msg, url, apos=None):
        self.start_status_animation(status_msg)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.thread = ScriptRunner(url, apos)
        self.thread.finished.connect(self.ao_terminar_execucao)
        self.thread.start()

    def ao_terminar_execucao(self, apos=None):
        self.stop_status_animation()

        if apos == "spotify_install":
            self.label_status.setText("Spotify instalado!\nFaça login para instalar o Spicetify!")
            self.label_status.setVisible(True)
        elif apos == "spotify_uninstall":
            self.label_status.setText("Spotify desinstalado com sucesso!")
            self.label_status.setVisible(True)
        elif apos == "spicetify_install":
            self.label_status.setText("Spicetify instalado com sucesso!")
            self.label_status.setVisible(True)
        elif apos == "spicetify_uninstall":
            self.label_status.setText("Spicetify desinstalado com sucesso!")
            QTimer.singleShot(10000, lambda: self.label_status.setVisible(False))
        QApplication.restoreOverrideCursor()

    # FUNÇÃO PARA COPIAR BACKUP DO GIST
    def copiar_gist(self):
        url = "https://gist.githubusercontent.com/hi-bernardo/5abd76c0f4f7dd366c6a22d90d5b59da/raw/spotify-backup.json"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                pyperclip.copy(resposta.text)
                self.mostrar_mensagem_estilizada("ACESSE AS CONFIGS DO SPICETIFY.\nNA SESSÃO: 'BACKUP', COLE E IMPORTE AS CONFIGS!")
            else:
                self.mostrar_mensagem_estilizada("Erro ao acessar o backup :(")
        except Exception as e:
            self.mostrar_mensagem_estilizada(f"Erro: {str(e)}")

    def start_status_animation(self, text_base):
        self.label_status.setVisible(True)
        self.status_base_text = text_base
        self.dot_phase = 0
        self.update_dots()
        self.dot_timer.start(500)

    def stop_status_animation(self):
        self.dot_timer.stop()
        self.label_status.setVisible(False)

    def update_dots(self):
        dots = "." * (self.dot_phase % 4)
        self.label_status.setText(f"{self.status_base_text}{dots}")
        self.dot_phase += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpicetifyInstaller()
    window.show()
    sys.exit(app.exec_())
