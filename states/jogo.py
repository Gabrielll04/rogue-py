from core import config, state_manager

class Jogo:
    def __init__(self, play_sound_callback, keys_callback):
        self.play_sound = play_sound_callback
        self.keys = keys_callback

    def draw(self, screen):
        screen.clear()
        screen.draw.text("JOGO", center=(config.WIDTH/2, config.HEIGHT/2), fontsize=60, color="green")

    def on_key_down(self, key):
        if key == self.keys.ESCAPE:
            from states.menu import Menu
            state_manager.estado_atual = Menu(play_sound_callback=self.play_sound, keys_callback=self.keys)
            if config.SONS_ATIVOS:
                self.play_sound()