from core import config, state_manager
from ui.button import Button
from states.game import Game
from pgzero import music


class Menu:
    def __init__(
        self,
        play_sound_callback,
        keys_callback,
        keyboard_ref,
        config_ref,
        mouse_ref,
    ):
        self.buttons = [
            Button("Jogar", 300, 200),
            Button("Sair", 300, 300),
            Button("Música: ON", 50, 500, 180, 50),
            Button("Sons: ON", 250, 500, 180, 50),
        ]

        self.play_sound = play_sound_callback
        self.keys = keys_callback
        self.keyboard = keyboard_ref
        self.config = config_ref
        self.mouse = mouse_ref

    def draw(self, screen):
        screen.clear()
        screen.draw.text(
            "MENU PRINCIPAL",
            center=(config.WIDTH / 2, 100),
            fontsize=60,
        )
        for button in self.buttons:
            button.draw(screen)

    def on_mouse_move(self, pos, rel, buttons):
        for button in self.buttons:
            button.verify_hover(pos)

    def on_mouse_down(self, pos, button):
        if self.buttons[0].clicked(pos):  # Jogar
            state_manager.current_state = Game(
                play_sound_callback=self.play_sound,
                keys_callback=self.keys,
                keyboard_ref=self.keyboard,
                config_ref=self.config,
                mouse_ref=self.mouse,
            )
            if config.SOUNDS_ACTIVE:
                self.play_sound("click")

        elif self.buttons[1].clicked(pos):  # Sair
            exit()

        elif self.buttons[2].clicked(pos):  # Música ON/OFF
            config.MUSIC_ACTIVE = not config.MUSIC_ACTIVE
            self.buttons[2].text = (
                f"Música: {'ON' if config.MUSIC_ACTIVE else 'OFF'}"
            )
            if config.MUSIC_ACTIVE:
                music.play("bgm")
                music.set_volume(0.5)
            else:
                music.stop()

        elif self.buttons[3].clicked(pos):  # Sons ON/OFF
            config.SOUNDS_ACTIVE = not config.SOUNDS_ACTIVE
            self.buttons[3].text = (
                f"Sons: {'ON' if config.SOUNDS_ACTIVE else 'OFF'}"
            )
            if config.SOUNDS_ACTIVE:
                self.play_sound("click")
