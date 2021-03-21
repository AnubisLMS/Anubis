import sqlalchemy.exc
from flask import Blueprint

from anubis.models import db, Assignment, AssignmentQuestion, AssignedStudentQuestion
from anubis.utils.auth import require_admin
from anubis.utils.decorators import json_response, json_endpoint
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import error_response, success_response
from anubis.utils.questions import (
    hard_reset_questions,
    get_all_questions,
    assign_questions,
)

questions = Blueprint("admin-questions", __name__, url_prefix="/admin/questions")


@questions.route("/add/<string:unique_code>")
@require_admin()
@log_endpoint("admin", lambda: "add new question")
@json_response
def private_questions_add_unique_code(unique_code: str):
    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response("Unable to find assignment"), 400

    aq = AssignmentQuestion(
        assignment_id=assignment.id,
        sequence=0,
        question='',
        solution='',
        code_question=False,
        code_language='',
        placeholder='',
    )
    db.session.add(aq)
    db.session.commit()

    return success_response({
        "status": "Question added",
    })


@questions.route("/delete/<string:assignment_question_id>")
@require_admin()
@log_endpoint("admin", lambda: "delete question")
@json_response
def private_questions_del(assignment_question_id: str):
    aq = AssignmentQuestion.query.filter(
        AssignmentQuestion.id == assignment_question_id,
    ).first()
    if aq is None:
        return error_response('Could not find question'), 400

    try:
        AssignmentQuestion.query.filter(
            AssignmentQuestion.id == assignment_question_id,
        ).delete()
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return error_response('Question is already assigned to students. Reset assignments to delete.')

    return success_response({
        "status": "Question deleted",
        'variant': 'warning',
    })


@questions.route("/hard-reset/<string:unique_code>")
@require_admin()
@log_endpoint("admin", lambda: "question hard reset")
@json_response
def private_questions_hard_reset_unique_code(unique_code: str):
    """
    This endpoint should be used very sparingly. When this is hit,
    assuming the assignment exists, it will delete all questions
    for the given assignment. This is potentially very destructive,
    because you will not be able to get the question assignments
    back without a database backup.

    * If you chose to use this half way into an assignment without
    being able to reset, you will need to assign new questions to
    students! *

    If you end up needing to re-assign questions, this has the
    potential to create a great deal of confusion among students.

    ** Be careful with this one **

    :param unique_code:
    :return:
    """
    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response("Unable to find assignment")

    # Hard reset questions
    hard_reset_questions(assignment)

    return success_response({
        "status": "Questions hard reset",
        'variant': 'warning',
    })


@questions.route("/reset-assignments/<string:unique_code>")
@require_admin()
@log_endpoint("admin", lambda: "reset question assignments")
@json_response
def private_questions_reset_assignments_unique_code(unique_code: str):
    """
    This endpoint should be used very sparingly. When this is hit,
    assuming the assignment exists, it will delete all questions
    for the given assignment. This is potentially very destructive,
    because you will not be able to get the question assignments
    back without a database backup.

    * If you chose to use this half way into an assignment without
    being able to reset, you will need to assign new questions to
    students! *

    If you end up needing to re-assign questions, this has the
    potential to create a great deal of confusion among students.

    ** Be careful with this one **

    :param unique_code:
    :return:
    """
    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response("Unable to find assignment")

    AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.assignment_id == assignment.id
    ).delete()
    db.session.commit()

    return success_response({
        "status": "Questions assignments reset",
        'variant': 'warning',
    })


@questions.route("/update/<string:assignment_question_id>", methods=["POST"])
@require_admin()
@log_endpoint("admin", lambda: "question update")
@json_endpoint(required_fields=[('question', dict)])
def admin_questions_update(assignment_question_id: str, question: dict):
    """
    Update the text for a question

    :param assignment_question_id:
    :param question:
    :return:
    """

    db_assignment_question = AssignmentQuestion.query.filter(
        AssignmentQuestion.id == assignment_question_id
    ).first()
    db_assignment_question: AssignmentQuestion

    if db_assignment_question is None:
        return error_response('question not found')

    db_assignment_question.question = question['question']
    db_assignment_question.solution = question['solution']
    db_assignment_question.code_language = question['code_language']
    db_assignment_question.code_question = question['code_question']
    db_assignment_question.sequence = question['sequence']

    db.session.commit()

    return success_response({
        'status': 'Question updated'
    })


@questions.route("/get/<string:unique_code>")
@require_admin()
@log_endpoint("admin", lambda: "questions get")
@json_response
def private_questions_get_unique_code(unique_code: str):
    """
    Get all questions for the given assignment.

    :param unique_code:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response("Unable to find assignment")

    assignment_questions = AssignmentQuestion.query.filter(
        AssignmentQuestion.assignment_id == assignment.id,
    ).order_by(AssignmentQuestion.sequence, AssignmentQuestion.created.desc()).all()

    return success_response({
        'questions': [
            assignment_question.full_data
            for assignment_question in assignment_questions
        ]
    })


@questions.route("/get-assignments/<string:unique_code>")
@require_admin()
@log_endpoint("admin", lambda: "get question assignments")
@json_response
def private_questions_get_assignments_unique_code(unique_code: str):
    """
    Get all questions for the given assignment.

    :param unique_code:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response("Unable to find assignment")

    return success_response({
        'questions': get_all_questions(assignment)
    })


@questions.route("/assign/<string:unique_code>")
@require_admin()
@log_endpoint("admin", lambda: "question assign")
@json_response
def private_questions_assign_unique_code(unique_code: str):
    """
    Assign questions that have been created. This action will only run once.
    Once a question is assigned to a student, the only way to change it is
    by manually editing the database. This is by design to reduce confusion.

    Questions must already be created to use this.

    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response("Unable to find assignment")

    # Assign the questions
    assigned_questions = assign_questions(assignment)

    # Pass back the response
    return success_response({
        'assigned': assigned_questions,
        'status': 'Questions assigned'
    })
