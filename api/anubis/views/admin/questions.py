import io
from datetime import datetime

import sqlalchemy.exc
from flask import Blueprint, send_file

from anubis.lms.courses import assert_course_context, assert_course_superuser
from anubis.lms.questions import (
    assign_questions,
    export_assignment_questions,
    export_assignment_question_history,
    get_all_questions,
    get_question_assignments,
    hard_reset_questions,
    reset_question_assignments,
)
from anubis.lms.assignments import clean_assignment_name
from anubis.models import User, AssignedStudentQuestion, Assignment, AssignmentQuestion, db
from anubis.utils.auth.http import require_admin
from anubis.utils.data import req_assert
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_endpoint, json_response

questions = Blueprint("admin-questions", __name__, url_prefix="/admin/questions")


@questions.route("/add/<string:assignment_id>")
@require_admin()
@json_response
def admin_questions_add_unique_code(assignment_id: str):
    """
    Add a new blank question to the assignment.

    :param assignment_id:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # If the assignment does not exist, then stop
    req_assert(assignment is not None, message="assignment does not exist")

    # Assert that the set course context matches the course of the assignment
    assert_course_context(assignment)

    # Create a new, blank question
    aq = AssignmentQuestion(
        assignment_id=assignment.id,
        pool=0,
        question="",
        solution="",
        code_question=False,
        code_language="",
        placeholder="",
    )

    # Add and commit the question
    db.session.add(aq)
    db.session.commit()

    # Return the status
    return success_response(
        {
            "status": "Question added",
        }
    )


@questions.route("/delete/<string:assignment_question_id>")
@require_admin()
@json_response
def admin_questions_delete_question_id(assignment_question_id: str):
    """
    Delete an assignment question

    :param assignment_question_id:
    :return:
    """

    # Get the assignment question
    assignment_question: AssignmentQuestion = AssignmentQuestion.query.filter(
        AssignmentQuestion.id == assignment_question_id,
    ).first()

    # Verify that the question exists
    req_assert(assignment_question is not None, message="question does not exist")

    # Assert that the set course context matches the course of the assignment
    assert_course_context(assignment_question)

    try:
        # Try to delete the question
        AssignmentQuestion.query.filter(
            AssignmentQuestion.id == assignment_question_id,
        ).delete()

        # Try to commit the delete
        db.session.commit()

    except sqlalchemy.exc.IntegrityError:
        # Rollback the commit
        db.session.rollback()

        # If this commit fails, then it is assigned to students
        return error_response("Question is already assigned to students. Reset assignments to delete.")

    # Return the status
    return success_response(
        {
            "status": "Question deleted",
            "variant": "warning",
        }
    )


@questions.route("/hard-reset/<string:assignment_id>")
@require_admin()
@json_response
def private_questions_hard_reset_unique_code(assignment_id: str):
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

    :param assignment_id:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # If the assignment does not exist, then stop
    req_assert(assignment is not None, message="assignment does not exist")

    # Assert that the current user is a professor or superuser
    assert_course_superuser(assignment.course_id)

    # Assert that the set course context matches the course of the assignment
    assert_course_context(assignment)

    # Hard reset questions
    hard_reset_questions(assignment)

    # Pass back the status
    return success_response(
        {
            "status": "Questions hard reset",
            "variant": "warning",
        }
    )


@questions.route("/reset-assignments/<string:assignment_id>")
@require_admin()
@json_response
def private_questions_reset_assignments_assignment_id(assignment_id: str):
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

    :param assignment_id:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # Verify that the assignment exists
    req_assert(assignment is not None, message="assignment does not exist")

    # Assert that the current user is a professor or superuser
    assert_course_superuser(assignment.course_id)

    # Assert that the set course context matches the course of the assignment
    assert_course_context(assignment)

    # Reset the question assignments
    reset_question_assignments(assignment, commit=True)

    # Pass back the status
    return success_response(
        {
            "status": "Questions assignments reset",
            "variant": "warning",
        }
    )


@questions.route("/update/<string:assignment_question_id>", methods=["POST"])
@require_admin()
@json_endpoint(required_fields=[("question", dict)])
def admin_questions_update(assignment_question_id: str, question: dict):
    """
    Update the text for a question

    :param assignment_question_id:
    :param question:
    :return:
    """

    # Get the assignment question
    db_assignment_question: AssignmentQuestion = AssignmentQuestion.query.filter(
        AssignmentQuestion.id == assignment_question_id
    ).first()

    # Verify that the assignment question exists
    req_assert(db_assignment_question is not None, message="question does not exist")

    # Assert that the set course context matches the course of the assignment
    assert_course_context(db_assignment_question)

    # Update the fields of the question
    db_assignment_question.question = question["question"]
    db_assignment_question.solution = question["solution"]
    db_assignment_question.code_language = question["code_language"]
    db_assignment_question.code_question = question["code_question"]
    db_assignment_question.pool = question["pool"]

    # Commit any changes
    db.session.commit()

    # Pass back status
    return success_response({"status": "Question updated"})


@questions.route("/get-assignments/<string:assignment_id>")
@require_admin()
@json_response
def private_questions_get_assignments_unique_code(assignment_id: str):
    """
    Get all questions for the given assignment.

    :param assignment_id:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # If the assignment does not exist, then stop
    req_assert(assignment is not None, message="assignment does not exist")

    # Assert that the assignment is within the course context
    assert_course_context(assignment)

    # Get all the question assignments
    question_assignments = get_question_assignments(assignment)

    return success_response(
        {
            "assignments": question_assignments,
        }
    )


@questions.route("/get/<string:assignment_id>")
@require_admin()
@json_response
def private_questions_get_unique_code(assignment_id: str):
    """
    Get all questions for the given assignment.

    :param assignment_id:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # Verify that the assignment exists
    req_assert(assignment is not None, message="assignment does not exist")

    # Assert that the assignment is within the course context
    assert_course_context(assignment)

    assigned_question_count = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.assignment_id == assignment.id
    ).count()

    return success_response(
        {
            "assignment_name": assignment.name,
            "questions": get_all_questions(assignment),
            "questions_assigned": assignment.questions_assigned,
            "assigned_question_count": assigned_question_count,
        }
    )


@questions.route("/assign/<string:assignment_id>")
@require_admin()
@json_response
def private_questions_assign_unique_code(assignment_id: str):
    """
    Assign questions that have been created. This action will only run once.
    Once a question is assigned to a student, the only way to change it is
    by manually editing the database. This is by design to reduce confusion.

    Questions must already be created to use this.

    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # Verify that we got an assignment
    req_assert(assignment is not None, message="assignment does not exist")

    # Verify that the assignment is accessible to the user in the current course context
    assert_course_context(assignment)

    # Assign the questions
    assigned_questions = assign_questions(assignment)

    # Pass back the response
    return success_response({"assigned": assigned_questions, "status": "Questions assigned"})


@questions.get("/export/<string:assignment_id>")
@require_admin()
def admin_assignments_export(assignment_id: str):
    """
    Export question assignments to a (potentially) large zip archive.

    :param assignment_id:
    :return:
    """

    # Get the assignment
    assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # Verify that we got an assignment
    req_assert(assignment is not None, message="assignment does not exist")

    # Verify that the assignment is accessible to the user in the current course context
    assert_course_context(assignment)

    # Get now datetime
    now = datetime.now().replace(microsecond=0)

    # Generate an export of the assignment data
    zip_blob = export_assignment_questions(assignment.id)

    # Get a filename from the assignment name and datetime
    assignment_name = clean_assignment_name(assignment)
    filename = f"anubis-question-assignments-{assignment_name}-{str(now)}.zip".replace(" ", "_").replace(":", "")

    # Send the file back
    return send_file(io.BytesIO(zip_blob), attachment_filename=filename, as_attachment=True)


@questions.get("/history/<string:assignment_id>/<string:user_id>")
@require_admin()
def admin_assignments_history(assignment_id: str, user_id: str):
    """
    Export question response history to a (potentially) large json file
    for a specific student.

    :param assignment_id:
    :param user_id:
    :return:
    """

    # Get the assignment & user
    assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    user = User.query.filter(User.id == user_id).first()

    # Verify that we got an assignment
    req_assert(assignment is not None, message="assignment does not exist")
    req_assert(user is not None, message="user does not exist")

    # Verify that the assignment is accessible to the user in the current course context
    assert_course_context(assignment, user)

    # Get now datetime
    now = datetime.now().replace(microsecond=0)

    # Generate an export of the assignment data
    history_json = export_assignment_question_history(assignment.id, user.id) or '{}'

    # Get a filename from the assignment name and datetime
    assignment_name = clean_assignment_name(assignment)
    filename = f"anubis-question-responses-{user.netid}-{assignment_name}-{str(now)}.json".replace(" ", "_").replace(":", "")

    # Send the file back
    return send_file(io.BytesIO(history_json.encode()), attachment_filename=filename, as_attachment=True)
