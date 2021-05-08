import pygame
import sys

from argparse import ArgumentParser, Namespace
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


def parse_args(args) -> Namespace:
    parser = ArgumentParser(description='Generate a new map.')
    parser.add_argument(
        '-m',
        '--map',
        type=str,
        default=None,
        help='The name of the map to generate.',
    )
    parser.add_argument(
        '-s',
        '--seed',
        type=str,
        default=None,
        help='The random seed to use for map generation.',
    )
    args = parser.parse_args()
    return args


def setup_pygame(**kwargs) -> None:
    pygame.init()
    pygame.display.set_caption('Lobby')
    game_window = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT + CHAT_WINDOW_HEIGHT)
    )

    if kwargs:
        Map(**kwargs)
    else:
        _game_loop(game_window)


def _game_loop(game_window: Sprite) -> None:
    game_is_running = True
    clock = pygame.time.Clock()

    Map.load(GAME_MAP)
    game = NewGame(game_window, _setup_network(), _get_username())
    while game_is_running:
        for event in pygame.event.get():
            game.check_keyboard_input(event)
            if game.is_typing:
                game.chat_box.text_input.check_input(event)
            if event.type == pygame.QUIT:
                game_is_running = False

        # Time diff to determine frame rate based on game clock.
        dt = clock.tick() * TIME_DIFF_MULTIPLYER

        game.fetch_player_data()

        _player_methods(game, dt)
        game.draw_game_objects(dt)

        _chat_box_methods(game, game_window)
        game.hover_messages.draw(game.player, NewGame.other_players)
        game.hover_messages.delete_expired_messages()

        if not game.is_typing:
            game.chat_box.text_input.save_message(game_window, game.player.id)

        pygame.display.update()


def _player_methods(game: NewGame, dt: int) -> None:
    game.player.check_collisions(Map.blocked_nodes, Map.reduced_speed_nodes)
    game.player.move(dt)
    game.player.animation_loop()
    game.player.animate(dt)
    game.player.prevent_movement_beyond_screen(dt)


def _chat_box_methods(game: NewGame, game_window: Sprite) -> None:
    game.chat_box.text_input.draw(game_window)
    game.chat_box.text_input.draw_messages(game_window)
    game.chat_box.text_input.get_new_messages(game.hover_messages)
    game.chat_box.text_input.delete_old_msg_ids()


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
    args = parse_args(sys.argv[1:])
    if args.map:
        setup_pygame(seed_=args.seed, map_name=args.map)
    else:
        setup_pygame()
