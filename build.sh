# Basic script for dist folder - replace with build system later
rm -rf dist/*
cp -pRv LICENSE dist
cp -pRv prodREADME.md dist/README.md
cp -pRv src/requirements.txt src/dockerfile src/docker-compose.yml dist
cp -pRv src/init-db dist/init-db
cp -pRv src/geoapi dist/geoapi
