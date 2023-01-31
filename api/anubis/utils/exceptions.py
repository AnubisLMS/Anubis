import functools
import traceback
from datetime import date, datetime

from flask import Flask, jsonify


class AnubisError(Exception):
    """
    Generic Anubis error
    """
    pass


class AssertError(AnubisError):
    """
    This exception should be raised when an assertion
    fails in the request.
    """

    def __init__(self, message: str, status_code: int = 400):
        super(AssertError, self).__init__(message)
        self._message = message
        self._status_code = status_code

    def response(self):
        return self._message, self._status_code


class AuthenticationError(AnubisError):
    """
    This exception should be raised if a request
    lacks the proper authentication fow whatever
    action they are requesting.

    If the view function is wrapped in any of the
    require auth decorators, then this exception
    will be caught and return a 401.
    """


class LackCourseContext(AnubisError):
    """
    Most of the admin actions require there to
    be a course context to be set. This exception
    should be raised if there is not a course
    context set.

    If there is some other permission issue involving
    the course context, then a AuthenticationError
    may be more appropriate.
    """


class GoogleCredentialsException(AnubisError):
    """
    This is raised when the google credentials are
    invalid in any way. This is not something that
    will ever be raised in a request context. Because
    the google apis are only used in rpc jobs, we only
    need to worry about having exception handlers for
    this exception there.
    """


def add_app_exception_handlers(app: Flask):
    """
    Add exception handlers to the flask app.

    :param app:
    :return:
    """

    from anubis.utils.http import error_response
    from anubis.utils.logging import logger

    # set AuthenticationError handler
    @app.errorhandler(AuthenticationError)
    def handler_authentication_error(e: AuthenticationError):
        logger.error(traceback.format_exc())
        return jsonify(error_response(str(e) or "Unauthenticated")), 401

    # set LackCourseContext handler
    @app.errorhandler(LackCourseContext)
    def handle_lack_course_context(e: LackCourseContext):
        logger.error(traceback.format_exc())
        return jsonify(error_response(str(e) or "Please set your course context"))

    @app.errorhandler(AssertError)
    def handle_assertion_error(e: AssertError):
        from anubis.models import db
        db.session.rollback()
        logger.error(traceback.format_exc())
        message, status_code = e.response()
        return jsonify(error_response(message)), status_code


def send_alert_email_on_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from anubis.utils.email.event import send_email_event_admin

            # Get full function name
            function_name: str = f'{func.__module__}.{func.__qualname__}'

            # Send email event
            send_email_event_admin(
                reference_id=function_name,
                reference_type=f'{date.today()} error',  # Limit to one per day using this
                template_key=f'error',
                context={
                    'traceback':     traceback.format_exc(),
                    'function_name': function_name,
                    'datetime':      datetime.now()
                }
            )

            raise e

    return wrapper
