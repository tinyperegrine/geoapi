"""
configuration for the api
- API_CONFIG is the global holding the configuration
- init loads the configuration for the api, should only be called once from main
    all other modules that need config should import API_CONFIG

"""
import os
import configparser
from pathlib import Path
from typing import Dict, Tuple

# global dict with all config items
API_CONFIG: dict = {}

def init(default_config_ini_filepath: Path, config_ini_env_key: str)->Tuple[Dict, bool]:
    """Loads the configuration for the API, should only be called once from main

    Args:
        default_config_ini_filepath (FilePath): app embedded default config file
        config_ini_env_key (str): env variable for externally provided config file

    Returns:
        tuple (dict: bool):
            api_config (dict) - dictionary of config keys and values
            external_config_load_error (bool) - True if externally provided config is specified
                but cannot be loaded else False
                Note - even if it returns True, config exists
                since at-least the embedded and possibly the env vars will be there

    Data Requirements:
        config.ini must have 'DEFAULT' section
        ENV VARS must start with 'GEOAPI_'

    Loading order:
        Base defaults are from a default_config_ini which is a part of the app,
        so always available and loaded first - expect this to alwaysload successfully.
        Another config ini can be specified through the config_ini_env_key.
        If it is specified, it is loaded next.  If it is not specified, it is skipped.
        If it is specified but cannot be loaded then an error is returned and it is skipped.
        Env vars are loaded last if any are there.
        Thus env vars overwrite external config file, which overwrites embedded config

    TODO: Add command line parms as the last loaded items

    """

    config = configparser.ConfigParser()
    # get external ini file also - if it exists, else only use embedded file
    config_ini_file = os.environ.get(config_ini_env_key)
    if config_ini_file is not None:
        config_ini_filepath: Path = Path(config_ini_file)
        files_read = config.read([default_config_ini_filepath, config_ini_filepath])
        # if unable to read external config file (if specified) then an error
        external_config_load_error = bool(len(files_read) < 2)
    else:
        config.read(default_config_ini_filepath)
        external_config_load_error = False
    # now overwrite with any env vars if they exist and have values
    os_config_items = {
        k: v for k, v in os.environ.items()
        if k.startswith('GEOAPI_') and v is not None}
    config.read_dict({'DEFAULT': os_config_items})
    api_config = {key.upper(): config['DEFAULT'][key] for key in config['DEFAULT']}
    return (api_config, external_config_load_error)
