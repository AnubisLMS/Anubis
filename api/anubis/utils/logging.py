import logging

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
