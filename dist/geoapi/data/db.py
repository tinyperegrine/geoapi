"""Database Container Class

Returns:
    DB: Database Container Class, returns the databases.Database object
        (which allows connections and transactions to the actual db)
        and the sqlalchemy tables loaded in the db with the associated
        command and query objects for each table
"""

import databases
import sqlalchemy
from sqlalchemy.dialects import postgresql
from geoalchemy2.types import Geography
from geoapi.data.queries import RealPropertyQueries
from geoapi.data.commands import RealPropertyCommands


class DB():
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
        """Property for access to connections and transactions

        Returns:
            databases.Database: Database object for connections and transactions
        """
        return self._connection

    @property
    def real_property_queries(self) -> RealPropertyQueries:
        """Query Object for the Real Property SQL Alchemy Table
        Provides access to all read only queries to the table

        Returns:
            RealPropertyQueries: All Read Only Queries to the Real Property Table
        """
        return self._real_property_queries

    @property
    def real_property_commands(self) -> RealPropertyCommands:
        """Command Object for the Real Property SQL Alchemy Table
        Provides access to all commands that modify the data in the table

        Returns:
            RealPropertyCommands: All Commands that modify the Real Property Table data
        """
        return self._real_property_commands
