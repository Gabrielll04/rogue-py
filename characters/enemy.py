import math
from pgzero.rect import Rect
from pgzero.actor import Actor

TILE_SIZE = 10
PLAYER_SIZE = 40

class Enemy:
    def __init__(self, x, y, wave, is_tank=False):
        self.x = x
        self.y = y
        self.sprites = ["enemy_walk1", "enemy_walk2"]
        self.sprite_index = 0
        self.anim_timer = 0
        self.actor = Actor(self.sprites[0])

        if is_tank:
            self.hp = (2 + wave * 2) * 2
            self.max_hp = self.hp
            self.size_multiplier = 1.8
            self.damage = 2
            self.speed = 0.1
            self.type = "tank"
        else:
            self.hp = 2 + wave
            self.max_hp = self.hp
            self.size_multiplier = 1.0
            self.damage = 1
            self.speed = 0.3
            self.type = "normal"

        self.attack_cooldown = 0

    def animate(self):
        self.anim_timer += 1
        if self.anim_timer >= 5:
            self.anim_timer = 0
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            self.actor.image = self.sprites[self.sprite_index]

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.hypot(dx, dy))

        min_dist = ((PLAYER_SIZE // 2 + 10 * self.size_multiplier) / TILE_SIZE)
        if dist <= min_dist:
            if self.attack_cooldown <= 0:
                player.hp -= self.damage
                self.attack_cooldown = 20
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.animate()

    def draw(self, screen, offset_x, offset_y):
        self.actor.pos = (self.x * TILE_SIZE + offset_x,
                          self.y * TILE_SIZE + offset_y)

        if self.type == "tank":
            original_scale = getattr(self.actor, '_scale', 1.0)
            self.actor._scale = self.size_multiplier
            self.actor.draw()
            self.actor._scale = original_scale
        else:
            self.actor.draw()

        # Barra de vida
        health_bar_width = int(40 * self.size_multiplier)
        health_percentage = self.hp / self.max_hp
        health_width = int(health_bar_width * health_percentage)

        bg_health_rect = Rect(
            (self.actor.pos[0] - health_bar_width // 2,
             self.actor.pos[1] - 35 * self.size_multiplier),
            (health_bar_width, 6)
        )
        screen.draw.filled_rect(bg_health_rect, "darkred")

        if health_width > 0:
            health_rect = Rect(
                (self.actor.pos[0] - health_bar_width // 2,
                 self.actor.pos[1] - 35 * self.size_multiplier),
                (health_width, 6)
            )
            if health_percentage > 0.6:
                color = "green"
            elif health_percentage > 0.3:
                color = "yellow"
            else:
                color = "red"
            screen.draw.filled_rect(health_rect, color)