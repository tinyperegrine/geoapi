# Basic script for dist folder - replace with build system later
rm -rf dist/*
cp -pRv LICENSE dist

# Since prod readme is different from overall readme that includes dev info
cp -pRv prodREADME.md dist/README.md

cp -pRv src/requirements.txt src/dockerfile src/docker-compose.yml dist
cp -pRv src/init-db dist/init-db
cp -pRv src/geoapi dist/geoapi

rm -rf dist/geoapi/rundev.py
rm -rf dist/geoapi/log/logs/*.log
rm -rf dist/geoapi/log/logs/*.prof
rm -rf dist/geoapi/static/tmp/*.jpg
rm -rf dist/geoapi/static/tmp/*.tif

