import traceback
from datetime import datetime
from functools import wraps

from elasticsearch import Elasticsearch
from flask import request
from geoip import geolite2
from werkzeug import exceptions

from anubis.utils.http import get_request_ip
from anubis.config import config

es = Elasticsearch(['http://elasticsearch:9200'])


def log_endpoint(log_type, message_func):
    """
    Use this to decorate a route and add logging.
    The message_func should be a calleble object
    that returns a string to be logged.

    eg.

    @log_event('LOG-TYPE', lambda: 'somefunction was just called')
    def somefunction(arg1, arg2):
        ....

    :log_type str: log type to noted in event
    :message_func callable: function to return message to be logged
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            ip = get_request_ip()
            location = geolite2.lookup(ip)

            # Skip indexing if the app has ELK disabled
            if not config.DISABLE_ELK:
                es.index(index='request', body={
                    'type': log_type.lower(),
                    'path': request.path,
                    'msg': message_func(),
                    'location': location.location[::-1] if location is not None else location,
                    'ip': ip,
                    'timestamp': datetime.utcnow(),
                })

            return function(*args, **kwargs)

        return wrapper

    return decorator


def esindex(index='error', **kwargs):
    """
    Index anything with elasticsearch

    :kwargs dict:
    """
    if config.DISABLE_ELK:
        return
    es.index(index=index, body={
        'timestamp': datetime.utcnow(),
        **kwargs,
    })


def add_global_error_handler(app):
    @app.errorhandler(Exception)
    def global_err_handler(error):
        tb = traceback.format_exc()  # get traceback string
        esindex(
            'error',
            type='global-handler',
            logs=request.url + ' - ' + get_request_ip() + '\n' + tb,
            submission=None,
            netid=None,
        )
        if isinstance(error, exceptions.NotFound):
            return '', 404
        return 'err'
