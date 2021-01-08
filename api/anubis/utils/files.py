import magic
from flask import Response, make_response

from anubis.models import StaticFile


def get_mime_type(blob: bytes) -> str:
    m = magic.Magic(mime=True)
    return m.from_buffer(blob)


def make_blob_response(file: StaticFile) -> Response:
    # Make a flask response from file data blob
    response = make_response(file.blob)

    # Set its content type header to the proper value
    response.headers['Content-Type'] = file.content_type

    # Hand the flask response back
    return response
