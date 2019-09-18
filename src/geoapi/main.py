# cd to src and archive
# git archive -o geapi1.zip --prefix=geoapi/ HEAD
# cd to src, then:
# unzip
# uvicorn geoapi.main:app --reload

# regular use during development:
# cd to /Users/ugp/Projects/baseapis/geoapi
# source venv/bin/activate
# code .
# cd to src
# uvicorn geoapi.main:app --reload

from typing import List
from fastapi import FastAPI, HTTPException

from geoapi.data.db import DB
from asyncpg.exceptions import UniqueViolationError
from geoapi.common.json_models import RealPropertyIn, RealPropertyOut

DATABASE_URL = "postgresql://postgres:engineTest888@localhost:5555/zesty"

db = DB(DATABASE_URL)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.connection.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.connection.disconnect()


@app.get("/")
async def root():
    return {"message": "Welcome to the GEOAPI. Please go to /docs for help"}


@app.get("/properties/", response_model=List[RealPropertyOut])
async def get_all_real_properties():
    out_list = await db.real_property_queries.get_all()
    return out_list


@app.get("/properties/{property_id}/", response_model=RealPropertyOut)
async def get_real_property(property_id: str):
    real_property = await db.real_property_queries.get(property_id)
    return real_property


@app.post("/properties/", response_model=RealPropertyOut)
async def create_real_property(real_property: RealPropertyIn):
    """written as a 'post' with the provided id - should probably be a 'put',
    with logic to create or update depending on if the id exists.  Depends on 
    business logic details"""
    try:
        await db.real_property_commands.create(real_property)
    except UniqueViolationError as ue:
        # replace with custom API exceptions to remove db dependency
        error_details = ue.as_dict()
        raise HTTPException(status_code=409,
                            detail={
                                'message': error_details['message'],
                                'detail': error_details['detail']
                            })
    else:
        new_real_property = await db.real_property_queries.get(real_property.id)
        return new_real_property
