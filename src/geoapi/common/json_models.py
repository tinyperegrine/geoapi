from pydantic import BaseModel, UrlStr
from typing import Optional, List
from geojson import Point, Polygon
import geoapi.common.spatial_utils as spatial_utils


class RealPropertyBase(BaseModel):
    """Base for all Geojson Data Transfer Objects"""
    id: str  #: property id
    geocode_geo: Optional[
        Point] = None  #: Optional Geojson Point representing property location
    parcel_geo: Optional[
        Polygon] = None  #: Optional Geojson Polygon representing parcels
    building_geo: Optional[
        Polygon] = None  #: Optional Geojson Polygon representing buildings
    image_bounds: Optional[
        Polygon] = None  #: Optional Geojson Polygon representing the image bounding box
    image_url: Optional[UrlStr] = None  #: Optional URL to image


class RealPropertyIn(RealPropertyBase):
    """Geojson Data Transfer Object for incoming data to the API"""
    pass


class RealPropertyOut(RealPropertyBase):
    """Geojson Data Transfer Object for outgoing data from the API"""

    @classmethod
    def from_db(cls, db_row):
        """Factory method - create instance from db row"""
        geocode_geo_json = spatial_utils.to_geo_json(db_row["geocode_geo"])
        parcel_geo_json = spatial_utils.to_geo_json(db_row["parcel_geo"])
        building_geo_json = spatial_utils.to_geo_json(db_row["building_geo"])
        image_bounds_geo_json = spatial_utils.from_bbox_array(
            db_row["image_bounds"])
        return cls(id=db_row["id"],
                   geocode_geo=geocode_geo_json,
                   parcel_geo=parcel_geo_json,
                   building_geo=building_geo_json,
                   image_bounds=image_bounds_geo_json,
                   image_url=db_row["image_url"])
