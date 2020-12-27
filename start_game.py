import pygame

from enums.base import Window
from game.map import Map
from game.menu import Menu
from game.player import Player
from game.typing import Sprite
from game.utils import get_config, random_xy
from network.network import Network, fetch_player_data

config = get_config()

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
grid_spacing = config['GRID_SPACING']
framerate = config['FRAMERATE']
game_map = config['MAP']
background = config['BACKGROUND_IMG']
grid_colour = Window.GRID_COLOUR.value

if grid_spacing != 10:
    raise NotImplementedError('Do not adjust the grid spacing.')


def setup_pygame() -> None:
    pygame.init()
    pygame.display.set_caption('Lobby')
    game_window = pygame.display.set_mode(
        (window_width, window_height)
    )

    _start_game_loop(game_window)


def _start_game_loop(game_window: Sprite) -> None:
    game_is_running = True
    clock = pygame.time.Clock()

    Map.load(game_map)
    # Map(341)
    game = NewGame(game_window, _setup_network(), _get_username())

    while game_is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_running = False

            game.check_keyboard_input(event)

        _refresh_game(clock)
        game.fetch_player_data()
        game.player.check_collisions(
            Map.blocked_nodes, Map.reduced_speed_nodes
        )
        game.player.move()
        game.player.prevent_movement_beyond_screen()
        game.player.animation_loop()
        game.draw_game_objects()


def _get_username() -> str:
    return 'testUser'


def _setup_network() -> Network:
    net = Network()

    if net.data is None:
        print('cannot connect to server.')
    else:
        print('successfully connected to server.')

    return net


def _refresh_game(clock: pygame.time.Clock) -> int:
    return clock.tick(framerate)


class NewGame:
    """Setup a new game and handle game loop methods."""

    def __init__(self, game_window: Sprite, net: Network, username: str):
        self.background = pygame.image.load(background).convert()
        self.window = game_window
        self.net = net
        self.username = username
        self.menu = False
        self.grid = False

        self.player = Player(
            xy=random_xy(Map.nodes),
            player_id=0,
            username=self.username,
        )

        # Other player objects
        self.player.p2 = None

        self.player.id = self.net.player_id

    def check_keyboard_input(self, event: pygame.event.Event) -> None:
        """Check for keyboard input.

        Press Z for menu.
        Press X to show the grid.
        Press B to use the bike.
        """
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                self.menu = True if not self.menu else False
            if event.key == pygame.K_x:
                self.grid = True if not self.grid else False
            if event.key == pygame.K_b:
                if self.player.bike:
                    self.player.bike = False
                else:
                    self.player.bike = True
                    self.player.bike_sound.play()

    def fetch_player_data(self) -> None:
        """get data from server."""
        fetch_player_data(self.player, self.net)

    def draw_game_objects(self) -> None:
        """Draw objects onto the screen."""
        self.window.blit(self.background, (0, 0))

        self._draw_grid()
        Map.draw(self.window)
        self.player.draw(self.window)

        # Draw all players.
        if self.player.p2:
            self.player.p2.draw(self.window)

        if self.menu:
            self._show_menu()

        pygame.display.update()

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

    def _show_menu(self) -> None:
        Menu(
            self.window,
            [self.player.stats, self.player.username],
            [[p.stats, p.username] for p in self.players if p]
        )


if __name__ == '__main__':
    setup_pygame()
