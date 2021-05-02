import pytest

from game.messages import Messages, HoverMessages
from typing import Iterator
from unittest.mock import call, Mock, patch


@pytest.fixture
def mock_pygame():
    with patch('game.messages.pygame') as pygame:
        yield pygame


@pytest.fixture
def mock_get_rendered_text_dimensions():
    with patch(
        'game.messages.HoverMessages._get_rendered_text_dimensions'
    ) as dimensions:

        dimensions.return_value = (10, 10)
        yield dimensions


@pytest.fixture
def mock_render_text():
    with patch('game.messages.HoverMessages._render_text') as text:
        text.side_effect = lambda value: value
        yield text


@pytest.fixture
def mock_draw_wrapped_speech_bubble():
    with patch(
        'game.messages.HoverMessages._draw_wrapped_speech_bubble'
    ) as speech_bubble:
        yield speech_bubble


@pytest.fixture
def mock_get_this_player():
    with patch(
        'game.messages.HoverMessages._get_this_player'
    ) as get_this_player:

        get_this_player.return_value = 0
        yield get_this_player


@pytest.fixture
def mock_message_expired():
    with patch(
        'game.messages.HoverMessages._message_expired'
    ) as message_expired:

        yield message_expired


@pytest.fixture
def mock_start_timeout():
    with patch(
        'game.messages.HoverMessages.start_timeout'
    ) as start_timeout:

        start_timeout.return_value = 1000
        yield start_timeout


class TestMessages:
    def test_len(self):
        messages = Messages()
        messages.list = [1, 2, 3]
        assert len(messages) == len(messages.list) == 3

    def test_queue(self):
        messages = Messages()
        messages.list = [1, 2, 3]
        assert isinstance(messages.queue, Iterator)
        assert next(messages.queue) == 3

    def test_add_new_message(self):
        test_message = {}
        test_message['data'] = (
            '{"username": "testUser", "text": "hello world",'
            '"username_rect": {"x": 0, "y": 470, "width": 47,'
            '"height": 10}, "text_rect": {"x": 47, "y": 470,'
            '"width": 10,'
            '"height": 10}, "player_id": 0}'
        )
        test_message['id'] = 'f92d896ac90b4fed8dcc3c986ca0c1f0'
        messages = Messages()
        messages.add_new_message(test_message)

        assert test_message['id'] in messages.cache
        assert messages.height == 10
        assert messages.list == [
            {
                'player_id': 0,
                'text': 'hello world',
                'text_rect': {'height': 10, 'width': 10, 'x': 47, 'y': 470},
                'username': 'testUser',
                'username_rect': {'height': 10, 'width': 47, 'x': 0, 'y': 470}
            }
        ]


class TestHoverMessages:
    def test_overwrite_message(self):
        hover_messages = HoverMessages(window=Mock())
        hover_messages.dict = {0: 'test', 1: 'test', 2: 'test', 3: 'test'}
        hover_messages.overwrite_message(1)
        hover_messages.overwrite_message(0)

        assert hover_messages.dict == {2: 'test', 3: 'test'}

    def test_should_wrap_text(self, mock_messages_window_width):
        hover_messages = HoverMessages(window=Mock())

        assert hover_messages.should_wrap_text(text_width=500)
        assert hover_messages.should_wrap_text(text_width=200)
        assert not hover_messages.should_wrap_text(text_width=50)
        assert not hover_messages.should_wrap_text(text_width=100)

    def test_divide_text_gives_3_parts(self, mock_messages_window_width):
        hover_messages = HoverMessages(window=Mock())
        divided_text = hover_messages.divide_text('my test text', 300)

        assert len(divided_text) == 3

    def test_divide_text_gives_2_parts(self, mock_messages_window_width):
        hover_messages = HoverMessages(window=Mock())
        divided_text = hover_messages.divide_text('my test text', 200)

        assert len(divided_text) == 2

    @pytest.mark.parametrize('test_input, expected_output', [
        ('123', ['1', '2', '3']),
        ('1234', ['1', '2', '34']),
        ('12345', ['1', '23', '45']),
        ('my test text ', ['my t', 'est ', 'text ']),
        (' 23 56  9', [' 23', ' 56', '  9']),
        ])
    def test_divide_text_into_3_parts(
        self, mock_messages_window_width, test_input, expected_output
    ):
        hover_messages = HoverMessages(window=Mock())
        divided_text = hover_messages._divide_text_into_3_parts(test_input)

        assert divided_text[0] == expected_output[0]
        assert divided_text[1] == expected_output[1]
        assert divided_text[2] == expected_output[2]

        if len(test_input) % 3 == 0:
            assert(
                len(expected_output[0]) ==
                len(expected_output[1]) ==
                len(expected_output[2])
            )
        else:
            assert (
                len(expected_output[2]) >=
                len(expected_output[1]) >=
                len(expected_output[0])
            )

    @pytest.mark.parametrize('test_input, expected_output', [
        ('12', ['1', '2']),
        ('123', ['1', '23']),
        ('12345', ['12', '345']),
        ('my test text ', ['my tes', 't text ']),
        (' 23 56  9', [' 23 ', '56  9']),
        ])
    def test_divide_text_into_2_parts(
        self, mock_messages_window_width, test_input, expected_output
    ):
        hover_messages = HoverMessages(window=Mock())
        divided_text = hover_messages._divide_text_into_2_parts(test_input)

        assert divided_text[0] == expected_output[0]
        assert divided_text[1] == expected_output[1]

        if len(test_input) % 2 == 0:
            assert len(expected_output[0]) == len(expected_output[1])
        else:
            assert len(expected_output[1]) > len(expected_output[0])

    @pytest.mark.parametrize('test_input, expected_output', [
        (('hello', 'world'), 'hello-'),
        (('hello', ' world'), 'hello'),
        (('hello ', 'world'), 'hello '),
        ((' g o o d', 'afternoon !'), ' g o o d-'),
        ])
    def test_ammend_mid_word_divide(self, test_input, expected_output):
        hover_messages = HoverMessages(window=Mock())
        sentence = test_input[0]
        next_sentence = test_input[1]
        ammended_sentence = hover_messages._ammend_mid_word_divide(
            sentence, next_sentence
        )

        assert ammended_sentence == expected_output

    def test_create_texts_for_wrapping(
        self, mock_get_rendered_text_dimensions, mock_render_text
    ):
        hover_messages = HoverMessages(window=Mock())
        divided_text = [
            'hello world tes-', 'ting the dividin-', 'g up of the text'
        ]

        texts = hover_messages.create_texts_for_wrapping(divided_text)

        assert texts[0]['text_img'] == 'g up of the text'
        assert texts[0]['text_rect']['relative_ypos'] == 0

        assert texts[1]['text_img'] == 'ting the dividin-'
        assert texts[1]['text_rect']['relative_ypos'] == -10

        assert texts[2]['text_img'] == 'hello world tes-'
        assert texts[2]['text_rect']['relative_ypos'] == -20

    def test_add_messages(self, mock_pygame, mock_start_timeout):
        hover_messages = HoverMessages(window=Mock())
        text_rect = {'width': 10, 'height': 10}
        mock_text_img = 'test text img'

        hover_messages.add_message(
            player_id=0, text_img=mock_text_img, text_rect=text_rect
        )
        hover_messages.add_message(
            player_id=1, text_img=mock_text_img, text_rect=text_rect
        )
        hover_messages.add_message(
            player_id=2, text_img=mock_text_img, text_rect=text_rect
        )

        assert hover_messages.dict == {
            0:
                {
                    'height': 10,
                    'start_timeout': 1000,
                    'text_img': 'test text img',
                    'width': 10
                 },
            1:
                {
                    'height': 10,
                    'start_timeout': 1000,
                    'text_img': 'test text img',
                    'width': 10
                },
            2:
                {
                    'height': 10,
                    'start_timeout': 1000,
                    'text_img': 'test text img',
                    'width': 10
                }
        }

    def test_add_wrapped_message(self, mock_pygame):
        hover_messages = HoverMessages(window=Mock())
        texts = [
            {
                'text_img': 'mock text img 3',
                'text_rect': {
                    'width': 10,
                    'height': 10,
                    'relative_ypos': 0
                    }
            },
            {
                'text_img': 'mock text img 2',
                'text_rect': {
                    'width': 35,
                    'height': 10,
                    'relative_ypos': -10
                }
            },
            {
                'text_img': 'mock text img 1',
                'text_rect': {
                    'width': 41,
                    'height': 10,
                    'relative_ypos': -20
                }
            }
        ]
        hover_messages.add_wrapped_message(player_id=0, texts=texts)

        assert hover_messages.dict[0]['wrapped'] == {
            'heights': [10, 10, 10],
            'relative_ypos': [0, -10, -20],
            'text_imgs': [
                'mock text img 3', 'mock text img 2', 'mock text img 1'
            ],
            'widths': [10, 35, 41]
        }
        assert 'start_timeout' in hover_messages.dict[0]

    def test_draw_wrapped_message(
        self,
        mock_draw_wrapped_speech_bubble,
        mock_pygame,
        mock_get_this_player,
        mock_message_expired
    ):
        hover_messages = HoverMessages(window=Mock())

        hover_messages.dict = {
            0: {
                'start_timeout': 14187,
                'wrapped': {
                    'heights': [11, 10, 10],
                    'relative_ypos': [0, -11, -21],
                    'text_imgs': [
                        'mock text img 3', 'mock text img 2', 'mock text img 1'
                    ],
                    'widths': [94, 91, 90]
                }
            }
         }

        hover_messages.draw(player=Mock(), other_players=Mock())

        assert mock_draw_wrapped_speech_bubble.call_count == 3
        assert mock_draw_wrapped_speech_bubble.call_args_list == [
            call(
                    {
                        'heights': [11, 10, 10],
                        'relative_ypos': [0, -11, -21],
                        'text_imgs': [
                            'mock text img 3',
                            'mock text img 2',
                            'mock text img 1'
                        ],
                        'widths': [94, 91, 90]
                    },
                    0,
                    0
            ),
            call(
                    {
                        'heights': [11, 10, 10],
                        'relative_ypos': [0, -11, -21],
                        'text_imgs': [
                            'mock text img 3',
                            'mock text img 2',
                            'mock text img 1'
                        ],
                        'widths': [94, 91, 90]
                    },
                    1,
                    0
            ),
            call(
                    {
                        'heights': [11, 10, 10],
                        'relative_ypos': [0, -11, -21],
                        'text_imgs': [
                            'mock text img 3',
                            'mock text img 2',
                            'mock text img 1'
                        ],
                        'widths': [94, 91, 90]
                    },
                    2,
                    0
                )
        ]
