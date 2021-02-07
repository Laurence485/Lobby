import pygame
import time

from game.typing import Sprite
from game.utils import get_config

config = get_config()

WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
CHAT_WINDOW_HEIGHT = config['CHAT_WINDOW_HEIGHT']


class ChatBox:
    x = 0
    y = WINDOW_HEIGHT
    width = WINDOW_WIDTH
    height = CHAT_WINDOW_HEIGHT

    def __init__(self):
        self.colour = (210, 210, 210, 210)
        self.box = pygame.Surface((self.width, self.height))
        self.box.fill(self.colour)
        self.text_input = TextInput()

    def draw(self, window: Sprite) -> None:
        """Draw chat box at bottom of screen."""
        window.blit(self.box, (self.x, self. y))


class TextInput(ChatBox):
    def __init__(self):
        self.colour = (0, 0, 0)
        self.text = ''
        self.font = pygame.font.SysFont(None, 15)
        self.text_img = self.font.render(self.text, True, self.colour)

        self.rect = self.text_img.get_rect()
        self.y_ = self.y + CHAT_WINDOW_HEIGHT - self.rect.height
        self.rect.topleft = (self.x, self.y_)
        self.cursor = pygame.Rect(self.rect.topright, (3, self.rect.height))

    def check_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                if not self.rect.width >= self.width:
                    self.text += event.unicode

            self.text_img = self.font.render(self.text, True, self.colour)
            self.rect.size = self.text_img.get_size()
            self.cursor.topleft = self.rect.topright

    def draw(self, window: Sprite) -> None:
        """Draw text onto screen and flash cursor every 0.5 seconds."""
        window.blit(self.text_img, self.rect)
        if time.time() % 1 > 0.5:
            pygame.draw.rect(window, self.colour, self.cursor)
