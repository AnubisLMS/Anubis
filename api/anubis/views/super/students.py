from flask import Blueprint

from flask import Blueprint

from anubis.lms.students import get_students
from anubis.utils.auth.http import require_superuser
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response

students_ = Blueprint("super-students", __name__, url_prefix="/super/students")


@students_.route("/list")
@require_superuser()
@json_response
def super_students_list():
    """
    List all users within the current course context

    :return:
    """

    # Get all students
    students = get_students(None)

    # Pass back the students
    return success_response({"students": students})
