from enum import Enum


class Player(Enum):
    WIDTH = 15   # Used for collision detection.
    HEIGHT = 19  # Used for collision detection.


class Window(Enum):
    WALL_WIDTH = 70  # Rock wall on the right of the screen.
    GRID_COLOUR = 125
