import logging

from anubis.config import config


def _get_logger(logger_name):
    """
    For any of the anubis services that use the API, the
    logger name should be specified. In prod, container
    logs will be captured by filebeat and pushed into
    elasticsearch in the elastic namespace.

    :param logger_name:
    :return:
    """
    from anubis.utils.data import is_debug

    # Initialize a logger for this app with the logger
    # name specified
    _logger = logging.getLogger(logger_name)

    # Set the log level to debug if in debug mode
    if is_debug():
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)

    return _logger


# Create a single logger object for the current app instance
logger = _get_logger(config.LOGGER_NAME)
