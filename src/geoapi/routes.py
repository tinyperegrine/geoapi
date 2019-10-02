"""API Routes Construction Module

Returns:
    APIRouter: FastAPI Router with all routes configured
"""

from typing import List
import aiohttp
from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse
from asyncpg.exceptions import UniqueViolationError
from geoapi.common.exceptions import ResourceNotFoundError, ResourceMissingDataError
from geoapi.data.db import DB
from geoapi.common.json_models import RealPropertyIn
from geoapi.common.json_models import RealPropertyOut
from geoapi.common.json_models import GeometryAndDistanceIn
from geoapi.common.json_models import StatisticsOut


# pylint: disable=unused-variable
def create_routes(api_db: DB) -> APIRouter:
    """Creator function for all API Routes

    Args:
        api_db (DB): geoapi.data.db.DB - the container for the database connection

    Raises:
        HTTPException: 404 resource not found
        HTTPException: 422 resource is missing required data
        HTTPException: 500 server timeouts, etc.
        HTTPException: 409 data integrity error - unique key constraint violation

    Returns:
        APIRouter: FastAPI Router with all routes configured
    """
    router = APIRouter()

    @router.get(
        "/properties/{property_id}/display/",
        responses={
            200: {
                "content": {
                    "image/jpeg": {}
                },
                "description": "Return the property image.",
            }
        },
    )
    async def display_property_image(property_id: str):
        """Get image for a property

        Args:

            property_id (str): property id,

        Raises:

            HTTPException(404): Raised if no property with property_id found in the db
            HTTPException(422): Raised if property with property_id does not have image url
            HTTPException(500): Raised if server timed out getting image

        Returns:

            property image as a jpeg file (original tiff file is also saved)
        """
        try:
            image_file = await api_db.real_property_queries.get_image(
                property_id)
        except ResourceNotFoundError as rnf:
            raise HTTPException(status_code=404,
                                detail={'message': rnf.args[0]})
        except ResourceMissingDataError as rmd:
            raise HTTPException(status_code=422,
                                detail={'message': rmd.args[0]})
        except aiohttp.client_exceptions.ServerTimeoutError as ste:
            raise HTTPException(
                status_code=500,
                detail={
                    'message': 'Server timeout while getting image.',
                    'detail': ste.args[0]
                }) from ste
        else:
            return FileResponse(image_file, media_type="image/jpeg")

    @router.get("/properties/{property_id}/statistics/",
                response_model=StatisticsOut)
    async def get_statistics_near_property(property_id: str,
                                           distance: int = 10) -> StatisticsOut:
        """Get statistics for data near a property

        Args:

            property_id (str): property id,
            distance (int): Distance (in meters) to buffer the property. Defaults to 10.

        Raises:

            HTTPException(404): Raised if no property with property_id found in the db
            HTTPException(422): Raised if property with property_id does not have enough data
                to calculate statistics

        Returns:

            StatisticsOut: outgoing statistics object
        """
        try:
            statistics_out = await api_db.real_property_queries.statistics(
                property_id, distance)
        except ResourceNotFoundError as rnf:
            raise HTTPException(status_code=404,
                                detail={'message': rnf.args[0]})
        except ResourceMissingDataError as rmd:
            raise HTTPException(status_code=422,
                                detail={'message': rmd.args[0]})
        else:
            return statistics_out

    @router.get("/properties/{property_id}/", response_model=RealPropertyOut)
    async def get_property(property_id: str) -> RealPropertyOut:
        """Get a single property record

        Args:

            property_id (str): string representation of a UUID without dashes

        Raises:

            HTTPException(404): Raised if no property with property_id found in the db

        Returns:

            RealPropertyOut: RealPropertyOut is the Geojson based
            Data Transfer Object for outgoing data from the API.
        """
        try:
            real_property = await api_db.real_property_queries.get(property_id)
        except ResourceNotFoundError as rnf:
            raise HTTPException(status_code=404,
                                detail={'message': rnf.args[0]})
        else:
            return real_property

    @router.get("/properties/", response_model=List[RealPropertyOut])
    async def get_all_properties() -> List[RealPropertyOut]:
        """Get all property records

        Todo:

            Add paging support

        Raises:

            HTTPException(404): Raised if no properties found in db

        Returns:

            List[RealPropertyOut]: List of RealPropertyOut objects,
                which are the Geojson based Data Transfer Objects
                for outgoing data from the API.
        """
        try:
            out_list = await api_db.real_property_queries.get_all()
        except ResourceNotFoundError as rnf:
            raise HTTPException(status_code=404,
                                detail={'message': rnf.args[0]})
        else:
            return out_list

    @router.post("/properties/find/", response_model=List[str])
    async def find_properties_near_location(
            geometry_distance: GeometryAndDistanceIn) -> List[str]:
        """Get property records based on buffer around a geometry

        Todo:

            Add paging support

        Args:

            geometry_distance (GeometryAndDistanceIn): GeometryAndDistanceIn is the Geojson based
                Data Transfer Object for incoming geometry and distance data to the API.

            Example:
                {
                    "distance": 10000000,
                    "location_geo": {"type": "Point", "coordinates": [-73.748751,40.918548]}
                }

        Raises:

            HTTPException(404): Raised if no properties found within distance of the geometry

        Returns:

            List[str]: List of property ids.
        """
        try:
            out_list = await api_db.real_property_queries.find(geometry_distance
                                                              )
        except ResourceNotFoundError as rnf:
            raise HTTPException(status_code=404,
                                detail={'message': rnf.args[0]})
        else:
            return out_list

    @router.post("/properties/", response_model=RealPropertyOut)
    async def create_property(real_property: RealPropertyIn) -> RealPropertyOut:
        """Insert a single property record

        Todo:

            Written as a 'post' with the provided id.
            Should probably be a 'put',
            with logic to create or update depending on if the id exists.
            Resolution of this issue depends on discovering business rules.

        Args:

            real_property (RealPropertyIn): RealPropertyIn is the Geojson based Data Transfer Object
                for incoming data to the API.

            Example:
                {
                    "id": "b2cddf80a32a41daaa34454d4883b903",
                    "geocode_geo": {"type": "Point", "coordinates": [-73.748751,40.918548]},
                    "parcel_geo": {"type": "Polygon", "coordinates": [[
                        [-73.748527,40.918404],[-73.748847,40.918296],
                        [-73.748993,40.918552],[-73.748663,40.918656],[-73.748527,40.918404]]]
                    },
                    "building_geo": {"type": "Polygon", "coordinates": [[
                        [-73.74885,40.918602],[-73.748832,40.918567],
                        [-73.748887,40.918551],[-73.748663,40.918465],[-73.748623,40.918528],
                        [-73.748684,40.918649],[-73.74885,40.918602]]]
                    },
                    "image_bounds": {"type": "Polygon", "coordinates": [[
                        [-73.748332,40.918232],[-73.748332,40.918865],
                        [-73.74917,40.918865],[-73.74917,40.918232],[-73.748332,40.918232]]]
                    },
                    "image_url": "https://www.google.com"
                }

        Raises:

            HTTPException(409): Raised if there is an underlying UniqueViolationError from the db,
                caused by trying to insert a record with a property_id that already exists in the db
            HTTPException(500): Raised if property could not be created in the db,
                caused by internal server error

        Returns:

            RealPropertyOut: The newly inserted record where RealPropertyOut is the
                Geojson based Data Transfer Object for outgoing data from the API.
        """
        try:
            await api_db.real_property_commands.create(real_property)
            new_real_property = await api_db.real_property_queries.get(
                real_property.id)
        except UniqueViolationError as uve:
            # replace with custom API exceptions to remove api_db dependency
            error_details = uve.as_dict()
            raise HTTPException(status_code=409,
                                detail={
                                    'message': error_details['message'],
                                    'detail': error_details['detail']
                                }) from uve
        except ResourceNotFoundError as rnf:
            raise HTTPException(
                status_code=500,
                detail={
                    'message':
                        rnf.args[0],
                    'detail':
                        'Resource creation failed due to internal server error.'
                })
        else:
            return new_real_property

    return router
