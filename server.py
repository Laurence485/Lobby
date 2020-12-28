import pickle
import socket

from copy import deepcopy
from game.utils import get_config, network_data
from _thread import start_new_thread

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
BUFFER_SIZE = config['BUFFER_SIZE']
CONNECTIONS = config['MAX_CONNECTIONS']

current_player_id = 0
players = {}


def client(conn, player_id: int) -> None:
    with conn:
        conn.send(pickle.dumps(player_id))

        players[player_id] = network_data()

        while True:
            try:
                player_attributes = pickle.loads(conn.recv(BUFFER_SIZE))
            except EOFError:
                disconnect_player(player_id)
                break
            else:
                players[player_id] = player_attributes

                if not player_attributes:
                    print('Disconnected from server.')
                    break
                else:
                    responses = deepcopy(players)
                    del responses[player_id]

                conn.sendall(pickle.dumps(responses))


def disconnect_player(player_id) -> None:
    username = players[player_id]['username']
    players[player_id]['x'] = None
    print(f'Connection dropped ({username}, Player id: {player_id}).')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    print('Server started, waiting for connection...')

    while True:
        conn, addr = s.accept()
        print('Connected by:', addr, f'Player id: {current_player_id}')

        start_new_thread(client, (conn, current_player_id))
        current_player_id += 1
