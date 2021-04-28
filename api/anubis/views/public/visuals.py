from flask import Blueprint, make_response

from anubis.utils.data import is_debug
from anubis.utils.http.https import success_response
from anubis.utils.services.cache import cache
from anubis.utils.visuals.usage import get_usage_plot, get_raw_submissions

visuals = Blueprint('public-visuals', __name__, url_prefix='/public/visuals')


@visuals.route('/usage')
@cache.cached(timeout=360, unless=is_debug)
def public_visuals_usage():
    blob = get_usage_plot()

    response = make_response(blob)
    response.headers['Content-Type'] = 'image/png'

    return response


@visuals.route('/raw-usage')
def public_visuals_raw_usage():
    usage = get_raw_submissions()

    return success_response({
        'usage': usage
    })
