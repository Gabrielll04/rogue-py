from core import config, state_manager
from pgzero.rect import Rect
import random

TILE_SIZE = 10
PLAYER_SIZE = 40
MAP_WIDTH, MAP_HEIGHT = 200, 200
PLAYER_SPEED = 15

class Jogo:
    def __init__(self, play_sound_callback, keys_callback, keyboard_ref):
        self.play_sound = play_sound_callback
        self.keys = keys_callback
        self.keyboard = keyboard_ref

        self.player_x = MAP_WIDTH * TILE_SIZE // 2
        self.player_y = MAP_HEIGHT * TILE_SIZE // 2

        # mapa com variação de "grama"
        self.map_data = self.gerar_mapa()

    def gerar_mapa(self):
        """Gera o mapa com variação de tons de verde (grama)."""
        cores = ["#2e8b57", "#3cb371", "#228b22"]
        return [[random.choice(cores) for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    def draw(self, screen):
        screen.fill((30, 30, 30))

        offset_x = config.WIDTH // 2 - self.player_x
        offset_y = config.HEIGHT // 2 - self.player_y

        # desenha tiles do mapa
        for y, linha in enumerate(self.map_data):
            for x, cor in enumerate(linha):
                rect = Rect(
                    (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y),
                    (TILE_SIZE, TILE_SIZE)
                )
                screen.draw.filled_rect(rect, cor)

        # desenha o jogador (retângulo fixo no centro da tela)
        player_rect = Rect(
            (config.WIDTH // 2 - PLAYER_SIZE // 2, config.HEIGHT // 2 - PLAYER_SIZE // 2),
            (PLAYER_SIZE, PLAYER_SIZE)
        )
        screen.draw.filled_rect(player_rect, "darkgreen")

    def update(self):
        if self.keyboard[self.keys.W]:
            self.player_y -= PLAYER_SPEED
        if self.keyboard[self.keys.S]:
            self.player_y += PLAYER_SPEED
        if self.keyboard[self.keys.A]:
            self.player_x -= PLAYER_SPEED
        if self.keyboard[self.keys.D]:
            self.player_x += PLAYER_SPEED

    def on_key_down(self, key):
        if key == self.keys.ESCAPE:
            from states.menu import Menu
            state_manager.estado_atual = Menu(
                play_sound_callback=self.play_sound,
                keys_callback=self.keys
            )
            if config.SONS_ATIVOS:
                self.play_sound()
