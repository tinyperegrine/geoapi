"""Command Object for all commands that modify Real Property table data
"""

import logging
import decimal
from typing import Optional, List
from dataclasses import dataclass, asdict
import databases
import sqlalchemy
from geoalchemy2.types import WKBElement
from asyncpg.exceptions import UniqueViolationError
import geoapi.common.spatial_utils as spatial_utils
from geoapi.common.json_models import RealPropertyIn


@dataclass
class RealPropertyDB():
    """Geoalchemy based Data Transfer Object for incoming data to the database"""

    # keep id as field name to conform to the db
    id: str # pylint: disable=invalid-name
    geocode_geo: Optional[WKBElement] = None
    parcel_geo: Optional[WKBElement] = None
    building_geo: Optional[WKBElement] = None
    image_bounds: Optional[List[decimal.Decimal]] = None
    image_url: Optional[str] = None

    @classmethod
    def from_real_property_in(cls, real_property_in: RealPropertyIn):
        """factory method - create instance from Real Property In geojson"""
        geocode_geo_geoalchemy_element = spatial_utils.to_geoalchemy_element(
            real_property_in.geocode_geo)
        parcel_geo_geoalchemy_element = spatial_utils.to_geoalchemy_element(
            real_property_in.parcel_geo)
        building_geo_geoalchemy_element = spatial_utils.to_geoalchemy_element(
            real_property_in.building_geo)
        image_bounds_sqlalchemy_array = spatial_utils.to_bbox_array(
            real_property_in.image_bounds)
        return cls(id=real_property_in.id,
                   geocode_geo=geocode_geo_geoalchemy_element,
                   parcel_geo=parcel_geo_geoalchemy_element,
                   building_geo=building_geo_geoalchemy_element,
                   image_bounds=image_bounds_sqlalchemy_array,
                   image_url=real_property_in.image_url)


# pylint: disable=too-few-public-methods
# (there will be more in the future)
class RealPropertyCommands():
    """Repository for all DB Transaction Operations
    Different from the repository for all query operations."""

    def __init__(self, connection: databases.Database,
                 real_property_table: sqlalchemy.Table):
        self._connection = connection
        self._real_property_table = real_property_table
        self.logger = logging.getLogger(__name__)

    async def create(self, real_property_in: RealPropertyIn) -> bool:
        """Insert command for the Real Property Table
        use real_property_db, which is a mapping of realpropertyin geojson to the database types

        Args:
            real_property_in (RealPropertyIn): Incoming geojson based object for insertion

        Returns:
            bool: whether the transaction was successful
        """

        real_property_db = RealPropertyDB.from_real_property_in(
            real_property_in)
        insert_query = self._real_property_table.insert().values(
            asdict(real_property_db))

        transaction = await self._connection.transaction()
        try:
            await self._connection.execute(insert_query)
        except UniqueViolationError as uve:
            self.logger.error('Duplicate id - details: %s', uve.as_dict())
            await transaction.rollback()
            # replace raising this with custom API exceptions to remove db dependency for API
            raise
        except Exception as exc:
            self.logger.exception(str(exc))
            await transaction.rollback()
            raise
        else:
            await transaction.commit()
            return True
