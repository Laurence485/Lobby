import socket

from enums.base import Server_
from logger import get_logger
from server.server import Server
import threading

log = get_logger(__name__, file_log_level='INFO')

MAX_CONNECTIONS = Server_.MAX_CONNECTIONS.value


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    if __name__ == '__main__':
        server = Server()
        sock.bind((server.host, server.port))
        sock.listen(MAX_CONNECTIONS)

        log.info('Server started, waiting for connection...')

        while True:
            conn, addr = sock.accept()
            log.info(
                f'Connected by: {addr}. Player id: {server.current_player_id}'
            )

            threading.Thread(
                target=server.client,
                args=(conn, server.current_player_id)
            ).start()

            Server.current_player_id += 1
