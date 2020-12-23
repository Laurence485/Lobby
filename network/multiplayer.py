from game.player import Player
from network.network import Network


class Multiplayer:
    """Handle methods for checking data from the server."""
    @staticmethod
    def fetch_player_data(this_player, net: Network):
        """Get player data from server and map data to local
        player objects."""

        # Get attributes of other players
        fetched_player_data = net.send(this_player.attributes())
        f = fetched_player_data
        p2 = this_player.p2

        # create new player instance if:
        # 1) we haven't already created an instance
        # 2) they have an ID (they are connected to server)
        if p2 is None:
            print(f'{f["username"]} connected.')
            this_player.p2 = Player((f['x'], f['y']), f['id'])

        # Update player from server
        else:
            p2.x, p2.y = f['x'], f['y']
            p2.left, p2.right, p2.up, p2.down = f['L'], f['R'], f['U'], f['D']
            p2.standing, p2.walk_count = f['standing'], f['walk count']
            p2.hit_slow, p2.bike = f['hit slow'], f['bike']
            p2.id = f['id']
            p2.username = f['username']

