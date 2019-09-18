import json
from typing import Optional
import geoalchemy2
from geoalchemy2.types import WKBElement
import geojson
from geojson import Point
import shapely
from shapely import geometry


def to_geo_json(geoalchemy_geometry: WKBElement):
    """returns a geojson geometry object from geoalchemy object"""
    if geoalchemy_geometry is not None:
        shapely_geometry = geoalchemy2.shape.to_shape(geoalchemy_geometry)
        shapely_geo_json = shapely.geometry.mapping(shapely_geometry)
        json_geometry = json.dumps(shapely_geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        return geo_json_obj
    else:
        return None


def to_geoalchemy_element(geo_json) -> Optional[WKBElement]:
    """returns a geoalchemy geometry object from geojson object"""
    if geo_json is not None:
        json_geometry = json.dumps(geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        shapely_geo_json = geometry.shape(geo_json_obj)
        shapely_geo_json = geometry.shape(geo_json_obj)
        geoalchemy_element = geoalchemy2.shape.from_shape(shapely_geo_json)
        return geoalchemy_element
    else:
        return None


def from_lon_lat(lon: float, lat: float) -> Optional[WKBElement]:
    """returns geoalchemy geometry from longitude, latitude pair"""
    if lon and lat:
        shapely_point = shapely.geometry.Point(lon, lat)
        geoalchemy_element = geoalchemy2.shape.from_shape(shapely_point)
        return geoalchemy_element
    else:
        return None
