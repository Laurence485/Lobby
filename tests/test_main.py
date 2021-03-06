from unittest.mock import Mock, call, patch

import pytest

from game.utils import get_config


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


@pytest.fixture
def mock_config():
    with patch('game.utils.get_config') as config:
        config.return_value = {
            'WINDOW_WIDTH': 400,
            'WINDOW_HEIGHT': 400,
            'CHAT_WINDOW_HEIGHT': 80,
            'GRID_SPACING': 400,
            'FRAMERATE': 10,
            'MAP': 10,
            'BACKGROUND_IMG': 10,
            'PLAYER_VELOCITY': 10,
            'BIKE_SOUND': 10,
            'MUSHROOM_SOUND': 10,
            'GRASS_SPEED': 6,
            'WATER_SPEED': 4,
            'MAX_CONNECTIONS': 5,
        }
        yield config


def test_invalid_grid_spacing(mock_config):
    with pytest.raises(NotImplementedError) as err:
        import main  # noqa

    err.match('Do not adjust the grid spacing.')

    grid_spacing = mock_config.return_value['GRID_SPACING']
    assert grid_spacing != 10


def test_setup_pygame(pygame):
    assert pygame.init.call_args == call()
    assert pygame.get_caption.return_value == ('Lobby', 'Lobby')
    assert pygame.get_window_size.return_value == (400, 400)
