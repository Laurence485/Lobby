#  Add verbose, coverage, isort, mypy to tox
#  For successful testing time should be controlled by the game not the clock

import pygame

from pytest_testconfig import config
from game.start_game import setup_pygame

def test_setup_pygame():
    setup_pygame()

    assert pygame.display.get_init()
    # assert pygame.display.
