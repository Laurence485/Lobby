import pickle
from unittest.mock import patch

import pytest

from game.errors import ServerError
from network.network import Network, fetch_player_data


@pytest.fixture
def mock_os_config(monkeypatch):
    host = '127.0.0.1'
    port = 12345
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', str(port))

    return host, port


@pytest.fixture
def mock_player():
    def _mock_player(player_id=0):
        class Player:
            def __init__(self, player_id):
                self.id = player_id
                self.username = 'TestUser'
                self.x = 0
                self.y = 0
                self.left = False
                self.right = False
                self.up = False
                self.down = True
                self.standing = True
                self._current_step = 0
                self.walk_count = 0
                self.in_slow_area = False
                self.bike = False
                self.id = False
                self.username = False
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
def mock_other_players(mock_player):
    players = {
                1: mock_player(player_id=1).attributes,
                2: mock_player(player_id=2).attributes,
                3: mock_player(player_id=3).attributes,
                4: mock_player(player_id=4).attributes,
                5: mock_player(player_id=5).attributes
    }
    return players


@pytest.fixture
def mock_recv_player_data(mock_os_config, mock_other_players):
    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.recv.return_value = pickle.dumps(
            mock_other_players
        )
        yield Network()


@pytest.fixture
def mock_no_data_from_server(mock_os_config):
    with patch('socket.socket') as mock_socket:
        mock_player_id = 0
        mock_socket.return_value.recv.return_value = pickle.dumps(
            mock_player_id
        )
        net = Network()
        mock_socket.return_value.recv.return_value = b''
        yield net


def test_init(mock_os_config):
    with patch('socket.socket') as mock_socket:
        mock_player_id = 0
        mock_socket.return_value.recv.return_value = pickle.dumps(
            mock_player_id
        )
        net = Network()

        assert net.addr == mock_os_config
        assert net.data
        net.client.connect.assert_called_with(mock_os_config)


def test_init_server_down(mock_os_config):
    with pytest.raises(ServerError) as err:
        net = Network()

        assert net.addr == mock_os_config
        assert not net.data

    err.match('Could not connect to server.')


def test_fetch_player_data(
    mock_player, mock_other_players, mock_recv_player_data
):

    fetch_player_data(mock_player(), mock_other_players, mock_recv_player_data)


def test_fetch_player_data_cannot_recieve_data(
    mock_player, mock_other_players, mock_no_data_from_server
):
    with pytest.raises(ServerError) as err:
        fetch_player_data(
            mock_player(), mock_other_players, mock_no_data_from_server
        )

    err.match('Could not receive data from server.')


def test_fetch_player_data_ignore_local_user_player_data(
    mock_player, mock_other_players, mock_recv_player_data
):
    # Pass in 1 received player attributes with id matching our player id
    pass


def test_fetch_player_data_only_one_player_online(mock_os_config):
    pass


def test_fetch_player_data_player_disconnected(mock_os_config):
    pass


def test_delete_player():
    pass


def test_delete_player_invalid_player_key():
    pass
