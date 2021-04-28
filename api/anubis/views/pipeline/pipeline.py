import json

from flask import request, Blueprint
from parse import parse

from anubis.models import Submission, SubmissionTestResult, AssignmentTest
from anubis.models import db
from anubis.utils.http.decorators import json_response, check_submission_token, json_endpoint
from anubis.utils.http.https import success_response
from anubis.utils.services.logger import logger

pipeline = Blueprint("pipeline", __name__, url_prefix="/pipeline")


@pipeline.route("/report/panic/<string:submission_id>", methods=["POST"])
@check_submission_token
@json_response
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

    logger.error(
        "submission panic reported",
        extra={
            "type": "panic_report",
            "submission_id": submission.id,
            "assignment_id": submission.assignment_id,
            "owner_id": submission.owner_id,
            "data": json.dumps(request.json),
        },
    )

    submission.processed = True
    submission.state = (
        "Whoops! There was an error on our end. The error has been logged."
    )
    submission.errors = {"panic": request.json}

    db.session.add(submission)
    db.session.commit()

    # for user in User.query.filter(User.is_admin == True).all():
    #     notify(user, panic_msg.format(
    #         submission=json.dumps(submission.data, indent=2),
    #         assignment=json.dumps(submission.assignment.data, indent=2),
    #         user=json.dumps(submission.owner.data, indent=2),
    #         panic=json.dumps(request.json, indent=2),
    #     ), 'Anubis pipeline panic submission_id={}'.format(submission.id))

    return success_response("Panic successfully reported")


@pipeline.route("/report/build/<string:submission_id>", methods=["POST"])
@check_submission_token
@json_endpoint(required_fields=[("stdout", str), ("passed", bool)])
def pipeline_report_build(submission: Submission, stdout: str, passed: bool, **kwargs):
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

    logger.info(
        "submission build reported",
        extra={
            "type": "build_report",
            "submission_id": submission.id,
            "assignment_id": submission.assignment_id,
            "owner_id": submission.owner_id,
            "passed": passed,
            "stdout": stdout,
        },
    )

    # Update submission build
    submission.build.stdout = stdout
    submission.build.passed = passed

    # If the build did not passed, then the
    # submission pipeline is done
    if passed is False:
        submission.processed = True
        submission.state = "Build did not succeed"

    # Add and commit
    db.session.add(submission)
    db.session.add(submission.build)
    db.session.commit()

    # Report success
    return success_response("Build successfully reported.")


@pipeline.route("/report/test/<string:submission_id>", methods=["POST"])
@check_submission_token
@json_endpoint(
    required_fields=[
        ("test_name", str),
        ("passed", bool),
        ("message", str),
        ("stdout", str),
    ]
)
def pipeline_report_test(
        submission: Submission,
        test_name: str,
        passed: bool,
        message: str,
        stdout: str,
        **kwargs
):
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

    logger.info(
        "submission test reported",
        extra={
            "type": "test_result",
            "submission_id": submission.id,
            "assignment_id": submission.assignment_id,
            "owner_id": submission.owner_id,
            "test_name": test_name,
            "test_message": message,
            "passed": passed,
            "stdout": stdout,
        },
    )

    submission_test_result: SubmissionTestResult = None

    # Look for corresponding submission_test_result based on given name
    for result in submission.test_results:
        # Compare name
        if result.assignment_test.name == test_name:
            submission_test_result = result
            break

    # Verify we got a match
    if submission_test_result is None:
        logger.error(
            "Invalid submission test result reported", extra={"request": request.json}
        )
        return success_response({
            'status': "invalid test name"
        })

    # Update the fields
    submission_test_result.passed = passed
    submission_test_result.message = message
    submission_test_result.stdout = stdout

    # Add and commit
    db.session.add(submission_test_result)
    db.session.commit()

    return success_response("Test data successfully added.")


@pipeline.route("/report/state/<string:submission_id>", methods=["POST"])
@check_submission_token
@json_endpoint(required_fields=[("state", str)])
def pipeline_report_state(submission: Submission, state: str, **kwargs):
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

    logger.info(
        "submission state update",
        extra={
            "type": "state_report",
            "submission_id": submission.id,
            "assignment_id": submission.assignment_id,
            "owner_id": submission.owner_id,
            "state": state,
        },
    )

    processed = request.args.get("processed", default="0")
    submission.processed = processed != "0"

    hidden_test = False
    match = parse('Running test: {}', state)
    if match:
        test_name = match[0]
        assignment_test = AssignmentTest.query.filter(
            AssignmentTest.assignment_id == submission.assignment_id,
            AssignmentTest.name == test_name
        ).first()
        hidden_test = assignment_test is not None and assignment_test.hidden

    # Update state field
    if not hidden_test:
        submission.state = state

    # If processed was specified and is of type bool, then update that too
    if "processed" in request.json and isinstance(request.json["processed"], bool):
        submission.processed = request.json["processed"]

    # Add and commit
    db.session.add(submission)
    db.session.commit()

    return success_response("State successfully updated.")
