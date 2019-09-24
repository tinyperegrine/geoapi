from geoapi.main import main
# only for development
# then run:
# uvicorn geoapi.rundev:api --host 0.0.0.0 --port 8000 --reload --log-level debug
# (since reload from within main is broken due to a bug in uvicorn)

api = main()
