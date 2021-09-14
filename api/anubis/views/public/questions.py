from datetime import datetime

from flask import Blueprint
from sqlalchemy.exc import IntegrityError, DataError

from anubis.models import db, Assignment, AssignedStudentQuestion, AssignedQuestionResponse
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http.decorators import json_endpoint, load_from_id, json_response
from anubis.utils.http import error_response, success_response
from anubis.utils.lms.assignments import get_assignment_due_date
from anubis.utils.lms.courses import is_course_admin
from anubis.utils.lms.questions import get_assigned_questions

questions = Blueprint("public-questions", __name__, url_prefix="/public/questions")


@questions.route("/get/<string:id>")
@require_user()
@load_from_id(Assignment, verify_owner=False)
@json_response
def public_assignment_questions_id(assignment: Assignment):
    """
    Get assigned questions for the current user for a given assignment.

    :param assignment:
    :return:
    """

    return success_response({
        "questions": get_assigned_questions(assignment.id, current_user.id)
    })


@questions.route("/save/<assignment_question_id>", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("response", str)])
def public_questions_save(assignment_question_id: str, response: str):
    """
    Save the response for an assigned question.

    body = {
      response: str
    }

    :param assignment_question_id:
    :param response:
    :return:
    """

    # Try to find the assigned question
    assigned_question = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.id == assignment_question_id,
    ).first()

    # Verify that the assigned question they are attempting to update
    # actually exists
    req_assert(assigned_question is not None, message='assigned question does not exist')

    # Check that the person that the assigned question belongs to the
    # user. If the current user is a course admin (TA, Professor or superuser)
    # then we can skip this check.
    if not is_course_admin(assigned_question.assignment.course_id, current_user.id):
        req_assert(
            assigned_question.owner_id == current_user.id,
            message='assigned question does not exist'
        )

    # Verify that the response is a string object
    req_assert(isinstance(response, str), message='response must be a string')

    # Get the assignment that this question exists for
    assignment = assigned_question.assignment

    # If the assignment is set to not accept late submissions,
    # then we need to do a quick check to make sure they are submitting
    # on time.
    if not assignment.accept_late:
        # Calculate now
        now = datetime.now()

        # Calculate the assignment due date for this student
        due_date = get_assignment_due_date(current_user.id, assignment.id)

        # Make sure that the deadline has not passed. If it has, then
        # we should give them an error saying that they can request a
        # regrade from the Professor.
        req_assert(
            now < due_date,
            message='This assignment does not accept late submissions.'
        )

    # Create a new response
    res = AssignedQuestionResponse(
        assigned_question_id=assigned_question.id,
        response=response
    )

    # Add the response to the session
    db.session.add(res)

    try:
        # Try to commit the response
        db.session.commit()
    except (IntegrityError, DataError):
        # If the response they gave was too long then a DataError will
        # be raised. The max length for the mariadb TEXT type is something
        # like 2^16 characters. If they hit this limit, then they are doing
        # something wrong.
        return error_response("Server was unable to save your response.")

    return success_response({
        "status": "Response Saved",
        "response": res.data,
    })
