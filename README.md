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
Details in requirements.txt:
- GeoAlchemy2/SQLAlchemy/Shapely/geojson
- asyncpg/databases
- aiofiles/aiohttp
- uvicorn/uvloop/starlette/FastAPI
- Pillow
- mypy/pylint/Pydantic/yapf/absl-py

## Setup
### Development
- Install docker, docker-compose and git
- Clone this git repository
- Make changes to the code in the src folder
- Run `build.sh`. This simple script copies all required files from the `src` folder to the `dist` folder, replacing what may have previously existed in the dist folder.  Build.sh may need to be modified if new files are added that are not getting copied to the dist folder

### Application Startup
From the repo dist folder, run `docker-compose up -d`.  This will start the following:
- It will start the PostgreSQL database needed by the REST API.  The database server is exposed on port 5556 (the port can be changed in the docker-compose.yml file)
- It will start the REST API that connects to this database.  The REST API is exposed on port 8001 (the port can be changed in the docker-compose.yml file)
- The REST API will then be available at http://localhost:8001 
- The REST API endpoints are documented at http://localhost:8001/docs which shows the Swagger UI and links to the OpenAPI spec for the api 

## Using the REST API
The REST API is accessible at http://localhost:8001 and provides the following endpoints (documented with examples at http://localhost:8001/docs):
- `http://localhost:8001/properties/{property_id}/display/` - gets a jpg image of the property given it's property_id and saves a tiff image in the geoapi/static/tmp folder)
- `http://localhost:8001/properties/{property_id}/statistics/` - gets a statistics json object for data near a property given it's property_id and a search distance in meters
- `http://localhost:8001/properties/{property_id}/` - get a json object for property with property_id, including geojson for geography fields
- `http://localhost:8001/properties/` - get a list of json objects for all properties, including geojson for geography fields
- `http://localhost:8001/properties/find/` - (POST) - get a list of property ids when posted a geojson geometry and a distance
- `http://localhost:8001/properties/` - (POST) - get a new property as json object for property, including geojson for geography fields, when json object posted for a new property with geojson for geography fields

## Restoring from Archive and Reload during Development
To Archive:
- cd to src and archive with `git archive -o geapi1.zip --prefix=geoapi/ HEAD`
To Restore:
- cd to src, then unzip
For Reload During Development:
- expose the `app` variable in `main.py` globally by uncommenting: `app = create_app()` (since reload from within main is broken due to a bug)
- then run: `uvicorn geoapi.main:app --reload`

## Regular Use during Development:
- cd to `geoapi`
- `source venv/bin/activate`
- `code .` (assuming use of Visual Studio Code)
- cd to `src`
- see note above for `app` variable
- `uvicorn geoapi.main:app --reload`

## Docker related Deployment:
Production deployment:
- comment out the line: `app = create_app()` in `main.py`
- run `git add .`, `git commit -m 'message'`, `git push origin master`
- run `source ./build.sh`

Running containers - from `src` or `dist` folders:
- `docker-compose up -d`
- `docker-compose down`
- `docker-compose up --build -d` (when rebuilding image)
Getting new image:
- `docker login`
- `docker tag local-image:tagname new-repo:tagname` or 
- `docker tag image_id tinyperegrine/geoapi:1.0`
- `docker push tinyperegrine/geoapi:1.0`

MIT © [tinyperegrine]()
