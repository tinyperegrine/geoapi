"""API Construction Module

Raises:
    exc: On database connection errors

Returns:
    FastAPI: An API with routes and db connection created
"""

import logging
import asyncio
from typing import Optional, Dict
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
import geoapi.common.config as config
from geoapi.data.db import DB
from geoapi.routes import create_routes


# pylint: disable=unused-variable
def create_api(database_url: Optional[str] = None,
               api_version: str = config.DEFAULT_API_VERSION
              ) -> Optional[FastAPI]:
    """API constructor function

    Args:
        database_url (str, optional): db connection url to a postgis enabled postgres db.
            Defaults to None.
        api_version (str, optional): api version for display and routing prefix.
            Defaults to config DEFAULT_API_VERSION e.g. 1.0.0

    Raises:
        exc: On database connection errors

    Returns:
        FastAPI: An API with routes and db connection created
    """

    # database_url = "postgresql://postgres:engineTest888@localhost:5555/zesty"
    if not database_url:
        return None

    # 1. setup api
    api = FastAPI(
        title="GeoAPI",
        description="A Python based REST API for geospatial data",
        version=api_version,
    )

    # 2. setup db
    db_api = DB(database_url)

    # 3. connect/disconnect db on api startup/shutdown events
    @api.on_event("startup")
    async def startup():
        """improve initial connection with health checks and docker based functions"""

        # log
        logger = logging.getLogger(__name__)
        logger.info('Database: %s', database_url)
        logger.info('connecting to db')
        tries = 3
        for i in range(tries):
            try:
                logger.info('trying %d', i + 1)
                await db_api.connection.connect()
            except Exception as exc:  # pylint: disable=broad-except
                # log, wait and retry - retry interval 60
                # broad exception is acceptable here since it is logged and
                # eventually raised if persistent
                if i < tries - 1:
                    logger.error(
                        'failed to connect to db, trying again. Error: %s',
                        str(exc))
                    await asyncio.sleep(60)
                    continue
                else:
                    logger.error('failed to connect to db, exiting!')
                    raise exc
            break
        logger.info('connected to db')

    @api.on_event("shutdown")
    async def shutdown():
        await db_api.connection.disconnect()

    # 4. setup api home route
    @api.get("/")
    async def root() -> Dict[str, str]:
        """GeoAPI Home

        Returns:
            {
                "message": "Welcome to the GEOAPI. Please go to /docs for help"
            }
        """
        return {"message": "Welcome to the GEOAPI. Please go to /docs for help"}

    # 5. setup all other routes
    router = create_routes(db_api)
    # specify api version in routes - use major version only, e.g. for 1.0.0 "/geoapi/v1"
    prefix = '/geoapi/v' + str(api_version.split('.', 1)[0])
    api.include_router(
        router,
        prefix=prefix,
        tags=["api routes"],
        responses={404: {
            "description": "Not found"
        }},
    )

    # eventually manage with gunicorn, etc.
    api.mount("/static", StaticFiles(directory="geoapi/static"), name="static")

    return api
