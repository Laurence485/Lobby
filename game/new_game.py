import pygame

from enums.base import Window
from game.chat_box import ChatBox
from game.map import Map
from game.player import Player
from game.typing import Sprite
from game.utils import get_config, random_xy
from network.network import Network, fetch_player_data

config = get_config()

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
grid_spacing = config['GRID_SPACING']
background = config['BACKGROUND_IMG']
grid_colour = Window.GRID_COLOUR.value

# Dict to hold id:attributes for all the other players on the network.
other_players = {}


class NewGame:
    """Setup a new game and handle game loop methods."""

    def __init__(self, game_window: Sprite, net: Network, username: str):
        self.background = pygame.image.load(background).convert()
        self.window = game_window
        self.net = net
        self.username = username
        self.menu = False
        self.grid = False
        self.is_typing = False
        self.chat_box = ChatBox()
        self.player = Player(
            xy=random_xy(Map.nodes),
            player_id=self.net.player_id,
            username=self.username,
        )

    def check_keyboard_input(self, event: pygame.event.Event) -> None:
        """Check for keyboard input.

        Press Enter to type.
        Press Z for menu.
        Press X to show the grid.
        Press B to use the bike.
        """
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                self.is_typing = True if not self.is_typing else False
            if event.key == pygame.K_x and not self.is_typing:
                self.grid = True if not self.grid else False
            if event.key == pygame.K_b and not self.is_typing:
                if self.player.bike:
                    self.player.bike = False
                else:
                    self.player.bike = True
                    self.player.bike_sound.play()

    def fetch_player_data(self) -> None:
        """get data from server."""
        fetch_player_data(self.player, other_players, self.net)

    def draw_game_objects(self, dt) -> None:
        """Draw objects onto the screen."""
        self.window.blit(self.background, (0, 0))

        self._draw_grid()
        Map.draw(self.window)
        self.chat_box.draw(self.window)
        self.player.draw(self.window, dt)

        if other_players:
            for player in other_players.values():
                player.draw(self.window)

    def _draw_grid(self) -> None:
        if self.grid:
            for x in range(0, window_width, grid_spacing):
                for y in range(0, window_height, grid_spacing):
                    pygame.draw.rect(
                        self.window,
                        (
                            grid_colour, grid_colour, grid_colour
                        ),
                        (x, y, grid_spacing, grid_spacing),
                        1
                    )
