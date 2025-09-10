import pgzrun
from core import config, state_manager
from states.menu import Menu

# Estado inicial
state_manager.estado_atual = Menu(
    play_sound_callback=sounds.click.play,
    keys_callback=keys,
    keyboard_ref=keyboard,
    config_ref=config,
    mouse_ref=mouse
)

# Música inicial
music.play("bgm")
music.set_volume(0.5)

def draw():
    state_manager.estado_atual.draw(screen)

def update():
    if hasattr(state_manager.estado_atual, "update"):
        state_manager.estado_atual.update()

def on_mouse_move(pos, rel, buttons):
    if hasattr(state_manager.estado_atual, "on_mouse_move"):
        state_manager.estado_atual.on_mouse_move(pos, rel, buttons)

def on_mouse_down(pos, button):
    if hasattr(state_manager.estado_atual, "on_mouse_down"):
        state_manager.estado_atual.on_mouse_down(pos, button)

def on_key_down(key):
    if hasattr(state_manager.estado_atual, "on_key_down"):
        state_manager.estado_atual.on_key_down(key)

pgzrun.go()
