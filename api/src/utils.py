from sqlalchemy.exc import IntegrityError
from dataclasses import dataclass
from functools import wraps
from flask import request
from redis import Redis
from rq import Queue

from .jobs import test_repo
from .models import Events
from .app import db


"""
We will use rq to enqueue and dequeue jobs.
"""
def enqueue(func, *args):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """
    with Redis(host='redis') as conn:
        q = Queue(connection=conn)
        q.enqueue(func, *args)


def enqueue_webhook_job(*args):
    """
    Enqueues a test job

    :repo_url str: github repo url (eg https://github.com/os3224/...)
    """
    print(args)
    enqueue(
        test_repo,
        *args
    )


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


def log_event(log_type, message_func):
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
            event = Events(
                type=log_type,
                message=message_func()
            )
            db.session.add(event)
            try:
                db.session.commit()
            except IntegrityError as e:
                print('EVENT LOG ERROR', e)
            return function(*args, **kwargs)
        return wrapper
    return decorator


