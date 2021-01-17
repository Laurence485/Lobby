import pickle
from unittest.mock import patch

import pytest

from game.errors import ServerError
from network.network import (
    Network,
    _delete_player,
    _update_player,
    fetch_player_data,
    _create_player
)


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
def mock_player_attributes(mock_player):
    def _mock_player_attributes(player_id=0, *args, **kwargs):
        return {player_id: mock_player(player_id, *args, **kwargs).attributes}
    return _mock_player_attributes


@pytest.fixture
def mock_other_players(mock_player):
    players = {
                1: mock_player(player_id=1),
                2: mock_player(player_id=2),
                3: mock_player(player_id=3),
                4: mock_player(player_id=4),
                5: mock_player(player_id=5)
    }
    return players


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
def mock_recv_player_data(mock_os_config, mock_other_players_attributes):
    def _mock_recv_player_data(players=mock_other_players_attributes):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recv.return_value = pickle.dumps(
                players
            )
            return Network()

    return _mock_recv_player_data


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


@pytest.fixture
def mock_create_player(mock_player):
    with patch('network.network.Player') as mock_create_player:
        mock_create_player.return_value = mock_player()
        yield mock_create_player


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
    fetch_player_data(
        mock_player(), mock_other_players, mock_recv_player_data()
    )


def test_fetch_player_data_cannot_recieve_data(
    mock_player, mock_other_players, mock_no_data_from_server
):
    with pytest.raises(ServerError) as err:
        fetch_player_data(
            mock_player(), mock_other_players, mock_no_data_from_server
        )

    err.match('Could not receive data from server.')


def test_fetch_player_data_ignore_local_user_player_data(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_recv_player_data
):
    fetch_player_data(
        mock_player(),
        mock_other_players,
        mock_recv_player_data(mock_player_attributes())
    )


def test_fetch_player_data_only_one_player_online(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_recv_player_data
):
    fetch_player_data(
        mock_player(),
        mock_other_players,
        mock_recv_player_data(
            mock_player_attributes(
                player_id=1, username=None
            )
        )
    )


def test_fetch_player_data_player_disconnected(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_recv_player_data
):
    fetch_player_data(
        mock_player(),
        mock_other_players,
        mock_recv_player_data(
            mock_player_attributes(
                player_id=1, x=None
            )
        )
    )


def test_delete_player(
    mock_player,
    mock_player_attributes,
    mock_other_players,
):

    mock_player_data = mock_player_attributes(player_id=1)[1]
    _delete_player(mock_other_players, mock_player_data)


def test_delete_player_invalid_player_key(
    mock_player,
    mock_player_attributes,
    mock_other_players,
):

    mock_player_data = mock_player_attributes(player_id=10)[10]
    _delete_player(mock_other_players, mock_player_data)


def test_update_player(
    mock_player,
    mock_player_attributes,
    mock_other_players,
):
    new_x = 123
    new_y = 456
    mock_player_data = mock_player_attributes(
        player_id=1, x=new_x, y=new_y
    )[1]
    _update_player(mock_other_players, mock_player_data)

    assert mock_other_players[mock_player_data['id']].x == new_x
    assert mock_other_players[mock_player_data['id']].y == new_y


def test_update_player_create_new_player(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_create_player,
):
    mock_player_data = mock_player_attributes(player_id=10)[10]

    _update_player(mock_other_players, mock_player_data)


def test_create_player(
    mock_other_players, mock_player_attributes, mock_create_player
):
    mock_player_data = mock_player_attributes(player_id=10)[10]
    _create_player(mock_other_players, mock_player_data)
