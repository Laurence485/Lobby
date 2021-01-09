import pickle
import socket

from game.utils import get_config, network_data
import threading

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
BUFFER_SIZE = config['BUFFER_SIZE']
CONNECTIONS = config['MAX_CONNECTIONS']

current_player_id = 0
players = {}
disconnected_player_ids = []


def client(conn: socket, player_id: int) -> None:
    with conn:
        conn.send(pickle.dumps(player_id))

        players[player_id] = network_data()

        while True:
            try:
                player_attributes = pickle.loads(conn.recv(BUFFER_SIZE))
            except EOFError:
                _disconnect_player(player_id)
                # There are no players playing.
                # The last player is not yet removed from the server
                # as no data is received until another player connects.
                if len(players) == 1:
                    _delete_disconnected_players()
                    _reset_players()
                break
            else:
                players[player_id] = player_attributes

                if not player_attributes:
                    print('Disconnected from server.')
                    break

                conn.sendall(pickle.dumps(players))

                if disconnected_player_ids:
                    _delete_disconnected_players()


def _disconnect_player(player_id: int) -> None:
    # Indicate that this player should be deleted locally.
    players[player_id]['x'] = None
    disconnected_player_ids.append(player_id)
    print(
        f'Connection dropped ({players[player_id]["username"]},'
        f' Player id: {player_id}).'
    )


def _delete_disconnected_players() -> None:
    for id_ in disconnected_player_ids:
        try:
            del players[id_]
            print(f'Deleted player with id {id_} from server.')
        except KeyError:
            print(
                f'Could not delete player ({players[id_]["username"]},'
                f' id: {id_})  from server.'
            )
        disconnected_player_ids.remove(id_)


def _reset_players() -> None:
    """Reset global player variables."""
    if players:
        players.clear()

    global current_player_id
    current_player_id = 0

    print('All players reset.')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    print('Server started, waiting for connection...')

    while True:
        conn, addr = s.accept()
        print('Connected by:', addr, f'Player id: {current_player_id}')

        threading.Thread(target=client, args=(conn, current_player_id)).start()

        current_player_id += 1
