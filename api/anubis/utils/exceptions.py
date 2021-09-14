import traceback

from flask import Flask, jsonify


class AssertError(Exception):
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


class AuthenticationError(Exception):
    """
    This exception should be raised if a request
    lacks the proper authentication fow whatever
    action they are requesting.

    If the view function is wrapped in any of the
    require auth decorators, then this exception
    will be caught and return a 401.
    """


class LackCourseContext(Exception):
    """
    Most of the admin actions require there to
    be a course context to be set. This exception
    should be raised if there is not a course
    context set.

    If there is some other permission issue involving
    the course context, then a AuthenticationError
    may be more appropriate.
    """


def add_app_exception_handlers(app: Flask):
    """
    Add exception handlers to the flask app.

    :param app:
    :return:
    """

    from anubis.utils.http import error_response
    from anubis.utils.logging import logger

    # Set AuthenticationError handler
    @app.errorhandler(AuthenticationError)
    def handler_authentication_error(e: AuthenticationError):
        logger.error(traceback.format_exc())
        return jsonify(error_response(str(e) or 'Unauthenticated')), 401

    # Set LackCourseContext handler
    @app.errorhandler(LackCourseContext)
    def handle_lack_course_context(e: LackCourseContext):
        logger.error(traceback.format_exc())
        return jsonify(error_response(str(e) or 'Please set your course context'))

    @app.errorhandler(AssertError)
    def handle_assertion_error(e: AssertError):
        logger.error(traceback.format_exc())
        message, status_code = e.response()
        return jsonify(error_response(message)), status_code
