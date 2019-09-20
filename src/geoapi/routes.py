from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException
from asyncpg.exceptions import UniqueViolationError

from geoapi.data.db import DB
from geoapi.common.json_models import RealPropertyIn, RealPropertyOut, GeometryAndDistanceIn


# pylint: disable=unused-variable
def create_routes(db: DB) -> APIRouter:
    router = APIRouter()

    @router.get("/properties/", response_model=List[RealPropertyOut])
    async def get_all_real_properties() -> List[RealPropertyOut]:
        """Get all property records

        Todo:
            Add paging support, add better messaging, status code if no records found
        
        Returns:
            List[RealPropertyOut]: List of RealPropertyOut objects, which  
            are the Geojson based Data Transfer Objects for outgoing data from the API 
            or None if no records found.
        """
        out_list = await db.real_property_queries.get_all()
        return out_list

    @router.get("/properties/{property_id}/", response_model=RealPropertyOut)
    async def get_real_property(property_id: str) -> Optional[RealPropertyOut]:
        """Get a single property record

        Todo:
            Add better messaging, status code if no record found
        
        Args:
            property_id (str): string representation of a UUID without dashes
        
        Returns:
            Optional[RealPropertyOut]: RealPropertyOut is the Geojson based   
            Data Transfer Object for outgoing data from the API
            or None if no record found.
        """
        real_property = await db.real_property_queries.get(property_id)
        return real_property

    @router.post("/properties/", response_model=RealPropertyOut)
    async def create_real_property(real_property: RealPropertyIn
                                  ) -> Optional[RealPropertyOut]:
        """Insert a single property record

        Todo:
            Should not be returning a new record optionally.  
            Either return the record or raise error.
            Written as a 'post' with the provided id.  Should probably be a 'put',
            with logic to create or update depending on if the id exists.
            Resolution depends on determining business logic details.
        
        Args:
            real_property (RealPropertyIn): RealPropertyIn is the Geojson based 
                Data Transfer Object for incoming data to the API.
        
        Raises:
            HTTPException: Raised if there is an underlying UniqueViolationError
                from the db - caused by trying to insert a record with a property_id 
                that already exists in the db
        
        Returns:
            Optional[RealPropertyOut]: The newly inserted record where 
            RealPropertyOut is the Geojson based Data Transfer Object for outgoing data from the API
            or None if no record inserted.
        """
        try:
            await db.real_property_commands.create(real_property)
        except UniqueViolationError as ue:
            # replace with custom API exceptions to remove db dependency
            error_details = ue.as_dict()
            raise HTTPException(status_code=409,
                                detail={
                                    'message': error_details['message'],
                                    'detail': error_details['detail']
                                })
        else:
            new_real_property = await db.real_property_queries.get(
                real_property.id)
            return new_real_property

    @router.post("/properties/find/", response_model=List[RealPropertyOut])
    async def find_real_properties(geometry_distance: GeometryAndDistanceIn
                                  ) -> List[RealPropertyOut]:
        """Get property records based on buffer around a geometry

        Todo:
            Add paging support, add better messaging, status code if no records found

        Args:
            geometry_distance (GeometryAndDistanceIn): GeometryAndDistanceIn is the Geojson based 
                Data Transfer Object for incoming geometry and distance data to the API.
                
        Returns:
            List[RealPropertyOut]: List of RealPropertyOut objects, which  
            are the Geojson based Data Transfer Objects for outgoing data from the API 
            or None if no records found.
        """
        out_list = await db.real_property_queries.find(geometry_distance)
        return out_list

    return router
