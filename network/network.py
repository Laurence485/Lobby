import pickle
import socket

from game.player import Player
# from game.errors import ServerError
from game.utils import get_config
from typing import Union

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
BUFFER_SIZE = config['BUFFER_SIZE']


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
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


def fetch_player_data(
    this_player: Player,
    other_players: dict[int, Player],
    net: Network
) -> None:
    """Send and receive player data from the server."""

    response = net.send(this_player.attributes)

    for data in response.values():
        # No players have connected yet.
        if data['username'] is None:
            return None
        # Xpos was set to None, so this player has disconnected.
        elif data['x'] is None:
            try:
                del other_players[data['id']]
            except KeyError:
                pass
            else:
                print(f'{data["username"]} disconnected.')
            finally:
                return None
        try:
            player = other_players[data['id']]
        # Create new player instance if we haven't done so yet.
        except KeyError:
            other_players[data['id']] = Player(
                (data['x'], data['y']),
                data['id'],
                data['username']
            )
            print(f'{data["username"]} connected.')
        # Update player data from server.
        else:
            for attribute, value in data.items():
                if attribute == '_current_step':
                    setattr(player, 'walk_count', value)
                else:
                    setattr(player, attribute, value)
