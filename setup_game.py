import pygame

from game.map import Map
from game.new_game import NewGame
from game.typing import Sprite
from game.utils import get_config
from network.network import Network

config = get_config()

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
chat_window_height = config['CHAT_WINDOW_HEIGHT']
grid_spacing = config['GRID_SPACING']
framerate = config['FRAMERATE']
game_map = config['MAP']

if grid_spacing != 10:
    raise NotImplementedError('Do not adjust the grid spacing.')


def setup_pygame() -> None:
    pygame.init()
    pygame.display.set_caption('Lobby')
    game_window = pygame.display.set_mode(
        (window_width, window_height + chat_window_height)
    )

    _start_game_loop(game_window)


def _start_game_loop(game_window: Sprite) -> None:
    game_is_running = True
    clock = pygame.time.Clock()

    Map.load(game_map)
    # Map(341)
    game = NewGame(game_window, _setup_network(), _get_username())
    while game_is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_running = False
            game.check_keyboard_input(event)
            if game.is_typing:
                game.chat_box.text_input.check_input(event)

        game.fetch_player_data()
        game.player.check_collisions(
            Map.blocked_nodes, Map.reduced_speed_nodes
        )
        dt = clock.tick() * 0.01
        game.player.move(dt)
        game.player.animate(dt)
        game.player.prevent_movement_beyond_screen(dt)
        game.draw_game_objects(dt)
        game.chat_box.text_input.draw(game_window)
        game.player.animation_loop()
        pygame.display.update()


def _get_username() -> str:
    return 'testUser'


def _setup_network() -> Network:
    net = Network()

    if net.data is None:
        print('cannot connect to server.')
    else:
        print('successfully connected to server.')

    return net


if __name__ == '__main__':
    setup_pygame()
