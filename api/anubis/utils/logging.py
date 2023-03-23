import functools
import logging
import traceback

from anubis.env import env
from anubis.utils.data import is_debug


def _get_logger(logger_name):
    """
    For any of the anubis services that use the API, the
    logger name should be specified. In prod, container
    logs will be captured by filebeat and pushed into
    elasticsearch in the elastic namespace.

    :param logger_name:
    :return:
    """

    # Initialize a logger for this app with the logger
    # name specified
    streamer = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(name)s %(filename)s %(levelname)s :: %(message)s")
    streamer.setFormatter(formatter)
    _logger = logging.getLogger(logger_name)
    _logger.setLevel(logging.DEBUG if is_debug() else logging.INFO)
    _logger.addHandler(streamer)

    return _logger


# Create a single logger object for the current app instance
logger = _get_logger(env.LOGGER_NAME)


def verbose_call(log_func=logger.info, reraise: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name: str = f'{func.__module__}.{func.__qualname__}'
            func_str: str = f'{func_name}( {args=}, {kwargs=} )'
            log_func(func_str)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if reraise:
                    log_func(func_str)
                    raise e
                else:
                    log_func(f'{func_str}\nException={e}\n{traceback.format_exc()}')

        return wrapper

    return decorator
