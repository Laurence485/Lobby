import pygame.image
import pygame.mixer

# from map import nodes
from random import choice


def random_xy(nodes: list) -> tuple:
    if not nodes:
        print('Warning: no nodes supplied.')
    return choice(tuple(nodes))


def load_player_img(
    img: str,
    img_dir: str = 'sprites/player',
    player_id: int = 0
) -> pygame.Surface:

    return pygame.image.load(
        f'{img_dir} {player_id}/{img}.png'
    ).convert_alpha()


def sound(path_to_sound_file: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(path_to_sound_file)
