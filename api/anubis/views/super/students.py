from flask import Blueprint

from anubis.lms.students import get_students
from anubis.models import User, db
from anubis.utils.auth.http import require_superuser
from anubis.utils.data import req_assert
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response

students_ = Blueprint("super-students", __name__, url_prefix="/super/students")


@students_.route("/list")
@require_superuser()
@json_response
def super_students_list():
    """
    list all users within the current course context

    :return:
    """

    # Get all students
    students = get_students(None)

    # Pass back the students
    return success_response({"students": students})


@students_.route("/toggle-superuser/<string:id>")
@require_superuser()
@json_response
def super_students_toggle_superuser(id: str):
    """
    Toggle the superuser status for a user. Requires user to be superuser
    to be able to make this change.

    :param id:
    :return:
    """

    # Get the other user
    other = User.query.filter(User.id == id).first()

    # If the other user was not found, then stop
    req_assert(other is not None, message="user does not exist")

    # Toggle the superuser field
    other.is_superuser = not other.is_superuser

    # Commit the change
    db.session.commit()

    # Pass back the status based on if the other is now a superuser
    if other.is_superuser:
        return success_response({"status": f"{other.name} is now a superuser", "variant": "warning"})

    # Pass back the status based on if the other user is now no longer a superuser
    else:
        return success_response({"status": f"{other.name} is no longer a superuser", "variant": "success"})


@students_.route("/toggle-anubis_developer/<string:id>")
@require_superuser()
@json_response
def super_students_toggle_anubis_developer(id: str):
    """
    Toggle the superuser status for a user. Requires user to be superuser
    to be able to make this change.

    :param id:
    :return:
    """

    # Get the other user
    other: User = User.query.filter(User.id == id).first()

    # If the other user was not found, then stop
    req_assert(other is not None, message="user does not exist")

    # Toggle the superuser field
    other.is_anubis_developer = not other.is_anubis_developer

    # Commit the change
    db.session.commit()

    # Pass back the status based on if the other is now a superuser
    if other.is_anubis_developer:
        return success_response({"status": f"{other.name} is now an anubis developer", "variant": "warning"})

    # Pass back the status based on if the other user is now no longer a superuser
    else:
        return success_response({"status": f"{other.name} is no longer an anubis developer", "variant": "success"})
