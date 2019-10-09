"""Integration tester for all routes in the api
"""

import unittest
from starlette.testclient import TestClient
from fastapi import FastAPI
import geoapi.main


class IntegrationTestsRoutes(unittest.TestCase):
    """Integration tester for routes
    """

    def setUp(self):
        self.api: FastAPI = geoapi.main.main()
        #self.client: TestClient = TestClient(api)

    def test_root(self):
        """Test of the root route
        """
        with TestClient(self.api) as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {
                    "message": "Welcome to the GEOAPI. Please go to /docs for help"
                }
            )

    def test_create_property(self):
        """Test of the create property route
        """
        with TestClient(self.api) as client:
            response = client.post(
                "/geoapi/v1/properties/",
                json={
                    "id": "b2cddf80a32a41daaa34454d4883b903",
                    "geocode_geo": {"type": "Point", "coordinates": [-73.748751, 40.918548]},
                    "parcel_geo": {"type": "Polygon", "coordinates": [[
                        [-73.748527, 40.918404], [-73.748847, 40.918296],
                        [-73.748993, 40.918552], [-73.748663, 40.918656],
                        [-73.748527, 40.918404]]]},
                    "building_geo": {"type": "Polygon", "coordinates": [[
                        [-73.74885, 40.918602], [-73.748832, 40.918567],
                        [-73.748887, 40.918551], [-73.748663, 40.918465], [-73.748623, 40.918528],
                        [-73.748684, 40.918649], [-73.74885, 40.918602]]]},
                    "image_bounds": {"type": "Polygon", "coordinates": [[
                        [-73.748332, 40.918232], [-73.748332, 40.918865],
                        [-73.74917, 40.918865], [-73.74917, 40.918232], [-73.748332, 40.918232]]]},
                    "image_url": "https://docs.mapbox.com/help/data/landsat.tif"
                },
            )
            print(response.json())
            self.assertEqual(
                response.json(),
                {
                    "id": "b2cddf80a32a41daaa34454d4883b903",
                    "geocode_geo": {"type": "Point", "coordinates": [-73.748751, 40.918548]},
                    "parcel_geo": {"type": "Polygon", "coordinates": [[
                        [-73.748527, 40.918404], [-73.748847, 40.918296],
                        [-73.748993, 40.918552], [-73.748663, 40.918656],
                        [-73.748527, 40.918404]]]},
                    "building_geo": {"type": "Polygon", "coordinates": [[
                        [-73.74885, 40.918602], [-73.748832, 40.918567],
                        [-73.748887, 40.918551], [-73.748663, 40.918465], [-73.748623, 40.918528],
                        [-73.748684, 40.918649], [-73.74885, 40.918602]]]},
                    "image_bounds": {"type": "Polygon", "coordinates": [[
                        [-73.748332, 40.918232], [-73.748332, 40.918865],
                        [-73.74917, 40.918865], [-73.74917, 40.918232], [-73.748332, 40.918232]]]},
                    "image_url": "https://docs.mapbox.com/help/data/landsat.tif"
                },
            )
            self.assertEqual(response.status_code, 200)


    def test_create_property_twice(self):
        """Test of the create property route by passing the same property twice, should fail
        """
        with TestClient(self.api) as client:
            response = client.post(
                "/geoapi/v1/properties/",
                json={
                    "id": "b2cddf80a32a41daaa34454d4883b903",
                    "geocode_geo": {"type": "Point", "coordinates": [-73.748751, 40.918548]},
                    "parcel_geo": {"type": "Polygon", "coordinates": [[
                        [-73.748527, 40.918404], [-73.748847, 40.918296],
                        [-73.748993, 40.918552], [-73.748663, 40.918656],
                        [-73.748527, 40.918404]]]},
                    "building_geo": {"type": "Polygon", "coordinates": [[
                        [-73.74885, 40.918602], [-73.748832, 40.918567],
                        [-73.748887, 40.918551], [-73.748663, 40.918465], [-73.748623, 40.918528],
                        [-73.748684, 40.918649], [-73.74885, 40.918602]]]},
                    "image_bounds": {"type": "Polygon", "coordinates": [[
                        [-73.748332, 40.918232], [-73.748332, 40.918865],
                        [-73.74917, 40.918865], [-73.74917, 40.918232], [-73.748332, 40.918232]]]},
                    "image_url": "https://docs.mapbox.com/help/data/landsat.tif"
                },
            )
            print(response.json())
            self.assertEqual(
                response.json(),
                {'detail': {
                    'message': 'duplicate key value violates unique constraint "properties_pk"',
                    'detail': 'Key (id)=(b2cddf80a32a41daaa34454d4883b903) already exists.'
                }}
            )
            self.assertEqual(response.status_code, 409)

if __name__ == '__main__':
    unittest.main()
