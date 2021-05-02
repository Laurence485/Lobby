import pytest

from game.chat_box import TextInput
from game.messages import HoverMessages
from unittest.mock import patch, Mock


@pytest.fixture
def mock_pygame():
    with patch('game.chat_box.pygame') as pygame:
        yield pygame


@pytest.fixture
def mock_redis():
    with patch('game.chat_box.RedisClient') as redis:
        yield redis


@pytest.fixture
def mock_event():
    event = Mock()
    event.type = True
    event.key = True
    return event


@pytest.fixture
def mock_pygame_keys():
    with patch('game.chat_box.pygame') as pygame:
        pygame.KEYDOWN = True
        pygame.K_BACKSPACE = True
        yield pygame


@pytest.fixture
def mock_add_text():
    with patch('game.chat_box.TextInput._add_text') as add_text:
        yield add_text


@pytest.fixture
def hover_messages():
    return HoverMessages(window=Mock())


@pytest.fixture
def create_mock_text_input_with_redis_data(mock_pygame):
    def _create_mock_text_input_with_redis_data(width=0, player_id=0):
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
            redis.return_value.get_message.return_value = None

            return TextInput('test user')
    return _create_mock_text_input_with_redis_data


@pytest.fixture
def mock_msgs_cache():
    with patch('game.chat_box.Messages') as messages:
        messages.return_value.cache = {
            'f92d896ac90b4fed8dcc3c986ca0c1f0',
            'f92d896ac90b4fed8dcc3c986ca0c1f1',
            'f92d896ac90b4fed8dcc3c986ca0c1f2',
            'f92d896ac90b4fed8dcc3c986ca0c1f3'
        }
        yield messages


@pytest.fixture
def mock_msgs_cache_one_id():
    with patch('game.chat_box.Messages') as messages:
        messages.return_value.cache = {'f92d896ac90b4fed8dcc3c986ca0c1f0'}
        yield messages


@pytest.fixture
def mock_edge_distance():
    with patch('game.chat_box.EDGE_DISTANCE', 0) as edge_distance:
        yield edge_distance


@pytest.fixture
def mock_chat_box_height():
    with patch('game.chat_box.CHAT_WINDOW_HEIGHT', 80) as chat_window_height:
        yield chat_window_height


@pytest.fixture
def mock_create_rect_dict():
    with patch('game.chat_box.TextInput._create_rect_dict') as rect_dict:
        rect_dict.return_value = {'height': 1, 'width': 1, 'x': 1, 'y': 1}
        yield rect_dict


@pytest.fixture
def mock_msgs_list():
    with patch('game.chat_box.Messages') as messages:
        messages.return_value.__len__ = messages.return_value.list
        messages.return_value.list = [{
            'text_rect': {
                'x': 0,
                'y': 10,
                'height': 8,
                'width': 10
            },
            'username_rect': {
                'x': 0,
                'y': 10,
                'height': 10,
                'width': 10
            },
            'username': 'test',
            'text': 'test text'
        },
            {
            'text_rect': {
                'x': 0,
                'y': 20,
                'height': 12,
                'width': 10
            },
            'username_rect': {
                'x': 0,
                'y': 20,
                'height': 10,
                'width': 10
            },
            'username': 'test2',
            'text': 'test text'
        }]
        messages.return_value.queue = reversed(messages.return_value.list)
        yield messages


@pytest.fixture
def mock_update_messages():
    with patch('game.chat_box.TextInput._update_messages') as update_messages:
        yield update_messages


class TestTextInput:
    def test_get_new_messages_does_not_wrap_text(
        self,
        create_mock_text_input_with_redis_data,
        mock_messages_window_width,
        hover_messages
    ):
        width = 54
        player_id = 0
        textInput = create_mock_text_input_with_redis_data(width, player_id)

        textInput.get_new_messages(hover_messages)

        assert 'f92d896ac90b4fed8dcc3c986ca0c1f0' in textInput.msgs.cache
        assert textInput.msgs.list[-1] == {
            "username": "testUser",
            "text": "hello world",
            "username_rect": {"x": 0, "y": 470, "width": 47, "height": 10},
            "text_rect": {"x": 47, "y": 470, "width": width, "height": 10},
            "player_id": player_id
        }
        assert textInput.msgs.height == 10

        assert player_id in hover_messages.dict
        assert 'height' in hover_messages.dict[player_id]
        assert 'start_timeout' in hover_messages.dict[player_id]
        assert 'text_img' in hover_messages.dict[player_id]
        assert 'width' in hover_messages.dict[player_id]

    @pytest.mark.parametrize('text_width', [150, 500])
    def test_get_new_messages_wraps_text(
        self,
        create_mock_text_input_with_redis_data,
        mock_messages_window_width,
        text_width,
        hover_messages,
        mock_pygame_messages
    ):
        width = text_width
        player_id = 0
        textInput = create_mock_text_input_with_redis_data(width, player_id)

        textInput.get_new_messages(hover_messages)

        assert 'f92d896ac90b4fed8dcc3c986ca0c1f0' in textInput.msgs.cache
        assert textInput.msgs.list[-1] == {
            "username": "testUser",
            "text": "hello world",
            "username_rect": {"x": 0, "y": 470, "width": 47, "height": 10},
            "text_rect": {"x": 47, "y": 470, "width": width, "height": 10},
            "player_id": player_id
        }
        assert textInput.msgs.height == 10

        assert player_id in hover_messages.dict
        assert 'wrapped' in hover_messages.dict[player_id]
        assert 'start_timeout' in hover_messages.dict[player_id]
        assert 'heights' in hover_messages.dict[player_id]['wrapped']
        assert 'text_imgs' in hover_messages.dict[player_id]['wrapped']
        assert 'widths' in hover_messages.dict[player_id]['wrapped']

        assert (
            len(hover_messages.dict[player_id]['wrapped']['heights']) ==
            len(hover_messages.dict[player_id]['wrapped']['text_imgs']) ==
            len(hover_messages.dict[player_id]['wrapped']['widths'])
        )

    def test_delete_old_msg_ids_no_cache(
        self, create_mock_text_input_with_redis_data
    ):
        textInput = create_mock_text_input_with_redis_data()
        textInput.delete_old_msg_ids()

        assert not textInput.msgs.cache

    def test_delete_old_msg_ids_with_cache(
        self, mock_msgs_cache, create_mock_text_input_with_redis_data
    ):
        textInput = create_mock_text_input_with_redis_data()
        textInput.delete_old_msg_ids()

        assert not textInput.msgs.cache

    def test_delete_old_msg_ids_with_only_one_id_in_cache(
        self, mock_msgs_cache_one_id, create_mock_text_input_with_redis_data
    ):
        textInput = create_mock_text_input_with_redis_data()
        textInput.delete_old_msg_ids()

        assert textInput.msgs.cache == {'f92d896ac90b4fed8dcc3c986ca0c1f0'}

    @pytest.mark.parametrize('test_input, expected_output', [
        ("test text!", "test text"),
        ("test text ", "test text"),
        (" t e st  textT", " t e st  text"),
        ])
    def test_check_input_backspace_removes_last_character(
        self,
        test_input,
        expected_output,
        mock_redis,
        mock_pygame_keys,
        mock_event
    ):
        text_input = TextInput('test user')
        text = test_input
        text_input.text = text
        text_input.check_input(mock_event)

        assert text_input.text == expected_output

    def test_check_input_backspace_empty_string_does_not_change(
        self, mock_redis, mock_pygame_keys, mock_event
    ):
        text_input = TextInput('test user')
        text = ""
        text_input.text = text
        text_input.check_input(mock_event)

        assert text_input.text == ""

    def test_check_input_keydown_calls_add_text_if_typing(
        self, mock_redis, mock_pygame_keys, mock_add_text
    ):
        event = Mock()
        event.type = True
        event.key = False
        event.unicode = 'test text'

        text_input = TextInput('test user')
        text_input.text_rect.width = 100
        text_input.username_img.get_width.return_value = 100

        text_input.check_input(event)

        assert mock_add_text.call_count == 1

    def test_add_text_width_is_less_than_max_allowed_width(
        self, mock_redis, mock_pygame_keys, mock_edge_distance
    ):
        event = Mock()
        event.type = True
        event.key = False
        event.unicode = 'test text'

        text_input = TextInput('test user')
        text_input.text = 'hello '
        text_input.text_rect.width = 99
        text_input.username_img.get_width.return_value = 100

        text_input._add_text(event)

        assert text_input.text == 'hello test text'

    def test_add_text_width_is_greater_than_max_allowed_width(
        self, mock_redis, mock_pygame_keys, mock_edge_distance
    ):
        event = Mock()
        event.type = True
        event.key = False
        event.unicode = 'test text'

        text_input = TextInput('test user')
        text_input.text = 'hello'
        text_input.text_rect.width = 500
        text_input.username_img.get_width.return_value = 100

        assert text_input.text == 'hello'

    def test_save_message_first_message_in_chat(
        self, mock_pygame, mock_strict_redis, mock_create_rect_dict
    ):
        """First message typed in the chat box, so should not call
        update_messages.
        """
        text_input = TextInput('test user')
        text_input.text = 'test'
        text_input.text_img.get_width.return_value = 100
        text_input.text_img.get_size.return_value = 100

        text_input.save_message(window=Mock(), player_id=0)

        redis = text_input.redis.redis
        expected_data_in_redis = (
            b'{"username": "test user", "text": "test", '
            b'"username_rect": {"height": 1, '
            b'"width": 1, "x": 1, "y": 1}, "text_rect": {"height": 1, '
            b'"width": 1, "x": 1, "y": 1}, "player_id": 0}'
        )
        assert redis.keys()
        assert redis.hgetall(redis.keys()[0]) == (
            {b'data': expected_data_in_redis}
        )

    def test_save_message(
        self,
        mock_pygame,
        mock_strict_redis,
        mock_create_rect_dict,
        mock_msgs_list,
        mock_update_messages
    ):
        text_input = TextInput('test user')
        text_input.text = 'test'
        text_input.text_img.get_width.return_value = 100
        text_input.text_img.get_size.return_value = 100
        text_input.text_rect.height = 0

        text_input.save_message(window=Mock(), player_id=0)

        redis = text_input.redis.redis
        expected_data_in_redis = (
            b'{"username": "test user", "text": "test", '
            b'"username_rect": {"height": 1, '
            b'"width": 1, "x": 1, "y": 1}, "text_rect": {"height": 1, '
            b'"width": 1, "x": 1, "y": 1}, "player_id": 0}'
        )
        assert redis.keys()
        assert redis.hgetall(redis.keys()[0]) == (
            {b'data': expected_data_in_redis}
        )

        assert mock_update_messages.call_count == 1

    def test_update_messages(self, mock_pygame, mock_redis, mock_msgs_list):
        text_input = TextInput('test user')
        text_input.text_rect.height = 10
        text_input._update_messages()

        assert text_input.msgs.list[0]['text_rect']['y'] == 0
        assert text_input.msgs.list[0]['username_rect']['y'] == 0
        assert text_input.msgs.list[1]['text_rect']['y'] == 10
        assert text_input.msgs.list[1]['username_rect']['y'] == 10

    def test_clear_text_input(self, mock_pygame, mock_redis):
        text_input = TextInput('test user')
        text_input.text = 'test text'
        text_input._clear_text_input(window=Mock())

        assert text_input.text == ''

    def test_draw_messages_updates_y_positions_of_messages(
        self, mock_pygame, mock_redis, mock_msgs_list, mock_chat_box_height
    ):
        text_input = TextInput('test user')
        text_input.y_text = 100
        text_input.msgs.height = 30
        text_input.text_rect.height = 20

        text_input.draw_messages(window=Mock())
        assert text_input.msgs.list == [
            {
                'text': 'test text',
                'text_rect': {'height': 8, 'width': 10, 'x': 0, 'y': 80},
                'username': 'test',
                'username_rect': {'height': 10, 'width': 10, 'x': 0, 'y': 78}
            },
            {
                'text': 'test text',
                'text_rect': {'height': 12, 'width': 10, 'x': 0, 'y': 88},
                'username': 'test2',
                'username_rect': {'height': 10, 'width': 10, 'x': 0, 'y': 90}
            }
        ]

    def test_delete_oldest_message_height_of_text_is_more_than_chat_box(
        self, mock_pygame, mock_redis, mock_msgs_list, mock_chat_box_height
    ):
        text_input = TextInput('test user')
        text_input.msgs.height = 100
        text_input.text_rect.height = 20
        text_input._delete_oldest_message()

        assert text_input.msgs.height == 92
        assert text_input.msgs.list == [{
            'text_rect': {
                'x': 0,
                'y': 20,
                'height': 12,
                'width': 10
            },
            'username_rect': {
                'x': 0,
                'y': 20,
                'height': 10,
                'width': 10
            },
            'username': 'test2',
            'text': 'test text'
        }]

    def test_delete_oldest_message_height_of_text_is_less_than_chat_box(
        self, mock_pygame, mock_redis, mock_msgs_list, mock_chat_box_height
    ):
        text_input = TextInput('test user')
        text_input.msgs.height = 30
        text_input.text_rect.height = 20
        text_input._delete_oldest_message()

        assert text_input.msgs.height == 30
        assert text_input.msgs.list == [{
            'text_rect': {
                'x': 0,
                'y': 10,
                'height': 8,
                'width': 10
            },
            'username_rect': {
                'x': 0,
                'y': 10,
                'height': 10,
                'width': 10
            },
            'username': 'test',
            'text': 'test text'
        },
            {
            'text_rect': {
                'x': 0,
                'y': 20,
                'height': 12,
                'width': 10
            },
            'username_rect': {
                'x': 0,
                'y': 20,
                'height': 10,
                'width': 10
            },
            'username': 'test2',
            'text': 'test text'
        }]
