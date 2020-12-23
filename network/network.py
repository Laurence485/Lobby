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
    def __init__(self, username: str):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
        self.addr = (self.HOST, self.PORT)
        self.username = username
        self.data = self.connect(username)  # ???????

    def connect(self, username: str) -> Union[bool, None]:
        try:
            self.client.connect(self.addr)
            self.client.send(pickle.dumps(username))
            self.player_id = pickle.loads(self.client.recv(BUFFER_SIZE))
            return True
        except socket.error:
            # raise ServerError("Could not connect to server.")
            print('Could not connect to server.')
            return None

    def send(self, data: dict) -> Union[dict, None]:
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(BUFFER_SIZE))
        except socket.error as e:
            print(f'Could not send data to server. Error: {e}.')


def fetch_player_data(this_player: Player, net: Network) -> None:
    """Get player data from server and map data to local
    player objects."""

    # Get attributes of other players
    fetched_player_data = net.send(this_player.attributes())
    f = fetched_player_data
    p2 = this_player.p2

    # create new player instance if:
    # 1) we haven't already created an instance
    # 2) they have an ID (they are connected to server)
    if p2 is None:
        print(f'{f["username"]} connected.')
        this_player.p2 = Player((f['x'], f['y']), f['id'])

    # Update player from server
    else:
        p2.x, p2.y = f['x'], f['y']
        p2.left, p2.right, p2.up, p2.down = f['L'], f['R'], f['U'], f['D']
        p2.standing, p2.walk_count = f['standing'], f['walk count']
        p2.hit_slow, p2.bike = f['hit slow'], f['bike']
        p2.id = f['id']
        p2.username = f['username']
