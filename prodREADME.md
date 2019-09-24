# geoapi
A Python based REST API for geospatial data
## A Python based REST API for Geospatial Data
This project creates a modern, high performance REST API using GIS data from a PostGres/PostGIS database.  It is based on the <a href="https://fastapi.tiangolo.com" target="_blank">FastAPI</a> web framework and uses Python 3.6+

## Major Technologies & Frameworks
- Python
- FastAPI
- Postgres
- PostGIS

## Major Python Libraries
Details in ./requirements.txt:
- GeoAlchemy2/SQLAlchemy/Shapely/geojson
- asyncpg/databases
- aiofiles/aiohttp
- uvicorn/uvloop/starlette/FastAPI
- Pillow
- mypy/pylint/Pydantic/yapf/absl-py

## Using the API
### Setup
- Install docker, docker-compose and git
- Clone this git repository

### Startup
cd to the repo **./dist** folder, run:

```Shell
docker-compose up -d
```  
This will start the following:
- A PostgreSQL database needed by the REST API.  The database server is exposed on port 5556 (can be changed in the docker-compose.yml file)
- A REST API that connects to this database.  The REST API is exposed on port 8001 (can be changed in the docker-compose.yml file)
- The REST API will then be available at http://localhost:8001 
- The REST API endpoints are documented at http://localhost:8001/docs which shows the Swagger UI and links to the OpenAPI spec for the API

## Running the API
The REST API is accessible at http://localhost:8001 and provides the following endpoints (documented with examples at http://localhost:8001/docs):
- http://localhost:8001/properties/{property_id}/display/ - gets a jpg image of the property given it's property id and saves a geotiff image in the geoapi/static/tmp folder)
- http://localhost:8001/properties/{property_id}/statistics/ - gets a statistics json object for data near a property given it's property id and a search distance in meters
- http://localhost:8001/properties/{property_id}/ - get a json object for a property (including geojson for geography fields), given the property_id
- http://localhost:8001/properties/ - get a list of json objects for all properties
- http://localhost:8001/properties/find/ - (POST) - post a geojson geometry and a search distance in meters, returns a list of property ids within the search distance to the input geometry
- http://localhost:8001/properties/ - (POST) - post a json object to insert a new property into the database (with geojson for geography fields), returns the new property as a json object.



MIT © [tinyperegrine]()
