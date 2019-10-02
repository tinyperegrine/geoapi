"""Configuration constants for the application
"""

from pydantic import FilePath
from geoapi.common.json_models import LogEnum

# logging
# - default yaml logging config file path
DEFAULT_LOG_CONFIG_YML_FILEPATH: FilePath = 'geoapi/log/logging.yml'  # type: ignore
# environmental variable for yaml logging config file path (if not using default above)
CONFIG_YML_ENV_KEY: str = 'LOG_YML'
# log level to use if none specified in env
DEFAULT_API_LOG_LEVEL: LogEnum = LogEnum.INFO

# api host and port to use if none specified in env
DEFAULT_API_HOST: str = '0.0.0.0'
DEFAULT_API_PORT: int = 8000

# api version to use if none specified in env
DEFAULT_API_VERSION: str = '1.0.0'
