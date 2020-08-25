import json
import logging
from json import dumps

from flask import request, Blueprint

from anubis.models import Submission, SubmissionTestResult
from anubis.models import User
from anubis.models import db
from anubis.routes.messages import panic_msg
from anubis.utils.data import success_response, error_response, notify
from anubis.utils.decorators import json_response, check_submission_token, json_endpoint
from anubis.utils.elastic import log_endpoint

pipeline = Blueprint('pipeline', __name__, url_prefix='/pipeline')


@pipeline.route('/report/panic/<int:submission_id>', methods=['POST'])
@log_endpoint('pipeline-panic', lambda: 'panic report from pipeline  ' + dumps(request.json))
@json_response
@check_submission_token
def pipeline_report_panic(submission: Submission):
    """
    POSTed json should be of the shape:

    {
      "message": "yikers this was a bad error",
      "traceback": "optional traceback",

    }

    :param submission:
    :return:
    """

    submission.processed = True
    submission.state = 'Whoops! There was an error on our end. The Anubis admins have been notified.'
    submission.errors = {'panic': request.json}

    logging.error('Panic from submission cluster', extra=request.json)

    db.session.add(submission)
    db.session.commit()

    for user in User.query.filter(User.is_admin == True).all():
        notify(user, panic_msg.format(
            submission=json.dumps(submission.data, indent=2),
            assignment=json.dumps(submission.assignment.data, indent=2),
            user=json.dumps(submission.owner.data, indent=2),
            panic=json.dumps(request.json, indent=2),
        ), 'Anubis pipeline panic submission_id={}'.format(submission.id))

    return success_response('Panic successfully reported')


@pipeline.route('/report/error/<int:submission_id>', methods=['POST'])
@log_endpoint('pipeline', lambda: 'error report from pipeline ' + dumps(request.json))
@json_response
@check_submission_token
def pipeline_report_error(submission: Submission):
    return success_response('Error was successfully reported')


@pipeline.route('/report/build/<int:submission_id>', methods=['POST'])
@log_endpoint('pipeline', lambda: 'build report from pipeline ' + dumps(request.json))
@check_submission_token
@json_endpoint(required_fields=[('stdout', str), ('passed', bool)])
def pipeline_report_build(submission: Submission, stdout: str, passed: bool):
    """
    POSTed json should be of the shape:

    {
      "stdout": "build logs...",
      "passed": True
    }

    :param submission:
    :param stdout:
    :param passed:
    :return:
    """

    # Update submission build
    submission.build.stdout = stdout
    submission.build.passed = passed

    # If the build did not passed, then the
    # submission pipeline is done
    if passed is False:
        submission.processed = True
        submission.state = 'Build did not succeed'

    # Add and commit
    db.session.add(submission)
    db.session.add(submission.build)
    db.session.commit()

    # Report success
    return success_response('Build successfully reported.')


@pipeline.route('/report/test/<int:submission_id>', methods=['POST'])
@log_endpoint('pipeline', lambda: 'build report from pipeline ' + dumps(request.json))
@check_submission_token
@json_endpoint(required_fields=[('test_name', str), ('passed', bool), ('message', str), ('stdout', str)])
def pipeline_report_test(submission: Submission, test_name: str, passed: bool, message: str, stdout: str):
    """
    POSTed json should be of the shape:

    {
      "test_name": "name of the test",
      "passed": True,
      "message": "This test worked",
      "stdout": "Command logs..."
    }

    :param submission:
    :param test_name:
    :param passed:
    :param message:
    :param stdout:
    :return:
    """
    submission_test_result: SubmissionTestResult = None

    # Look for corresponding submission_test_result based on given name
    for result in submission.test_results:
        # Compare name
        if result.assignment_test.name == test_name:
            submission_test_result = result
            break

    # Verify we got a match
    if submission_test_result is None:
        logging.error('Invalid submission test result reported', extra={'request': request.json})
        return error_response('Invalid'), 406

    # Update the fields
    submission_test_result.passed = passed
    submission_test_result.message = message
    submission_test_result.stdout = stdout

    # Add and commit
    db.session.add(submission_test_result)
    db.session.commit()

    return success_response('Test data successfully added.')


@pipeline.route('/report/state/<int:submission_id>', methods=['POST'])
@log_endpoint('pipeline', lambda: 'build report from pipeline ' + dumps(request.json))
@check_submission_token
@json_endpoint(required_fields=[('state', str)])
def pipeline_report_state(submission: Submission, state: str):
    """
    POSTed json should be of the shape:

    {
      "state": "",
      "processed": True  # optional
    }

    :param submission:
    :param state:
    :return:
    """

    # Update state field
    submission.state = state

    # If processed was specified and is of type bool, then update that too
    if 'processed' in request.json and isinstance(request.json['processed'], bool):
        submission.processed = request.json['processed']

    # Add and commit
    db.session.add(submission)
    db.session.commit()

    return success_response('State successfully updated.')
