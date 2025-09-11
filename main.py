import pgzrun
from pgzero import music

from core import config, state_manager
from states.menu import Menu


def play_sound(nome):
    if config.SOUNDS_ACTIVE:
        getattr(sounds, nome).play()


state_manager.current_state = Menu(
    play_sound_callback=play_sound,
    keys_callback=keys,
    keyboard_ref=keyboard,
    config_ref=config,
    mouse_ref=mouse,
)

music.play("bgm")
music.set_volume(0.5)


def draw():
    state_manager.current_state.draw(screen)


def update():
    if hasattr(state_manager.current_state, "update"):
        state_manager.current_state.update()


def on_mouse_move(pos, rel, buttons):
    if hasattr(state_manager.current_state, "on_mouse_move"):
        state_manager.current_state.on_mouse_move(pos, rel, buttons)


def on_mouse_down(pos, button):
    if hasattr(state_manager.current_state, "on_mouse_down"):
        state_manager.current_state.on_mouse_down(pos, button)


def on_key_down(key):
    if hasattr(state_manager.current_state, "on_key_down"):
        state_manager.current_state.on_key_down(key)


pgzrun.go()
