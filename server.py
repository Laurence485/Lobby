import pickle
import socket

from game.utils import get_config, network_data
from _thread import start_new_thread

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
BUFFER_SIZE = config['BUFFER_SIZE']
CONNECTIONS = config['MAX_CONNECTIONS']

current_player_id = 0
players = {}


def number_of_players() -> int:
    return current_player_id


def client(conn, player_id: int) -> None:
    with conn:
        conn.send(pickle.dumps((player_id)))

        players[player_id] = network_data()

        while True:
            try:
                player_attributes = pickle.loads(conn.recv(BUFFER_SIZE))

                players[player_id] = player_attributes

                if not player_attributes:
                    print('Disconnected from server.')
                    break
                else:
                    if player_id == 0:
                        reply = players[1]
                    elif player_id == 1:
                        reply = players[0]
                    else:
                        raise Exception(f'UNEXPECTED PLAYER ID: {player_id}')

                # print(reply, player_id)
                conn.sendall(pickle.dumps(reply))
            except socket.error as e:
                print(e)
                break

        current_player = players[player_id]['username']
        print(f'Connection dropped ({current_player}, ID: {player_id}).')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    print('Server started, waiting for connection...')

    while True:
        conn, addr = s.accept()
        print('Connected by:', addr, f'Player id: {current_player_id}')

        start_new_thread(client, (conn, current_player_id))
        current_player_id += 1
