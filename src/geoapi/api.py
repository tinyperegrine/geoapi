import logging
import asyncio
from typing import Optional, List, Dict
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from geoapi.data.db import DB
from geoapi.routes import create_routes


# pylint: disable=unused-variable
def create_api(database_url=None):

    # database_url = "postgresql://postgres:engineTest888@localhost:5555/zesty"
    if not database_url:
        return None

    # 1. setup api
    api = FastAPI(
        title="GeoAPI",
        description="A Python based REST API for geospatial data",
        version="1.0.0",
    )

    # 2. setup db
    db = DB(database_url)

    # 3. connect/disconnect db on api startup/shutdown events
    @api.on_event("startup")
    async def startup():
        """improve initial connection with health checks and docker based functions"""

        # log
        logger = logging.getLogger(__name__)
        logger.info('Database: {}'.format(database_url))
        logger.info('connecting to db')
        tries = 3
        for i in range(tries):
            try:
                logger.info('trying {}'.format(i + 1))
                await db.connection.connect()
            except Exception as ex:
                # log, wait and retry - retry interval 60
                if i < tries - 1:
                    await asyncio.sleep(60)
                    continue
                else:
                    logger.error('failed to connect to db!')
                    raise
            break
        logger.info('connected to db')

    @api.on_event("shutdown")
    async def shutdown():
        await db.connection.disconnect()

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
    router = create_routes(db)
    # specify api version in routes through config/env/commandline etc.
    api.include_router(
        router,
        prefix="/geoapi/v1",
        tags=["api routes"],
        responses={404: {
            "description": "Not found"
        }},
    )

    # eventually manage with gunicorn, etc.
    api.mount("/static", StaticFiles(directory="geoapi/static"), name="static")

    return api
