import math
import pygame.image
import pygame.mixer

from random import choice
from typing_extras import Sprite


def random_xy(nodes: list) -> tuple:
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
    player_id: int = 0
) -> Sprite:

    return pygame.image.load(
        f'{img_dir} {player_id}/{img}.png'
    ).convert_alpha()


def sound(path_to_sound_file: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(path_to_sound_file)


def sync_value_with_grid(n: float) -> int:
    """round n to nearest 10 (grid spacing size)."""
    floor = (n // 10) * 10
    ceil = math.ceil(n / 10) * 10

    return int(floor) if n - floor < 5 else int(ceil)
