import pygame

from enums.base import Window
from game.chat_box import ChatBox, HoverMessages
from game.map import Map
from game.player import Player
from game.typing import Sprite
from game.utils import get_config, random_xy
from logger import get_logger
from network.network import Network, fetch_player_data

log = get_logger(__name__)
config = get_config()

WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
GRID_SPACING = config['GRID_SPACING']
BACKGROUND = config['BACKGROUND_IMG']
GRID_COLOUR = Window.GRID_COLOUR.value


class NewGame:
    """Setup a new game and handle game loop methods."""

    # Dict to hold id:attributes for all the other players on the network.
    other_players = {}

    def __init__(self, game_window: Sprite, net: Network, username: str):
        self.background = pygame.image.load(BACKGROUND).convert()
        self.window = game_window
        self.net = net
        self.username = username
        self.menu = False
        self.grid = False
        self.is_typing = False
        self.chat_box = ChatBox(self.username)
        self.hover_messages = HoverMessages(game_window)
        self.player = Player(
            xy=random_xy(Map.nodes),
            player_id=self.net.player_id,
            username=self.username,
        )

        log.debug('Created a new game.')

    def check_keyboard_input(self, event: pygame.event.Event) -> None:
        """Check for keyboard input.

        Press Enter to type.
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
        fetch_player_data(self.player, self.other_players, self.net)

    def draw_game_objects(self, dt: float) -> None:
        """Draw objects onto the screen."""
        self.window.blit(self.background, (0, 0))

        self._draw_grid()
        Map.draw(self.window)
        self.chat_box.draw(self.window)
        self.player.draw(self.window, dt)

        if self.other_players:
            for player in self.other_players.values():
                player.draw(self.window, dt)

    def _draw_grid(self) -> None:
        if self.grid:
            for x in range(0, WINDOW_WIDTH, GRID_SPACING):
                for y in range(0, WINDOW_HEIGHT, GRID_SPACING):
                    pygame.draw.rect(
                        self.window,
                        (
                            GRID_COLOUR, GRID_COLOUR, GRID_COLOUR
                        ),
                        (x, y, GRID_SPACING, GRID_SPACING),
                        1
                    )
