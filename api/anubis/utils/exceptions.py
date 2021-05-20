import traceback

from flask import Flask, jsonify


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

    from anubis.utils.http.https import error_response
    from anubis.utils.services.logger import logger

    # Set AuthenticationError handler
    @app.errorhandler(AuthenticationError)
    def handler_authentication_error(e: AuthenticationError):
        logger.error(traceback.format_exc())
        return jsonify(error_response(str(e) or 'Unauthenticated')), 401

    # Set LackCourseContext handler
    @app.errorhandler(LackCourseContext)
    def handle_lack_course_context(e: LackCourseContext):
        logger.error(traceback.format_exc())
        return error_response(str(e) or 'Please set your course context')
