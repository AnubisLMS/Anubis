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

    # Initialize a logger for this app with the logger
    # name specified
    _logger = logging.getLogger(logger_name)

    return _logger


# Create a single logger object for the current app instance
logger = _get_logger(config.LOGGER_NAME)
