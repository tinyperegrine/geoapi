import databases
import sqlalchemy
from asyncpg.exceptions import UniqueViolationError
from dataclasses import dataclass, field, asdict
from geoalchemy2.types import WKBElement
from typing import Optional, List
import geoapi.spatial_utils as spatial_utils
from geoapi.json_models import RealPropertyIn, RealPropertyOut


@dataclass
class RealPropertyDB():
    """Data Transfer Object for incoming data to the database"""
    id: str
    image_url: Optional[str] = None
    geocode_geo: Optional[WKBElement] = None
    parcel_geo: Optional[WKBElement] = None
    building_geo: Optional[WKBElement] = None
    image_bounds: List[float] = field(default_factory=list)

    @classmethod
    def from_real_property_in(cls, real_property_in: RealPropertyIn):
        """factory method - create instance from Real Property In"""
        geocode_geo_geoalchemy_element = spatial_utils.to_geoalchemy_element(
            real_property_in.geocode_geo)
        parcel_geo_geoalchemy_element = spatial_utils.to_geoalchemy_element(
            real_property_in.parcel_geo)
        building_geo_geoalchemy_element = spatial_utils.to_geoalchemy_element(
            real_property_in.building_geo)
        return cls(id=real_property_in.id,
                   image_url=real_property_in.image_url,
                   geocode_geo=geocode_geo_geoalchemy_element,
                   parcel_geo=parcel_geo_geoalchemy_element,
                   building_geo=building_geo_geoalchemy_element,
                   image_bounds=[])


class RealPropertyRepository(object):
    """Repository for all DB CRUD Operations"""

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

    async def create(self, real_property_in: RealPropertyIn
                    ) -> Optional[RealPropertyOut]:
        # real_property_db is the mapping of realpropertyin geojson to the database types
        real_property_db = RealPropertyDB.from_real_property_in(
            real_property_in)
        insert_query = self._real_property_table.insert().values(
            asdict(real_property_db))
        transaction = await self._connection.transaction()
        try:
            await self._connection.execute(insert_query)
        except UniqueViolationError as ue:
            # TBD log
            print('Error Duplicate id details: {0}'.format(ue.as_dict()))
            await transaction.rollback()
            # replace raising this with custom API exceptions to remove db dependency for API
            raise
        except Exception as e:
            # TBD log
            print('Error: {0}'.format(e))
            await transaction.rollback()
            raise
        else:
            await transaction.commit()
            new_real_property = await self.get(real_property_db.id)
            return new_real_property
