import pickle
import socket

from enums.base import Network_
from game.utils import check_os_config, network_data


BUFFER_SIZE = Network_.BUFFER_SIZE.value


class Server:
    """The Server object handles inbound and outbound data to
    and from the server."""

    current_player_id = 0
    host = None
    port = None

    def __init__(self, host: int = None, port: int = None):
        self.players = {}
        self.disconnected_player_ids = []

        Server.host = check_os_config('HOST', host)
        Server.port = check_os_config('PORT', port)

    def client(self, conn: socket, player_id: int) -> None:
        with conn:
            conn.send(pickle.dumps(player_id))

            self.players[player_id] = network_data()

            while True:
                try:
                    player_attributes = pickle.loads(conn.recv(BUFFER_SIZE))
                except EOFError:
                    self._disconnect_player(player_id)
                    # There are no players playing.
                    # The last player is not yet removed from the server
                    # as the disconnected players are only checked for
                    # if there is more than 1 player playing.
                    if len(self.players) == 1:
                        self._delete_disconnected_players()
                        self._reset_players()
                    break
                else:
                    self.players[player_id] = player_attributes

                    if not player_attributes:
                        print('Disconnected from server.')
                        break

                    conn.sendall(pickle.dumps(self.players))

                    if self.disconnected_player_ids:
                        self._delete_disconnected_players()

    def _disconnect_player(self, player_id: int) -> None:
        # Indicate that this player should be deleted locally.
        self.players[player_id]['x'] = None
        self.disconnected_player_ids.append(player_id)
        print(
            f'Connection dropped ({self.players[player_id]["username"]},'
            f' Player id: {player_id}).'
        )

    def _delete_disconnected_players(self) -> None:
        for id_ in self.disconnected_player_ids:
            try:
                del self.players[id_]
            except KeyError:
                print(
                    f'Could not delete player ({self.players[id_]["username"]}'
                    f', id: {id_})  from server.'
                )
            else:
                print(f'Deleted player with id {id_} from server.')

            self.disconnected_player_ids.remove(id_)

    def _reset_players(self) -> None:
        if self.players:
            self.players.clear()

        Server.current_player_id = 0

        print('All players reset.')
