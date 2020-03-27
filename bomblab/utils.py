from geoip import geolite2
from elasticsearch import Elasticsearch
from datetime import datetime
from functools import wraps
from flask import request, Response
from werkzeug import exceptions
import traceback
import pymysql.cursors


es = Elasticsearch(['http://elasticsearch:9200'])


def get_request_ip():
    """
    Since we are using a request forwarder,
    the real client IP will be added as a header.
    This function will search the expected headers
    to find that ip.
    """
    def check(header):
        """get header from request else empty string"""
        return request.headers[
            header
        ] if header in request.headers else ''

    def check_(headers, n=0):
        """check headers based on ordered piority"""
        if n == len(headers):
            return ''
        return check(headers[n]) or check_(headers, n+1)

    return str(check_([
        'x-forwarded-for', # highest priority
        'X-Forwarded-For',
        'x-real-ip',
        'X-Real-Ip',       # lowest priority
    ]) or request.remote_addr or 'N/A')


def add_global_error_handler(app):
    @app.errorhandler(Exception)
    def global_err_handler(error):
        tb = traceback.format_exc() # get traceback string
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


def esindex(index='error', **kwargs):
    """
    Index anything with elasticsearch

    :kwargs dict:
    """
    es.index(index=index, body={
        'timestamp': datetime.utcnow(),
        **kwargs,
    })



def log_event(log_type, message_func, onlyif=None):
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
            if onlyif():
                ip = get_request_ip()
                location = geolite2.lookup(ip)
                es.index(index='request', body={
                    'type': log_type.lower(),
                    'msg': message_func(),
                    'location': location.location[::-1] if location is not None else location,
                    'ip': ip,
                    'timestamp': datetime.utcnow(),
                })

            return function(*args, **kwargs)
        return wrapper
    return decorator



def get_netids():
    """
    Gets all distinct netid's from the database. It does
    rely on the database student data to be up to date. Use
    the anubis cli student command for checking, and updating
    student data.
    """
    connection = pymysql.connect(
        host='db',
        user='root',
        password='password',
        db='os',
        charset='utf8mb4',
    )

    with connection.cursor() as cursor:
        # Create a new record
        sql = "select distinct netid from student;"
        cursor.execute(sql)
        data = cursor.fetchall()

    connection.close()

    return list(map(lambda x: x[0], data))
