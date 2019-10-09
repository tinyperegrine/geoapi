# geoapi
A Python based REST API for geospatial data
## A Python based REST API for Geospatial Data
This project creates a modern, high performance REST API using GIS data from a PostGres/PostGIS database.  It is based on the <a href="https://fastapi.tiangolo.com" target="_blank">FastAPI</a> web framework and uses Python 3.6+

**Docker Image:** https://cloud.docker.com/repository/docker/tinyperegrine/geoapi/general

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
- The REST API will produce logs in multiple destinations.  For details, review the logging section below (the log level can be changed in the docker-compose.yml file) 

### Running the API
The REST API is accessible at http://localhost:8001 and provides the following endpoints (documented with examples at http://localhost:8001/docs):
- http://localhost:8001/properties/{property_id}/display/ - gets a jpg image of the property given it's property id and saves a geotiff image in the geoapi/static/tmp folder)
- http://localhost:8001/properties/{property_id}/statistics/ - gets a statistics json object for data near a property given it's property id and a search distance in meters
- http://localhost:8001/properties/{property_id}/ - get a json object for a property (including geojson for geography fields), given the property_id
- http://localhost:8001/properties/ - get a list of json objects for all properties
- http://localhost:8001/properties/find/ - (POST) - post a geojson geometry and a search distance in meters, returns a list of property ids within the search distance to the input geometry
- http://localhost:8001/properties/ - (POST) - post a json object to insert a new property into the database (with geojson for geography fields), returns the new property as a json object.

### API Logging
The API logs to the following destinations (the log level can be changed in the docker-compose.yml file):
- stdout and stderr
- syslog (errors and exceptions only)
- JSON format rotating file logs in /usr/src/geoapi/geoapi/log/logs folder

## Development
### Development Setup:
The following instructions assume development on Mac or Linux:
- Install docker, docker-compose, git and Python 3.6+
- Clone this git repository
- cd to the repo root - **geoapi**, create a python virtual environment, activate it, upgrade pip and install python dependencies:

```Shell
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### On-going Development:
The following steps are to be used for ongoing development:
- activate the virtual environment 
- cd to the `./src` folder and run: `./rundev.sh` to get the development api and databases running:

```Shell
source rundev.sh
```
- rundev.sh calls docker-compose with docker-compose-dev.yml which only sets up the database container.  The REST API application itself is not containerized during development, only the development database is containerized.  In production, both the app and the db are containerized.
- rundev.sh calls .envdev.  This file defines the environmental variables needed for running the app in development.  This is not needed in production since docker manages those variables in the container for the app.
- Finally, rundev.sh calls uvicorn with the REST API in reload mode so that changes during development are immediately reflected in the running app.
- Now make changes to the code under the ./src folder with your chosen Python IDE.

### Testing:
The following steps are to be used for testing:
- activate the virtual environment 
- cd to the `./test` folder and run: `./runtest.sh` to get the development api and test databases running:

```Shell
source runtest.sh
```
- runtest.sh calls docker-compose with docker-compose-test.yml which only sets up the database container.  The REST API application itself is not containerized during testing, only the test database is containerized.
- runtest.sh calls .envtest.  This file defines the environmental variables needed for running the app in testing.
- runtest.sh calls unittest and runs it against the `./src/geoapi` package and reports results
- Finally, the test database container is shutdown and the volume removed.  Thus, the test database always runs with the originally loaded data

### Performance Monitoring:
The following steps are to be used for performance monitoring:
- Turn on performance monitoring by modifing the configuration.  Edit `./src/.envdev` and set 
GEOAPI_FUNCTION_TIMING to 1 
- Any function that requires monitoring can be decorated with one of three monitoring decorators.  These can be found in `./src/geoapi/common/decorators.py`
- Timing and profiling statistics can be obtained by decorating a function with the appropriate decorator.  Documentation is in the decorators module.

### Build and Deploy:
These steps are for final building and deployment:
- Make sure to update ./requirements.txt, if any new python packages have been installed
- Run `./build.sh`. This simple script copies all required files to the `./dist` folder, replacing what may have previously existed in the ./dist folder.  ./build.sh may need to be modified if new files are added that are not getting copied to the ./dist folder
- Commit the code to git
- cd to the `./dist` folder, rebuild the docker image and push it to the docker image repository as follows:

```Shell
docker-compose up --build -d
docker login
docker tag image_id tinyperegrine/geoapi:1.0
docker push tinyperegrine/geoapi:1.0
```


MIT © [tinyperegrine]()
