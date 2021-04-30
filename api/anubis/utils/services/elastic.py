import json
import traceback
from datetime import datetime
from functools import wraps

from flask import request
from geoip import geolite2
from werkzeug import exceptions

from anubis.config import config
from anubis.utils.http.https import get_request_ip
from anubis.utils.services.logger import logger


def log_endpoint(log_type, message_func=None):
    """
    Use this to decorate a route and add logging.
    The message_func should be a callable object
    that returns a string to be logged.

    eg.

    @log_event('LOG-TYPE', lambda: 'some_function was just called')
    def some_function(arg1, arg2):
        ....

    :param log_type: log type to noted in event
    :param message_func: callable function to return message to be logged
    :return:
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            ip = get_request_ip()
            location = geolite2.lookup(ip)
            longitude, latitude = location.location[::-1] \
                if location is not None \
                else [0, 0]

            # Skip indexing if the app has ELK disabled
            if not config.DISABLE_ELK:
                logger.info(
                    '{ip} -- {date} "{method} {path}"'.format(
                        ip=get_request_ip(),
                        date=datetime.now(),
                        method=request.method,
                        path=request.path,
                    ),
                    extra={
                        "body": {
                            "type": log_type.lower(),
                            "path": request.path,
                            "msg": message_func() if message_func is not None else None,
                            "longitude": longitude,
                            "latitude": latitude,
                            "ip": ip,
                            "timestamp": str(datetime.utcnow()),
                        }
                    },
                )

            return function(*args, **kwargs)

        return wrapper

    return decorator


def esindex(index: str = "error", **kwargs):
    """
    Index anything with elasticsearch

    :param index:
    :param kwargs: dict
    """
    if config.DISABLE_ELK:
        return
    logger.info("event", extra={"index": index, "body": kwargs})


def add_global_error_handler(app):
    """
    This function adds a global error handler to the flask
    app. There are a few reasons why this may not always be the
    best idea. Some exceptions raised should be handled by flask (for
    example: 404 not found exceptions).

    :param app:
    :return:
    """

    @app.errorhandler(Exception)
    def global_err_handler(error):
        # get traceback string
        tb = traceback.format_exc()

        # Log the traceback string through logstash, with extra information
        logger.error(tb, extra={
            "from": "global-error-handler",
            "traceback": tb,
            "ip": get_request_ip(),
            "method": request.method,
            "path": request.path,
            "query": json.dumps(dict(list(request.args.items()))),
            "headers": json.dumps(dict(list(request.headers.items()))),
        })

        # Handle the error if it is a 404
        if isinstance(error, exceptions.NotFound):
            return "", 404

        # If it is a method not allowed, return a 405
        if isinstance(error, exceptions.MethodNotAllowed):
            return "MethodNotAllowed", 405

        # Else return a vague 500
        return "err", 500
