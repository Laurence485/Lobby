from enum import Enum


class Player_(Enum):
    WIDTH = 15   # Used for collision detection.
    HEIGHT = 19  # Used for collision detection.


class Network_(Enum):
    PLAYER_ATTRIBUTES = {
        'x': 0,
        'y': 0,
        'left': False,
        'right': False,
        'up': False,
        'down': True,
        'standing': True,
        # We add the current step here instead of the walk count as the
        # step may be ahead of the walk count at the time the attributes
        # are sent to the server.
        '_current_step': 0,
        'in_slow_area': False,
        'bike': False,
        'id': None,
        'username': 'defaultuser',
    }


class Window(Enum):
    WALL_WIDTH = 70  # Rock wall on the right of the screen.
    GRID_COLOUR = 125
