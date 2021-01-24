import pygame
import pygame_textinput

from game.typing import Sprite
from game.utils import get_config

config = get_config()

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
chat_window_height = config['CHAT_WINDOW_HEIGHT']


class ChatBox:
    def __init__(self):
        self.width = window_width
        self.height = chat_window_height
        self.x = 0
        self.y = window_height
        self.img = pygame.Surface((self.width, self.height))
        self.img.fill((210, 210, 210, 210))

    def draw(self, window: Sprite) -> None:
        """Draw chat box at bottom of screen."""
        window.blit(self.img, (self.x, self. y))
