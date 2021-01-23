import pickle

import pytest

from unittest.mock import patch, Mock
from server.server import Server


@pytest.fixture
def mock_connection(mock_player):
    with patch('socket.socket') as mock_socket:
        mock_socket.recv.return_value = pickle.dumps(mock_player().attributes)
        # Interrupt infinite loop at end of first iteration.
        mock_socket.sendall.side_effect = Mock(side_effect=InterruptedError)
        yield mock_socket


@pytest.fixture
def mock_connection_(mock_player):
    def _mock_connection_(*args, **kwargs):
        with patch('socket.socket') as mock_socket:
            mock_socket.recv.return_value = pickle.dumps(
                mock_player(*args, **kwargs).attributes
            )
            return mock_socket
    return _mock_connection_


def test_init(mock_os_config):
    host, port = mock_os_config
    server = Server()

    assert server.host == host
    assert server.port == port


def test_client_adds_player_attributes(mock_os_config, mock_connection):
    server = Server()
    with pytest.raises(InterruptedError):
        server.client(mock_connection, 0)

    with pytest.raises(InterruptedError):
        server.client(mock_connection, 1)

    with pytest.raises(InterruptedError):
        server.client(mock_connection, 2)

    assert len(server.players) == 3


#  patch isnt working here
def tess_client_updates_player_attributes(mock_os_config, mock_connection_):
    server = Server()
    with pytest.raises(InterruptedError):
        server.client(mock_connection_(), 0)


def test_client_player_disconnected(mock_os_config, mock_connection):
    pass
