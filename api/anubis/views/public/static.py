from flask import Blueprint
from sqlalchemy import or_

from anubis.models import StaticFile
from anubis.utils.cache import cache
from anubis.utils.files import make_blob_response

static = Blueprint('public-static', __name__, url_prefix='/public/static')


@static.route('/<path:path>')
@cache.memoize(timeout=60)
def public_static(path: str):
    """
    Get some public static file.

    * response is possibly cached *

    :param path:
    :return:
    """

    blob = StaticFile.query.filter(
        or_(StaticFile.path == path, StaticFile == '/' + path)
    ).first()
    if blob is None:
        return '404 Not Found', 404

    return make_blob_response(blob)
