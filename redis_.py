from datetime import timedelta
from redis import StrictRedis
from uuid import uuid4

MESSAGE_LIFETIME = timedelta(hours=6)


class RedisClient:

    def __init__(self):
        self.redis = StrictRedis.Redis(
            host='localhost', port=6379, decode_responses=True, charset='utf-8'
        )

    def get_message(self, message_id: str) -> str:
        pass

    def save_message(self, username: str, message: str) -> None:
        message_id = uuid4().hex
        payload = {
            'username': username,
            'message': message
        }
        self.redis.hmset(message_id, payload)
        self.redis.expire(message_id, MESSAGE_LIFETIME)

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
