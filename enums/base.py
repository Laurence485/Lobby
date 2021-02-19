from enum import Enum


class Base(Enum):
    TIME_DIFF_MULTIPLYER = 0.01
    PLAYER_COLOURS = 6  # Total number of different player colours.
    # Don't let text exceed chat box width minus this amount.
    TEXT_DISTANCE_FROM_EDGE = 10


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
        'id': -1,
        'username': None,
    }
    BUFFER_SIZE = 2048


class Server_(Enum):
    MAX_CONNECTIONS = 50


class Window(Enum):
    WALL_WIDTH = 70  # Rock wall on the right of the screen.
    GRID_COLOUR = 125
