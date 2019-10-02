"""Data Transfer Objects used throughout the Application
"""

from enum import IntEnum
from typing import Optional, List, Dict
from pydantic import BaseModel, UrlStr
from geojson import Point, Polygon
import geoapi.common.spatial_utils as spatial_utils


class LogEnum(IntEnum):
    """Class for acceptable log levels for the application"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10


class RealPropertyBase(BaseModel):
    """Base for all property Geojson Data Transfer Objects"""
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
    """Geojson Data Transfer Object for incoming property data to the API"""


class RealPropertyOut(RealPropertyBase):
    """Geojson Data Transfer Object for outgoing property data from the API"""

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


class GeometryAndDistanceIn(BaseModel):
    """Geojson Data Transfer Object for incoming data for find query.
    Takes distance in meters and any simple point, line or polygon geometry.
    Should improve by adding validation for input geometry.
    """
    location_geo: Dict = {}  #: Geojson geometry representing simple point, line or polygon
    distance: int  #: Distance in meters


class IdAndDistanceIn(BaseModel):
    """Json Data Transfer Object for incoming data for statistics query.
    Takes distance in meters and a property id.
    Should improve by adding validation for input geometry.
    """
    property_id: str  #: property id
    distance: int  #: Distance in meters


class StatisticsOut(BaseModel):
    """Json Data Transfer Object for outgoing data from statistics query.
    """
    parcel_area: int  #: square meters
    buildings_area_distance: List[Dict[
        str,
        int]]  #: list of building areas (square meters) and distances to zone center (meters)
    zone_area: int  #: square meters
    zone_density: float  #: percentage of building area in zone
