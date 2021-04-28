from flask import Blueprint
from sqlalchemy import or_

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

    # If the filename was not specified, then search by path hash
    if filename is None:
        blob = StaticFile.query.filter(
            or_(StaticFile.path == path, StaticFile.path == "/" + path)
        ).first()

    # If filename was specified, then include it in the query
    else:
        blob = StaticFile.query.filter(
            or_(StaticFile.path == path, StaticFile.path == "/" + path),
            StaticFile.filename == filename,
        ).first()

    if blob is None:
        return "404 Not Found :(", 404

    return make_blob_response(blob)
