import pytest

from game.chat_box import ChatBox
from unittest.mock import patch


@pytest.fixture
def mock_chat_window_area():
    x, y, width, height = 0, 0, 400, 80
    return x, y, width, height


@pytest.fixture
def mock_chat_box(mock_chat_window_area):
    with patch('pygame.Surface') as mock_surface:
        mock_surface.return_value = mock_chat_window_area


def test_create_chat_area(mock_chat_box):
    chatbox = ChatBox()
    assert chatbox.img.get_rect() == (0, 0, 400, 80)
