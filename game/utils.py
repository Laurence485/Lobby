import math
import os
import yaml

from copy import copy
from enums.base import Network_
from random import choice

import pygame.image
import pygame.mixer

from game.errors import ConfigError
from game.typing import Sprite


def check_os_config(env_var: str, attribute: str = None) -> str:
    if attribute:
        return attribute

    try:
        return os.environ[env_var]
    except KeyError:
        error = (
            f'Environment variable {env_var} not set'
            ' or not passed to Server.'
            )
        raise ConfigError(error)


def get_config(filename: str = 'base') -> dict:
    with open(f'config/{filename}.yaml', 'r') as config_file:
        return yaml.safe_load(config_file)


def random_xy(nodes: set) -> tuple:
    if not nodes:
        print('Warning: no nodes supplied.')
    return choice(tuple(nodes))


def load_map_img(
    img: str,
    img_format: str = 'png',
    img_dir: str = 'sprites/objects'
) -> Sprite:
    return pygame.image.load(f'{img_dir}/{img}.{img_format}')


def load_player_img(
    img: str,
    img_dir: str = 'sprites/player',
    img_id: int = 0
) -> Sprite:
    return pygame.image.load(
        f'{img_dir} {img_id}/{img}.png'
    ).convert_alpha()


def network_data() -> dict:
    """The player data that gets sent back and forth from the server.
    """
    return copy(Network_.PLAYER_ATTRIBUTES.value)


def sound(path_to_sound_file: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(path_to_sound_file)


def sync_value_with_grid(n: float) -> int:
    """round n to nearest 10 (grid spacing size)."""
    floor = (n // 10) * 10
    ceil = math.ceil(n / 10) * 10

    return int(floor) if n - floor < 5 else int(ceil)
