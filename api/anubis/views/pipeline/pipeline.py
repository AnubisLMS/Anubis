import json
from typing import Union

from flask import request, Blueprint
from parse import parse

from anubis.models import Submission, SubmissionTestResult, AssignmentTest
from anubis.models import db
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http import success_response
from anubis.utils.logging import logger
from anubis.utils.pipeline.decorators import check_submission_token

pipeline = Blueprint("pipeline", __name__, url_prefix="/pipeline")


@pipeline.route("/report/panic/<string:submission_id>", methods=["POST"])
@check_submission_token
@json_response
def pipeline_report_panic(submission: Submission):
    """
    Pipeline workers will hit this endpoint if there was
    a panic that needs to be reported. This view function
    should mark the submission as processed, and update
    its state.

    POSTed json should be of the shape:

    {
      "message": "yikers this was a bad error",
      "traceback": "optional traceback",

    }

    :param submission:
    :return:
    """

    # log th panic
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

    # Set the submission state
    submission.processed = True
    submission.state = (
        "Whoops! There was an error on our end. The error has been logged."
    )
    submission.errors = {"panic": request.json}

    # commit the changes to the session
    db.session.add(submission)
    db.session.commit()

    return success_response("Panic successfully reported")


@pipeline.route("/report/build/<string:submission_id>", methods=["POST"])
@check_submission_token
@json_endpoint([("stdout", str), ("passed", bool)])
def pipeline_report_build(submission: Submission, stdout: str, passed: bool, **_):
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

    # Log the build being reported
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
    [("test_name", str), ("passed", bool), ("message", str), ("stdout", str)]
)
def pipeline_report_test(
    submission: Submission, test_name: str, passed: bool, message: str, stdout: str, **_
):
    """
    Submission pipelines will hit this endpoint when there
    is a test result to report.

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

    # Log the build
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

    submission_test_result: Union[SubmissionTestResult, None] = None

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
        return success_response({"status": "invalid test name"})

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
    When a submission pipeline wants to report a state, it
    hits this endpoint. If there is a ?processed=1 in the
    http query, then the submission will also be marked as
    processed.

    POSTed json should be of the shape:

    {
      "state": "",
      "processed": True  # optional
    }

    :param submission:
    :param state:
    :return:
    """

    # Log the state update
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

    # Get the processed option if it was specified
    processed = request.args.get("processed", default="0")

    # Set the processed field if it was specified
    submission.processed = processed != "0"

    # Figure out if the test is hidden
    # We do this by checking the state that was given,
    # to read the name of the test. If the assignment
    # test that was found is marked as hidden, then
    # we should not update the state of the submission
    # model.
    #
    # If we were to update the state of the submission
    # when a hidden test is reported, then it would be
    # visible to the students in the frontend.
    hidden_test = False

    # Do a basic match on the expected test
    match = parse("Running test: {}", state)

    # If we got a match
    if match:
        # Get the parsed assignment test name
        test_name = match[0]

        # Try to get the assignment test
        assignment_test = AssignmentTest.query.filter(
            AssignmentTest.assignment_id == submission.assignment_id,
            AssignmentTest.name == test_name,
        ).first()

        # Set hidden_test to True if the test exists, and if it is marked as hidden
        hidden_test = assignment_test is not None and assignment_test.hidden

    # Update state field if the state report is not for a hidden test
    if not hidden_test:
        submission.state = state

    # If processed was specified and is of type bool, then update that too
    if "processed" in request.json and isinstance(request.json["processed"], bool):
        submission.processed = request.json["processed"]

    # Add and commit
    db.session.add(submission)
    db.session.commit()

    return success_response("State successfully updated.")
