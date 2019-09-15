import databases
import sqlalchemy
from geoalchemy2.types import Geography
from pydantic import BaseModel, Json
from typing import Optional
import geoapi.spatial_utils as spatial_utils


class RealPropertyBase(BaseModel):
    id: str
    image_url: Optional[str] = None


class RealPropertyIn(RealPropertyBase):
    pass


class RealPropertyOut(RealPropertyBase):
    geocode_geo_json: Optional[str] = None


class RealPropertyRepository(object):

    def __init__(self, connection: databases.Database,
                 real_property_table: sqlalchemy.Table):
        self._connection = connection
        self._real_property_table = real_property_table

    async def get_all(self):
        query = self._real_property_table.select()
        db_rows = await self._connection.fetch_all(query)
        out_list = []
        for db_row in db_rows:
            geocode_geo_json_tmp = spatial_utils.to_geo_json(
                db_row["geocode_geo"])
            output_obj = RealPropertyOut(id=db_row["id"],
                                         image_url=db_row["image_url"],
                                         geocode_geo_json=geocode_geo_json_tmp)
            out_list.append(output_obj)
        return out_list

    async def get(self, property_id):
        query = self._real_property_table.select().where(
            self._real_property_table.c.id == property_id)
        db_rows = await self._connection.fetch_all(query)
        out_list = []
        for db_row in db_rows:
            geocode_geo_json_tmp = spatial_utils.to_geo_json(
                db_row["geocode_geo"])

            output_obj = RealPropertyOut(id=db_row["id"],
                                         image_url=db_row["image_url"],
                                         geocode_geo_json=geocode_geo_json_tmp)
            out_list.append(output_obj)
        return out_list[0]

    async def create(self, real_property: RealPropertyIn) -> RealPropertyOut:
        # element = spatial_utils.from_lon_lat(real_property.lon,
        #                                      real_property.lat)

        query = self._real_property_table.insert().values(
            id=real_property.id,
            image_url=real_property.image_url,
            geocode_geo=None,
            parcel_geo=None,
            building_geo=None,
            image_bounds=None)
        await self._connection.execute(query)
        new_real_property = await self.get(real_property.id)
        return new_real_property


class DB(object):

    def __init__(self, database_url: str):
        self._connection = databases.Database(database_url)
        metadata = sqlalchemy.MetaData()
        real_property_table = sqlalchemy.Table(
            "properties",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
            sqlalchemy.Column("geocode_geo",
                              Geography(geometry_type='POINT', srid=4326),
                              nullable=True),
            sqlalchemy.Column("parcel_geo",
                              Geography(geometry_type='POLYGON', srid=4326),
                              nullable=True),
            sqlalchemy.Column("building_geo",
                              Geography(geometry_type='POLYGON', srid=4326),
                              nullable=True),
            sqlalchemy.Column("image_bounds",
                              sqlalchemy.ARRAY(sqlalchemy.Numeric),
                              nullable=True),
            sqlalchemy.Column("image_url", sqlalchemy.String, nullable=True),
        )
        self._real_property_repository = RealPropertyRepository(
            self._connection, real_property_table)

    @property
    def connection(self) -> databases.Database:
        return self._connection

    @property
    def real_property_repository(self) -> RealPropertyRepository:
        return self._real_property_repository
