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
disconnected_player_ids = []


def client(conn, player_id: int) -> None:
    with conn:
        conn.send(pickle.dumps(player_id))

        players[player_id] = network_data()

        while True:
            try:
                player_attributes = pickle.loads(conn.recv(BUFFER_SIZE))
            except EOFError:
                _disconnect_player(player_id)
                break
            else:
                players[player_id] = player_attributes

                if not player_attributes:
                    print('Disconnected from server.')
                    break

                conn.sendall(pickle.dumps(players))

                if disconnected_player_ids:
                    delete_disconnected_players()


def _disconnect_player(player_id) -> None:
    # Indicate that this player should be deleted locally.
    players[player_id]['x'] = None
    disconnected_player_ids.append(player_id)
    print(
        f'Connection dropped ({players[player_id]["username"]},'
        f' Player id: {player_id}).'
    )


def delete_disconnected_players() -> None:
    for id_ in disconnected_player_ids:
        try:
            del players[id_]
        except KeyError:
            print(
                f'Could not delete player ({players[id_]["username"]},'
                f' id: {id_})  from server.'
            )
        disconnected_player_ids.remove(id_)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    print('Server started, waiting for connection...')

    while True:
        conn, addr = s.accept()
        print('Connected by:', addr, f'Player id: {current_player_id}')

        start_new_thread(client, (conn, current_player_id))
        current_player_id += 1
