from kivy.config import Config
Config.set('graphics', 'position', 'auto')
Config.set('graphics', 'resizable', False)
Config.set('kivy', 'window_icon', 'icon.ico')
from kivy.resources import resource_add_path
import sys
import os
import subprocess
import threading
from kivy.app import App
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty, ColorProperty,
    StringProperty, NumericProperty
)
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(__file__)

FONT_BOLD = os.path.join(base_dir, 'font', 'Montserrat-Bold.ttf')
FONT_SEMIBOLD = os.path.join(base_dir, 'font', 'Montserrat-SemiBold.ttf')

resource_add_path(os.path.join(base_dir, 'font'))

Window.size = (400, 270)
Window.clearcolor = (0.2, 0.6, 0.9, 1)

kv_string = '''
<HoverButton>:
    font_size: self.original_font_size
    background_normal: ''
    background_color: 0,0,0,0
    color: 0,0,0,1
    canvas.before:
        Color:
            rgba: self.hover_color if self.hovered else self.default_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]
    on_size: self.original_font_size = self.font_size
    on_pos: self.original_font_size = self.font_size

<Popup>:
    background_color: 0.129, 0.129, 0.129, 1
    separator_color: 0.424, 0.675, 0.894, 1
    title_color: 1,1,1,1
    title_size: 16
    title_font: app.FONT_SEMIBOLD
    canvas.before:
        Color:
            rgba: root.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15]

<MyWidget>:
    orientation: 'vertical'
    padding: 20
    spacing: 20
    canvas.before:
        Color:
            rgba: 0.129, 0.129, 0.129, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: 15

        Label:
            text: '[size=24][b]INSTALAR[/b][/size]'
            markup: True
            font_name: app.FONT_BOLD
            size_hint_y: None
            height: 25
            color: 1,1,1,1

        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 20
            HoverButton:
                text: 'Spotify'
                font_size: 16
                default_color: 0.424, 0.675, 0.894, 1
                hover_color: 0.3, 0.5, 0.7, 1
                on_press: root.instalar_spotify()
            HoverButton:
                text: 'Spicetify'
                font_size: 16
                default_color: 0.424, 0.675, 0.894, 1
                hover_color: 0.3, 0.5, 0.7, 1
                style: "elevated"
                pos_hint: {"center_x": .5, "center_y": .5}
                on_press: root.instalar_spicetify()

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: 15
        Label:
            text: '[size=24][b]DESINSTALAR[/b][/size]'
            markup: True
            font_name: app.FONT_BOLD
            size_hint_y: None
            height: 25
            color: 1,1,1,1
        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 20
            HoverButton:
                text: 'Spotify'
                font_size: 16
                default_color: 0.851, 0.208, 0.310, 1
                hover_color: 0.7, 0.1, 0.2, 1
                on_press: root.confirmar_desinstalacao('Spotify', root.desinstalar_spotify)
            HoverButton:
                text: 'Spicetify'
                font_size: 16
                default_color: 0.851, 0.208, 0.310, 1
                hover_color: 0.7, 0.1, 0.2, 1
                on_press: root.confirmar_desinstalacao('Spicetify', root.desinstalar_spicetify)

    HoverButton:
        text: 'SAIR'
        font_size: 16
        default_color: 0.357, 0.753, 0.871, 1
        hover_color: 0.2, 0.6, 0.8, 1
        size_hint_y: None
        height: 40
        on_press: root.confirmar_saida()
'''


class HoverBehavior:
    hovered = BooleanProperty(False)
    _current_hover = None

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super().__init__(**kwargs)

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        widget_pos = self.to_widget(*pos, relative=False)
        inside = self.collide_point(*widget_pos)

        if HoverBehavior._current_hover == self and not inside:
            self._leave()
        elif inside and HoverBehavior._current_hover != self:
            self._enter()

    def _enter(self):
        if HoverBehavior._current_hover:
            HoverBehavior._current_hover._leave()
        HoverBehavior._current_hover = self
        self.bold = True
        self.hovered = True
        self.dispatch('on_enter')

    def _leave(self):
        self.bold = False
        self.hovered = False
        self.dispatch('on_leave')
        HoverBehavior._current_hover = None


class HoverButton(Button, HoverBehavior):
    default_color = ColorProperty([0.4, 0.4, 0.4, 1])
    hover_color = ColorProperty([0.6, 0.6, 0.6, 1])
    original_font_size = NumericProperty(14)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_font_tracking)

    def _init_font_tracking(self, dt):
        self.original_font_size = self.font_size
        self.bind(font_size=self._update_font_size)

    def _update_font_size(self, instance, value):
        if not self.hovered:
            self.original_font_size = value

    def on_enter(self):
        Animation.cancel_all(self)
        anim = Animation(
            font_size=self.original_font_size * 1.2,
            duration=0.03,
            t='in_out_cubic'
        )
        anim.start(self)
        Window.set_system_cursor('hand')

    def on_leave(self):
        Animation.cancel_all(self)
        anim = Animation(
            font_size=self.original_font_size,
            duration=0.03,
            t='in_out_cubic'
        )
        anim.start(self)
        Window.set_system_cursor('arrow')

###########################################################


class MyWidget(BoxLayout):
    URLS = {
        'install_spotify': 'https://raw.githubusercontent.com/hi-bernardo/Spotify-Install/master/scripts/spotify.ps1',
        'install_spicetify': 'https://raw.githubusercontent.com/hi-bernardo/Spotify-Install/master/scripts/spicetify.ps1',
        'uninstall_spotify': 'https://raw.githubusercontent.com/hi-bernardo/Spotify-Install/master/scripts/remove_spotify.ps1',
        'uninstall_spicetify': 'https://raw.githubusercontent.com/hi-bernardo/Spotify-Install/master/scripts/remove_spicetify.ps1'
    }
    montserrat_bold = StringProperty('')
    montserrat_semibold = StringProperty('')

    def instalar_spotify(self):
        self.executar_comando(
            f'iwr -useb "{self.URLS["install_spotify"]}" | iex',
            'Iniciando instalação do Spotify...',
            'Spotify',
            'instalado'
        )

    def desinstalar_spotify(self):
        self.executar_comando(
            f'iwr -useb "{self.URLS["uninstall_spotify"]}" | iex',
            'Iniciando desinstalação do Spotify...',
            'Spotify',
            'desinstalado'
        )

    def instalar_spicetify(self):
        self.executar_comando(
            f'iwr -useb "{self.URLS["install_spicetify"]}" | iex',
            'Iniciando instalação do Spicetify...',
            'Spicetify',
            'instalado'
        )

    def desinstalar_spicetify(self):
        self.executar_comando(
            f'iwr -useb "{self.URLS["uninstall_spicetify"]}" | iex',
            'Iniciando desinstalação do Spicetify...',
            'Spicetify',
            'desinstalado'
        )

    def confirmar_desinstalacao(self, programa, acao):
        self.confirmar_acao(
            'Confirmar',
            f'Deseja desinstalar o {programa}?',
            acao
        )

    def confirmar_saida(self):
        self.confirmar_acao(
            'Confirmar',
            'Deseja realmente sair?',
            App.get_running_app().stop
        )

    def executar_comando(self, comando, mensagem, programa, acao):
        def run_cmd():
            try:
                resultado = subprocess.run(
                    ['powershell', '-Command', comando],
                    check=True,
                    capture_output=True,
                    text=True
                )
                # Mensagem simplificada para sucesso
                mensagem = f"[b]{programa}[/b] {acao} com sucesso!"
            except subprocess.CalledProcessError as e:
                # Mantém detalhes do erro para diagnóstico
                mensagem = f"Erro ao {acao.lower()} {programa}:\n{e.stderr}"
            except Exception as e:
                mensagem = f"Erro inesperado:\n{str(e)}"
            finally:
                Clock.schedule_once(lambda dt: popup.dismiss())
                Clock.schedule_once(
                    lambda dt: self.mostrar_popup('Resultado', mensagem, 5))
                Window.set_system_cursor('arrow')

        Window.set_system_cursor('wait')
        popup = self.mostrar_popup('Executando', mensagem)
        threading.Thread(target=run_cmd).start()

    def mostrar_popup(self, titulo, mensagem, tempo=0):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        lbl = Label(
            text=mensagem,
            color=(1, 1, 1, 1),
            markup=True,
            halign='center',
            font_size=dp(16),
            text_size=(dp(280), None)
        )

        btn = HoverButton(
            text='OK',
            size_hint_y=None,
            height=dp(40),
            default_color=(0.424, 0.675, 0.894, 1),
            hover_color=(0.3, 0.5, 0.7, 1)
        )

        content.add_widget(lbl)
        content.add_widget(btn)

        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(None, None),
            size=(dp(320), dp(200)),
            background_color=(0.129, 0.129, 0.129, 1)
        )

        btn.bind(on_press=popup.dismiss)

        if tempo > 0:
            Clock.schedule_once(lambda dt: popup.dismiss(), tempo)

        popup.open()
        return popup

    def confirmar_acao(self, titulo, mensagem, acao):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        btn_sim = HoverButton(text='Sim', default_color=(
            0.2, 0.8, 0.2, 1), hover_color=(0.1, 0.6, 0.1, 1))
        btn_nao = HoverButton(text='Não', default_color=(
            0.8, 0.2, 0.2, 1), hover_color=(0.6, 0.1, 0.1, 1))
        lbl = Label(
            text=mensagem,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        content.add_widget(lbl)

        botoes = BoxLayout(
            spacing=10,
            size_hint_y=None,
            height=40
        )

        btn_sim = HoverButton(
            text='Sim',
            default_color=(0.2, 0.8, 0.2, 1),
            hover_color=(0.1, 0.6, 0.1, 1)
        )
        btn_nao = HoverButton(
            text='Não',
            default_color=(0.8, 0.2, 0.2, 1),
            hover_color=(0.6, 0.1, 0.1, 1)
        )

        botoes.add_widget(btn_sim)
        botoes.add_widget(btn_nao)

        content.add_widget(botoes)

        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False
        )

        btn_sim.bind(on_press=lambda x: [acao(), popup.dismiss()])
        btn_nao.bind(on_press=popup.dismiss)

        popup.open()


class MyApp(App):
    FONT_BOLD = StringProperty('')
    FONT_SEMIBOLD = StringProperty('')

    def build(self):
        self.title = "FACILITANDO A VIDA"
        self.icon = "icon.png"
        self.FONT_BOLD = FONT_BOLD
        self.FONT_SEMIBOLD = FONT_SEMIBOLD
        Builder.load_string(kv_string)
        return MyWidget()


if __name__ == '__main__':
    MyApp().run()
