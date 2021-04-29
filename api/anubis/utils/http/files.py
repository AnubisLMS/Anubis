import magic
from flask import Response, make_response

from anubis.models import StaticFile


def get_mime_type(blob: bytes) -> str:
    """TODO"""
    m = magic.Magic(mime=True)
    return m.from_buffer(blob)


def make_blob_response(file: StaticFile) -> Response:
    # Make a flask response from file data blob
    response = make_response(file.blob)

    # Set its content type header to the proper value
    response.headers["Content-Type"] = file.content_type

    # If the image is an svg, then we need to make sure that it has
    # the +xml or it will not be rendered correctly in browser.
    if file.content_type == 'image/svg':
        response.headers["Content-Type"] = 'imag/svg+xml'

    # Hand the flask response back
    return response
