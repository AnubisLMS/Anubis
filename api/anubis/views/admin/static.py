from flask import Blueprint, request

from anubis.models import db, StaticFile
from anubis.utils.data import rand
from anubis.utils.files import get_mime_type
from anubis.utils.http import get_number_arg, get_request_file_stream, success_response, error_response
from anubis.utils.decorators import json_response
from anubis.utils.auth import require_admin

static = Blueprint('admin-static', __name__, url_prefix='/admin/static')


@static.route('/list')
@require_admin
@json_response
def static_public_list():
    """
    List all public blob files. Optionally specify a limit
    and an offset.

    /admin/static/list?limit=20&offset=20

    :return:
    """

    limit = get_number_arg('limit', default_value=20)
    offset = get_number_arg('offset', default_value=0)

    public_files = StaticFile.query.limit(limit).offset(offset).all()

    return success_response({
        'files': [
            public_file.data
            for public_file in public_files
        ]
    })


@static.route('/upload', methods=['POST'])
@require_admin
@json_response
def static_public_upload():
    """
    Upload a new public static file. The file will immediately be
    publicly available.

    The StaticFiles are unique by the path specified by the admin. If the path
    already exists, then the file is replaced.

    :return:
    """

    path = request.args.get('path', default=None)

    # If the path was not specified, then create some hash for it
    if path is None:
        path = '/' + rand()

    # Pull file from request
    stream, filename = get_request_file_stream(with_filename=True)

    # Make sure we got a file
    if stream is None:
        return error_response('No file uploaded'), 406

    # Figure out content type
    mime_type = get_mime_type(stream)

    # Check to see if blob path already exists
    blob = StaticFile.query.filter(
        StaticFile.path == path
    ).first()

    # If the blob doesn't already exist, create one
    if blob is None:
        blob = StaticFile(
            path=path,
        )

    # Update the fields
    blob.filename = filename
    blob.blob = stream
    blob.content_type = mime_type

    # Add to db
    db.session.add(blob)
    db.session.commit()

    return success_response({
        'status': 'uploaded',
        'blob': blob.data,
    })
