from logger import get_logger
from redis import StrictRedis
from uuid import uuid4

log = get_logger(__name__)

MSG_LIFETIME_SECONDS = 300


class RedisClient:

    def __init__(self):
        self.redis = StrictRedis(
            host='localhost', port=6379, decode_responses=True, charset='utf-8'
        )

        log.info('Connected to redis.')

    def get_message(self, message_id: str) -> str:
        pass

    def save_message(self, username: str, message: str) -> str:
        message_id = uuid4().hex
        payload = {
            'username': username,
            'message': message
        }
        self.redis.hmset(message_id, payload)
        self.redis.expire(message_id, MSG_LIFETIME_SECONDS)

        return message_id

    def get_all_messages(self) -> list:
        return [
            {
                'id': message_id,
                'username': self.redis.hget(message_id, 'username'),
                'message': self.redis.hget(message_id, 'message'),
                'expires_in': self.redis.ttl(message_id)
            }
            for message_id in self.redis.keys()
        ]

    def sort_messages_by_expiry(self, messages: list) -> list:
        return sorted(
            messages,
            key=lambda message: message['expires_in'],
            reverse=False
        )
