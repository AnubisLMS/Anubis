from flask import Blueprint
from sqlalchemy.orm import defer

from anubis.lms.courses import assert_course_context, course_context
from anubis.models import StaticFile, db
from anubis.utils.auth.http import require_admin
from anubis.utils.data import req_assert
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response
from anubis.utils.http.files import process_file_upload

static = Blueprint("admin-static", __name__, url_prefix="/admin/static")


@static.route("/delete/<string:static_id>")
@require_admin()
@json_response
def admin_static_delete_static_id(static_id: str):
    """
    Delete a static file item.

    :param static_id:
    :return:
    """

    # Get the static file object
    static_file = StaticFile.query.filter(StaticFile.id == static_id).first()

    # Verify that static file exists
    req_assert(static_file is not None, message="static file does not exist")

    # Assert that the static file is within the current course context
    assert_course_context(static_file)

    # Delete the object
    db.session.delete(static_file)

    # Commit the delete
    db.session.commit()

    # Pass back the status
    return success_response(
        {
            "status": "File deleted",
            "variant": "warning",
        }
    )


@static.route("/list")
@require_admin()
@json_response
def admin_static_list():
    """
    List all public blob files. Optionally specify a limit
    and an offset.

    /admin/static/list

    :return:
    """

    # Build Query. Defer the blob field so
    # it is not loaded.
    query = (
        StaticFile.query.filter(StaticFile.course_id == course_context.id)
        .order_by(StaticFile.created.desc())
        .options(defer(StaticFile.blob))
    )

    # Get all public static files within this course
    public_files = query.all()

    # Pass back the list of files
    return success_response({"files": [public_file.data for public_file in public_files]})


@static.route("/upload", methods=["POST"])
@require_admin(unless_debug=True)
@json_response
def admin_static_file_upload():
    """
    Upload a new public static file. The file will immediately be
    publicly available.

    The StaticFiles are unique by the path specified by the admin. If the path
    already exists, then the file is replaced.

    :return:
    """

    blob = process_file_upload()

    # Pass back the status
    return success_response(
        {
            "status": f"{blob.filename} uploaded",
            "blob": blob.data,
        }
    )
