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


def fetch_player_data(this_player: Player, net: Network) -> None:
    """Send and receive player data from the server."""

    received_data = net.send(this_player.attributes)

    # The other player has not yet connected.
    if received_data['id'] is None:
        return None

    p2 = getattr(this_player, 'p2', None)

    # Create new player instance if we haven't done so yet.
    if p2 is None:
        print(f'{received_data["username"]} connected.')
        this_player.p2 = Player(
            (received_data['x'], received_data['y']),
            received_data['id'],
            received_data['username']
        )
    # Update player data from server
    else:
        for attribute, value in received_data.items():
            if attribute == '_current_step':
                setattr(p2, 'walk_count', value)
            else:
                setattr(p2, attribute, value)
