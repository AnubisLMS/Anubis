from functools import wraps

from flask import request

from anubis.models import Submission
from anubis.utils.http import error_response
from anubis.utils.logging import logger


def check_submission_token(func):
    """
    This decorator should be exclusively used on the pipeline manager.
    For the report endpoints, it will find and verify submission data
    for endpoints that follow the shape:

    /report/.../<int:submission_id>?token=<token>

    If the submission and the token are not verified, and error response
    with status code 406 (rejected) will be returned.

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(submission_id: str):
        # Try to get the submission
        submission = Submission.query.filter(Submission.id == submission_id).first()

        # Try to get a token from the request query
        token = request.args.get("token", default=None)

        # Verify submission exists
        if submission is None:
            # Log that there was an issue with finding the submission
            logger.error(
                "Invalid submission from submission pipeline",
                extra={
                    "submission_id": submission_id,
                    "path":          request.path,
                    "headers":       request.headers,
                    "ip":            request.remote_addr,
                },
            )

            # Give back a 406 rejected error
            return error_response("Invalid"), 406

        # Verify we got a token
        if token is None:
            # Log that there was an issue with finding a token
            logger.error(
                "Attempted report post with no token",
                extra={
                    "submission_id": submission_id,
                    "path":          request.path,
                    "headers":       request.headers,
                    "ip":            request.remote_addr,
                },
            )

            # Give back a 406 rejected error
            return error_response("Invalid"), 406

        # Verify token matches
        if token != submission.token:
            # Log that there was an issue verifying tokens
            logger.error(
                "Invalid token reported from pipeline",
                extra={
                    "submission_id": submission_id,
                    "path":          request.path,
                    "headers":       request.headers,
                    "ip":            request.remote_addr,
                },
            )

            # Give back a 406 rejected error
            return error_response("Invalid"), 406

        # Log that the request was validated
        logger.info("Pipeline request validated {}".format(request.path))

        # Call the view function, and pass the
        # submission sqlalchemy object.
        return func(submission)

    return wrapper
