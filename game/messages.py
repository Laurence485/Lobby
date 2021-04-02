import pygame

from enums.base import Chat
from game.speech_bubble import SpeechBubble
from game.typing import Sprite

HOVER_MESSAGE_TIMEOUT = Chat.HOVER_MESSAGE_TIMEOUT.value


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

    def add_message(
        self,
        player_id: int,
        text_img: Sprite,
        text_rect: dict
    ) -> None:

        self.dict[player_id] = (
            {
                'text_img': text_img,
                'width': text_rect['width'],
                'height': text_rect['height'],
                'start_timeout': self.start_timeout()
            }
        )

    def draw(self, player, other_players: dict) -> None:
        for player_id, data in self.dict.items():
            this_player = self._get_this_player(
                player_id, player, other_players
            )
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
        player,
        other_players: dict
    ) -> None:

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
