import pytest

from fakeredis import FakeStrictRedis
from unittest.mock import patch


@pytest.fixture
def mock_os_config(monkeypatch):
    host = '127.0.0.1'
    port = 12345
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', str(port))

    return host, port


@pytest.fixture
def mock_player():
    def _mock_player(
        player_id=0, username='TestUser', x=0, y=0, _current_step=0
    ):
        class Player:
            def __init__(self):
                self.id = player_id
                self.username = username
                self.x = x
                self.y = y
                self.left = False
                self.right = False
                self.up = False
                self.down = True
                self.standing = True
                self._current_step = _current_step
                self.walk_count = 0
                self.in_slow_area = False
                self.bike = False
                self.attributes = {
                    'x': self.x,
                    'y': self.y,
                    'left': self.left,
                    'right': self.right,
                    'up': self.up,
                    'down': self.down,
                    'standing': self.standing,
                    '_current_step': self._current_step,
                    'in_slow_area': self.in_slow_area,
                    'bike': self.bike,
                    'id': self.id,
                    'username': self.username
                }
        return Player()
    return _mock_player


@pytest.fixture
def mock_other_players_attributes(mock_player):
    players = {
        1: mock_player(player_id=1).attributes,
        2: mock_player(player_id=2).attributes,
        3: mock_player(player_id=3).attributes,
        4: mock_player(player_id=4).attributes,
        5: mock_player(player_id=5).attributes
    }
    return players


@pytest.fixture
def mock_strict_redis():
    with patch('redis.StrictRedis') as redis:
        redis.return_value = FakeStrictRedis()
        yield redis
        redis.return_value.flushall()


@pytest.fixture
def mock_messages_window_width():
    with patch('game.messages.WINDOW_WIDTH', 400) as window_width:
        yield window_width
