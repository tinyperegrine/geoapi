import os
import sys
import logging
import uvicorn
import geoapi.common.config as config
from geoapi.log.api_logger import create_logger
from geoapi.api import create_api

# for production, cd to dist folder and run:
# python -m geoapi.main


def main():
    api_log_level = os.environ.get('API_LOG_LEVEL')
    if not api_log_level:
        # use defaults
        logger = create_logger(level=config.DEFAULT_API_LOG_LEVEL)
    else:
        levelnum = logging.getLevelName(api_log_level.upper())
        logger = create_logger(level=levelnum)

    try:
        # should fail if no db url specified (no defaults for this)
        db_url = os.environ['DATABASE_URL']
        api = create_api(database_url=db_url)
        return api
    except KeyError:
        logger.error('Environmental Variable not set! DATABASE_URL')
        raise
    except Exception as e:
        # for all uncaught exceptions
        logger.exception("Uncaught exception: {0}".format(str(e)))
        raise


if __name__ == "__main__":
    """App Production Entry Point:

    TODO: also have command line args, add the build system, include may be gunicorn and parallel workers (or docker swarm) and related configs
    """
    api = main()
    logger = logging.getLogger(__name__)
    if api:
        # set host and port
        api_host = os.environ.get('API_HOST')
        if not api_host:
            api_host = config.DEFAULT_API_HOST
        port = os.environ.get('API_PORT')
        if not port:
            api_port = config.DEFAULT_API_PORT
        else:
            api_port = int(port)

        # set uvicorn log level
        # get the configured log level since it's already been set in main()
        api_log_level = logger.getEffectiveLevel()
        # make the uvicorn log level the same as the root logger
        uvi_log_level = logging.getLevelName(api_log_level).lower()

        uvicorn.run(api, host=api_host, port=api_port, log_level=uvi_log_level)
        logger.info('API started.')
    else:
        logger.error('API cannot run!')
