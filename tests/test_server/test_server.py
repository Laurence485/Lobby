import pickle

import pytest

from unittest.mock import patch, Mock
from server.server import Server


@pytest.fixture
def mock_connection_interrupt(mock_player):
    def _mock_connection_interrupt(*args, **kwargs):
        with patch('socket.socket') as mock_socket:
            mock_socket.recv.return_value = pickle.dumps(
                mock_player(*args, **kwargs).attributes
            )
            # Interrupt infinite loop at end of first iteration.
            mock_socket.sendall.side_effect = Mock(
                side_effect=InterruptedError
            )
            return mock_socket
    return _mock_connection_interrupt


@pytest.fixture
def mock_connection():
    with patch('socket.socket') as mock_socket:
        mock_socket.recv.return_value = pickle.dumps('test')
        yield mock_socket


@pytest.fixture
def mock_delete_disconnected_players_interrupt():
    with patch.object(Server, '_delete_disconnected_players') as mock_method:
        mock_method.side_effect = Mock(side_effect=InterruptedError)
        yield mock_method


@pytest.fixture
def mock_connection_no_data():
    with patch('socket.socket') as mock_socket:
        mock_socket.recv.return_value = b''
        yield mock_socket


def test_init(mock_os_config):
    host, port = mock_os_config
    Server()

    assert Server.host == host
    assert Server.port == port


def test_client_adds_player_attributes(
    mock_os_config, mock_connection_interrupt
):
    server = Server()
    with pytest.raises(InterruptedError):
        server.client(mock_connection_interrupt(), 0)

    with pytest.raises(InterruptedError):
        server.client(mock_connection_interrupt(), 1)

    with pytest.raises(InterruptedError):
        server.client(mock_connection_interrupt(), 2)

    assert len(server.players) == 3


@pytest.mark.parametrize('test_user', [
    (0, 'TEST_USER_1', 50, 100),
    (1, 'TEST_USER_2', 123, 456),
    (2, 'TEST_USER_3', 23, 22)
    ])
def test_client_updates_player_attributes(
    mock_os_config, mock_connection_interrupt, test_user
):
    server = Server()
    player_id, username, x, y = test_user

    with pytest.raises(InterruptedError):
        server.client(mock_connection_interrupt(*test_user), player_id)

    assert server.players[player_id]['username'] == username
    assert server.players[player_id]['x'] == x
    assert server.players[player_id]['y'] == y


def test_client_player_disconnected(mock_os_config, mock_connection_no_data):
    server = Server()
    server.client(mock_connection_no_data, 0)


def test_server_has_disconnected_players(
    mock_os_config,
    mock_connection,
    mock_delete_disconnected_players_interrupt
):
    server = Server()
    server.disconnected_player_ids = [4, 2]
    with pytest.raises(InterruptedError):
        server.client(mock_connection, 0)


def test_disconnect_player(mock_os_config, mock_other_players_attributes):
    server = Server()
    server.players = mock_other_players_attributes
    id_to_disconnect = 2
    server._disconnect_player(player_id=id_to_disconnect)

    assert server.players[id_to_disconnect]['x'] is None
    assert id_to_disconnect in server.disconnected_player_ids


def test_delete_disconnected_players(
    mock_os_config, mock_other_players_attributes
):
    server = Server()
    server.players = mock_other_players_attributes
    server.disconnected_player_ids = list(mock_other_players_attributes.keys())
    server._delete_disconnected_players()

    assert server.players == {}
    assert server.disconnected_player_ids == []


def test_delete_disconnected_players_player_not_found(
    mock_os_config, mock_player
):
    server = Server()
    test_player = {1: mock_player().attributes}
    server.players = test_player
    server.disconnected_player_ids = [4, 8]
    server._delete_disconnected_players()

    assert server.players == test_player
    assert server.disconnected_player_ids == []


def test_reset_players(mock_os_config, mock_other_players_attributes):
    server = Server()
    server.players = mock_other_players_attributes
    Server.current_player_id = 99
    server._reset_players()

    assert server.players == {}
    assert Server.current_player_id == 0
