#  For successful testing, the time should be controlled by the game not the clock

import pytest

from pytest_testconfig import config

from unittest.mock import Mock

# We dont actually need (or want) to Mock here. We should use yield to setup and teardown pygame
# We can mock tests for the db and server though
@pytest.fixture
def pygame():
    pygame = Mock()
    pygame.init()
    pygame.get_init.return_value = True
    pygame.get_caption.return_value = ('Lobby', 'Lobby')
    pygame.get_window_size.return_value = (400, 400)
    return pygame


def test_setup_pygame(self, pygame):
    pygame.init.assert_called_once()
    assert pygame.get_init.return_value
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
