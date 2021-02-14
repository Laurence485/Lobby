import pygame

from enums.base import Base
from game.map import Map
from game.new_game import NewGame
from game.typing import Sprite
from game.utils import get_config
from logger import get_logger
from network.network import Network

log = get_logger(__name__)
config = get_config()

TIME_DIFF_MULTIPLYER = Base.TIME_DIFF_MULTIPLYER.value
WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
CHAT_WINDOW_HEIGHT = config['CHAT_WINDOW_HEIGHT']
GRID_SPACING = config['GRID_SPACING']
GAME_MAP = config['MAP']

if GRID_SPACING != 10:
    raise NotImplementedError('Do not adjust the grid spacing.')


def setup_pygame() -> None:
    pygame.init()
    pygame.display.set_caption('Lobby')
    game_window = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT + CHAT_WINDOW_HEIGHT)
    )

    _start_game_loop(game_window)


def _start_game_loop(game_window: Sprite) -> None:
    game_is_running = True
    clock = pygame.time.Clock()

    Map.load(GAME_MAP)
    # Map(341)
    game = NewGame(game_window, _setup_network(), _get_username())
    while game_is_running:
        for event in pygame.event.get():
            game.check_keyboard_input(event)
            if game.is_typing:
                game.chat_box.text_input.check_input(event)
            # else:
            #     game.chat_box.text_input.draw_entered_text(game_window)
            if event.type == pygame.QUIT:
                game_is_running = False

        dt = clock.tick() * TIME_DIFF_MULTIPLYER

        game.fetch_player_data()

        game.player.check_collisions(
            Map.blocked_nodes, Map.reduced_speed_nodes
        )

        game.player.move(dt)
        game.player.animation_loop()
        game.player.animate(dt)
        game.player.prevent_movement_beyond_screen(dt)

        game.draw_game_objects(dt)
        game.chat_box.text_input.draw(game_window)
        game.chat_box.text_input.draw_previous_text(game_window)
        if not game.is_typing:
            game.chat_box.text_input.store_entered_text(game_window)

        pygame.display.update()


def _get_username() -> str:
    return 'testUser'


def _setup_network() -> Network:
    net = Network()

    if net.data is None:
        log.info('cannot connect to server.')
    else:
        log.info('successfully connected to server.')

    return net


if __name__ == '__main__':
    setup_pygame()
