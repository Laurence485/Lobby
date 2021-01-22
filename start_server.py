import socket

from enums.base import Server_
from server.server import Server
import threading

CONNECTIONS = Server_.MAX_CONNECTIONS.value


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    if __name__ == '__main__':
        server = Server('localhost', 12345)
        sock.bind((server.host, server.port))
        sock.listen(CONNECTIONS)

        print('Server started, waiting for connection...')

        while True:
            conn, addr = sock.accept()
            print(
                'Connected by:', addr, f'Player id: {server.current_player_id}'
            )

            threading.Thread(
                target=server.client,
                args=(conn, server.current_player_id)
            ).start()

            server.current_player_id += 1