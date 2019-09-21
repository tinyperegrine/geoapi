import asyncio
import databases
import sqlalchemy
from sqlalchemy.sql import select, func
from typing import Optional, List, Dict, Any
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

    async def find(self, geometry_distance: GeometryAndDistanceIn) -> List[str]:
        geoalchemy_element_buffered = spatial_utils.buffer(
            geometry_distance.location_geo, geometry_distance.distance)
        select_query = select([self._real_property_table.c.id]).where(
            self._real_property_table.c.geocode_geo.ST_Intersects(
                geoalchemy_element_buffered))
        db_rows = await self._connection.fetch_all(select_query)
        out_list = [db_row["id"] for db_row in db_rows]
        return out_list

    """just for testing parallel running of queries"""

    # async def _query_parcels(self, select_query_parcels):
    #     parcel_area = await self._connection.fetch_val(select_query_parcels)
    #     return parcel_area

    # async def _query_buildings(self, select_query_buildings):
    #     db_rows = await self._connection.fetch_all(select_query_buildings)
    #     return db_rows
    async def statistics(self, property_id: str,
                         distance: int) -> Dict[str, Any]:
        result = {}
        select_query = select([
            self._real_property_table.c.geocode_geo
        ]).where(self._real_property_table.c.id == property_id)
        db_row = await self._connection.fetch_one(select_query)
        if not db_row:
            return {}

        # get zone - buffer around property
        geojson_obj = spatial_utils.to_geo_json(db_row["geocode_geo"])
        geoalchemy_element_buffered = spatial_utils.buffer(
            geojson_obj, distance)
        zone_area = spatial_utils.area(geoalchemy_element_buffered)
        if not zone_area:
            return {}

        # get parcel area
        select_query_parcels = select(
            [func.sum(self._real_property_table.c.parcel_geo.ST_Area())]).where(
                self._real_property_table.c.parcel_geo.ST_Intersects(
                    geoalchemy_element_buffered))

        # get buildings
        select_query_buildings = select(
            [self._real_property_table.c.building_geo]).where(
                self._real_property_table.c.building_geo.ST_Intersects(
                    geoalchemy_element_buffered))

        parcel_area = await self._connection.fetch_val(select_query_parcels)
        db_rows = await self._connection.fetch_all(select_query_buildings)
        """just for testing:
        as an alternative - comment out the two rows above
        and uncomment the four rows below and this will
        run the queries in parallel since they are not dependent on each other
        """
        # parcel_area, db_rows = await asyncio.gather(
        #     self._query_parcels(select_query_parcels),
        #     self._query_buildings(select_query_buildings),
        # )

        # get final results
        if not parcel_area:
            parcel_area = 0
        result['parcel_area_sqm'] = round(parcel_area)
        # get distance and area for buildings
        if db_rows:
            area_distance_list = [
                spatial_utils.area_distance(db_row["building_geo"], geojson_obj)
                for db_row in db_rows
            ]
            building_area = sum([dc['area'] for dc in area_distance_list])
        else:
            area_distance_list = []
            building_area = 0
        result['building_area_distance'] = area_distance_list
        zone_density_percentage = 100 * building_area / zone_area
        result['zone_density_percentage'] = round(zone_density_percentage)

        return result
