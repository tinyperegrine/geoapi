# cd to src and archive
# git archive -o geapi1.zip --prefix=geoapi/ HEAD
# cd to src, then:
# unzip
# expose the app variable below globally by uncommenting: app = create_app()
# (since reload from within main is broken due to a bug)
# then run:
# uvicorn geoapi.main:app --reload

# regular use during development:
# cd to /Users/ugp/Projects/baseapis/geoapi
# source venv/bin/activate
# code .
# cd to src
# see note above for app variable
# uvicorn geoapi.main:app --reload

# production deployment:
# comment out the line: app = create_app()
# now run:
# python -m geoapi.main

import os
import uvicorn
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from starlette.staticfiles import StaticFiles

from geoapi.data.db import DB
from geoapi.routes import create_routes


# pylint: disable=unused-variable
def create_app():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = "postgresql://postgres:engineTest888@localhost:5555/zesty"
    db = DB(database_url)

    app = FastAPI(
        title="GeoAPI",
        description="A Python based REST API for geospatial data",
        version="1.0.0",
    )

    @app.on_event("startup")
    async def startup():
        await db.connection.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await db.connection.disconnect()

    @app.get("/")
    async def root() -> Dict[str, str]:
        """GeoAPI Home"""
        return {"message": "Welcome to the GEOAPI. Please go to /docs for help"}

    router = create_routes(db)
    app.include_router(
        router,
        prefix="/geoapi/v1",
        tags=["api routes"],
        responses={404: {
            "description": "Not found"
        }},
    )

    app.mount("/static", StaticFiles(directory="geoapi/static"), name="static")

    return app


# only for development, uncomment line below (since reload from within main is broken due to a bug)
# then run uvicorn geoapi.main:app --reload
app = create_app()

if __name__ == "__main__":
    app = create_app()
    api_host = os.environ.get('API_HOST')
    if not api_host:
        api_host = "127.0.0.1"
    port = os.environ.get('API_PORT')
    if not port:
        api_port = 8000
    else:
        api_port = int(port)
    uvicorn.run(app, host=api_host, port=api_port, log_level="info")