from flask import Blueprint, make_response

from anubis.utils.visuals.usage import get_usage_plot
from anubis.utils.services.cache import cache
from anubis.utils.http.data import is_debug

visuals = Blueprint('visuals', __name__, url_prefix='/public/visuals')


@visuals.route('/usage')
@cache.cached(timeout=360, unless=is_debug)
def public_visuals_usage():
    blob = get_usage_plot()

    response = make_response(blob)
    response.headers['Content-Type'] = 'image/png'

    return response

