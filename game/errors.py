class ConfigError(Exception):
    pass


class ServerError(Exception):
    pass


class DatabaseTimeoutError(Exception):
    pass


class RedisError(Exception):
    pass
