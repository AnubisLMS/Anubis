from datetime import datetime

from flask import Blueprint
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.sql import func

from anubis.lms.assignments import get_assignment_due_date
from anubis.lms.questions import get_assigned_questions
from anubis.models import AssignedQuestionResponse, AssignedStudentQuestion, Assignment, db
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_endpoint, json_response, load_from_id, verify_data_shape

questions_ = Blueprint("public-questions", __name__, url_prefix="/public/questions")


@questions_.route("/get/<string:id>")
@require_user()
@load_from_id(Assignment, verify_owner=False)
@json_response
def public_assignment_questions_id(assignment: Assignment):
    """
    Get assigned questions for the current user for a given assignment.

    :param assignment:
    :return:
    """

    return success_response({"questions": get_assigned_questions(assignment.id, current_user.id)})


@questions_.route("/save/<assignment_id>", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("questions", list)])
def public_questions_save(assignment_id: str, questions: list):
    """
    Save the response for an assigned question.

    body = {
      response: str
    }

    :param questions:
    :return:
    """

    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id
    ).first()
    req_assert(assignment, message='Assignment does not exist')

    # If the assignment is set to not accept late submissions,
    # then we need to do a quick check to make sure they are submitting
    # on time.
    if not assignment.accept_late:
        # Calculate now
        now = datetime.now()

        # Calculate the assignment due date for this student
        due_date = get_assignment_due_date(current_user.id, assignment.id, grace=True)

        # Make sure that the deadline has not passed. If it has, then
        # we should give them an error saying that they can request a
        # regrade from the Professor.
        req_assert(now < due_date, message="This assignment does not accept late submissions.")

    req_assert(len(questions) > 0, message='Provide at least one question response.')

    print(questions)
    shape_good, shape_error = verify_data_shape(questions, [{"question": dict, "response": dict, "id": str}])
    req_assert(shape_good, message=shape_error)

    assigned_questions: list[AssignedStudentQuestion] = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.owner_id == current_user.id,
        AssignedStudentQuestion.assignment_id == assignment.id,
    ).all()

    last_responses: list[AssignedQuestionResponse] = AssignedQuestionResponse.query.filter(
        AssignedQuestionResponse.assigned_question_id.in_([
            assigned_question.id for assigned_question in assigned_questions
        ]),
    ).group_by(AssignedQuestionResponse.assigned_question_id, AssignedQuestionResponse.id) \
        .having(func.max(AssignedQuestionResponse.created)).all()

    req_assert(len(assigned_questions) > 0, message='No questions assigned')

    for question in questions:
        assignment_question_id = question['id']
        response = question['response'].get('text', '')

        # Skip if there is no response data
        if not response:
            continue

        # Try to find the assigned question
        for _assigned_question in assigned_questions:
            if _assigned_question.id == assignment_question_id:
                assigned_question = _assigned_question
                break
        else:
            continue

        # Verify that the response is a string object
        req_assert(isinstance(response, str), message="response must be a string")

        # Skip creating a new response if it matches the last one
        skip = False
        for last_response in last_responses:
            if last_response.assigned_question_id == assignment_question_id:
                if last_response.response == response:
                    skip = True
                    break
        if skip:
            continue

        # Create a new response
        res = AssignedQuestionResponse(assigned_question_id=assigned_question.id, response=response)

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
        "questions": get_assigned_questions(assignment_id, current_user.id),
        "status": "Response Saved",
    })
