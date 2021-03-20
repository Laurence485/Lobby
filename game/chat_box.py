import json
import pygame
import time

from enums.base import Chat
from game.redis import RedisClient
from game.typing import Event, Sprite
from game.utils import get_config

config = get_config()

WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
CHAT_WINDOW_HEIGHT = config['CHAT_WINDOW_HEIGHT']
EDGE_DISTANCE = Chat.TEXT_DISTANCE_FROM_EDGE.value
CHAT_BOX_COLOUR = Chat.CHAT_BOX_COLOUR.value
USERNAME_COLOUR = Chat.USERNAME_COLOUR.value
TEXT_COLOUR = Chat.TEXT_COLOUR.value
FONT_SIZE = Chat.FONT_SIZE.value


class ChatMixin:
    x = 0
    y = WINDOW_HEIGHT
    width = WINDOW_WIDTH
    height = CHAT_WINDOW_HEIGHT
    redis = RedisClient()
    previous_text = []


class ChatBox(ChatMixin):
    def __init__(self, username: str):
        self.colour = CHAT_BOX_COLOUR
        self.box = pygame.Surface((self.width, self.height))
        self.box.fill(self.colour)
        self.text_input = TextInput(username)
        # self.previous_text = []
        self.previous_text_ids = set()

    def draw(self, window: Sprite) -> None:
        """Draw chat box at bottom of screen."""
        window.blit(self.box, (self.x, self. y))

    def get_new_messages(self):
        messages = self.redis.get_all_messages()
        if messages:
            sorted_messages = self.redis.sort_messages_by_expiry(messages)

            for message in sorted_messages:
                if message['id'] not in self.previous_text_ids:
                    self.previous_text_ids.add(message['id'])
                    self.previous_text.append(json.loads(message['data']))


    def check_message_ids():
        """Check message ids periodically to see if still active
        in redis so we can clear self.previous_text_ids
        IS THERE A WAY WE CAN AVOID SENDING REQS TO DB??
        E.G. MAKE USE OF A TIMESTAMP
        """
        pass

class TextInput(ChatMixin):
    def __init__(self, username: str):
        self.colour = TEXT_COLOUR
        self.username_colour = USERNAME_COLOUR
        self.text = ''
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.previous_text_height = 0
        self.username = username
        self._setup_imgs()
        self._setup_rects()

    def _setup_imgs(self) -> None:
        self.text_img = self._render_text(self.text)
        self.username_img = self._render_text(self.username, True)

    def _setup_rects(self) -> None:
        self.text_rect = self.text_img.get_rect()
        self.username_rect = self.username_img.get_rect()
        self.y_ = self.y + self.height - self.text_rect.height

        self.text_rect.topleft = (
            self.x + self.username_img.get_width(), self.y_
        )
        self.username_rect.topleft = (self.x, self.y_)

        self.cursor = pygame.Rect(
            self.text_rect.topright, (3, self.text_rect.height)
        )

    def check_input(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self._add_text(event)

            self._set_new_text_input()

    def _add_text(self, event: Event) -> None:
        if not self.text_rect.width >= (
            self.width - self.username_img.get_width() - EDGE_DISTANCE
        ):
            self.text += event.unicode

    def _set_new_text_input(self) -> None:
        """Update the new text and cursor to be drawn."""
        self.text_img = self._render_text(self.text)
        self.text_rect.size = self.text_img.get_size()
        self.cursor.topleft = self.text_rect.topright

    def _render_text(self, text: str, username: bool = False):
        if username:
            text += ': '
            colour = self.username_colour
        else:
            colour = self.colour
        return self.font.render(text, True, colour)

    def store_entered_text(self, window: Sprite) -> None:
        """Store the entered text for display."""
        if self.text_img.get_width():
            username_rect = self._create_rect_dict('username_rect')
            text_rect = self._create_rect_dict('text_rect')

            text = {
                'username': self.username,
                'text': self.text,
                'username_rect': username_rect,
                'text_rect': text_rect
            }
            self.redis.save_message(text)

            if self.previous_text:
                self._update_previous_text()

            # self.previous_text.append(text)
            self._clear_text_input(window)

    def _create_rect_dict(self, attribute: str) -> dict:
        return {
            'x': getattr(self, attribute).x,
            'y': getattr(self, attribute).y - getattr(self, attribute).height,
            'width': getattr(self, attribute).width,
            'height': getattr(self, attribute).height
        }

    def _update_previous_text(self) -> None:
        """Move previous text up to allow room for new text."""
        for text in self.previous_text:
            text['text_rect']['y'] -= self.text_rect.height
            text['username_rect']['y'] -= self.text_rect.height

        self.previous_text_height += self.text_rect.height

    def _clear_text_input(self, window: Sprite) -> None:
        self.text = ''
        self._set_new_text_input()
        self.draw(window)

    def draw(self, window: Sprite) -> None:
        """Draw text and cursor onto screen."""
        window.blit(
            self._render_text(self.username, username=True),
            self.username_rect
        )
        window.blit(self._render_text(self.text), self.text_rect)
        self._draw_cursor(window)

    def _draw_cursor(self, window: Sprite) -> None:
        """Flash cursor every 0.5 seconds."""
        if time.time() % 1 > 0.5:
            pygame.draw.rect(window, self.colour, self.cursor)

    def draw_previous_text(self, window: Sprite) -> None:
        """Draw the previously entered text above the text input box."""
        for text in self.previous_text:
            username_rect = text['username_rect']
            username_img = self._render_text(text['username'], username=True)
            text_img = self._render_text(text['text'])
            text_rect = text['text_rect']
            window.blit(username_img, self._get_rect_from_dict(username_rect))
            window.blit(text_img, self._get_rect_from_dict(text_rect))

        self._delete_oldest_message()

    def _get_rect_from_dict(self, rect: dict) -> tuple:
        return (
            rect['x'],
            rect['y'],
            rect['width'],
            rect['height']
        )

    def _delete_oldest_message(self) -> None:
        """If height of text in text box is greater than the height
        of the text box itself then delete the oldest message."""
        if self.previous_text_height >= self.height - self.text_rect.height:
            oldest_text_height = self.previous_text[0]['text_rect']['height']
            self.previous_text_height -= oldest_text_height
            del self.previous_text[0]
