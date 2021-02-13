import logging

from datetime import datetime
from game.errors import ConfigError
from game.typing import Logger


def get_logger(file: str, file_log_level: str = 'WARNING') -> Logger:
    """Create and log todays logs to Lobby/logs."""
    level = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logger = logging.getLogger(file)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    )

    date = datetime.now().strftime('%Y-%m-%d')
    filename = f'logs/{date}.log'

    file_handler = logging.FileHandler(filename)
    try:
        file_handler.setLevel(level[file_log_level])
    except KeyError:
        raise ConfigError(f'Log level expected to be in {level.keys()}.')
    else:
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(stream_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
