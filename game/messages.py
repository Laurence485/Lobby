import json
import pygame

from enums.base import Chat
from game.player import Player
from game.speech_bubble import SpeechBubble
from game.typing import Sprite
from game.utils import get_config
from typing import Callable

config = get_config()
WINDOW_WIDTH = config['WINDOW_WIDTH']
HOVER_MESSAGE_COLOUR = Chat.HOVER_MESSAGE_COLOUR.value
HOVER_MESSAGE_TIMEOUT = Chat.HOVER_MESSAGE_TIMEOUT.value
FONT_SIZE = Chat.FONT_SIZE.value


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

    def add_new_message(self, message: dict) -> None:
        data = json.loads(message['data'])
        self.cache.add(message['id'])
        self.list.append(data)
        self.height += data['text_rect']['height']


class HoverMessages:
    """Handles the dict of hover messages to be drawn over players
    or removed from the screen.
    """
    def __init__(self, window: Sprite):
        self.dict = {}
        self.expired_messages = set()
        self.window = window

    def overwrite_message(self, player_id: int) -> None:
        """Check if there is already a hover message for the given
        player id and if so, remove that message.
        """
        if player_id in self.dict:
            del self.dict[player_id]

    def should_wrap_text(self, text_width: int) -> bool:
        if text_width > WINDOW_WIDTH // 3:
            return True

    def divide_text(self, text: str, text_width: int, parts: int = 2) -> list:
        """If text width > 1/3 of screen width, divide into 2 parts.
        If text width > 1/2 of screen width, divide in 3 parts.
        """
        if text_width > WINDOW_WIDTH // 2:
            parts = 3

        if parts == 2:
            midpoint = len(text) // 2

            part_1 = text[:midpoint]
            part_2 = text[midpoint:]
            new_part_1 = self._ammend_mid_word_divide(part_1, part_2)

            divided_text = [new_part_1, part_2]
        else:
            third = len(text) // 3
            two_thirds = int(len(text) * (2/3))

            part_1 = text[:third]
            part_2 = text[third:two_thirds]
            part_3 = text[two_thirds:]
            new_part_1 = self._ammend_mid_word_divide(part_1, part_2)
            new_part_2 = self._ammend_mid_word_divide(part_2, part_3)

            divided_text = [new_part_1, new_part_2, part_3]

        return divided_text

    def _ammend_mid_word_divide(
        self,
        sentence: str,
        next_sentence: str
    ) -> str:
        """If the sentence does not end with a space, then add a hyphen
        to indicate that the last word of the sentence flows onto the
        next line.
        """
        if sentence[-1:] != " " and next_sentence[0] != " ":
            sentence += "-"
        return sentence

    def create_texts_for_wrapping(
        self,
        divided_text: list[str],
        render_text: Callable
    ) -> list[dict]:

        texts = []
        relative_ypos = 0
        for text in reversed(divided_text):
            rendered_text = render_text(
                text, colour=HOVER_MESSAGE_COLOUR
            )
            width = rendered_text.get_width()
            height = rendered_text.get_height()
            text_rect = {
                'width': width,
                'height': height,
                'relative_ypos': relative_ypos
            }
            relative_ypos -= height
            texts.append({'text': rendered_text, 'text_rect': text_rect})

        return texts

    def add_message(
        self,
        player_id: int,
        text_img: Sprite,
        text_rect: dict,
    ) -> None:

        self.dict[player_id] = (
            {
                'text_img': text_img,
                'width': text_rect['width'],
                'height': text_rect['height'],
                'start_timeout': self.start_timeout()
            }
        )

    def add_wrapped_message(self, player_id: int, texts: list[dict]) -> None:
        self.dict[player_id] = (
            {
                'wrapped': {
                    'text_imgs': [],
                    'widths': [],
                    'heights': [],
                    'relative_ypos': [],
                },
                'start_timeout': self.start_timeout()
            }
        )
        for text in texts:
            key = self.dict[player_id]['wrapped']
            key['text_imgs'].append(text['text'])
            key['widths'].append(text['text_rect']['width'])
            key['heights'].append(text['text_rect']['height'])
            key['relative_ypos'].append(text['text_rect']['relative_ypos'])

    def draw(self, player: Player, other_players: dict[int, Player]) -> None:
        for player_id, data in self.dict.items():
            this_player = self._get_this_player(
                player_id, player, other_players
            )
            if data.get('wrapped'):
                data_w = data['wrapped']
                for i in range(len(data_w['text_imgs'])):
                    SpeechBubble(
                        data_w['text_imgs'][i],
                        this_player.x,
                        this_player.y + data_w['relative_ypos'][i],
                        data_w['widths'][i],
                        data_w['heights'][i],
                        self.window
                    )
            else:
                SpeechBubble(
                    data['text_img'],
                    this_player.x,
                    this_player.y,
                    data['width'],
                    data['height'],
                    self.window
                )

            if(self._message_expired(data['start_timeout'])):
                self.expired_messages.add(player_id)

        if self.expired_messages:
            self._delete_expired_messages()

    def _get_this_player(
        self,
        player_id: int,
        player: Player,
        other_players: dict[int, Player]
    ) -> Player:

        if player_id in other_players:
            return other_players[player_id]
        else:
            return player

    def start_timeout(self) -> int:
        return pygame.time.get_ticks()

    def _message_expired(self, start_timeout: int) -> bool:
        seconds = (pygame.time.get_ticks() - start_timeout) / 1000
        if seconds > HOVER_MESSAGE_TIMEOUT:
            return True

    def _delete_expired_messages(self) -> None:
        for expired in self.expired_messages:
            del self.dict[expired]
        self.expired_messages.clear()
