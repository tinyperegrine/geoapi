from pydantic import BaseModel, UrlStr
from typing import Optional, List
from geojson import Point, Polygon
import geoapi.common.spatial_utils as spatial_utils


class RealPropertyBase(BaseModel):
    """Base for all JSON Data Transfer Objects"""
    id: str
    image_url: Optional[UrlStr] = None
    geocode_geo: Optional[Point] = None
    parcel_geo: Optional[Polygon] = None
    building_geo: Optional[Polygon] = None


class RealPropertyIn(RealPropertyBase):
    """JSON Data Transfer Object for incoming data to the API"""
    pass


class RealPropertyOut(RealPropertyBase):
    """JSON Data Transfer Object for outgoing data from the API"""

    @classmethod
    def from_db(cls, db_row):
        """Factory method - create instance from db row"""
        geocode_geo_json = spatial_utils.to_geo_json(db_row["geocode_geo"])
        parcel_geo_json = spatial_utils.to_geo_json(db_row["parcel_geo"])
        building_geo_json = spatial_utils.to_geo_json(db_row["building_geo"])
        return cls(id=db_row["id"],
                   image_url=db_row["image_url"],
                   geocode_geo=geocode_geo_json,
                   parcel_geo=parcel_geo_json,
                   building_geo=building_geo_json)
