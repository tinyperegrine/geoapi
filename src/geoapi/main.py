"""App Entry Point Module:

Direct call to the module is only used during production,
    main() is imported and called during development

TODO: change uvicorn to hypercorn and insure http/2 usage with uviloop
    also have command line args and add the build system,
    include may be gunicorn and parallel workers (or docker swarm) and related configs
"""

import logging
from pathlib import Path
import uvicorn
from fastapi import FastAPI
import geoapi.config.api_configurator as config
import geoapi.log.api_logger as api_logger
import geoapi.api


def main() -> FastAPI:
    """Application Entry Point

    Returns:
        FastAPI: A fully configured running instance of FastAPI

    Usage:
        for production, cd to dist folder and run:
            docker-compose up -d
            (else, manually insure db is running and envars are setup, and then run
                python -m geoapi.main)
        for development, cd to src folder and run:
            source rundev.sh
    """

    # get api configuration
    # - default embedded config file path
    embedded_config_ini_filepath: Path = Path('geoapi/config/config.ini')
    # environmental variable for external config file path (if not using default above)
    config_ini_env_key: str = 'GEOAPI_CONFIG_INI'
    api_config, external_config_load_error = config.init(
        embedded_config_ini_filepath, config_ini_env_key)
    # set the global config dictionary so other modules can import and use it
    config.API_CONFIG = api_config

    # get logging
    api_log_level = config.API_CONFIG['GEOAPI_LOG_LEVEL']
    levelnum = logging.getLevelName(api_log_level.upper())
    logger = api_logger.init(level=levelnum)
    if external_config_load_error:
        logger.error(
            'Unable to load external supplied config.ini file. \
            Using default embedded config.ini file')

    try:
        fast_api = geoapi.api.create_api(
            database_url=config.API_CONFIG['GEOAPI_DATABASE_URL'],
            api_version=config.API_CONFIG['GEOAPI_VERSION'])
        if not fast_api:
            raise Exception("Error creating API")
        return fast_api
    except Exception as exc:
        # for all uncaught exceptions
        logger.exception("Uncaught exception: %s", str(exc))
        raise


if __name__ == "__main__":

    # Main should be called first so logging, configuration, env vars and api
    # already setup
    api: FastAPI = main()

    main_logger: logging.Logger = logging.getLogger()
    if api:
        # to set the uvicorn log level
        # first get the configured log level
        log_level: int = main_logger.getEffectiveLevel()
        # make the uvicorn log level the same as the configured root logger
        uvi_log_level: str = logging.getLevelName(log_level).lower()
        api_host: str = config.API_CONFIG['GEOAPI_HOST']
        port: str = config.API_CONFIG['GEOAPI_PORT']
        api_port: int = int(port)
        uvicorn.run(api,
                    host=api_host,
                    port=api_port,
                    log_level=uvi_log_level)
        main_logger.info('API started.')
    else:
        main_logger.error('API cannot run!')
