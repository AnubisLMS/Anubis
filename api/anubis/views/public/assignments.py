from flask import Blueprint, request

from anubis.models import User, Assignment, AssignedStudentQuestion, db
from anubis.utils.lms.assignments import get_assignments
from anubis.utils.users.auth import current_user, require_user
from anubis.utils.http.decorators import json_response, load_from_id, json_endpoint
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.http.https import success_response
from anubis.utils.lms.questions import get_assigned_questions

assignments = Blueprint(
    "public-assignments", __name__, url_prefix="/public/assignments"
)


@assignments.route("/")
@require_user()
@log_endpoint("public-assignments")
@json_response
def public_assignments():
    """
    Get all the assignments for a user. Optionally specify a class
    name as a get query.

    /api/public/assignments?class=Intro to OS

    :return: { "assignments": [ assignment.data ] }
    """

    # Get optional class filter from get query
    course_id = request.args.get("courseId", default=None)

    # Load current user
    user: User = current_user()

    # Get (possibly cached) assignment data
    assignment_data = get_assignments(user.netid, course_id)

    # Iterate over assignments, getting their data
    return success_response({"assignments": assignment_data})


@assignments.route("/questions/get/<string:id>")
@require_user()
@log_endpoint("public-questions-get", lambda: "get questions")
@load_from_id(Assignment, verify_owner=False)
@json_response
def public_assignment_questions_id(assignment: Assignment):
    """
    Get assigned questions for the current user for a given assignment.

    :param assignment:
    :return:
    """
    # Load current user
    user: User = current_user()

    return success_response(
        {"questions": get_assigned_questions(assignment.id, user.id)}
    )


@assignments.route("/questions/save/<string:id>")
@require_user()
@log_endpoint("public-questions-save", lambda: "save questions")
@load_from_id(AssignedStudentQuestion, verify_owner=True)
@json_endpoint(required_fields=[("response", str)])
def public_assignment_questions_save_id(
        assigned_question: AssignedStudentQuestion, response: str, **kwargs
):
    """
    Save response for a given assignment question

    :param assigned_question:
    :param response:
    :param kwargs:
    :return:
    """
    assigned_question.response = response

    db.session.add(assigned_question)
    db.session.commit()

    return success_response("Success")
