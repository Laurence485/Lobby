#  For successful testing, the time should be controlled by the game not the clock

import pytest

from game.utils import get_config
from unittest.mock import call, Mock


@pytest.fixture(scope='session')
def base_config():
    return get_config('base')


@pytest.fixture
def pygame(base_config):
    pygame = Mock()
    pygame.init()
    pygame.get_caption.return_value = ('Lobby', 'Lobby')
    pygame.get_window_size.return_value = (
        base_config['WINDOW_WIDTH'], base_config['WINDOW_HEIGHT']
    )
    return pygame


def test_setup_pygame(pygame):
    assert pygame.init.call_args == call()
    assert pygame.get_caption.return_value == ('Lobby', 'Lobby')
    assert pygame.get_window_size.return_value == (400, 400)


class TestNewGame:

    # Test instance vars

    def test_check_keyboard_input(self):
        pass

    # Add values from config file
    #  Add test configs: verbose, coverage, isort, mypy, py versions to tox
    # Where should tests for the nested methods e.g. game.player.xyz() go?
    #  these should be tested in their own files... also only test
    #  stuff which can break...no need to test everything
