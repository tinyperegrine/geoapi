"""App Entry Point Module:

TODO (tinyperegrine@): also have command line args and add the build system,
include may be gunicorn and parallel workers (or docker swarm) and related configs
"""

import os
import logging
import uvicorn
from fastapi import FastAPI
import geoapi.common.config as config
import geoapi.log.api_logger as api_logger
import geoapi.api


def _get_env_vars():
    logger = logging.getLogger(__name__)
    # to set the uvicorn log level
    # first get the configured log level since it should already have been set in main()
    log_level = logger.getEffectiveLevel()
    # make the uvicorn log level the same as the root logger
    uvi_log_level = logging.getLevelName(log_level).lower()
    api_host = os.environ.get('API_HOST')
    if not api_host:
        api_host = config.DEFAULT_API_HOST
    port = os.environ.get('API_PORT')
    if not port:
        api_port = config.DEFAULT_API_PORT
    else:
        api_port = int(port)
    return {'log_level': uvi_log_level, 'host': api_host, 'port': api_port}


def main() -> FastAPI:
    """Application Entry Point

    Returns:
        FastAPI: A fully configured running instance of FastAPI

    Usage:
        for production, cd to dist folder and run:
            python -m geoapi.main
        for development, cd to src folder run:
            source rundev.sh
    """
    api_log_level = os.environ.get('API_LOG_LEVEL')
    if not api_log_level:
        # use defaults
        logger = api_logger.create_logger(level=config.DEFAULT_API_LOG_LEVEL)
    else:
        levelnum = logging.getLevelName(api_log_level.upper())
        logger = api_logger.create_logger(level=levelnum)
    api_version = os.environ.get('API_VERSION')
    if not api_version:
        # use defaults
        api_version = config.DEFAULT_API_VERSION
    try:
        # should fail if no db url specified (no defaults for this)
        db_url = os.environ['DATABASE_URL']
        fast_api = geoapi.api.create_api(database_url=db_url,
                                         api_version=api_version)
        if not fast_api:
            raise Exception("Error creating API")
        return fast_api
    except KeyError:
        logger.error('Environmental Variable not set! DATABASE_URL')
        raise
    except Exception as exc:
        # for all uncaught exceptions
        logger.exception("Uncaught exception: %s", str(exc))
        raise


if __name__ == "__main__":
    api: FastAPI = main()
    main_logger: logging.Logger = logging.getLogger(__name__)
    if api:
        env_vars: dict = _get_env_vars()
        uvicorn.run(api,
                    host=env_vars['host'],
                    port=env_vars['port'],
                    log_level=env_vars['log_level'])
        main_logger.info('API started.')
    else:
        main_logger.error('API cannot run!')
