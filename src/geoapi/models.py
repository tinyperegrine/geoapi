import databases
import sqlalchemy
from geoalchemy2.types import Geography
from pydantic import BaseModel, Json

import geoapi.spatial_utils as spatial_utils


class CoffeeShopBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip: str
    lat: float
    lon: float


class CoffeeShopIn(CoffeeShopBase):
    pass


class CoffeeShopOut(CoffeeShopBase):
    id: int
    geo_json: str


class CoffeeShopRepository(object):

    def __init__(self, connection: databases.Database,
                 coffee_shop_table: sqlalchemy.Table):
        self._connection = connection
        self._coffee_shop_table = coffee_shop_table

    async def get_all(self):
        query = self._coffee_shop_table.select()
        db_rows = await self._connection.fetch_all(query)
        out_list = []
        for db_row in db_rows:
            geo_json_tmp = spatial_utils.to_geo_json(db_row["location"])
            output_obj = CoffeeShopOut(id=db_row["id"],
                                       name=db_row["name"],
                                       address=db_row["address"],
                                       city=db_row["city"],
                                       state=db_row["state"],
                                       zip=db_row["zip"],
                                       lat=db_row["lat"],
                                       lon=db_row["lon"],
                                       geo_json=geo_json_tmp)
            out_list.append(output_obj)
        return out_list

    async def get(self, shop_id):
        query = self._coffee_shop_table.select().where(
            self._coffee_shop_table.c.id == shop_id)
        db_rows = await self._connection.fetch_all(query)
        out_list = []
        for db_row in db_rows:
            geo_json_tmp = spatial_utils.to_geo_json(db_row["location"])

            output_obj = CoffeeShopOut(id=db_row["id"],
                                       name=db_row["name"],
                                       address=db_row["address"],
                                       city=db_row["city"],
                                       state=db_row["state"],
                                       zip=db_row["zip"],
                                       lat=db_row["lat"],
                                       lon=db_row["lon"],
                                       geo_json=geo_json_tmp)
            out_list.append(output_obj)
        return out_list[0]

    async def create(self, coffeeshop: CoffeeShopIn) -> CoffeeShopOut:
        element = spatial_utils.from_lon_lat(coffeeshop.lon, coffeeshop.lat)

        query = self._coffee_shop_table.insert().values(
            name=coffeeshop.name,
            address=coffeeshop.address,
            city=coffeeshop.city,
            state=coffeeshop.state,
            zip=coffeeshop.zip,
            lat=coffeeshop.lat,
            lon=coffeeshop.lon,
            location=element)
        last_record_id = await self._connection.execute(query)

        new_coffee_shop = await self.get(last_record_id)
        return new_coffee_shop


class DB(object):

    def __init__(self, database_url: str):
        self._connection = databases.Database(database_url)
        metadata = sqlalchemy.MetaData()
        coffee_shop_table = sqlalchemy.Table(
            "g_coffee_shops",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("name", sqlalchemy.String),
            sqlalchemy.Column("address", sqlalchemy.String),
            sqlalchemy.Column("city", sqlalchemy.String),
            sqlalchemy.Column("state", sqlalchemy.String),
            sqlalchemy.Column("zip", sqlalchemy.String),
            sqlalchemy.Column("lat", sqlalchemy.Numeric),
            sqlalchemy.Column("lon", sqlalchemy.Numeric),
            sqlalchemy.Column("location",
                              Geography(geometry_type='POINT', srid=4326)),
        )
        self._coffee_shop_repository = CoffeeShopRepository(
            self._connection, coffee_shop_table)

    @property
    def connection(self) -> databases.Database:
        return self._connection

    @property
    def coffee_shop_repository(self) -> CoffeeShopRepository:
        return self._coffee_shop_repository
