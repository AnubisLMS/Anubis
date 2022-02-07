from flask import Blueprint

from anubis.models import Course
from anubis.utils.http import req_assert
from anubis.utils.http.files import make_png_response
from anubis.utils.visuals.usage import get_usage_plot, get_usage_plot_playgrounds, get_usage_plot_active

visuals_ = Blueprint("public-visuals", __name__, url_prefix="/public/visuals")


@visuals_.route("/usage/playgrounds")
def public_visuals_usage_playgrounds():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_playgrounds()

    return make_png_response(blob)


@visuals_.route("/usage/<string:course_id>")
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

    return make_png_response(blob)


@visuals_.route("/usage/active")
def public_visuals_usage_active():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_active()

    return make_png_response(blob)


@visuals_.route("/usage/active-month")
def public_visuals_usage_active_month():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_active(30, 7)

    return make_png_response(blob)
