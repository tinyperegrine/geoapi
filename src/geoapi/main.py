# cd to src and archive
# git archive -o geapi1.zip --prefix=geoapi/ HEAD
# cd to src, then:
# unzip
# uvicorn geoapi.main:app --reload
from typing import List
from fastapi import FastAPI

from geoapi.models import DB
from geoapi.models import RealPropertyIn
from geoapi.models import RealPropertyOut

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
    out_list = await db.real_property_repository.get_all()
    return out_list


@app.get("/properties/{property_id}/", response_model=RealPropertyOut)
async def get_real_property(property_id: str):
    real_property = await db.real_property_repository.get(property_id)
    return real_property


@app.post("/properties/", response_model=RealPropertyOut)
async def create_real_property(real_property: RealPropertyIn):
    new_real_property = await db.real_property_repository.create(real_property)
    return new_real_property
