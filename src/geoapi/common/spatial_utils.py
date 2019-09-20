import json
import decimal
from typing import Optional, List
import sqlalchemy
import geoalchemy2
from geoalchemy2.types import WKBElement
import geojson
from geojson import Point
import shapely
from shapely import geometry
import pyproj
from shapely.ops import transform


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
    else:
        return None


def to_bbox_array(geo_json) -> Optional[List[decimal.Decimal]]:
    """returns a sqlalchemy array object from geojson object.  
    Keeping default number of decimal places to 6 for now, 
    can change depending on data precision requirements."""
    if geo_json is not None:
        json_geometry = json.dumps(geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        shapely_geo_json = geometry.shape(geo_json_obj)
        shapely_geo_json_bounds = shapely_geo_json.bounds
        sqlalchemy_array = [
            shapely_geo_json_bounds[0], shapely_geo_json_bounds[1],
            shapely_geo_json_bounds[2], shapely_geo_json_bounds[3]
        ]
        return sqlalchemy_array
    else:
        return None


def buffer(geo_json, distance: int) -> Optional[WKBElement]:
    if geo_json is not None and distance:
        json_geometry = json.dumps(geo_json)
        geo_json_obj = geojson.loads(json_geometry)
        shapely_geo_json = geometry.shape(geo_json_obj)
        print(shapely_geo_json)
        # project to create buffer
        project_in = pyproj.Transformer.from_proj(
            pyproj.Proj(init='epsg:4326'),  # source 
            pyproj.Proj(init='epsg:3857'))  # destination
        shapely_geo_json_projected = transform(project_in.transform,
                                               shapely_geo_json)
        print(shapely_geo_json_projected)
        # buffer
        shapely_geo_json_buffered_projected = shapely_geo_json_projected.buffer(
            distance)
        print(shapely_geo_json_buffered_projected)
        # project back
        project_out = pyproj.Transformer.from_proj(
            pyproj.Proj(init='epsg:3857'),  # source 
            pyproj.Proj(init='epsg:4326'))  # destination
        shapely_geo_json_buffered = transform(
            project_out.transform, shapely_geo_json_buffered_projected)
        print(shapely_geo_json_buffered)
        geoalchemy_element = geoalchemy2.shape.from_shape(
            shapely_geo_json_buffered)
        return geoalchemy_element
    else:
        return None
