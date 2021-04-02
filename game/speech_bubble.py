import pygame

from enums.base import Chat, Player_
from game.typing import Sprite
from game.utils import get_config


config = get_config()
WINDOW_WIDTH = config['WINDOW_WIDTH']
WINDOW_HEIGHT = config['WINDOW_HEIGHT']
HOVER_MESSAGE_BG_COLOUR = Chat.HOVER_MESSAGE_BG_COLOUR.value


class SpeechBubble:
    """Handles the positioning and rendering of hover messages
    into a speechbubble.
    """
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
        background = self._create_text_background()
        window.blit(self.text_img, (self.x, self.y, self.width, self.height))
        window.blit(background, (self.x, self.y, self.width, self.height))

    def _create_text_background(self) -> Sprite:
        surface = pygame.Surface(self.text_img.get_size())
        surface.fill(HOVER_MESSAGE_BG_COLOUR)
        surface.blit(self.text_img, (0, 0))
        return surface
