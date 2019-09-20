import databases
import sqlalchemy
from typing import Optional, List
from geoapi.common.json_models import RealPropertyIn, RealPropertyOut, GeometryAndDistanceIn
import geoapi.common.spatial_utils as spatial_utils


class RealPropertyQueries(object):
    """Repository for all DB Query Operations.
    Different from repository for all transaction operations."""

    def __init__(self, connection: databases.Database,
                 real_property_table: sqlalchemy.Table):
        self._connection = connection
        self._real_property_table = real_property_table

    async def get_all(self) -> List[RealPropertyOut]:
        select_query = self._real_property_table.select()
        db_rows = await self._connection.fetch_all(select_query)
        out_list = [RealPropertyOut.from_db(db_row) for db_row in db_rows]
        return out_list

    async def get(self, property_id) -> Optional[RealPropertyOut]:
        select_query = self._real_property_table.select().where(
            self._real_property_table.c.id == property_id)
        db_row = await self._connection.fetch_one(select_query)
        if db_row:
            return RealPropertyOut.from_db(db_row)
        else:
            return None

    async def find(self, geometry_distance: GeometryAndDistanceIn
                  ) -> List[RealPropertyOut]:
        geoalchemy_element_buffered = spatial_utils.buffer(
            geometry_distance.location_geo, geometry_distance.distance)
        select_query = self._real_property_table.select().where(
            self._real_property_table.c.geocode_geo.ST_Intersects(
                geoalchemy_element_buffered))
        db_rows = await self._connection.fetch_all(select_query)
        out_list = [RealPropertyOut.from_db(db_row) for db_row in db_rows]
        return out_list
