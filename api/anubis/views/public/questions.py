from datetime import datetime

from flask import Blueprint
from sqlalchemy.exc import IntegrityError, DataError

from anubis.models import db, Assignment, AssignedStudentQuestion, AssignedQuestionResponse, User
from anubis.utils.data import req_assert
from anubis.utils.auth import require_user, current_user
from anubis.utils.http.decorators import json_endpoint, load_from_id, json_response
from anubis.utils.http.https import success_response, error_response
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
    # Load current user
    user: User = current_user()

    return success_response({
        "questions": get_assigned_questions(assignment.id, user.id)
    })


@questions.route("/save/<string:id>", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("response", str)])
def public_questions_save(id: str, response: str):
    """
    Save the response for an assigned question.

    body = {
      response: str
    }

    :param id:
    :return:
    """

    # Get the current user
    user: User = current_user()

    # Try to find the assigned question
    assigned_question = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.id == id,
    ).first()

    # Verify that the assigned question they are attempting to update
    # actually exists
    req_assert(assigned_question is not None, message='assigned question does not exist')

    # Check that the person that the assigned question belongs to the
    # user. If the current user is a course admin (TA, Professor or superuser)
    # then we can skip this check.
    req_assert(
        is_course_admin(user.id) or assigned_question.owner_id != user.id,
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
        due_date = get_assignment_due_date(user, assignment)

        # Make sure that the deadline has not passed. If it has, then
        # we should give them an error saying that they can request a
        # regrade from the Professor.
        req_assert(
            now < due_date,
            message='This assignment does not accept late submissions. You can request an extension from your Professor.'
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
