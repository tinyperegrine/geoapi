docker-compose -f docker-compose-dev.yml up -d
export DATABASE_URL=postgresql://postgres:engineTest888@localhost:5557/zesty
uvicorn geoapi.rundev:api --host 0.0.0.0 --port 8000 --reload --log-level info
