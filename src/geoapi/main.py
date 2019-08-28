# cd to src, then:
# uvicorn geoapi.main:app --reload
from typing import List
from typing import Union
from typing import Optional
from fastapi import FastAPI

from geoapi.models import DB
from geoapi.models import CoffeeShopIn
from geoapi.models import CoffeeShopOut

DATABASE_URL = "postgresql://docker:docker@localhost:25432/gis"

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


@app.get("/coffeeshops/", response_model=List[CoffeeShopOut])
async def get_all_coffee_shops():
    out_list = await db.coffee_shop_repository.get_all()
    return out_list


@app.get("/coffeeshops/{shop_id}/", response_model=CoffeeShopOut)
async def get_coffee_shop(shop_id: int):
    coffee_shop = await db.coffee_shop_repository.get(shop_id)
    return coffee_shop


@app.post("/coffeeshops/", response_model=CoffeeShopOut)
async def create_coffee_shop(coffeeshop: CoffeeShopIn):
    new_coffee_shop = await db.coffee_shop_repository.create(coffeeshop)
    return new_coffee_shop
