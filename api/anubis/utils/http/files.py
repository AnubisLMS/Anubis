from flask import Response, make_response

from anubis.lms.courses import course_context
from anubis.models import StaticFile, db
from anubis.utils.data import rand, req_assert
from anubis.utils.http import get_request_file_stream


def get_mime_type(blob: bytes) -> str:
    """
    Get an approximate content type for a given blob. This
    is very useful for getting the content-type of an
    uploaded file.

    * This function uses libmagic, which requires some
    extra .so files outside of the python install *

    :param blob:
    :return:
    """

    # If this fails to import, you probably need to
    # install libmagic system wide. It should be:
    #
    # OSX     : brew install libmagic
    # Windows : pip install python-magic-bin
    # Debian  : apt install libmagic1
    # Arch    : pacman -S imagemagick
    import magic

    # Create some magic
    m = magic.Magic(mime=True)

    # Calculate mime from bytes
    return m.from_buffer(blob)


def make_blob_response(file: StaticFile) -> Response:
    """
    Take a static file object, and form a flask response,
    having the correct bytes content and content-type header.

    :param file:
    :return:
    """
    # Make a flask response from file data blob
    response = make_response(file.blob)

    # set its content type header to the proper value
    response.headers["Content-Type"] = file.content_type

    # If the image is an svg, then we need to make sure that it has
    # the +xml or it will not be rendered correctly in browser.
    if file.content_type == "image/svg":
        response.headers["Content-Type"] = "imag/svg+xml"

    # Hand the flask response back
    return response


def process_file_upload(course_id: str = None) -> StaticFile:
    # Create a path hash
    path = "/" + rand(16)

    # Pull file from request
    stream, filename = get_request_file_stream(with_filename=True)

    # Make sure we got a file
    req_assert(stream is not None, message="No file uploaded")

    # Figure out content type
    mime_type = get_mime_type(stream)

    if mime_type == "image/svg":
        mime_type = "image/svg+xml"

    # Check to see if blob path already exists
    blob = StaticFile.query.filter(StaticFile.path == path).first()

    # If the blob doesn't already exist, create one
    if blob is None:
        blob = StaticFile(path=path, course_id=course_context.id)

    # Update the fields
    blob.filename = filename
    blob.blob = stream
    blob.content_type = mime_type

    # Add to db
    db.session.add(blob)
    db.session.commit()

    return blob


def make_png_response(blob: bytes) -> Response:
    # Take the png bytes, and make a flask response
    response = make_response(blob)

    # set the response content type
    response.headers["Content-Type"] = "image/png"

    # Pass back the image response
    return response
