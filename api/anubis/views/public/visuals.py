from flask import Blueprint

from anubis.models import Course
from anubis.utils.http import req_assert
from anubis.utils.http.files import make_png_response
from anubis.utils.visuals.usage import get_usage_plot, get_usage_plot_playgrounds, get_usage_plot_active
from anubis.utils.visuals.users import get_platform_users_plot

visuals_ = Blueprint("public-visuals", __name__, url_prefix="/public/visuals")


@visuals_.route("/playgrounds")
def public_visuals_usage_playgrounds():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_playgrounds()

    return make_png_response(blob)


@visuals_.route("/course/<string:course_id>")
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


@visuals_.route("/active/14/1")
def public_visuals_usage_active_14_1():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_active(days=14, step=1)

    return make_png_response(blob)


@visuals_.route("/active/180/1")
def public_visuals_usage_active_180_1():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_active(days=180, step=1)

    return make_png_response(blob)


@visuals_.route("/active/90/7")
def public_visuals_usage_active_90_7():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_active(days=90, step=7)

    return make_png_response(blob)


@visuals_.route("/active/365/30")
def public_visuals_usage_active_365_30():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot_active(days=365, step=30)

    return make_png_response(blob)


@visuals_.route("/users/365/1")
def public_visuals_users_365_1():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_platform_users_plot(days=365, step=1)

    return make_png_response(blob)


@visuals_.route("/users/365/30")
def public_visuals_users_365_30():
    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_platform_users_plot(days=365, step=30)

    return make_png_response(blob)
