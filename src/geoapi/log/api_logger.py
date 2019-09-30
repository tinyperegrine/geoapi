import os
import sys
import logging
import asyncio
import logging.handlers
from queue import SimpleQueue
from typing import List
import yaml
import logging.config
import geoapi.common.config as config
from geoapi.common.json_models import LogEnum


class LocalQueueHandler(logging.handlers.QueueHandler):
    """Simplified queue handler for logging in async scenarios
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)


# currently unused
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


def _setup_logging_queue() -> None:
    """Move log handlers to a separate thread.

    Replace handlers on the root logger with a LocalQueueHandler,
    and start a logging.QueueListener holding the original
    handlers.

    """
    queue: SimpleQueue = SimpleQueue()
    root = logging.getLogger()

    handlers: List[logging.Handler] = []

    handler = LocalQueueHandler(queue)
    root.addHandler(handler)
    for h in root.handlers[:]:
        if h is not handler:
            root.removeHandler(h)
            handlers.append(h)

    listener = logging.handlers.QueueListener(queue,
                                              *handlers,
                                              respect_handler_level=True)
    listener.start()


def create_logger(level: LogEnum, use_yml: bool = True) -> logging.Logger:
    """Creates the Python Logger - either a basic logger or a logger configured from yaml
    
    Args:
        level (LogEnum, required): log level enum - one of the five possible log levels
        use_yml (bool, optional): configure based on yaml. Defaults to True.

    Constants:
        DEFAULT_LOG_CONFIG_YML_FILEPATH: Path to the built-in yaml file, defaults to 'geoapi/log/logging.yml'
        CONFIG_YML_ENV_KEY = Env variable for path to custom yaml file, defaults to 'LOG_YML' and by default is empty so built-in yaml is used
    
    Returns:
        logging.Logger: A fully configured logger
    """
    # First setup basic logging in case use_yml is true but yaml loading fails
    logging.basicConfig(level=level)
    logger = logging.getLogger()

    if use_yml:
        # First setup default yaml logging config - in case custom yaml is specified but fails
        default_path = config.DEFAULT_LOG_CONFIG_YML_FILEPATH
        with open(default_path) as f:
            logging_config = yaml.safe_load(f.read())
            logging.config.dictConfig(logging_config)

        # get the custom yaml config file path if specified by env
        # (e.g. in case production logging is different from dev logging)
        env_path = os.environ.get(config.CONFIG_YML_ENV_KEY)
        if env_path:
            try:
                with open(env_path) as f:
                    logging_config = yaml.safe_load(f.read())
                    logging.config.dictConfig(logging_config)
            except Exception as e:
                msg = 'Error loading custom yaml config for logging, default yaml config loaded instead.  custom yaml: {}, error: {}'.format(
                    env_path, str(e))
                logging.exception(msg)

        logger = logging.getLogger()
        logger.setLevel(level)

    # finally setup queue based logging
    _setup_logging_queue()
    logger.info('Using Log Level: {}'.format(logging.getLevelName(level)))
    return logger
