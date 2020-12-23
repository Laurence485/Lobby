from enum import Enum


class Base(Enum):
    PLAYER_WIDTH = 15   # Used for collision detection.
    PLAYER_HEIGHT = 19  # Used for collision detection.
    WINDOW_WALL_WIDTH = 70  # Rock wall on the right of the screen.


class Player(Enum):
    WIDTH = 15   # Used for collision detection.
    HEIGHT = 19  # Used for collision detection.


class Window(Enum):
    WALL_WIDTH = 70  # Rock wall on the right of the screen.
