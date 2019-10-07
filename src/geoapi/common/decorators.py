"""Decorators

"""

import logging
import functools
import time
import io
import cProfile
import pstats
import uuid
import pathlib

import geoapi.config.api_configurator as config


def logtime(repeat: int = 1):
    """Timing and repeat decorator
    Will only run when config parameter GEOAPI_FUNCTION_TIMING is set to True

    Args:
        repeat (int, optional): runs the function multiple times. Defaults to 1.
            ignored if 0

    Returns:
        Log Message: INFO log message with min, max time for running the function
    """
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if config.API_CONFIG['GEOAPI_FUNCTION_TIMING'] and repeat:
                timing_results = [0.0 for x in range(repeat)]
                for i in range(repeat):
                    start = time.perf_counter()
                    result = func(*args, **kwargs)
                    timing_results[i] = time.perf_counter() - start
                logger = logging.getLogger(func.__module__)
                logger.info(
                    'Timing [%s]: Min: %2.4f sec - Max: %2.4f sec',
                    func.__name__,
                    min(timing_results),
                    max(timing_results))
            else:
                result = func(*args, **kwargs)
            return result
        return wrapper
    return actual_decorator


def logprofile(func):
    """Profiling decorator

    Args:
        func: decorated function - must be synchronous and not running timing code

    Returns:
        file: returns a file with statistics in geoapi/log/logs called
            module_function_uuid.prof stored in geoapi/log/logs folder
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if config.API_CONFIG['GEOAPI_FUNCTION_TIMING']:
            unique = uuid.uuid4().hex
            filename = '%s_%s_%s.prof' % (func.__module__, func.__name__, unique)
            dirpath = pathlib.Path('geoapi/log/logs')
            filepath = dirpath / filename
            profile = cProfile.Profile()
            result = profile.runcall(func, *args, **kwargs)
            buffer = io.StringIO()
            sortby = 'cumulative'
            stats = pstats.Stats(profile, stream=buffer).sort_stats(sortby)
            stats.print_stats()
            with open(filepath, 'w') as perf_file:
                perf_file.write(buffer.getvalue())
        else:
            result = func(*args, **kwargs)
        return result
    return wrapper
