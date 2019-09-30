from geoapi.main import main
# only for development
# then run:
# source rundev.sh
# (since reload from within main is broken due to a bug in uvicorn)

api = main()
