import json

from dateutil.parser import parse as dateparse
from flask import Blueprint
from sqlalchemy.exc import DataError, IntegrityError

from anubis.models import db, Assignment, User, AssignmentTest, SubmissionTestResult
from anubis.utils.auth import require_admin
from anubis.utils.data import rand
from anubis.utils.data import row2dict
from anubis.utils.http.decorators import load_from_id, json_response, json_endpoint
from anubis.utils.http.https import error_response, success_response
from anubis.utils.lms.assignments import assignment_sync
from anubis.utils.lms.course import assert_course_admin, get_course_context, assert_course_context
from anubis.utils.lms.questions import get_assigned_questions
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.services.logger import logger

assignments = Blueprint("admin-assignments", __name__, url_prefix="/admin/assignments")


@assignments.route("/assignment/<string:id>/questions/get/<string:netid>")
@require_admin()
@log_endpoint("cli", lambda: "question get")
@load_from_id(Assignment, verify_owner=False)
@json_response
def private_assignment_id_questions_get_netid(assignment: Assignment, netid: str):
    """
    Get questions assigned to a given student.

    :param assignment:
    :param netid:
    :return:
    """
    user = User.query.filter_by(netid=netid).first()
    if user is None:
        return error_response("user not found")

    course = get_course_context()
    assert_course_admin(assignment.course_id)
    assert_course_context(course.id == assignment.course_id)

    return success_response(
        {
            "netid": user.netid,
            "questions": get_assigned_questions(assignment.id, user.id),
        }
    )


@assignments.route("/get/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_response
def admin_assignments_get_id(assignment: Assignment):
    """
    Get the full data for an assignment id. The course context
    must be set, and will be checked.

    :param assignment:
    :return:
    """
    # Get the course context
    course = get_course_context()

    # Verify that the current user is an admin for the course
    # that the assignment is apart of
    assert_course_admin(assignment.course_id)

    # Confirm that the assignment they are asking for is part
    # of this course
    assert_course_context(course.id == assignment.course_id)

    # Pass back the full data
    return success_response({"assignment": assignment.full_data})


@assignments.route("/list")
@require_admin()
@json_response
def admin_assignments_list():
    """
    List all assignments within the course context.

    * The response will be the row2dict of the assignment, not a data prop *

    :return:
    """

    # Get the course context
    course = get_course_context()

    # Get all the assignment objects within the course context,
    # sorted by the due date.
    all_assignments = Assignment.query.filter(
        Assignment.course_id == course.id
    ).order_by(Assignment.due_date.desc()).all()

    # Pass back the row2dict of each assignment object
    return success_response({
        "assignments": [row2dict(assignment) for assignment in all_assignments]
    })


@assignments.route('/tests/toggle-hide/<string:assignment_test_id>')
@require_admin()
@json_response
def admin_assignment_tests_toggle_hide_assignment_test_id(assignment_test_id: str):
    """
    Toggle an assignment test being hidden.

    :param assignment_test_id:
    :return:
    """

    # Get the course context
    course = get_course_context()

    # Pull the assignment test
    assignment_test: AssignmentTest = AssignmentTest.query.filter(
        AssignmentTest.id == assignment_test_id,
    ).first()

    # Make sure the assignment test exists
    if assignment_test is None:
        return error_response('test not found')

    # Verify that the current user is an admin for the course the
    # assignment test is apart of
    assert_course_admin(assignment_test.assignment.course_id)

    # Verify that course the assignment test is apart of and
    # the course context match
    assert_course_context(course.id == assignment_test.assignment.course_id)

    # Toggle the hidden field
    assignment_test.hidden = not assignment_test.hidden

    # Commit the change
    db.session.commit()

    return success_response({
        'status': 'test updated',
        'assignment_test': assignment_test.data
    })


@assignments.route('/tests/delete/<string:assignment_test_id>')
@require_admin()
@json_response
def admin_assignment_tests_delete_assignment_test_id(assignment_test_id: str):
    """
    Delete an assignment test.

    :param assignment_test_id:
    :return:
    """

    # Get the course context
    course = get_course_context()

    # Pull the assignment test
    assignment_test = AssignmentTest.query.filter(
        AssignmentTest.id == assignment_test_id,
    ).first()

    # Make sure the assignment test exists
    if assignment_test is None:
        return error_response('test not found')

    # Verify that the current user is an admin for the course the
    # assignment test is apart of
    assert_course_admin(assignment_test.assignment.course_id)

    # Verify that course the assignment test is apart of and
    # the course context match
    assert_course_context(course.id == assignment_test.assignment.course_id)

    # Save the test name so we can use it in the response
    test_name = assignment_test.name

    # Delete all the submission test results that are pointing to
    # this test
    SubmissionTestResult.query.filter(
        SubmissionTestResult.assignment_test_id == assignment_test.id,
    ).delete()

    # Delete the test itself
    AssignmentTest.query.filter(
        AssignmentTest.id == assignment_test_id,
    ).delete()

    # Commit the changes
    db.session.commit()

    # Pass back the status
    return success_response({
        'status': f'{test_name} deleted',
        'variant': 'warning',
    })


@assignments.route("/save", methods=["POST"])
@require_admin()
@json_endpoint(required_fields=[("assignment", dict)])
def private_assignment_save(assignment: dict):
    """
    Save assignment from raw fields

    :param assignment:
    :return:
    """
    logger.info(json.dumps(assignment, indent=2))

    # Get assignment
    assignment_id = assignment["id"]
    db_assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # Make sure it exists
    if db_assignment is None:
        # Create it if it doesn't exist
        db_assignment = Assignment()
        assignment["id"] = rand()
        db.session.add(db_assignment)

    course = get_course_context()
    assert_course_admin(db_assignment.course_id)
    assert_course_context(course.id == db_assignment.course_id)

    # Update all it's fields
    for key, value in assignment.items():
        if 'date' in key:
            value = dateparse(value.replace('T', ' ').replace('Z', ''))
        setattr(db_assignment, key, value)

    # Attempt to commit
    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        # Tell frontend what error happened
        return error_response(str(e))

    # Return status
    return success_response(
        {
            "status": "Assignment updated",
        }
    )


@assignments.route("/sync", methods=["POST"])
@require_admin(unless_debug=True, unless_vpn=True)
@log_endpoint("cli", lambda: "assignment-sync")
@json_endpoint(required_fields=[("assignment", dict)])
def private_assignment_sync(assignment: dict):
    """
    Sync assignment data from the CLI. This should be used to create and update assignment data.

    body = {
      "assignment": {
        "name": "{name}",
        "course": "CS-UY 3224",
        "hidden": true,
        "github_classroom_url": "",
        "unique_code": "{code}",
        "pipeline_image": "registry.osiris.services/anubis/assignment/{code}",
        "date": {
          "release": "{now}",
          "due": "{week_from_now}",
          "grace": "{week_from_now}"
        },
        "description": "This is a very long description that encompasses the entire assignment\n",
        "questions": [
          {
            "sequence": 1,
            "questions": [
              {
                "q": "What is 3*4?",
                "a": "12"
              },
              {
                "q": "What is 3*2",
                "a": "6"
              }
            ]
          },
          {
            "sequence": 2,
            "questions": [
              {
                "q": "What is sqrt(144)?",
                "a": "12"
              }
            ]
          }
        ]
      }
    }

    response = {
      assignment : {}
      questions: {
        accepted: [ ... ]
        ignored: [ ... ]
        rejected: [ ... ]
      }
    }

    :param assignment_data:
    :param test_data:
    :param question_data:
    :return:
    """

    # The course context assertion happens in the sync function

    # Create or update assignment
    message, success = assignment_sync(assignment)

    # If there was an error, pass it back
    if not success:
        return error_response(message), 406

    # Return
    return success_response(message)
