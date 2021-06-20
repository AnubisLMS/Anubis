from flask import Blueprint
from sqlalchemy.sql import or_
from sqlalchemy.orm import undefer

from anubis.models import StaticFile
from anubis.utils.http.files import make_blob_response
from anubis.utils.services.cache import cache

static = Blueprint("public-static", __name__, url_prefix="/public/static")


@static.route("/<string:path>")
@static.route("/<string:path>/<string:filename>")
@cache.memoize(timeout=60)
def public_static(path: str, filename: str = None):
    """
    Get some public static file.

    * response is possibly cached *

    :param filename:
    :param path:
    :return:
    """

    query = (
        StaticFile.query
            .option(undefer(StaticFile.blob))  # undefer blob attr to avoid followup query
            .filter(or_(StaticFile.path == path, StaticFile.path == "/" + path))
    )

    # If filename was specified, then include it in the query
    if filename is not None:
        query = query.filter(StaticFile.filename == filename)

    # Execute the query
    blob = query.first()

    # If the blob is None, then 404
    if blob is None:
        return "404 Not Found :(", 404

    # Form the blob response
    return make_blob_response(blob)
