import databases
import sqlalchemy
from geoalchemy2.types import Geography
from geoapi.db_models import RealPropertyRepository


class DB(object):
    """Container for the Database"""

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
