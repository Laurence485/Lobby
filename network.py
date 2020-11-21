import socket
import pickle
import yaml

with open('config/base.yaml', 'r') as config_file:
    config = yaml.load(config_file, yaml.Loader)

HOST = config['HOST']
PORT = config['PORT']
buffer_size = config['BUFFER_SIZE']


class Network:
    def __init__(self, username):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
        self.addr = (self.HOST, self.PORT)
        self.username = username
        self.data = self.connect(username)

    def connect(self, username):
        try:  # connect and get shuffled maps and player ID
            self.client.connect(self.addr)
            self.client.send(pickle.dumps(username))
            self.maps, self.playerID, self.leaderboard = pickle.loads(
                self.client.recv(buffer_size)
            )
            return True
        except socket.error as e:
            #  Raise ServerError
            print(f"could not connect to server. Error: {e}")
            return None

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(buffer_size))
        except socket.error as e:
            print(f"could not connect to server. Error: {e}")
