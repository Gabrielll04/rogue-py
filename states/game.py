import random
import math
from pgzero.rect import Rect
from characters.player import Player
from characters.enemy import Enemy
from ui.button import Button
from core import state_manager

TILE_SIZE = 10
PLAYER_SIZE = 40
MAP_WIDTH, MAP_HEIGHT = 200, 200

class Game:
    def __init__(self, play_sound_callback, keys_callback, keyboard_ref,
                 config_ref, mouse_ref):
        self.play_sound = play_sound_callback
        self.keys = keys_callback
        self.keyboard = keyboard_ref
        self.config = config_ref
        self.mouse = mouse_ref

        self.mouse_pos = (0, 0)
        self.mouse_left_pressed = False

        self.game_state = "playing"

        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2,
                             self.play_sound, self.config,
                             self.keyboard, self.keys)
        self.enemies = []
        self.wave = 1
        self.spawn_wave()

        self.upgrade_options = []
        self.selected_upgrade = None
        self.menu_button = None

        self.map_data = self.gerar_mapa()

    def gerar_mapa(self):
        cores = ["#2e8b57", "#3cb371", "#228b22"]
        return [[random.choice(cores) for _ in range(MAP_WIDTH)]
                for _ in range(MAP_HEIGHT)]

    def spawn_wave(self):
        self.enemies.clear()
        quantidade_total = 3 + self.wave * 2
        tank_chance = min(0.4, 0.2 + (self.wave - 1) * 0.05)

        for _ in range(quantidade_total):
            ex = random.randint(0, MAP_WIDTH)
            ey = random.randint(0, MAP_HEIGHT)
            is_tank = random.random() < tank_chance
            self.enemies.append(Enemy(ex, ey, self.wave, is_tank))

    def update(self):
        if self.game_state == "upgrade_selection":
            self.handle_upgrade_selection()
            return

        if self.game_state == "game_over":
            return

        if self.player.hp <= 0:
            self.game_state = "game_over"
            if self.menu_button is None:
                self.menu_button = Button(
                    "Voltar ao Menu",
                    self.config.WIDTH // 2 - 100,
                    300,
                    200,
                    60,
                    cor="darkred",
                    cor_hover="red"
                )
            return

        # Update player
        self.player.update(self.mouse_left_pressed, self.mouse_pos)

        # Bullets colidindo
        for bullet in self.player.bullets[:]:
            bullet["x"] += bullet["dx"] * bullet["speed"]
            bullet["y"] += bullet["dy"] * bullet["speed"]

            for enemy in self.enemies[:]:
                enemy_radius = (20 * enemy.size_multiplier) / TILE_SIZE
                dist = math.hypot(bullet["x"] - enemy.x,
                                  bullet["y"] - enemy.y)
                if dist < enemy_radius:
                    enemy.hp -= self.player.damage
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                    break

            if not (0 <= bullet["x"] < MAP_WIDTH and
                    0 <= bullet["y"] < MAP_HEIGHT):
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)

        # Update inimigos
        for enemy in self.enemies[:]:
            enemy.update(self.player)

        if not self.enemies:
            self.wave += 1
            self.player.hp = self.player.max_hp
            self.game_state = "upgrade_selection"
            self.generate_upgrade_options()

    def handle_upgrade_selection(self):
        if self.keyboard[self.keys.W] or self.keyboard[self.keys.UP]:
            self.selected_upgrade = max(0, self.selected_upgrade - 1)
        if self.keyboard[self.keys.S] or self.keyboard[self.keys.DOWN]:
            self.selected_upgrade = min(2, self.selected_upgrade + 1)

        if (self.keyboard[self.keys.RETURN] or
            self.keyboard[self.keys.SPACE]):
            chosen_upgrade = self.upgrade_options[self.selected_upgrade]
            self.apply_upgrade(chosen_upgrade["tipo"])
            self.game_state = "playing"
            self.spawn_wave()

    def generate_upgrade_options(self):
        all_upgrades = [
            {"tipo": "vida", "nome": "Mais Vida",
             "descricao": f"+5 HP (Atual: {int(self.player.hp)})"},
            {"tipo": "cadencia", "nome": "Cadência de Tiro",
             "descricao": f"Tiros mais rápidos (Atual: {self.player.fire_rate})"},
            {"tipo": "velocidade", "nome": "Velocidade",
             "descricao": f"Movimento mais rápido (Atual: {self.player.speed:.2f})"},
            {"tipo": "dano", "nome": "Mais Dano",
             "descricao": f"Dano por tiro +1 (Atual: {self.player.damage})"}
        ]
        self.upgrade_options = random.sample(all_upgrades, 3)
        self.selected_upgrade = 0

    def apply_upgrade(self, upgrade_tipo):
        if upgrade_tipo == "vida":
            self.player.max_hp += 5
            self.player.hp += 5
        elif upgrade_tipo == "cadencia":
            self.player.fire_rate = max(3, self.player.fire_rate - 3)
        elif upgrade_tipo == "velocidade":
            self.player.speed += 0.1
        elif upgrade_tipo == "dano":
            self.player.damage += 1

    def draw(self, screen):
        if self.game_state == "upgrade_selection":
            self.draw_game(screen)
            self.draw_upgrade_selection(screen)
        elif self.game_state == "game_over":
            self.draw_game(screen)
            self.draw_game_over(screen)
        else:
            self.draw_game(screen)

    def draw_game(self, screen):
        screen.fill((30, 30, 30))
        offset_x = self.config.WIDTH // 2 - self.player.x * TILE_SIZE
        offset_y = self.config.HEIGHT // 2 - self.player.y * TILE_SIZE

        for y, linha in enumerate(self.map_data):
            for x, cor in enumerate(linha):
                rect = Rect(
                    (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y),
                    (TILE_SIZE, TILE_SIZE)
                )
                screen.draw.filled_rect(rect, cor)

        self.player.draw(screen, offset_x, offset_y)

        for enemy in self.enemies:
            enemy.draw(screen, offset_x, offset_y)

        screen.draw.text(f"HP: {int(self.player.hp)}/{self.player.max_hp}",
                         (10, 10), color="white")
        screen.draw.text(f"Wave: {self.wave}", (10, 30), color="white")
        screen.draw.text(f"Inimigos: {len(self.enemies)}",
                         (10, 50), color="white")

    def draw_upgrade_selection(self, screen):
        overlay = Rect((0, 0), (self.config.WIDTH, self.config.HEIGHT))
        screen.draw.filled_rect(overlay, (0, 0, 0, 180))

        title_text = f"Wave {self.wave} Concluída!"
        title_x = self.config.WIDTH // 2 - len(title_text) * 6
        screen.draw.text(title_text, (title_x, 100),
                         color="white", fontsize=30)

        subtitle_text = "Escolha um upgrade:"
        subtitle_x = self.config.WIDTH // 2 - len(subtitle_text) * 4
        screen.draw.text(subtitle_text, (subtitle_x, 140),
                         color="lightgray", fontsize=20)

        start_y = 200
        for i, upgrade in enumerate(self.upgrade_options):
            y_pos = start_y + i * 80
            if i == self.selected_upgrade:
                highlight_rect = Rect((50, y_pos - 10),
                                      (self.config.WIDTH - 100, 70))
                screen.draw.filled_rect(highlight_rect, (50, 50, 100))
            screen.draw.text(upgrade["nome"], (70, y_pos),
                             color="white", fontsize=24)
            screen.draw.text(upgrade["descricao"], (70, y_pos + 25),
                             color="lightgray", fontsize=16)

        instructions = [
            "Use W/S ou setas para navegar",
            "Enter ou Espaço para confirmar"
        ]
        for i, instruction in enumerate(instructions):
            inst_x = self.config.WIDTH // 2 - len(instruction) * 3
            screen.draw.text(instruction, (inst_x, 450 + i * 20),
                             color="yellow", fontsize=14)

    def draw_game_over(self, screen):
        overlay = Rect((0, 0), (self.config.WIDTH, self.config.HEIGHT))
        screen.draw.filled_rect(overlay, (0, 0, 0, 200))

        title_text = "GAME OVER"
        title_x = self.config.WIDTH // 2 - len(title_text) * 6
        screen.draw.text(title_text, (title_x, 150),
                         color="red", fontsize=50)

        if self.menu_button:
            self.menu_button.desenhar(screen)

    def on_mouse_move(self, pos, rel, buttons):
        self.mouse_pos = pos
        self.mouse_left_pressed = self.mouse.LEFT in buttons
        if self.game_state == "game_over" and self.menu_button:
            self.menu_button.verify_hover(pos)

    def on_mouse_down(self, pos, button):
        if button == 1:
            if (self.game_state == "game_over" and self.menu_button and 
                self.menu_button.clicado(pos)):
                from states.menu import Menu
                state_manager.estado_atual = Menu(
                    play_sound_callback=self.play_sound,
                    keys_callback=self.keys,
                    keyboard_ref=self.keyboard,
                    config_ref=self.config,
                    mouse_ref=self.mouse
                )
                return
            self.mouse_left_pressed = True

    def on_mouse_up(self, pos, button):
        if button == 1:
            self.mouse_left_pressed = False