import pytest

from game.chat_box import TextInput
from game.messages import HoverMessages
from unittest.mock import patch


@pytest.fixture
def mock_font():
    with patch('game.chat_box.pygame') as pygame:
        pygame.return_value = 'mocked pygame'
        yield pygame


@pytest.fixture
def create_mock_text_input_with_redis_data(mock_font):
    def _create_mock_text_input_with_redis_data(width, player_id):
        with patch('game.chat_box.RedisClient') as redis:
            redis.return_value.sort_messages_by_expiry.return_value = (
                [{'id': 'f92d896ac90b4fed8dcc3c986ca0c1f0',
                 'data': (
                            '{"username": "testUser", "text": "hello world",'
                            '"username_rect": {"x": 0, "y": 470, "width": 47,'
                            '"height": 10}, "text_rect": {"x": 47, "y": 470,'
                            f'"width": {width},'
                            f'"height": 10}}, "player_id": {player_id}}}'
                        ),
                  'expires_in': 5}]
            )
            return TextInput('test user')
    return _create_mock_text_input_with_redis_data


@pytest.fixture
def mock_messages_window_width():
    with patch('game.messages.WINDOW_WIDTH', 400) as window_width:
        yield window_width


def test_get_new_messages_should_not_wrap_text(
    create_mock_text_input_with_redis_data,
    mock_font,
    mock_messages_window_width
):
    hover_messages = HoverMessages('mock window')
    width = 54
    player_id = 0
    mock_textInput = create_mock_text_input_with_redis_data(width, player_id)

    mock_textInput.get_new_messages(hover_messages)

    assert 'f92d896ac90b4fed8dcc3c986ca0c1f0' in mock_textInput.msgs.cache
    assert {
                "username": "testUser",
                "text": "hello world",
                "username_rect": {"x": 0, "y": 470, "width": 47, "height": 10},
                "text_rect": {"x": 47, "y": 470, "width": width, "height": 10},
                "player_id": player_id
            } == mock_textInput.msgs.list[-1]
    assert mock_textInput.msgs.height == 10

    assert player_id in hover_messages.dict
    assert 'height' in hover_messages.dict[player_id]
    assert 'start_timeout' in hover_messages.dict[player_id]
    assert 'text_imgs' in hover_messages.dict[player_id]
    assert 'width' in hover_messages.dict[player_id]
