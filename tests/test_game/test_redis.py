import json
import pytest

from fakeredis import FakeStrictRedis
from game.errors import DatabaseTimeoutError
from game.redis import RedisClient
from time import sleep
from unittest.mock import patch, Mock


@pytest.fixture
def mock_redis():
    with patch('redis.StrictRedis') as redis:
        redis.return_value = FakeStrictRedis()
        yield redis
        redis.return_value.flushall()


@pytest.fixture
def uuid4():
    with patch('game.redis.uuid4') as uuid4:
        yield uuid4


@pytest.fixture
def mock_message_lifetime():
    with patch('game.redis.MSG_LIFETIME_SECONDS', 1) as lifetime:
        yield lifetime


@pytest.fixture
def mock_timeout_error():
    with patch('redis.StrictRedis') as redis:
        redis.return_value.ping.side_effect = Mock(
            side_effect=DatabaseTimeoutError(
                'Timeout connecting to the database.'
            )
        )
        yield redis


@pytest.fixture
def mock_payload():
    def _mock_payload(payload):
        return {'data': json.dumps(payload)}
    return _mock_payload


def test_connect_to_redis(mock_redis):
    redis_client = RedisClient()
    assert redis_client.redis.ping()


def test_timeout_connect_to_redis(mock_timeout_error):
    with pytest.raises(DatabaseTimeoutError) as err:
        RedisClient()
    err.match('Timeout connecting to the database.')


def test_get_message(mock_redis):
    redis = RedisClient()

    redis.redis.hset('message-1', 'test', 'My test message!')

    message = redis.get_message('message-1')
    assert message.get(b'test') == b'My test message!'


@pytest.mark.slow
def test_save_message(mock_redis, mock_message_lifetime, uuid4):
    uuid4.return_value.hex = 'myrandomhex123'
    redis = RedisClient()

    message_id = redis.save_message({'hello': 'world'})
    saved_data = redis.redis.hgetall(message_id.encode())

    assert message_id == 'myrandomhex123'
    assert saved_data.get(b'data') == b'{"hello": "world"}'

    sleep(1)

    expired_message = redis.redis.hgetall(message_id.encode())
    assert not expired_message


def test_get_all_messages(mock_redis, mock_payload):
    payload_1 = mock_payload({'hello': 'world'})
    payload_2 = mock_payload({'fee': 'fi fo fum'})
    payload_3 = mock_payload({'greetings': 'traveller'})

    redis = RedisClient()
    redis.redis.hmset('message-1', payload_1)
    redis.redis.hmset('message-2', payload_2)
    redis.redis.hmset('message-3', payload_3)

    messages = redis.get_all_messages()

    assert messages == [
        {
            'id': b'message-1',
            'data': b'{"hello": "world"}',
            'expires_in': -1
        },
        {
            'id': b'message-2',
            'data': b'{"fee": "fi fo fum"}',
            'expires_in': -1
        },
        {
            'id': b'message-3',
            'data': b'{"greetings": "traveller"}',
            'expires_in': -1
        }
    ]


def test_sort_messages_by_expiry(mock_redis):
    redis = RedisClient()
    messages = [
        {
            'id': b'message-1',
            'data': b'{"hello": "world"}',
            'expires_in': 12
        },
        {
            'id': b'message-2',
            'data': b'{"fee": "fi fo fum"}',
            'expires_in': 3
        },
        {
            'id': b'message-3',
            'data': b'{"greetings": "traveller"}',
            'expires_in': 531
        }
    ]

    sorted_messages = redis.sort_messages_by_expiry(messages)

    assert sorted_messages == [
        {
            'id': b'message-3',
            'data': b'{"greetings": "traveller"}',
            'expires_in': 531
        },
        {
            'id': b'message-1',
            'data': b'{"hello": "world"}',
            'expires_in': 12
        },
        {
            'id': b'message-2',
            'data': b'{"fee": "fi fo fum"}',
            'expires_in': 3
        }
    ]
