from typing import List

from flask import Blueprint

from anubis.lms.courses import assert_course_context, assert_course_superuser, course_context
from anubis.lms.repos import get_repos
from anubis.lms.students import get_students
from anubis.lms.theia import get_recent_sessions
from anubis.models import Assignment, Course, InCourse, Submission, User, db
from anubis.utils.auth.http import require_admin, require_superuser
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http import get_number_arg, success_response
from anubis.utils.http.decorators import json_endpoint, json_response

students_ = Blueprint("super-students", __name__, url_prefix="/super/students")


@students_.route("/list")
@require_superuser()
@json_response
def admin_students_list():
    """
    List all users within the current course context

    :return:
    """

    # Get all students
    students = [s.data for s in User.query.all()]

    # Pass back the students
    return success_response({"students": students})
