from pydantic import FilePath
from geoapi.common.json_models import LogEnum

# logging
DEFAULT_LOG_CONFIG_YML_FILEPATH: FilePath = 'geoapi/log/logging.yml'  # type: ignore - default yaml logging config file path
CONFIG_YML_ENV_KEY: str = 'LOG_YML'  #: environmental variable for yaml logging config file path (if not using default above)
DEFAULT_API_LOG_LEVEL: LogEnum = LogEnum.INFO  #: log level to use if none specified in env

# api host and port to use if none specified in env
DEFAULT_API_HOST: str = '0.0.0.0'
DEFAULT_API_PORT: int = 8000
