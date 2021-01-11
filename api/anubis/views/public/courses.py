from flask import Blueprint

from anubis.models import User
from anubis.utils.assignments import get_courses
from anubis.utils.auth import require_user, current_user
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response

courses = Blueprint("public-courses", __name__, url_prefix="/public/courses")


@courses.route("/")
@require_user
@log_endpoint("public-classes")
@json_response
def public_classes():
    """
    Get class data for current user

    :return:
    """
    user: User = current_user()
    return success_response({"classes": get_courses(user.netid)})
