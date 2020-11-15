from characters import Player
from map_generation import Map
from random_node import RandomNode
from menu import Menu
from network import Network
from multiplayer import Multiplayer
import config
import pygame


class NewGame:
    """Setup a new game."""

    def __init__(self, net, username):
        self.menu = False
        self.grid = False
        self.net = net
        self.window = pygame.display.set_mode(
            (config.window_width, config.window_height)
        )

        self.background = pygame.image.load('sprites/background.jpg').convert()

        Map.load('myfirstmap')

        self.ash = Player(RandomNode(Map.nodes).node, 0, username, 0)

        # Other player objects
        p2, p3, p4, p5 = None, None, None, None
        self.players = [p2, p3, p4, p5]

        # music = pygame.mixer.music.load(config.theme)
        # pygame.mixer.music.set_volume(0.5)
        # pygame.mixer.music.play(-1)

        self.ash.ID = 0

    def redraw_gamewindow(self):
        """Draw objects onto the screen.
        Draw background, grid, players and map objects.
        """
        self.window.blit(self.background, (0, 0))

        # Draw Grid.
        if self.grid:
            for x in range(0, config.window_width, config.grid_spacing):
                for y in range(0, config.window_height, config.grid_spacing):
                    pygame.draw.rect(
                        self.window,
                        (125, 125, 125),
                        (x, y, config.grid_spacing, config.grid_spacing),
                        1
                    )

        # Draw objects.
        Map.draw(self.window)
        # Draw our player.
        self.ash.draw(self.window)

        # Draw all players.
        for p in self.players:
            if p and p.ID is not None:
                p.draw(self.window)

        if self.menu:
            Menu(
                self.window,
                [self.ash.stats, self.ash.username],
                [[p.stats, p.username] for p in self.players if p]
            )

        pygame.display.update()

    def check_keyboard_input(self, event):
        """Check for keyboard input.

        Press Z for menu.
        Press X to show the grid.
        """
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                self.menu = True if not self.menu else False
            if event.key == pygame.K_x:
                self.grid = True if not self.grid else False

    def fetch_data(self):
        '''get data from server, player positions, stats, kill status etc'''
        Multiplayer.get_player_data(self.ash, self.net, self.players, self.bikes, self.mushrooms)
        Multiplayer.check_death_status(self.ash, self.players)

    def check_collisions_and_pickups(self):
        self.ash.move(Map.objs_area, Map.movement_cost_area)


if __name__ == '__main__':

    pygame.init()
    game_is_running = True

    pygame.display.set_caption("Lobby")

    username = 'testUser'

    net = Network(username.lower())

    game = NewGame(net, username)

    if net.data is not None:
        print('successfully connected to server.')
    else:
        print('cannot connect to server.')

    clock = pygame.time.Clock()

    while game_is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_running = False

        clock.tick(9)
        # game.fetch_data()
        game.check_keyboard_input(event)
        game.check_collisions_and_pickups()
        game.redraw_gamewindow()
