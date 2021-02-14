import pygame
import time

from enums.base import Base
from game.typing import Event, Sprite
from game.utils import get_config

config = get_config()

WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
CHAT_WINDOW_HEIGHT = config['CHAT_WINDOW_HEIGHT']
EDGE_DISTANCE = Base.MAX_TEXT_DISTANCE_FROM_EDGE.value


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
        self.y_ = self.y + self.height - self.rect.height
        self.rect.topleft = (self.x, self.y_)
        self.cursor = pygame.Rect(self.rect.topright, (3, self.rect.height))
        self.previous_text = []
        self.previous_text_height = 0

    def check_input(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self._add_text(event)

            self._set_new_text_input()

    def _add_text(self, event: Event) -> None:
        if not self.rect.width >= self.width - EDGE_DISTANCE:
            self.text += event.unicode

    def _set_new_text_input(self) -> None:
        """Update the new text and cursor to be drawn."""
        self.text_img = self.font.render(self.text, True, self.colour)
        self.rect.size = self.text_img.get_size()
        self.cursor.topleft = self.rect.topright

    def store_entered_text(self, window: Sprite) -> None:
        """Store the entered text for display."""
        if self.text_img.get_width():
            text = [
                self.text_img,
                [
                    self.rect.x,
                    self.rect.y - self.rect.height,
                    self.rect.width,
                    self.rect.height
                ]
            ]
            if self.previous_text:
                self._update_previous_text()
                self.previous_text_height += self.rect.height

            self.previous_text.append(text)
            self._clear_text_input(window)

    def _update_previous_text(self) -> None:
        """Move previous text up to allow room for new text."""
        for text in self.previous_text:
            # ypos = text[1][1]
            text[1][1] -= self.rect.height

    def _clear_text_input(self, window: Sprite) -> None:
        self.text = ''
        self._set_new_text_input()
        self.draw(window)

    def draw(self, window: Sprite) -> None:
        """Draw text onto screen and flash cursor every 0.5 seconds."""
        window.blit(self.text_img, self.rect)
        if time.time() % 1 > 0.5:
            pygame.draw.rect(window, self.colour, self.cursor)

    def draw_previous_text(self, window: Sprite) -> None:
        """Draw the previously entered text above the text input box."""
        for text in self.previous_text:
            text_img, text_rect = text[0], text[1]
            window.blit(text_img, text_rect)

        self._delete_oldest_message()

    def _delete_oldest_message(self) -> None:
        """If height of text in text box is greater than the height
        of the text box itself then delete the oldest message."""
        if self.previous_text_height >= self.height - self.rect.height:
            # Oldest message = self.previous_text[0]
            oldest_text_height = self.previous_text[0][1][3]
            self.previous_text_height -= oldest_text_height
            del self.previous_text[0]
