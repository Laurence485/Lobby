import pickle
import socket

from game.utils import get_config
from _thread import start_new_thread

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
BUFFER_SIZE = config['BUFFER_SIZE']
CONNECTIONS = 2

attributes = {
    'x': 0,
    'y': 0,
    'L': False,
    'R': False,
    'U': False,
    'D': True,
    'standing': True,
    'walk count': 0,
    'hit slow': False,
    'bike': False,
    'id': 1,
    'username': 'Noob',
}
players = [attributes] * CONNECTIONS


def client(conn, player_id: int) -> None:
    with conn:
        conn.send(pickle.dumps(player_id))

        while True:
            try:
                # received player attributes.
                data = pickle.loads(conn.recv(BUFFER_SIZE))

                players[player_id] = data

                if not data:
                    print('Disconnected from server.')
                    break
                else:
                    reply = players[0] if player_id == 1 else players[1]

                conn.sendall(pickle.dumps(reply))
            except socket.error as e:
                print(e)
                break

        current_player = players[player_id]['username']
        print(f'connection dropped ({current_player}, ID:{player_id}).')


player = 0  # Player ID

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    print("Server started, waiting for connection...")

    while True:
        conn, addr = s.accept()
        print("Connected by:", addr)

        start_new_thread(client, (conn, player))
        player += 1
