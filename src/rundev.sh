# docker-compose-dev just defines the database container to be used for development
# the full docker-compose.yml defines both app and db services and is only for production
docker-compose -f docker-compose-dev.yml up -d

# .envsrc is not checked into source control
# it defines the following environmental variables:
# export GEOAPI_DATABASE_URL=postgresql://postgres:engineTest888@localhost:5557/zesty
# export GEOAPI_LOG_LEVEL=debug
# export GEOAPI_HOST=0.0.0.0
# export GEOAPI_PORT=8000
# export GEOAPI_VERSION=1.0.0
# export GEOAPI_FUNCTION_TIMING=0
# export GEOAPI_CONFIG_INI=geoapi/config/config.ini
# export GEOAPI_LOG_CONFIG_YML=geoapi/log/logging.yml
source .envsrc

# uvicorn is called directly in order for reload to work properly during development
# rundev below defines the global api variable that is the result of running main
uvicorn geoapi.rundev:api --host $GEOAPI_HOST --port $GEOAPI_PORT --reload --log-level $GEOAPI_LOG_LEVEL
