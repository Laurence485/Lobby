import pygame
import yaml

from characters import Player
from map import Map
from menu import Menu
from multiplayer import Multiplayer
from network import Network
from utils import random_xy

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file)

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
grid_spacing = config['GRID_SPACING']
framerate = config['FRAMERATE']
game_map = config['MAP']
background = config['BACKGROUND_IMG']


def setup_pygame() -> None:
    pygame.init()
    pygame.display.set_caption("Lobby")
    game_window = pygame.display.set_mode(
        (window_width, window_height)
    )

    start_game_loop(game_window)


def start_game_loop(game_window: pygame.Surface) -> None:
    game_is_running = True
    clock = pygame.time.Clock()

    Map.load(game_map)
    game = NewGame(game_window, setup_network(get_username()))

    while game_is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_running = False

            game.check_keyboard_input(event)

        refresh_game(clock)
        # game.fetch_data()
        game.check_collisions_and_pickups()
        game.redraw_gamewindow()


def get_username() -> str:
    return 'testUser'


def setup_network(username: str) -> Network:
    net = Network(username.lower())

    if net.data is None:
        print('cannot connect to server.')
    else:
        print('successfully connected to server.')

    return net


def refresh_game(clock: pygame.time.Clock) -> int:
    return clock.tick(framerate)


class NewGame:
    """Setup a new game and handle game loop methods."""

    def __init__(self, game_window: pygame.Surface, net: Network):
        self.background = pygame.image.load(background).convert()
        self.window = game_window
        self.net = net
        self.username = self.net.username
        self.menu = False
        self.grid = False

        self.player = Player(
            xy=random_xy(Map.nodes),
            ID=0,
            username=self.username,
            current_map=0
        )

        # Other player objects
        p2, p3, p4, p5 = None, None, None, None
        self.players = [p2, p3, p4, p5]

        self.player.ID = 0

    def check_keyboard_input(self, event: pygame.event.Event) -> None:
        """Check for keyboard input.

        Press Z for menu.
        Press X to show the grid.
        """
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                self.menu = True if not self.menu else False
            if event.key == pygame.K_x:
                self.grid = True if not self.grid else False

    def fetch_data(self) -> None:
        """get data from server, player positions, stats, kill status etc"""
        Multiplayer.get_player_data(
            self.player, self.net, self.players, self.bikes, self.mushrooms
        )
        Multiplayer.check_death_status(self.player, self.players)

    def check_collisions_and_pickups(self) -> None:
        self.player.move(Map.objs_area, Map.movement_cost_area)

    def redraw_gamewindow(self) -> None:
        """Draw objects onto the screen."""
        self.window.blit(self.background, (0, 0))

        self.draw_grid()
        Map.draw(self.window)
        self.player.draw(self.window)

        # Draw all players.
        for p in self.players:
            if p and p.ID is not None:
                p.draw(self.window)

        if self.menu:
            self.show_menu()

        pygame.display.update()

    def draw_grid(self) -> None:
        if self.grid:
            for x in range(0, window_width, grid_spacing):
                for y in range(0, window_height, grid_spacing):
                    pygame.draw.rect(
                        self.window,
                        (125, 125, 125),
                        (x, y, grid_spacing, grid_spacing),
                        1
                    )

    def show_menu(self) -> None:
        Menu(
            self.window,
            [self.player.stats, self.player.username],
            [[p.stats, p.username] for p in self.players if p]
        )


if __name__ == '__main__':
    setup_pygame()
