"""Spatial Processing Functions
EPSG 4326 and 3857 are harcoded in these functions.
TODO: Update to detect and use other CRS/SRS as configurable constants
    as well as inputs to functions
"""

import json
import decimal
from functools import lru_cache
from typing import Optional, List, Dict
import geoalchemy2
from geoalchemy2.types import WKBElement
import geojson
import pyproj
import shapely
from shapely import geometry
from shapely.ops import transform
import geoapi.common.decorators as decorators


def to_geo_json(geoalchemy_geometry: WKBElement):
    """returns a geojson geometry object from geoalchemy object"""
    if geoalchemy_geometry is not None:
        shapely_geometry = geoalchemy2.shape.to_shape(geoalchemy_geometry)
        shapely_geo_json = shapely.geometry.mapping(shapely_geometry)
        json_geometry = json.dumps(shapely_geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        return geo_json_obj

    return None


def to_geoalchemy_element(geo_json) -> Optional[WKBElement]:
    """returns a geoalchemy geometry object from geojson object"""
    if geo_json:
        json_geometry = json.dumps(geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        shapely_geo_json = geometry.shape(geo_json_obj)
        geoalchemy_element = geoalchemy2.shape.from_shape(shapely_geo_json)
        return geoalchemy_element

    return None


def from_lon_lat(lon: float, lat: float) -> Optional[WKBElement]:
    """returns geoalchemy geometry from longitude, latitude pair"""
    if lon and lat:
        shapely_point = shapely.geometry.Point(lon, lat)
        geoalchemy_element = geoalchemy2.shape.from_shape(shapely_point)
        return geoalchemy_element

    return None


def from_bbox_array(bbox_array: List[decimal.Decimal]):
    """returns a geojson geometry object from a bounding box array.
    Keeping default number of decimal places to 6 for now,
    can change depending on data precision requirements."""
    if bbox_array:
        shapely_geometry = shapely.geometry.box(bbox_array[0], bbox_array[1],
                                                bbox_array[2], bbox_array[3])
        shapely_geo_json = shapely.geometry.mapping(shapely_geometry)
        json_geometry = json.dumps(shapely_geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        return geo_json_obj

    return None


def to_bbox_array(geo_json) -> Optional[List[decimal.Decimal]]:
    """returns a sqlalchemy array object from geojson object.
    Keeping default number of decimal places to 6 for now,
    can change depending on data precision requirements."""
    if geo_json:
        json_geometry = json.dumps(geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        shapely_geo_json = geometry.shape(geo_json_obj)
        shapely_geo_json_bounds = shapely_geo_json.bounds
        sqlalchemy_array = [
            shapely_geo_json_bounds[0], shapely_geo_json_bounds[1],
            shapely_geo_json_bounds[2], shapely_geo_json_bounds[3]
        ]
        return sqlalchemy_array

    return None


# @decorators.logprofile
# @decorators.logtime(5)
# @lru_cache(maxsize=128, typed=False)
def _buffer(json_geometry: str, distance: int) -> WKBElement:
    """assumes source crs is 4326 and projected crs to use is 3857"""

    geo_json_obj = geojson.loads(json_geometry)
    shapely_geo_json = geometry.shape(geo_json_obj)
    # project to create buffer
    project_in = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:4326'),  # source
        pyproj.Proj(init='epsg:3857'))  # destination
    shapely_geo_json_projected = transform(project_in.transform,
                                           shapely_geo_json)
    # buffer
    shapely_geojson_buffer_project = shapely_geo_json_projected.buffer(
        distance)
    # project back
    project_out = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:3857'),  # source
        pyproj.Proj(init='epsg:4326'))  # destination
    shapely_geo_json_buffered = transform(
        project_out.transform, shapely_geojson_buffer_project)
    # convert to geoalchemy element
    geoalchemy_element = geoalchemy2.shape.from_shape(
        shapely_geo_json_buffered)
    return geoalchemy_element



def buffer(geo_json, distance: int) -> Optional[WKBElement]:
    """assumes source crs is 4326 and projected crs to use is 3857"""

    if geo_json and distance:
        json_geometry = json.dumps(geo_json)
        # _buffer exists since it can be cached
        # alternative to string conversion are custom geojson hashable geometry classes
        geoalchemy_element = _buffer(json_geometry, distance)
        return geoalchemy_element

    return None


def area_distance(geoalchemy_polygon: WKBElement,
                  geocode_geo_json=None) -> Dict[str, int]:
    """calculates area of polygon wkbelement and
    optionally distance to a geojson gemetry if it is provided.

    Args:
        geoalchemy_polygon (WKBElement): polygon whose area is desired
        geocode_geo_json (geojson geometry): geometry to calculate distance to

    Returns:
        Dict[str, int]: {'area': area in sqm, 'distance': distance in meters}
        if no input geojson geometry for distance calculation then returns -1 for distance
    """

    input_polygon_shapely_geometry = geoalchemy2.shape.to_shape(
        geoalchemy_polygon)
    # project
    project_in = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:4326'),  # source
        pyproj.Proj(init='epsg:3857'))  # destination

    # get area
    input_polygon_projected = transform(project_in.transform,
                                        input_polygon_shapely_geometry)
    area = round(input_polygon_projected.area)

    # get distance
    if geocode_geo_json:
        geocode_json_geometry = json.dumps(geocode_geo_json)
        geocode_geo_json_obj = geojson.loads(geocode_json_geometry)
        geocode_shapely = geometry.shape(geocode_geo_json_obj)
        geocode_projected = transform(project_in.transform, geocode_shapely)
        distance = round(
            geocode_projected.distance(input_polygon_projected.centroid))
        return {'area': area, 'distance': distance}

    return {'area': area, 'distance': -1}
