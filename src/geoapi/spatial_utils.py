import geojson
import geoalchemy2
from geoalchemy2.types import Geography
import shapely


def to_geo_json(geoalchemy_geo: Geography):
    shapely_geo = geoalchemy2.shape.to_shape(geoalchemy_geo)
    shapely_geo_json = shapely.geometry.mapping(shapely_geo)
    geo_json_obj = geojson.dumps(shapely_geo_json)
    return geo_json_obj


def from_lon_lat(lon: float, lat: float):
    shapely_point = shapely.geometry.Point(lon, lat)
    geoalchemy_element = geoalchemy2.shape.from_shape(shapely_point)
    return geoalchemy_element
