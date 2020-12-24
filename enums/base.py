from enum import Enum


class Player_(Enum):
    WIDTH = 15   # Used for collision detection.
    HEIGHT = 19  # Used for collision detection.


class Network_(Enum):
    PLAYER_ATTRIBUTES = {
        'x': 0,
        'y': 0,
        'L': False,
        'R': False,
        'U': False,
        'D': True,
        'standing': True,
        'current_step': 0,
        'hit slow': False,
        'bike': False,
        'id': 0,
        'username': 'defaultuser',
    }


class Window(Enum):
    WALL_WIDTH = 70  # Rock wall on the right of the screen.
    GRID_COLOUR = 125
