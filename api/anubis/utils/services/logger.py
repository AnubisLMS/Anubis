import logging

import logstash

from anubis.config import config


def _get_logger(logger_name):
    """
    For any of the anubis services that use the API, the
    logger name should be specified so that all the logs
    that are thrown at logstash, then elasticsearch
    can be tracked back to a specific service.

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

    # If the disable ELK option is not enabled, then
    # add the logstash udp logging layer.
    if not config.DISABLE_ELK:
        _logger.addHandler(logstash.LogstashHandler("logstash", 5000))

    return _logger


# Create a single logger object for the current app instance
logger = _get_logger(config.LOGGER_NAME)
