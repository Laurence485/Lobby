import json
import pygame
import time

from enums.base import Chat, Player_
from game.redis import RedisClient
from game.typing import Event, Sprite
from game.utils import get_config
from logger import get_logger

log = get_logger(__name__)
config = get_config()

WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
CHAT_WINDOW_HEIGHT = config['CHAT_WINDOW_HEIGHT']
EDGE_DISTANCE = Chat.TEXT_DISTANCE_FROM_EDGE.value
CHAT_BOX_COLOUR = Chat.CHAT_BOX_COLOUR.value
USERNAME_COLOUR = Chat.USERNAME_COLOUR.value
TEXT_COLOUR = Chat.TEXT_COLOUR.value
FONT_SIZE = Chat.FONT_SIZE.value
HOVER_MESSAGE_TIMEOUT = Chat.HOVER_MESSAGE_TIMEOUT.value


class ChatMixin:
    x = 0
    y = WINDOW_HEIGHT
    width = WINDOW_WIDTH
    height = CHAT_WINDOW_HEIGHT


class ChatBox(ChatMixin):
    def __init__(self, username: str):
        self.colour = CHAT_BOX_COLOUR
        self.box = pygame.Surface((self.width, self.height))
        self.box.fill(self.colour)
        self.text_input = TextInput(username)

    def draw(self, window: Sprite) -> None:
        """Draw chat box at bottom of screen."""
        window.blit(self.box, (self.x, self. y))


class Messages:
    """Handles the list of messages to be drawn to the chat box."""
    def __init__(self):
        self.list = []
        self.height = 0
        self.cache = set()

    def __len__(self):
        return len(self.list)

    @property
    def queue(self) -> list:
        return reversed(self.list)


class HoverMessages:
    """Handles the list of hover messages to be drawn over players
    or removed from the screen.
    """
    def __init__(self, window: Sprite):
        self.list = []
        self.window = window

    @property
    def queue(self) -> list:
        return reversed(self.list)

    def draw(self, player, other_players: dict) -> None:
        for data in self.queue:
            if data['player_id'] in other_players:
                this_player = other_players[data['player_id']]
            else:
                this_player = player
            SpeechBubble(
                data['text_img'],
                this_player.x,
                this_player.y,
                data['width'],
                data['height'],
                self.window
            )

            if(self._message_expired(data['start_timeout'])):
                self.list.remove(data)

    def start_timeout(self) -> int:
        return pygame.time.get_ticks()

    def _message_expired(self, start_timeout: int) -> bool:
        seconds = (pygame.time.get_ticks() - start_timeout) / 1000
        if seconds > HOVER_MESSAGE_TIMEOUT:
            return True


class SpeechBubble:
    """Handles the positioning and rendering of hover messages."""
    def __init__(
        self,
        text_img: Sprite,
        x: int,
        y: int,
        width: int,
        height: int,
        window: Sprite
    ):
        self.text_img = text_img
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._centralise_and_position_text_over_player()
        self._keep_text_on_screen()
        self._draw_bubble(window)

    def _centralise_and_position_text_over_player(self) -> None:
        # Centralise text over the middle of the player.
        self.x -= self.width // 2 - Player_.WIDTH.value // 2
        # The bottom of the text should be at the top of the player.
        self.y -= self.height

    def _keep_text_on_screen(self) -> None:
        if self.x < 0:
            self.x = 0
        elif self.x > WINDOW_WIDTH - self.width:
            self.x = WINDOW_WIDTH - self.width
        if self.y < 0:
            self.y = 0

    def _draw_bubble(self, window: Sprite) -> None:
        window.blit(self.text_img, (self.x, self.y, self.width, self.height))


class TextInput(ChatMixin):
    def __init__(self, username: str):
        self.colour = TEXT_COLOUR
        self.username_colour = USERNAME_COLOUR
        self.text = ''
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.username = username
        self._setup_imgs()
        self._setup_rects()
        self.redis = RedisClient()
        self.msgs = Messages()

    def _setup_imgs(self) -> None:
        self.text_img = self._render_text(self.text)
        self.username_img = self._render_text(self.username, True)

    def _setup_rects(self) -> None:
        self.text_rect = self.text_img.get_rect()
        self.username_rect = self.username_img.get_rect()
        self.y_text = self.y + self.height - self.text_rect.height

        self.text_rect.topleft = (
            self.x + self.username_img.get_width(), self.y_text
        )
        self.username_rect.topleft = (self.x, self.y_text)

        self.cursor = pygame.Rect(
            self.text_rect.topright, (3, self.text_rect.height)
        )

    def get_new_messages(self, hover_messages: HoverMessages) -> None:
        """Check redis for any new messages and update the list of
        previous messages and hover-messages with any new ones found.
        """
        messages = self.redis.get_all_messages(cache=self.msgs.cache)
        if messages:
            sorted_messages = self.redis.sort_messages_by_expiry(messages)

            for message in sorted_messages:
                data = json.loads(message['data'])
                self.msgs.cache.add(message['id'])
                self.msgs.list.append(data)
                self.msgs.height += data['text_rect']['height']

                hover_messages.list.append(
                    {
                        'text_img': self._render_text(data['text']),
                        'player_id': data['player_id'],
                        'width': data['text_rect']['width'],
                        'height': data['text_rect']['height'],
                        'start_timeout': hover_messages.start_timeout()
                    }
                )

    def delete_old_msg_ids(self) -> None:
        """Clear out old message ids which have been stored to prevent
        message duplication in the chat. Check whether the message
        is present in redis, and if not, remove it from the previous
        messages cache as the message has expired.
        """
        if len(self.msgs.cache) > 1:
            log.debug('Clearing old message ids.')

            for message_id in list(self.msgs.cache):
                if not self.redis.get_message(message_id):
                    self.msgs.cache.remove(message_id)

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

    def _render_text(self, text: str, username: bool = False) -> Sprite:
        if username:
            text += ': '
            colour = self.username_colour
        else:
            colour = self.colour

        return self.font.render(text, True, colour)

    def save_message(self, window: Sprite, player_id: int) -> None:
        """Save entered messages to redis."""
        if self.text_img.get_width():
            username_rect = self._create_rect_dict('username_rect')
            text_rect = self._create_rect_dict('text_rect')

            data = {
                'username': self.username,
                'text': self.text,
                'username_rect': username_rect,
                'text_rect': text_rect,
                'player_id': player_id
            }
            self.redis.save_message(data)

            if len(self.msgs):
                self._update_messages()

            self._clear_text_input(window)

    def _create_rect_dict(self, attribute: str) -> dict:
        return {
            'x': getattr(self, attribute).x,
            'y': getattr(self, attribute).y,
            'width': getattr(self, attribute).width,
            'height': getattr(self, attribute).height
        }

    def _update_messages(self) -> None:
        """Move previous message up to allow room for new messages."""
        for data in self.msgs.list:
            data['text_rect']['y'] -= self.text_rect.height
            data['username_rect']['y'] -= self.text_rect.height

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

    def draw_messages(self, window: Sprite) -> None:
        """Draw previous messages above the text input box."""
        ypos = self.y_text
        for data in self.msgs.queue:
            username_img = self._render_text(data['username'], username=True)
            username_rect = data['username_rect']
            username_rect['y'] = ypos - username_rect['height']

            text_img = self._render_text(data['text'])
            text_rect = data['text_rect']
            text_rect['y'] = ypos - text_rect['height']

            ypos -= text_rect['height']  # Move message up the chat box

            window.blit(username_img, self._get_rect_from_dict(username_rect))
            window.blit(text_img, self._get_rect_from_dict(text_rect))
            # speechBubble(
            #     data['player_xy'],
            #     text_img,
            #     {'width': text_rect['width'], 'height': text_rect['height']},
            #     window
            # )

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
        of the text box itself then delete the oldest message.
        """
        if self.msgs.height >= self.height - self.text_rect.height:
            oldest_text_height = (
                self.msgs.list.pop(0)['text_rect']['height']
            )
            self.msgs.height -= oldest_text_height
