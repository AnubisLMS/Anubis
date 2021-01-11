import logging

import logstash

from anubis.config import config


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if not config.DISABLE_ELK:
        logger.addHandler(logstash.LogstashHandler("logstash", 5000))

    return logger


logger = get_logger(config.LOGGER_NAME)
