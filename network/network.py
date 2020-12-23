import pickle
import socket

# from game.errors import ServerError
from game.utils import get_config
from typing import Union

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
buffer_size = config['BUFFER_SIZE']


class Network:
    def __init__(self, username: str):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
        self.addr = (self.HOST, self.PORT)
        self.username = username
        self.data = self.connect(username)  # ??

    def connect(self, username: str) -> Union[bool, None]:
        try:
            self.client.connect(self.addr)
            self.client.send(pickle.dumps(username))
            self.player_id = pickle.loads(self.client.recv(buffer_size))
            return True
        except socket.error:
            # raise ServerError("Could not connect to server.")
            print('Could not connect to server.')
            return None

    def send(self, data: dict) -> dict:
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(buffer_size))
        except socket.error as e:
            print(f'Could not send data to server. Error: {e}.')
