# docker-compose-dev just defines the database container to be used for development
# the full docker-compose.yml defines both app and db services and is only for production
docker-compose -f docker-compose-dev.yml up -d

# .envsrc is not checked into source control
# it defines the following environmental variables:
# export DATABASE_URL=postgresql://postgres:engineTest888@localhost:5557/zesty
# export API_LOG_LEVEL=debug
# export API_HOST=0.0.0.0
# export API_PORT=8000
source .envsrc

# uvicorn is called directly in order for reload to work properly during development
# rundev below defines the global api variable that is the result of running main
uvicorn geoapi.rundev:api --host $API_HOST --port $API_PORT --reload --log-level $API_LOG_LEVEL
