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
