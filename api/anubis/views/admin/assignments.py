import json
from datetime import datetime, timedelta

import parse
from dateutil.parser import parse as dateparse
from flask import Blueprint
from sqlalchemy.exc import DataError, IntegrityError

from anubis.github.repos import delete_assignment_repo
from anubis.lms.assignments import assignment_sync, delete_assignment, delete_assignment_repos, get_assignment_tests
from anubis.lms.courses import assert_course_context, course_context, is_course_superuser
from anubis.lms.questions import get_assigned_questions
from anubis.lms.shell_autograde import (
    verify_shell_autograde_exercise_path_allowed,
    verify_shell_exercise_repo_allowed,
    verify_shell_exercise_repo_format,
    autograde_shell_assignment_sync,
)
from anubis.lms.repos import list_repos_with_latest_commit
from anubis.models import Assignment, AssignmentRepo, AssignmentTest, SubmissionTestResult, User, db
from anubis.rpc.enqueue import enqueue_make_shared_assignment, enqueue_recalculate_late
from anubis.utils.auth.http import require_admin
from anubis.utils.auth.user import current_user
from anubis.utils.data import rand, req_assert, row2dict
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_endpoint, json_response, load_from_id
from anubis.utils.logging import logger

assignments = Blueprint("admin-assignments", __name__, url_prefix="/admin/assignments")


@assignments.post("/shared/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_endpoint([("groups", list)])
def admin_assignments_shared_id(assignment: Assignment, groups: list[list[str]], **__):
    """
    Make a shared assignment

    groups = [
      [netid1, netid2],
      [netid3],
      [netid4, netid5]
    ]

    :param assignment:
    :param groups:
    :return:
    """

    assert_course_context(assignment)

    enqueue_make_shared_assignment(assignment.id, groups)

    return success_response(
        {
            "assignment": assignment.full_data,
            "status":     "Group assignments enqueued",
        }
    )


@assignments.delete("/reset-repos/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
def admin_assignments_reset_repos_id(assignment: Assignment):
    """
    Fully reset an assignment. Delete all repos, submissions, etc...

    :param assignment:
    :return:
    """

    assert_course_context(assignment)

    delete_assignment_repos(assignment)
    db.session.commit()

    return success_response(
        {
            "assignment": assignment.full_data,
            "status":     "Repos reset",
            "variant":    "warning",
        }
    )


@assignments.get("/repos/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_response
def admin_assignments_repos_id(assignment: Assignment):
    """

    :param assignment:
    :return:
    """

    assert_course_context(assignment)

    repos = list_repos_with_latest_commit(assignment.id)

    def get_ssh_url(url):
        r = parse.parse("https://github.com/{}", url)
        path = r[0]
        path = path.removesuffix(".git")
        return f"git@github.com:{path}.git"

    return success_response(
        {
            "assignment": assignment.full_data,
            "repos":      [
                {
                    "id":     repo.id,
                    "url":    repo.repo_url,
                    "ssh":    get_ssh_url(repo.repo_url),
                    "netid":  repo.netid,
                    "name":   repo.owner_name if repo.owner_id is not None else "N/A",
                    "commit": repo.commit,
                }
                for repo in repos
            ],
        }
    )


@assignments.delete("/repo/<string:id>")
@require_admin()
@load_from_id(AssignmentRepo, verify_owner=False)
@json_response
def admin_assignments_repo_delete_id(assignment_repo: AssignmentRepo):
    """

    :param assignment_repo:
    :return:
    """

    # list of repos to delete
    repos: list[AssignmentRepo] = [assignment_repo]

    # If the assignment repo is shared
    if assignment_repo.shared:
        # Then we need to collect all the other repos, and delete those too
        repos = AssignmentRepo.query.filter(
            AssignmentRepo.repo_url == assignment_repo.repo_url,
        ).all()

    for repo in repos:
        # Get user
        user: User = repo.owner

        # Delete the assignment user
        delete_assignment_repo(user, repo.assignment)

    return success_response({"status": "Assignment repo deleted", "variant": "warning"})


@assignments.route("/assignment/<string:id>/questions/get/<string:netid>")
@require_admin()
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

    # Verify that the user exists, and that the assignment
    # is within the course context of the current user.
    req_assert(user is not None, message="user not found")
    assert_course_context(assignment)

    return success_response(
        {
            "netid":     user.netid,
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

    # Confirm that the assignment they are asking for is part
    # of this course
    assert_course_context(assignment)

    assignment_data = row2dict(assignment)

    if assignment.theia_image_id is not None:
        assignment_data["theia_image"] = assignment.theia_image.data
    else:
        assignment_data["theia_image"] = None

    # Pass back the full data
    return success_response(
        {
            "assignment": assignment_data,
            "tests":      get_assignment_tests(assignment, visible_only=False),
        }
    )


@assignments.delete("/delete/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_response
def admin_assignments_delete_id(assignment: Assignment):
    """
    Get the full data for an assignment id. The course context
    must be set, and will be checked.

    :param assignment:
    :return:
    """

    # Confirm that the assignment they are asking for is part
    # of this course
    assert_course_context(assignment)

    # Make sure they are allowed to delete this assignment
    if not is_course_superuser(course_context.id, current_user.id):
        return error_response("You must be a professor or a superuser to delete this assignment")

    # Delete the assignment
    delete_assignment(assignment)

    # Pass back the full data
    return success_response(
        {
            "status":  "Assignment deleted",
            "variant": "warning",
        }
    )


@assignments.route("/list")
@require_admin()
@json_response
def admin_assignments_list():
    """
    list all assignments within the course context.

    * The response will be the row2dict of the assignment, not a data prop *

    :return:
    """

    # Get all the assignment objects within the course context,
    # sorted by the due date.
    all_assignments = (
        Assignment.query.filter(Assignment.course_id == course_context.id).order_by(Assignment.due_date.desc()).all()
    )

    # Pass back the row2dict of each assignment object
    return success_response({"assignments": [row2dict(assignment) for assignment in all_assignments]})


@assignments.route("/tests/toggle-hide/<string:assignment_test_id>")
@require_admin()
@json_response
def admin_assignment_tests_toggle_hide_assignment_test_id(assignment_test_id: str):
    """
    Toggle an assignment test being hidden.

    :param assignment_test_id:
    :return:
    """

    # Pull the assignment test
    assignment_test: AssignmentTest = AssignmentTest.query.filter(
        AssignmentTest.id == assignment_test_id,
    ).first()

    # Make sure the assignment test exists
    req_assert(assignment_test is not None, message="test not found")

    # Verify that course the assignment test is apart of and
    # the course context match
    assert_course_context(assignment_test)

    # Toggle the hidden field
    assignment_test.hidden = not assignment_test.hidden

    # Commit the change
    db.session.commit()

    return success_response({"status": "test updated", "assignment_test": assignment_test.data})


@assignments.route("/tests/delete/<string:assignment_test_id>")
@require_admin()
@json_response
def admin_assignment_tests_delete_assignment_test_id(assignment_test_id: str):
    """
    Delete an assignment test.

    :param assignment_test_id:
    :return:
    """

    # Pull the assignment test
    assignment_test = AssignmentTest.query.filter(
        AssignmentTest.id == assignment_test_id,
    ).first()

    # Make sure the assignment test exists
    req_assert(assignment_test is not None, message="test not found")

    # Verify that course the assignment test is apart of and
    # the course context match
    assert_course_context(assignment_test)

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
    return success_response(
        {
            "status":  f"{test_name} deleted",
            "variant": "warning",
        }
    )


@assignments.post("/add")
@require_admin()
@json_response
def admin_assignments_add():
    new_assignment = Assignment(
        course_id=course_context.id,
        name="New Assignment",
        description="",
        hidden=True,
        autograde_enabled=False,
        github_repo_required=course_context.github_repo_required,
        ide_enabled=True,
        theia_image=course_context.theia_default_image,
        theia_options=course_context.theia_default_options,
        release_date=datetime.now() + timedelta(weeks=1),
        due_date=datetime.now() + timedelta(weeks=2),
        grace_date=datetime.now() + timedelta(weeks=2),
    )
    db.session.add(new_assignment)
    db.session.commit()

    return success_response(
        {
            "status":     "New assignment created.",
            "assignment": new_assignment.data,
        }
    )


@assignments.post("/save")
@require_admin()
@json_endpoint(required_fields=[("assignment", dict)])
def admin_assignments_save(assignment: dict):
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

    assert_course_context(db_assignment)

    # Update all it's fields
    for key, value in assignment.items():

        # If the key is a date, then convert to datetime
        if "date" in key and isinstance(value, str):
            value = dateparse(value.replace("T", " ").replace("Z", "")).replace(microsecond=0)

        # If github.com is in what the user gave, remove it
        if key in {"github_template", "shell_assignment_repo"} and value.startswith("https://github.com/"):
            value = value.removeprefix('https://github.com/')

        if key == "theia_image":
            if value is not None:
                db_assignment.theia_image_id = value["id"]
            else:
                db_assignment.theia_image_id = None
            continue

        if key == "theia_image_id":
            continue

        setattr(db_assignment, key, value)

    # Verify basics
    req_assert(
        verify_shell_exercise_repo_format(db_assignment),
        message='Shell Assignment Repo is in invalid form. Please use form "<github org>/<github repo>"'
    )
    req_assert(
        verify_shell_exercise_repo_allowed(db_assignment),
        message='Shell Assignment Repo is in not in a valid github organization/user. Please reach out to support'
    )
    req_assert(
        verify_shell_autograde_exercise_path_allowed(db_assignment),
        message='Shell Assignment Repo Path is in invalid form. Please use form "<subdirectory>/exercise.py"'
    )

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
@require_admin(unless_debug=True)
@json_endpoint(required_fields=[("assignment", dict)])
def private_assignment_sync(assignment: dict):
    """
    Sync assignment data from the CLI. This should be used to create and update assignment data.

    body = {
      "assignment": {
        "name": "{name}",
        "course": "CS-UY 3224",
        "unique_code": "{code}",
        "pipeline_image": "registry.digitalocean.com/anubis/assignment/{code}"
      }
    }

    response = {
      assignment : {...},
    }

    :return:
    """

    # The course context assertion happens in the sync function

    # Create or update assignment
    message, success = assignment_sync(assignment)

    # If there was an error, pass it back
    req_assert(success, message=message, status_code=406)

    # Return
    return success_response(message)


@assignments.get("/shell/sync/<string:id>")
@require_admin(unless_debug=True)
@json_response
@load_from_id(Assignment)
def admin_assignments_shell_sync(assignment: Assignment):
    """
    :return:
    """

    autograde_shell_assignment_sync(assignment)

    # Return
    return success_response({
        'status': 'Exercises synced. See "Edit Tests" page to see current tests.'
    })


@assignments.get("/recalculate-late/<string:id>")
@require_admin(unless_debug=True)
@json_response
@load_from_id(Assignment)
def admin_recalculate_late(assignment: Assignment):
    """
    :return:
    """

    enqueue_recalculate_late(assignment.id)

    # Return
    return success_response({
        'status': 'Enqueued recalculate'
    })
