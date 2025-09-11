import math
from pgzero.rect import Rect
from pgzero.actor import Actor

TILE_SIZE = 10
PLAYER_SIZE = 40

class Player:
    def __init__(self, x, y, play_sound, config, keyboard, keys):
        self.x = x
        self.y = y
        self.hp = 10
        self.max_hp = 10
        self.damage = 1
        self.fire_rate = 20
        self.speed = 0.6
        self.direction = "right"

        self.fire_cooldown = 0
        self.bullets = []

        self.play_sound = play_sound
        self.config = config
        self.keyboard = keyboard
        self.keys = keys

        # sprites
        self.idle_sprites = [
            "player_idle1", "player_idle2", "player_idle3", "player_idle4",
            "player_idle5", "player_idle6", "player_idle7", "player_idle8",
            "player_idle9"
        ]
        self.walk_sprites = [
            "player_walk1", "player_walk2", "player_walk3", "player_walk4"
        ]
        self.sprite_index = 0
        self.anim_timer = 0
        self.actor = Actor(self.idle_sprites[0])

    def animate(self, moving):
        self.anim_timer += 1
        if self.anim_timer >= 4:
            self.anim_timer = 0
            sprite_list = self.walk_sprites if moving else self.idle_sprites
            self.sprite_index = (self.sprite_index + 1) % len(sprite_list)
            base_name = sprite_list[self.sprite_index]
            if self.direction == "left":
                self.actor.image = base_name + "_left"
            else:
                self.actor.image = base_name

    def move(self):
        moving = False
        if self.keyboard[self.keys.W]:
            self.y -= self.speed
            moving = True
        if self.keyboard[self.keys.S]:
            self.y += self.speed
            moving = True
        if self.keyboard[self.keys.A]:
            self.x -= self.speed
            moving = True
            self.direction = "left"
        if self.keyboard[self.keys.D]:
            self.x += self.speed
            moving = True
            self.direction = "right"

        self.animate(moving)

    def update(self, mouse_left_pressed, mouse_pos):
        self.move()

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        if mouse_left_pressed and self.fire_cooldown == 0:
            self.shoot(mouse_pos)
            self.fire_cooldown = self.fire_rate

    def shoot(self, mouse_pos):
        mx, my = mouse_pos
        mouse_x = (mx / TILE_SIZE + self.x -
                   (self.config.WIDTH // 2) / TILE_SIZE)
        mouse_y = (my / TILE_SIZE + self.y -
                   (self.config.HEIGHT // 2) / TILE_SIZE)

        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        self.bullets.append({
            "x": self.x,
            "y": self.y,
            "dx": dx,
            "dy": dy,
            "speed": 2
        })

        self.play_sound("shoot")

    def draw(self, screen, offset_x, offset_y):
        self.actor.pos = (self.config.WIDTH // 2,
                          self.config.HEIGHT // 2)
        self.actor.draw()

        for bullet in self.bullets:
            rect = Rect((bullet["x"] * TILE_SIZE + offset_x,
                         bullet["y"] * TILE_SIZE + offset_y), (5, 5))
            screen.draw.filled_rect(rect, "yellow")