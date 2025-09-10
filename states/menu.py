from core import config, state_manager
from ui.botao import Botao
from states.jogo import Jogo
from pgzero import music

class Menu:
    def __init__(self, play_sound_callback, keys_callback, keyboard_ref):
        self.botoes = [
            Botao("Jogar", 300, 200),
            Botao("Sair", 300, 300),
            Botao("Música: ON", 50, 500, 180, 50),
            Botao("Sons: ON", 250, 500, 180, 50)
        ]

        self.play_sound = play_sound_callback
        self.keys = keys_callback
        self.keyboard = keyboard_ref

    def draw(self, screen):
        screen.clear()
        screen.draw.text("MENU PRINCIPAL", center=(config.WIDTH/2, 100), fontsize=60)
        for botao in self.botoes:
            botao.desenhar(screen)

    def on_mouse_move(self, pos):
        for botao in self.botoes:
            botao.verificar_hover(pos)

    def on_mouse_down(self, pos):
        if self.botoes[0].clicado(pos):  # Jogar
            state_manager.estado_atual = Jogo(play_sound_callback=self.play_sound, keys_callback=self.keys, keyboard_ref=self.keyboard)
            if config.SONS_ATIVOS:
                self.play_sound()

        elif self.botoes[1].clicado(pos):  # Sair
            exit()

        elif self.botoes[2].clicado(pos):  # Música ON/OFF
            config.MUSICA_ATIVA = not config.MUSICA_ATIVA
            self.botoes[2].texto = f"Música: {'ON' if config.MUSICA_ATIVA else 'OFF'}"
            if config.MUSICA_ATIVA:
                music.play("bgm")
                music.set_volume(0.5)
            else:
                music.stop()

        elif self.botoes[3].clicado(pos):  # Sons ON/OFF
            config.SONS_ATIVOS = not config.SONS_ATIVOS
            self.botoes[3].texto = f"Sons: {'ON' if config.SONS_ATIVOS else 'OFF'}"
            if config.SONS_ATIVOS:
                self.play_sound()

