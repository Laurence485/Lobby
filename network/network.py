import pickle
import socket

from enums.base import Network_
from game.player import Player
# from game.errors import ServerError
from game.utils import check_os_config
from typing import Union


BUFFER_SIZE = Network_.BUFFER_SIZE.value


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = check_os_config('HOST', 'localhost')
        self.PORT = check_os_config('PORT', 12345)
        self.addr = (self.HOST, self.PORT)
        self.data = self.connect()

    def connect(self) -> Union[bool, None]:
        try:
            self.client.connect(self.addr)
            self.player_id = pickle.loads(self.client.recv(BUFFER_SIZE))
            return True
        except socket.error:
            # raise ServerError("Could not connect to server.")
            print('Could not connect to server.')
            return None

    def send(self, player_attributes: dict) -> Union[dict, None]:
        try:
            self.client.send(pickle.dumps(player_attributes))
            return pickle.loads(self.client.recv(BUFFER_SIZE))
        except socket.error as e:
            print(f'Could not send data to server. Error: {e}.')
            return None


def fetch_player_data(
    this_player: Player,
    other_players: dict[int, Player],
    net: Network
) -> None:
    """Send and receive player data from the server."""

    response = net.send(this_player.attributes)

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
    except KeyError:
        print(
            f'Could not delete player ({data["username"]},'
            f' id: {data["id"]}).'
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
