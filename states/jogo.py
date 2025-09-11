import random
import math
from pgzero.rect import Rect
from pgzero.actor import Actor
from ui.botao import Botao
from core import state_manager

TILE_SIZE = 10
PLAYER_SIZE = 40
MAP_WIDTH, MAP_HEIGHT = 200, 200


class Jogo:
    def __init__(self, play_sound_callback, keys_callback, keyboard_ref,
                 config_ref, mouse_ref):
        self.play_sound = play_sound_callback
        self.keys = keys_callback
        self.keyboard = keyboard_ref
        self.config = config_ref
        self.mouse_pos = (0, 0)
        self.mouse_left_pressed = False
        self.mouse = mouse_ref

        self.game_state = "playing"

        self.player_x = MAP_WIDTH // 2
        self.player_y = MAP_HEIGHT // 2
        self.player_hp = 10
        self.player_max_hp = 10
        self.player_direction = "right"
        self.player_damage = 1
        self.player_fire_rate = 20
        self.player_speed = 0.6
        self.fire_cooldown = 0

        self.bullets = []
        self.enemies = []
        self.wave = 1
        self.spawn_wave()

        self.upgrade_options = []
        self.selected_upgrade = None

        self.map_data = self.gerar_mapa()

        # Player animation
        self.player_idle_sprites = [
            "player_idle1", "player_idle2", "player_idle3", "player_idle4",
            "player_idle5", "player_idle6", "player_idle7", "player_idle8",
            "player_idle9"
        ]
        self.player_walk_sprites = [
            "player_walk1", "player_walk2", "player_walk3", "player_walk4"
        ]
        self.player_sprite_index = 0
        self.player_anim_timer = 0
        self.player_actor = Actor(self.player_idle_sprites[0])

        # Botão para voltar ao menu (criado apenas quando necessário)
        self.menu_button = None

    def gerar_mapa(self):
        cores = ["#2e8b57", "#3cb371", "#228b22"]
        return [[random.choice(cores) for _ in range(MAP_WIDTH)]
                for _ in range(MAP_HEIGHT)]

    def spawn_wave(self):
        self.enemies.clear()
        quantidade_total = 3 + self.wave * 2
        
        # Chance de tanque: 20% na wave 1, aumenta 5% por wave até 40%
        tank_chance = min(0.4, 0.2 + (self.wave - 1) * 0.05)
        
        for _ in range(quantidade_total):
            ex = random.randint(0, MAP_WIDTH)
            ey = random.randint(0, MAP_HEIGHT)
            enemy_sprites = ["enemy_walk1", "enemy_walk2"]

            if random.random() < tank_chance:
                # Inimigo tanque
                self.enemies.append({
                    "x": ex,
                    "y": ey,
                    "hp": (2 + self.wave * 2) * 2, 
                    "max_hp": (2 + self.wave * 2) * 2,
                    "sprite_index": 0,
                    "anim_timer": 0,
                    "sprites": enemy_sprites,
                    "actor": Actor(enemy_sprites[0]),
                    "type": "tank",
                    "attack_cooldown": 0,
                    "size_multiplier": 1.8,
                    "damage": 2,
                    "speed": 0.1
                })
            else:
                self.enemies.append({
                    "x": ex,
                    "y": ey,
                    "hp": 2 + self.wave,
                    "max_hp": 2 + self.wave,
                    "sprite_index": 0,
                    "anim_timer": 0,
                    "sprites": enemy_sprites,
                    "actor": Actor(enemy_sprites[0]),
                    "attack_cooldown": 0,
                    "type": "normal",
                    "size_multiplier": 1.0,
                    "damage": 1,
                    "speed": 0.3
                })

    def animate_player(self, moving, direction="right"):
        self.player_anim_timer += 1
        if self.player_anim_timer >= 4:
            self.player_anim_timer = 0
            sprite_list = (self.player_walk_sprites if moving 
                          else self.player_idle_sprites)
            self.player_sprite_index = ((self.player_sprite_index + 1) 
                                       % len(sprite_list))
            base_name = sprite_list[self.player_sprite_index]
            if direction == "left":
                self.player_actor.image = base_name + "_left"
            else:
                self.player_actor.image = base_name

    def animate_enemy(self, enemy):
        enemy["anim_timer"] += 1
        if enemy["anim_timer"] >= 5:
            enemy["anim_timer"] = 0
            enemy["sprite_index"] = ((enemy["sprite_index"] + 1) 
                                    % len(enemy["sprites"]))
            enemy["actor"].image = enemy["sprites"][enemy["sprite_index"]]

    def update(self):
        if self.game_state == "upgrade_selection":
            self.handle_upgrade_selection()
            return

        if self.game_state == "game_over":
            return

        if self.player_hp <= 0:
            self.game_state = "game_over"
            # Criar botão quando entrar no game over
            if self.menu_button is None:
                self.menu_button = Botao(
                    "Voltar ao Menu",
                    self.config.WIDTH // 2 - 100,
                    300,
                    200,
                    60,
                    cor="darkred",
                    cor_hover="red"
                )

        moving = False

        if self.keyboard[self.keys.W]:
            self.player_y -= self.player_speed
            moving = True
        if self.keyboard[self.keys.S]:
            self.player_y += self.player_speed
            moving = True
        if self.keyboard[self.keys.A]:
            self.player_x -= self.player_speed
            moving = True
            self.player_direction = "left"
        if self.keyboard[self.keys.D]:
            self.player_x += self.player_speed
            moving = True
            self.player_direction = "right"

        self.animate_player(moving, self.player_direction)

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        if self.mouse_left_pressed and self.fire_cooldown == 0:
            self.shoot()
            self.fire_cooldown = self.player_fire_rate

        for bullet in self.bullets[:]:
            bullet["x"] += bullet["dx"] * bullet["speed"]
            bullet["y"] += bullet["dy"] * bullet["speed"]

            for enemy in self.enemies[:]:
                enemy_radius = (20 * enemy["size_multiplier"]) / TILE_SIZE  

                dist = math.hypot(bullet["x"] - enemy["x"], 
                                 bullet["y"] - enemy["y"])
                if dist < enemy_radius:
                    enemy["hp"] -= self.player_damage
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy["hp"] <= 0:
                        self.enemies.remove(enemy)
                    break
            if not (0 <= bullet["x"] < MAP_WIDTH and
                    0 <= bullet["y"] < MAP_HEIGHT):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

        for enemy in self.enemies[:]:
            dx = self.player_x - enemy["x"]
            dy = self.player_y - enemy["y"]
            dist = max(1, (dx**2 + dy**2) ** 0.5)

            min_dist = ((PLAYER_SIZE // 2 + 10 * enemy["size_multiplier"]) 
                       / TILE_SIZE)
            if dist <= min_dist:
                if enemy["attack_cooldown"] <= 0:
                    self.player_hp -= 1
                    # frames de recarga antes do próximo hit
                    enemy["attack_cooldown"] = 20  
            else:
                enemy["x"] += dx / dist * enemy["speed"]
                enemy["y"] += dy / dist * enemy["speed"]

            if enemy["attack_cooldown"] > 0:
                enemy["attack_cooldown"] -= 1

            self.animate_enemy(enemy)

        if not self.enemies:
            self.wave += 1
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

    def shoot(self):
        mx, my = self.mouse_pos
        mouse_x = (mx / TILE_SIZE + self.player_x -
                   (self.config.WIDTH // 2) / TILE_SIZE)
        mouse_y = (my / TILE_SIZE + self.player_y -
                   (self.config.HEIGHT // 2) / TILE_SIZE)

        dx = mouse_x - self.player_x
        dy = mouse_y - self.player_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        self.bullets.append({
            "x": self.player_x,
            "y": self.player_y,
            "dx": dx,
            "dy": dy,
            "speed": 2
        })

    def on_mouse_move(self, pos, rel, buttons):
        self.mouse_pos = pos
        self.mouse_left_pressed = self.mouse.LEFT in buttons
        
        # Atualizar hover do botão se estiver na tela de game over
        if self.game_state == "game_over" and self.menu_button:
            self.menu_button.verificar_hover(pos)

    def on_mouse_down(self, pos, button):
        if button == 1:
            # Verificar clique no botão de menu se estiver na tela de game over
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

    def generate_upgrade_options(self):
        all_upgrades = [
            {
                "tipo": "vida",
                "nome": "Mais Vida",
                "descricao": f"+5 HP (Atual: {int(self.player_hp)})"
            },
            {
                "tipo": "cadencia",
                "nome": "Cadência de Tiro",
                "descricao": f"Tiros mais rápidos (Atual: {self.player_fire_rate})"
            },
            {
                "tipo": "velocidade",
                "nome": "Velocidade",
                "descricao": f"Movimento mais rápido (Atual: {self.player_speed:.2f})"
            },
            {
                "tipo": "dano",
                "nome": "Mais Dano",
                "descricao": f"Dano por tiro +1 (Atual: {self.player_damage})"
            }
        ]
        self.upgrade_options = random.sample(all_upgrades, 3)
        self.selected_upgrade = 0

    def apply_upgrade(self, upgrade_tipo):
        if upgrade_tipo == "vida":
            self.player_max_hp += 5
            self.player_hp += 5
        elif upgrade_tipo == "cadencia":
            self.player_fire_rate = max(3, self.player_fire_rate - 3)
        elif upgrade_tipo == "velocidade":
            self.player_speed += 0.1
        elif upgrade_tipo == "dano":
            self.player_damage += 1

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
        offset_x = self.config.WIDTH // 2 - self.player_x * TILE_SIZE
        offset_y = self.config.HEIGHT // 2 - self.player_y * TILE_SIZE

        for y, linha in enumerate(self.map_data):
            for x, cor in enumerate(linha):
                rect = Rect(
                    (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y),
                    (TILE_SIZE, TILE_SIZE)
                )
                screen.draw.filled_rect(rect, cor)

        self.player_actor.pos = (self.config.WIDTH // 2,
                                 self.config.HEIGHT // 2)
        self.player_actor.draw()

        for bullet in self.bullets:
            rect = Rect((bullet["x"] * TILE_SIZE + offset_x,
                        bullet["y"] * TILE_SIZE + offset_y), (5, 5))
            screen.draw.filled_rect(rect, "yellow")

        for enemy in self.enemies:
            enemy["actor"].pos = (enemy["x"] * TILE_SIZE + offset_x,
                                  enemy["y"] * TILE_SIZE + offset_y)
            
            if enemy["type"] == "tank":
                original_scale = getattr(enemy["actor"], '_scale', 1.0)
                enemy["actor"]._scale = enemy["size_multiplier"]
                enemy["actor"].draw()
                enemy["actor"]._scale = original_scale
                
                tank_rect = Rect((enemy["actor"].pos[0] - 25, 
                                 enemy["actor"].pos[1] - 25), (50, 50))
                screen.draw.rect(tank_rect, "darkred")
            else:
                enemy["actor"].draw()

            health_bar_width = int(40 * enemy["size_multiplier"])
            health_percentage = enemy["hp"] / enemy["max_hp"]
            health_width = int(health_bar_width * health_percentage)
            
            bg_health_rect = Rect(
                (enemy["actor"].pos[0] - health_bar_width // 2,
                 enemy["actor"].pos[1] - 35 * enemy["size_multiplier"]), 
                (health_bar_width, 6)
            )
            screen.draw.filled_rect(bg_health_rect, "darkred")
            
            if health_width > 0:
                health_rect = Rect(
                    (enemy["actor"].pos[0] - health_bar_width // 2,
                     enemy["actor"].pos[1] - 35 * enemy["size_multiplier"]),
                    (health_width, 6)
                )
                if health_percentage > 0.6:
                    health_color = "green"
                elif health_percentage > 0.3:
                    health_color = "yellow"
                else:
                    health_color = "red"
                screen.draw.filled_rect(health_rect, health_color)

        screen.draw.text(f"HP: {int(self.player_hp)}/{self.player_max_hp}",
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

        # Usar o botão da UI em vez do desenho manual
        if self.menu_button:
            self.menu_button.desenhar(screen)