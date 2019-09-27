import os
import queue
import logging
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler


class APIFormatter(logging.Formatter):
    """Custom Formatter
    Defines the default format for logging messages and appends additional info to debug messages
    """

    date_format = "%Y-%m-%d %H:%M:%S"
    default_format_string = "%(asctime)s.%(msecs)03d [%(process)d:%(thread)d] %(levelname)s %(name)s [-] %(message)s"
    debug_format_suffix = "%(funcName)s %(pathname)s:%(lineno)d"

    def __init__(self):
        super().__init__(fmt=APIFormatter.default_format_string,
                         datefmt=APIFormatter.date_format,
                         style='%')

    def format(self, record):
        format_orig = self._style._fmt
        if record.levelno in [logging.DEBUG, logging.ERROR, logging.CRITICAL]:
            self._style._fmt = APIFormatter.default_format_string + " " + APIFormatter.debug_format_suffix

        result = logging.Formatter.format(self, record)
        self._style._fmt = format_orig
        return result


def create_log(log_file: str = 'geoapi/logs/geoapi.log'):
    """sets up all logging (formatting, handlers, queue and listener)
    Use this function in main to start logging.
    
    Args:
        log_file (str, optional): path and name of log file. Defaults to 'geoapi/logs/geoapi.log'.

    Returns:
        python logger: returns the configured root logger
    """

    log_queue: queue.Queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(queue_handler)

    console_handler = logging.StreamHandler()
    formatter = APIFormatter()
    console_handler.setFormatter(formatter)

    rotating_file_handler = RotatingFileHandler(log_file,
                                                maxBytes=100000,
                                                backupCount=10)
    rotating_file_handler.setFormatter(formatter)

    listener = QueueListener(log_queue, console_handler, rotating_file_handler)
    listener.start()
    return logger
