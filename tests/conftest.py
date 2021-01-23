import pytest


@pytest.fixture
def mock_os_config(monkeypatch):
    host = '127.0.0.1'
    port = 12345
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', str(port))

    return host, port


@pytest.fixture
def mock_player():
    def _mock_player(player_id=0, username='TestUser', x=0, y=0):
        class Player:
            def __init__(self, player_id):
                self.id = player_id
                self.username = username
                self.x = x
                self.y = y
                self.left = False
                self.right = False
                self.up = False
                self.down = True
                self.standing = True
                self._current_step = 0
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
        return Player(player_id)
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
