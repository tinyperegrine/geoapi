"""Query Object for all read-only queries to the Real Property table
"""

import os
import logging
from time import time
from typing import List
import asyncio
import aiohttp
import aiofiles
import databases
from PIL import Image
import sqlalchemy
from sqlalchemy.sql import select, func
import geoapi.common.spatial_utils as spatial_utils
import geoapi.common.decorators as decorators
from geoapi.common.exceptions import ResourceNotFoundError, ResourceMissingDataError
from geoapi.common.json_models import RealPropertyOut, GeometryAndDistanceIn, StatisticsOut


class RealPropertyQueries():
    """Repository for all DB Query Operations.
    Different from repository for all transaction operations."""

    def __init__(self, connection: databases.Database,
                 real_property_table: sqlalchemy.Table):
        self._connection = connection
        self._real_property_table = real_property_table
        self.logger = logging.getLogger(__name__)

    async def get_all(self) -> List[RealPropertyOut]:
        """Gets all the records

        TODO: add paging

        Raises:
            ResourceNotFoundError: if the table is empty

        Returns:
            List[RealPropertyOut]: List of outgoing geojson based objects
        """

        select_query = self._real_property_table.select()
        db_rows = await self._connection.fetch_all(select_query)
        if not db_rows:
            msg = "No Properties found!"
            self.logger.error(msg)
            raise ResourceNotFoundError(msg)
        out_list = [RealPropertyOut.from_db(db_row) for db_row in db_rows]
        return out_list

    async def get(self, property_id: str) -> RealPropertyOut:
        """Gets a single record

        Args:
            property_id (str): property id to search for

        Raises:
            ResourceNotFoundError: if property id not found

        Returns:
            RealPropertyOut: Outgoing geojson based object
        """

        select_query = self._real_property_table.select().where(
            self._real_property_table.c.id == property_id)
        db_row = await self._connection.fetch_one(select_query)
        if not db_row:
            msg = "Property not found - id: {}".format(property_id)
            self.logger.error(msg)
            raise ResourceNotFoundError(msg)
        return RealPropertyOut.from_db(db_row)

    async def find(self, geometry_distance: GeometryAndDistanceIn) -> List[str]:
        """Searches for properties within a given distance of a geometry

        Args:
            geometry_distance (GeometryAndDistanceIn): geojson based geometry and distance in object

        Raises:
            ResourceNotFoundError: if no properties found

        Returns:
            List[str]: list of property ids
        """

        geoalchemy_element_buffered = spatial_utils.buffer(
            geometry_distance.location_geo, geometry_distance.distance)
        select_query = select([self._real_property_table.c.id]).where(
            self._real_property_table.c.geocode_geo.ST_Intersects(
                geoalchemy_element_buffered))
        db_rows = await self._connection.fetch_all(select_query)
        if not db_rows:
            msg = "No Properties found!"
            self.logger.error(msg)
            raise ResourceNotFoundError(msg)
        out_list = [db_row["id"] for db_row in db_rows]
        return out_list

    # helpers for parallel running of queries
    async def _query_parcels(self, select_query_parcels):
        parcel_area = await self._connection.fetch_val(select_query_parcels)
        return parcel_area

    async def _query_buildings(self, select_query_buildings):
        db_rows = await self._connection.fetch_all(select_query_buildings)
        return db_rows

    async def statistics(self, property_id: str, distance: int) -> StatisticsOut:
        """Gets statistics for data near a property

        TODO: replace the property geocode with a redis geocode cache
            and maintain db sync with postgres with a redis queue.  Also, refactor
            to reduce 'too many locals'

        Args:
            property_id (str): property id
            distance (int): search radius in meters

        Raises:
            ResourceNotFoundError: if no property found for the given property id
            ResourceMissingDataError: if given property does not have geometry info to locate itself

        Returns:
            StatisticsOut: A summary statistics outgoing object
        """

        # get property geocode
        select_query = select([
            self._real_property_table.c.geocode_geo
        ]).where(self._real_property_table.c.id == property_id)
        db_row = await self._connection.fetch_one(select_query)
        if db_row is None:
            msg = "Property not found - id: {}".format(property_id)
            self.logger.error(msg)
            raise ResourceNotFoundError(msg)
        if db_row["geocode_geo"] is None:
            msg = "Property missing geocode_geo data - id: {}".format(
                property_id)
            self.logger.error(msg)
            raise ResourceMissingDataError(msg)
        # get zone - buffer around property
        geojson_obj = spatial_utils.to_geo_json(db_row["geocode_geo"])
        geoalchemy_element_buffered = spatial_utils.buffer(
            geojson_obj, distance)
        area_distance = spatial_utils.area_distance(geoalchemy_element_buffered,
                                                    None)
        zone_area = area_distance['area']

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

        # run queries in parallel
        parcel_area, db_rows = await asyncio.gather(
            self._query_parcels(select_query_parcels),
            self._query_buildings(select_query_buildings),
        )

        # get parcel area result
        if not parcel_area:
            parcel_area = 0
        parcel_area = round(parcel_area)

        # get distance and area for buildings
        if db_rows:
            area_distance_list = [
                spatial_utils.area_distance(db_row["building_geo"], geojson_obj)
                for db_row in db_rows
            ]
            building_area = sum(
                [area_distance['area'] for area_distance in area_distance_list])
        else:
            area_distance_list = []
            building_area = 0
        buildings_area_distance = area_distance_list

        # get final zone density
        zone_density_percentage = 100 * building_area / zone_area
        if zone_density_percentage > 100.00:
            zone_density_percentage = 100.00
        zone_density = round(zone_density_percentage, 2)

        statistics_out = StatisticsOut(
            parcel_area=parcel_area,
            buildings_area_distance=buildings_area_distance,
            zone_area=zone_area,
            zone_density=zone_density)
        return statistics_out

    @decorators.logtime_async(1)
    async def get_image(self, property_id) -> str:
        """Gets an image based on url from the database

        Args:
            property_id (str): property id

        Raises:
            ResourceNotFoundError: if property id not found
            ResourceMissingDataError: if property does not have a url for image

        Returns:
            str: image file name/path
        """

        # get property image url
        select_query = select([
            self._real_property_table.c.image_url
        ]).where(self._real_property_table.c.id == property_id)
        db_row = await self._connection.fetch_one(select_query)
        if db_row is None:
            msg = "Property not found - id: {}".format(property_id)
            self.logger.error(msg)
            raise ResourceNotFoundError(msg)
        if db_row["image_url"] is None:
            msg = "Property missing image url - id: {}".format(property_id)
            self.logger.error(msg)
            raise ResourceMissingDataError(msg)

        # get image
        # with temporary placeholder for progress reporting, add logging etc.
        # timeouts on url not found, badly formed urls, etc. not handled
        total_size = 0
        start = time()
        print_size = 0.0
        file_name = os.path.join('geoapi/static/tmp',
                                 os.path.basename(db_row["image_url"]))
        timeout = aiohttp.ClientTimeout(
            total=5 * 60, connect=30)  # could put in config eventually
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(db_row["image_url"]) as r:
                    async with aiofiles.open(file_name, 'wb') as fd:
                        self.logger.info('file download started: %s', db_row["image_url"])
                        while True:
                            chunk = await r.content.read(16144)
                            if not chunk:
                                break
                            await fd.write(chunk)
                            total_size += len(chunk)
                            print_size += len(chunk)
                            if (print_size / (1024 * 1024)
                               ) > 100:  # print every 100MB download
                                msg = f'{time() - start:0.2f}s, downloaded: {total_size / (1024 * 1024):0.0f}MB'
                                self.logger.info(msg)
                                print_size = (print_size / (1024 * 1024)) - 100
                        self.logger.info('file downloaded: %s', file_name)
                        log_msg = f'total time: {time() - start:0.2f}s, total size: {total_size / (1024 * 1024):0.0f}MB'
                        self.logger.info(log_msg)
            # convert to jpeg
            file_name_jpg = os.path.splitext(file_name)[0] + ".jpg"
            img = Image.open(file_name)
            img.save(file_name_jpg, "JPEG", quality=100)

        except aiohttp.client_exceptions.ServerTimeoutError as ste:
            self.logger.error('Time out: %s', str(ste))
            raise
        return file_name_jpg
