from unittest.mock import patch

import pickle
import pytest

from game.errors import ServerError
from network.network import Network


@pytest.fixture
def mock_os_config(monkeypatch):
    host = '127.0.0.1'
    port = 12345
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', str(port))

    return host, port


def test_init(mock_os_config):
    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.recv.return_value = pickle.dumps(0)
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


def test_fetch_player_data(mock_os_config):
    pass


def test_fetch_player_data_cannot_send_data(mock_os_config):
    pass


def test_fetch_player_data_ignore_local_user_player_data(mock_os_config):
    pass


def test_fetch_player_data_only_one_player_online(mock_os_config):
    pass


def test_fetch_player_data_player_disconnected(mock_os_config):
    pass


def test_delete_player():
    pass


def test_delete_player_invalid_player_key():
    pass
