import os
import uvicorn
from geoapi.api import create_api

# for production, cd to dist folder and run:
# python -m geoapi.main


def main():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        # log
        print('Environmental Variable: DATABASE_URL not set!')
        return None
    else:
        api = create_api(database_url=db_url)
    return api


if __name__ == "__main__":
    """Temporary Entry Point:

    todo: better handling of env vars, also have command line args, add the build system, include gunicorn, parallel workers and related configs
    """
    api = main()
    if api:
        api_host = os.environ.get('API_HOST')
        if not api_host:
            api_host = '0.0.0.0'
        port = os.environ.get('API_PORT')
        if not port:
            api_port = 8000
        else:
            api_port = int(port)
        api_log_level = os.environ.get('API_LOG_LEVEL')
        if not api_log_level:
            api_log_level = 'info'

        uvicorn.run(api, host=api_host, port=api_port, log_level=api_log_level)
    else:
        # log
        print('API cannot run!')
