from flask import Blueprint, request

from anubis.models import LectureNotes
from anubis.utils.auth import require_user, current_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response
from anubis.utils.lms.lectures import get_lecture_notes

lectures_ = Blueprint('public-lectures', __name__, url_prefix='/public/lectures')


@lectures_.get("/list")
@require_user()
@json_response
def public_static_lectures_list():
    """
    List all lecture notes for the course

    /public/lectures/list

    :return:
    """

    # Get optional class filter from get query
    course_id = request.args.get("courseId", default=None)

    # Get all public static files within this course
    lectures_data = get_lecture_notes(current_user.id, course_id)

    # Pass back the list of files
    return success_response({
        "lectures": lectures_data
    })
