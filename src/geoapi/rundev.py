"""App Driver for Development
(since reload from within main is broken due to a bug in uvicorn)
exposes the api globally, to allow command line running of uvicorn
called from rundev.sh
"""

from fastapi import FastAPI
import geoapi.main

api: FastAPI = geoapi.main.main()
