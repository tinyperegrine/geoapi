import databases
import sqlalchemy
from sqlalchemy.dialects import postgresql
from geoalchemy2.types import Geography
from geoapi.data.queries import RealPropertyQueries
from geoapi.data.commands import RealPropertyCommands


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
                              postgresql.ARRAY(postgresql.DOUBLE_PRECISION),
                              nullable=True),
            sqlalchemy.Column("image_url", sqlalchemy.String, nullable=True),
        )
        self._real_property_queries = RealPropertyQueries(
            self._connection, real_property_table)
        self._real_property_commands = RealPropertyCommands(
            self._connection, real_property_table)

    @property
    def connection(self) -> databases.Database:
        return self._connection

    @property
    def real_property_queries(self) -> RealPropertyQueries:
        return self._real_property_queries

    @property
    def real_property_commands(self) -> RealPropertyCommands:
        return self._real_property_commands
