# docker-compose-test just defines the database container to be used for testing
# during testing databases volumes do not persist
# docker-compose-dev just defines the database container to be used for development
# during development databases volumes persist
# the full docker-compose.yml defines both app and db services and is only for production
docker-compose -f docker-compose-test.yml up -d

# .envtest is not checked into source control
# it defines the following environmental variables:
# export GEOAPI_DATABASE_URL=postgresql://postgres:engineTest888@localhost:5558/zesty
# export GEOAPI_LOG_LEVEL=debug
# export GEOAPI_HOST=0.0.0.0
# export GEOAPI_PORT=8002
# export GEOAPI_VERSION=1.0.0
# export GEOAPI_FUNCTION_TIMING=0
# export GEOAPI_CONFIG_INI=geoapi/config/config.ini
# export GEOAPI_LOG_CONFIG_YML=geoapi/log/logging.yml
source .envtest

# tests are run and result is stored
cd ../src && python -m unittest discover -v -s geoapi
TESTSTATUS=$?
# bring down the db container and delete the volume to refresh for next time
cd ../test
docker-compose -f docker-compose-test.yml down
docker volume rm test_pg-data
# report result
if [ $TESTSTATUS -eq 0 ]
then
  echo "Success"
else
  echo "Failure"
fi
return $TESTSTATUS
