from flask import Blueprint
from sqlalchemy.exc import IntegrityError, DataError

from anubis.models import db, Assignment, AssignedStudentQuestion, AssignedQuestionResponse, User
from anubis.utils.auth import require_user, current_user
from anubis.utils.http.decorators import json_endpoint, load_from_id, json_response
from anubis.utils.http.https import success_response, error_response
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.lms.questions import get_assigned_questions


questions = Blueprint("public-questions", __name__, url_prefix="/public/questions")


@questions.route("/get/<string:id>")
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

    return success_response({
        "questions": get_assigned_questions(assignment.id, user.id)
    })


@questions.route("/save/<string:id>", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("response", str)])
def public_questions_save(id: str, response: str):
    """
    body = {
      response: str
    }

    :param id:
    :return:
    """
    user: User = current_user()

    assigned_question = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.id == id,
    ).first()

    if assigned_question is None:
        return error_response("Assigned question does not exist")

    if not user.is_superuser and assigned_question.owner_id != user.id:
        return error_response("Assigned question does not exist")

    if not isinstance(response, str):
        return error_response('response must be a string'), 400

    res = AssignedQuestionResponse(
        assigned_question_id=assigned_question.id,
        response=response
    )
    db.session.add(res)

    try:
        db.session.commit()
    except (IntegrityError, DataError):
        return error_response("Server was unable to save your response.")

    return success_response({
        "status": "Response Saved",
    })
