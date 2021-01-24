import pygame
import time

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
        self.box = pygame.Surface((self.width, self.height))
        self.box.fill((210, 210, 210, 210))

        self.GRAY = (200, 200, 200)
        self.text = 'this text is editable'
        self.font = pygame.font.SysFont(None, 48)
        self.img = self.font.render(self.text, True, self.GRAY)

        self.rect = self.img.get_rect()
        self.rect.topleft = (20, 20)
        self.cursor = pygame.Rect(self.rect.topright, (3, self.rect.height))

    def draw(self, window: Sprite) -> None:
        """Draw chat box at bottom of screen."""
        window.blit(self.box, (self.x, self. y))

    def check_text_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self.text += event.unicode

            self.img = self.font.render(self.text, True, self.GRAY)
            self.rect.size = self.img.get_size()
            self.cursor.topleft = self.rect.topright

    def draw_text_input(self, window: Sprite) -> None:
        window.blit(self.img, self.rect)
        if time.time() % 1 > 0.5:
            pygame.draw.rect(window, self.GRAY, self.cursor)


class TextInput(ChatBox):
    pass
