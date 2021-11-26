from flask import Blueprint, make_response

from anubis.models import Course
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.http import req_assert
from anubis.utils.visuals.usage import get_usage_plot

visuals = Blueprint("public-visuals", __name__, url_prefix="/public/visuals")


@visuals.route("/usage/<string:course_id>")
@cache.cached(timeout=360, unless=is_debug)
def public_visuals_usage(course_id: str):
    """
    Get the usage png graph. This endpoint is heavily
    cached.

    :param course_id:
    :return:
    """

    # Get the course
    course: Course = Course.query.filter(Course.id == course_id).first()

    # Confirm that the course exists
    req_assert(course is not None, message="Course does not exist")

    # Confirm that the course has visuals enabled
    req_assert(course.display_visuals, message="Course does not support usage visuals")

    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot(course.id)

    # Take the png bytes, and make a flask response
    response = make_response(blob)

    # Set the response content type
    response.headers["Content-Type"] = "image/png"

    # Pass back the image response
    return response
