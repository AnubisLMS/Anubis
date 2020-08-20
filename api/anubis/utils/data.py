from email.mime.text import MIMEText
from functools import wraps
from json import dumps
from os import environ
from smtplib import SMTP
from typing import Union, List

from flask import Response, request
from sqlalchemy.exc import IntegrityError

from anubis.models import db
from anubis.utils.redis_queue import enqueue_webhook_job


def jsonify(data):
    """
    Wrap a data response to set proper headers for json
    """
    res = Response(dumps(data))
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = 'https://anubis.osiris.services' \
        if not environ.get('DEBUG', False) \
        else 'https://localhost'
    return res


def json(func):
    """
    Wrap a route so that it always converts data
    response to proper json.

    @app.route('/')
    @json
    def test():
        return {
            'success': True
        }
    """

    @wraps(func)
    def json_wrap(*args, **kwargs):
        data = func(*args, **kwargs)
        return jsonify(data)

    return json_wrap


def regrade_submission(submission):
    """
    Regrade a submission

    :param submission: Submissions
    :return: dict response
    """

    if not submission.processed:
        return error_response('submission currently being processed')

    if not reset_submission(submission):
        return error_response('error regrading')

    enqueue_webhook_job(submission.id)

    return success_response({'message': 'regrade started'})


def reset_submission(submission):
    """
    This function will reset all the data for a submission,
    putting it in a pending state. To re-enqueue this submission
    as a job, use the enqueue_webhook_job function.

    :submission Submissions: submission object
    :return: bool indicating success
    """
    if not submission.processed:
        return False

    submission.processed = False

    for report in submission.reports:
        db.session.delete(report)
    for build in submission.builds:
        db.session.delete(build)
    for test in submission.tests:
        db.session.delete(test)
    for error in submission.errors:
        db.session.delete(error)

    try:
        # db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False
    return True


def json_response(func):
    """
    Wrap a route so that it always converts data
    response to proper json.

    @app.route('/')
    @json
    def test():
        return {
            'success': True
        }
    """

    @wraps(func)
    def json_wrap(*args, **kwargs):
        data = func(*args, **kwargs)
        status_code = 200
        if isinstance(data, tuple):
            data, status_code = data
        return jsonify(data, status_code)

    return json_wrap


def json_endpoint(required_fields: Union[List[str], None] = None):
    """
    Wrap a route so that it always converts data
    response to proper json.

    @app.route('/')
    @json
    def test():
        return {
            'success': True
        }
    """

    def wrapper(func):
        @wraps(func)
        def json_wrap(*args, **kwargs):
            if not request.headers.get('Content-Type', default=None).startswith('application/json'):
                return {
                           'success': False,
                           'error': 'Content-Type header is not application/json',
                           'data': None,
                       }, 406  # Not Acceptable
            json_data: dict = request.json

            if required_fields is not None:
                # Check required fields
                for field in required_fields:
                    if field not in json_data:
                        # field missing, return error
                        return {
                                   'success': False,
                                   'error': 'Malformed requests. Missing fields.',
                                   'data': None
                               }, 406  # Not Acceptable

            if required_fields is not None:
                return func(
                    *args,
                    *(json_data[field] for field in required_fields),
                    **{key: value for key, value in json_data.items() if key not in required_fields},
                    **kwargs)
            return func(json_data, *args, **kwargs)

        return json_wrap

    return wrapper


def error_response(error_message: str) -> dict:
    """
    Form an error REST api response dict.

    :param error_message: string error message
    :return:
    """
    return {
        'success': False,
        'error': error_message,
        'data': None,
    }


def success_response(data: dict) -> dict:
    """
    Form a success REST api response dict.

    :param data:
    :return:
    """
    return {
        'success': True,
        'error': None,
        'data': data,
    }


def is_debug() -> bool:
    """
    Returns true if the app is running in debug mode

    :return:
    """
    return environ.get('DEBUG', default=False) is not False


def send_noreply_email(msg, subject, to):
    """
    Use this function to send a noreply email to a user (ie student).

    * This will only work on the computer that has the dns pointed to it (ie the server)

    If you set up the dns with namecheap, you can really easily just set
    the email dns setting to private email. Once that is set, it configures
    all the spf stuff for you. Doing to MX and spf records by hand are super
    annoying.

    eg:
    send_noreply_email('this is the message', 'this is the subject', 'netid@nyu.edu')

    :msg str: email body or message to send
    :subject str: subject for email
    :to str: recipient of email (should be their nyu email)
    """

    if environ.get('DEBUG', False):
        return print(msg, subject, to, flush=True)

    msg = MIMEText(msg, "plain")
    msg["Subject"] = subject

    msg["From"] = "john@nyu.lol"
    msg["To"] = to

    s = SMTP("smtp")
    s.send_message(msg)
    s.quit()
