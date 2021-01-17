import pickle
import socket

from enums.base import Network_
from game.player import Player
from game.errors import ServerError
from game.utils import check_os_config


BUFFER_SIZE = Network_.BUFFER_SIZE.value


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = check_os_config('HOST')
        self.PORT = check_os_config('PORT')
        self.addr = (self.HOST, self.PORT)
        self.data = self._connect()

    def _connect(self) -> bool:
        try:
            self.client.connect(self.addr)
            self.player_id = pickle.loads(self.client.recv(BUFFER_SIZE))
            return True
        except socket.error as e:
            raise ServerError(f'Could not connect to server. Error: {e}.')

    def _send(self, player_attributes: dict) -> dict:
        try:
            self.client.send(pickle.dumps(player_attributes))
            return pickle.loads(self.client.recv(BUFFER_SIZE))
        except EOFError as e:
            raise ServerError(
                f'Could not receive data from server. Error: {e}.'
            )


def fetch_player_data(
    this_player: Player,
    other_players: dict[int, Player],
    net: Network
) -> None:
    """Send and receive player data from the server."""

    response = net._send(this_player.attributes)

    for data in response.values():
        if data['id'] == this_player.id:
            continue
        # No players have connected yet.
        if data['username'] is None:
            return None
        # Xpos was set to None, so this player has disconnected.
        if data['x'] is None:
            _delete_player(other_players, data)
            return None

        _update_player(other_players, data)


def _delete_player(other_players: dict[int, Player], data: dict) -> None:
    try:
        del other_players[data['id']]
    except KeyError as e:
        print(
            f'Could not delete player ({data["username"]},'
            f' id: {data["id"]}). Error: {e}.'
        )
    else:
        print(f'Deleted player with id {data["id"]}.')
        print(f'{data["username"]} disconnected.')


def _update_player(other_players: dict[int, Player], data: dict) -> None:
    """Update player data from the server if player has been created,
    otherwise create the player."""
    try:
        player = other_players[data['id']]
    except KeyError:
        _create_player(other_players, data)
        print(f'{data["username"]} connected.')
    else:
        for attribute, value in data.items():
            if attribute == '_current_step':
                setattr(player, 'walk_count', value)
            else:
                setattr(player, attribute, value)


def _create_player(other_players: dict[int, Player], data: dict) -> None:
    other_players[data['id']] = Player(
        (data['x'], data['y']),
        data['id'],
        data['username']
    )
