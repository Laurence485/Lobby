import json
import redis
import typing

from game.errors import DatabaseTimeoutError
from logger import get_logger
from uuid import uuid4

log = get_logger(__name__)

MSG_LIFETIME_SECONDS = 5  # 300


class RedisClient:
    def __init__(self):
        self.redis = redis.StrictRedis(
            host='localhost',
            port=6379,
            decode_responses=True,
            charset='utf-8',
            socket_connect_timeout=30
        )
        try:
            self.redis.ping()
            log.info('Connected to redis.')
        except redis.exceptions.TimeoutError as err:
            raise DatabaseTimeoutError(err)

    def get_message(self, message_id: str) -> str:
        pass

    def save_message(self, client_payload: dict) -> str:
        message_id = uuid4().hex
        payload = {
            'data': json.dumps(client_payload),
        }
        self.redis.hmset(message_id, payload)
        self.redis.expire(message_id, MSG_LIFETIME_SECONDS)

        log.debug(f'message saved!: {payload}')
        return message_id

    def get_all_messages(
        self, cached_keys: typing.collections.KeysView = None
    ) -> list:
        if cached_keys:
            keys = self.redis.keys() - cached_keys
        else:
            keys = self.redis.keys()
        return [
            {
                'id': message_id,
                'data': self.redis.hget(message_id, 'data'),
                'expires_in': self.redis.ttl(message_id)
            }
            for message_id in keys
        ]

    def sort_messages_by_expiry(self, messages: list) -> list:
        return sorted(
            messages,
            key=lambda message: message['expires_in'],
            reverse=True
        )
