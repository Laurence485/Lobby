import pickle
from unittest.mock import call, patch

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
def mock_update_player():
    with patch('network.network._update_player') as mock_update_player:
        mock_update_player.return_value = 'mocked update player'
        yield mock_update_player


@pytest.fixture
def mock_create_player(mock_player):
    with patch('network.network._create_player') as mock_create_player:
        mock_create_player.return_value = 'mocked create player'
        yield mock_create_player


@pytest.fixture
def mock_new_player(mock_player):
    with patch('network.network.Player') as mock_new_player_player:
        mock_new_player_player.return_value = mock_player()
        yield mock_new_player_player


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


def test_fetch_player_data_calls_update_player(
    mock_player, mock_other_players, mock_recv_player_data, mock_update_player
):
    fetch_player_data(
        mock_player(), mock_other_players, mock_recv_player_data()
    )

    assert mock_update_player.call_count == len(mock_other_players)


def test_fetch_player_data_cannot_receive_data(
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
    mock_recv_player_data,
    mock_update_player
):
    fetch_player_data(
        mock_player(),
        mock_other_players,
        mock_recv_player_data(mock_player_attributes())
    )

    assert mock_update_player.call_count == 0


def test_fetch_player_data_only_one_player_online(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_recv_player_data,
    mock_update_player
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

    assert mock_update_player.call_count == 0


def test_fetch_player_data_player_disconnected(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_recv_player_data,
    mock_update_player
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

    assert mock_update_player.call_count == 0


def test_delete_player(
    mock_player,
    mock_player_attributes,
    mock_other_players,
):

    player_id = 1
    mock_player_data = mock_player_attributes(player_id=1)[player_id]
    _delete_player(mock_other_players, mock_player_data)

    assert player_id not in mock_other_players


def test_delete_player_invalid_player_key(
    mock_player,
    mock_player_attributes,
    mock_other_players,
):

    player_id = 10
    mock_player_data = mock_player_attributes(player_id=player_id)[player_id]
    _delete_player(mock_other_players, mock_player_data)


def test_update_player(
    mock_player,
    mock_player_attributes,
    mock_other_players,
):
    new_x = 123
    new_y = 456
    _current_step = 4
    mock_player_data = mock_player_attributes(
        player_id=1, x=new_x, y=new_y, _current_step=_current_step
    )[1]
    _update_player(mock_other_players, mock_player_data)

    updated_player = mock_other_players[mock_player_data['id']]
    assert updated_player.x == new_x
    assert updated_player.y == new_y
    assert updated_player.walk_count == _current_step


def test_update_player_calls_create_new_player(
    mock_player,
    mock_player_attributes,
    mock_other_players,
    mock_create_player,
):
    mock_player_data = mock_player_attributes(player_id=10)[10]
    _update_player(mock_other_players, mock_player_data)

    assert mock_create_player.call_count == 1


def test_create_player(
    mock_other_players, mock_player_attributes, mock_new_player
):
    player_id = 99
    mock_player_data = mock_player_attributes(
        x=50, y=50, player_id=player_id, username='My Created Player'
    )[99]
    _create_player(mock_other_players, mock_player_data)

    assert mock_new_player.call_count == 1
    assert mock_new_player.call_args_list == [
        call((50, 50), 99, 'My Created Player')
    ]
    assert player_id in mock_other_players
