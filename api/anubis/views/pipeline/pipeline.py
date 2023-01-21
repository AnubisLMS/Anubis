import json

from flask import Blueprint, request
from parse import parse

from anubis.models import AssignmentTest, Submission, SubmissionTestResult, db
from anubis.utils.data import MYSQL_TEXT_MAX_LENGTH
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_endpoint, json_response
from anubis.utils.logging import logger
from anubis.utils.pipeline.decorators import check_submission_token
from anubis.lms.submissions import init_submission

pipeline = Blueprint("pipeline", __name__, url_prefix="/pipeline")


@pipeline.post("/report/panic/<string:submission_id>")
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

    # set the submission state
    submission.processed = True
    submission.state = "Whoops! There was an error on our end. The error has been logged."
    submission.errors = {"panic": request.json}

    # commit the changes to the session
    db.session.add(submission)
    db.session.commit()

    return success_response("Panic successfully reported")


@pipeline.post("/report/build/<string:submission_id>")
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

    if len(stdout) > MYSQL_TEXT_MAX_LENGTH:
        stdout = stdout[:MYSQL_TEXT_MAX_LENGTH]

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


@pipeline.post("/report/test/<string:submission_id>")
@check_submission_token
@json_endpoint([("test_name", str), ("passed", bool), ("message", str), ('output_type', str), ("output", str)])
def pipeline_report_test(submission: Submission, test_name: str, passed: bool, message: str, output_type: str,
                         output: str, **_):
    """
    Submission pipelines will hit this endpoint when there
    is a test result to report.

    POSTed json should be of the shape:

    {
      "test_name": "name of the test",
      "passed": True,
      "message": "This test worked",
      "output_type": "diff",
      "output": "--- \n\n+++ \n\n@@ -1,3 +1,3 @@\n\n a\n-c\n+b\n d"
    }

    :param submission:
    :param test_name:
    :param passed:
    :param message:
    :param output:
    :param output_type:
    :return:
    """

    if len(output) > MYSQL_TEXT_MAX_LENGTH:
        output = output[:MYSQL_TEXT_MAX_LENGTH]

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
            "output_type": output_type,
            "output": output,
        },
    )

    submission_test_result: SubmissionTestResult | None = None

    # Look for corresponding submission_test_result based on given name
    for result in submission.test_results:
        # Compare name
        if result.assignment_test.name == test_name:
            submission_test_result = result
            break

    # Verify we got a match
    if submission_test_result is None:
        logger.error("Invalid submission test result reported", extra={"request": request.json})
        return success_response({"status": "invalid test name"})

    # Update the fields
    submission_test_result.passed = passed
    submission_test_result.message = message
    submission_test_result.output_type = output_type
    submission_test_result.output = output

    # Add and commit
    db.session.add(submission_test_result)
    db.session.commit()

    return success_response("Test data successfully added.")


@pipeline.post("/report/state/<string:submission_id>")
@check_submission_token
@json_endpoint(required_fields=[("state", str)])
def pipeline_report_state(submission: Submission, state: str, **__):
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

    # set the processed field if it was specified
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

        # set hidden_test to True if the test exists, and if it is marked as hidden
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
from anubis.constants import SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE


@pipeline.get("/reset/<string:submission_id>")
@check_submission_token
@json_response
def pipeline_reset(submission: Submission):
    """
    Reset a submission to base state. Quite useful for live autograder to be
    able to reset on the fly.

    :param submission:
    :return:
    """

    extra = {}

    # If the submission is a shell autograde, preserve the state message
    if submission.state == SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE:
        extra['state'] = SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE

    # Resets submission to base state
    init_submission(submission, db_commit=True, **extra)

    return success_response("Reset")
