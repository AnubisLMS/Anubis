from flask import Blueprint

from anubis.lms.students import get_students
from anubis.models import User, db
from anubis.rpc.enqueue import enqueue_reap_pvc_user
from anubis.utils.auth.http import require_superuser
from anubis.utils.data import req_assert
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response, json_endpoint

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


@students_.route("/toggle-disabled/<string:id>")
@require_superuser()
@json_response
def super_students_toggle_disabled(id: str):
    """
    Toggle disable a user.

    :param id:
    :return:
    """

    # Get the other user
    other: User = User.query.filter(User.id == id).first()

    # If the other user was not found, then stop
    req_assert(other is not None, message="user does not exist")

    # Assert that user being disabled is not a superuser
    req_assert(not other.is_superuser, message="Cannot disable super user")

    # Toggle the superuser field
    other.disabled = not other.disabled

    # Commit the change
    db.session.commit()

    # Pass back the status based on if the other is now disabled
    if other.disabled:
        return success_response({"status": f"{other.name} is now disabled", "variant": "warning"})

    # Pass back the status based on if the other user is now no disabled
    else:
        return success_response({"status": f"{other.name} is now enabled", "variant": "success"})


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


@students_.delete("/pvc/<string:id>")
@require_superuser()
@json_response
def super_students_delete_pvc(id: str):
    """
    Delete a user's existing Persistent Volume Claim (PVC). Requires current user to be superuser
    to be able to make this change.

    :param id:
    :return:
    """

    # Get the other user and check if they exist, if not we stop
    other: User = User.query.filter(User.id == id).first()
    req_assert(other is not None, message="user does not exist")

    # Reap that pvc for that other user
    enqueue_reap_pvc_user(id)

    return success_response({
        "status":  f"Volume deletion scheduled for user: {other.netid}.",
        "variant": "warning"
    })


@students_.put("/add")
@require_superuser()
@json_endpoint([('netid', str), ('name', str)])
def super_students_add(netid: str, name: str):
    """
    Add a user

    :return:
    """

    user = User.query.filter(User.netid == netid.strip()).first()
    if user is not None:
        return success_response({
            "status": f"Student already exists {netid}",
            "user":   user.data,
        })

    user = User(netid=netid.strip(), name=name.strip())
    db.session.add(user)
    db.session.commit()

    return success_response({
        "status": f"Added student {netid}",
        "user":   user.data,
    })
