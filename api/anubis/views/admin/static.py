from flask import Blueprint, request

from anubis.models import db, StaticFile
from anubis.utils.auth import require_admin
from anubis.utils.data import rand
from anubis.utils.http.decorators import json_response
from anubis.utils.http.files import get_mime_type
from anubis.utils.http.https import (
    get_number_arg,
    get_request_file_stream,
    success_response,
    error_response,
)
from anubis.utils.lms.course import get_course_context, assert_course_admin

static = Blueprint("admin-static", __name__, url_prefix="/admin/static")


@static.route('/delete/<string:static_id>')
@require_admin()
@json_response
def static_delete_static_id(static_id: str):
    static_file = StaticFile.query.filter(
        StaticFile.id == static_id
    ).first()

    assert_course_admin(static_file.course_id)

    db.session.delete(static_file)
    db.session.commit()

    return success_response({
        'status': 'File deleted',
        'variant': 'warning',
    })


@static.route("/list")
@require_admin()
@json_response
def admin_static_list():
    """
    List all public blob files. Optionally specify a limit
    and an offset.

    /admin/static/list?limit=20&offset=20

    :return:
    """

    course = get_course_context()

    limit = get_number_arg("limit", default_value=20)
    offset = get_number_arg("offset", default_value=0)

    public_files = StaticFile.query \
        .filter(StaticFile.course_id == course.id) \
        .order_by(StaticFile.created.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

    return success_response(
        {"files": [public_file.data for public_file in public_files]}
    )


@static.route("/upload", methods=["POST"])
@require_admin(unless_debug=True)
@json_response
def admin_static_upload():
    """
    Upload a new public static file. The file will immediately be
    publicly available.

    The StaticFiles are unique by the path specified by the admin. If the path
    already exists, then the file is replaced.

    :return:
    """

    course = get_course_context()
    path = request.args.get("path", default=None)

    # If the path was not specified, then create some hash for it
    if path is None:
        path = "/" + rand(16)

    # Pull file from request
    stream, filename = get_request_file_stream(with_filename=True)

    # Make sure we got a file
    if stream is None:
        return error_response("No file uploaded"), 406

    # Figure out content type
    mime_type = get_mime_type(stream)

    if mime_type == 'image/svg':
        mime_type = 'image/svg+xml'

    # Check to see if blob path already exists
    blob = StaticFile.query.filter(StaticFile.path == path).first()

    # If the blob doesn't already exist, create one
    if blob is None:
        blob = StaticFile(
            path=path,
            course_id=course.id,
        )

    # Update the fields
    blob.filename = filename
    blob.blob = stream
    blob.content_type = mime_type

    # Add to db
    db.session.add(blob)
    db.session.commit()

    return success_response({
        "status": f"{filename} uploaded",
        "blob": blob.data,
    })
