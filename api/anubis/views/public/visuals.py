from flask import Blueprint, make_response

from anubis.utils.data import is_debug
from anubis.utils.http.https import success_response
from anubis.utils.services.cache import cache
from anubis.utils.visuals.usage import get_usage_plot, get_raw_submissions

visuals = Blueprint('public-visuals', __name__, url_prefix='/public/visuals')


@visuals.route('/usage')
@cache.cached(timeout=360, unless=is_debug)
def public_visuals_usage():
    """
    Get the usage png graph. This endpoint is heavily
    cached.

    :return:
    """

    # Get the png blob of the usage graph.
    # The get_usage_plot is itself a cached function.
    blob = get_usage_plot()

    # Take the png bytes, and make a flask response
    response = make_response(blob)

    # Set the response content type
    response.headers['Content-Type'] = 'image/png'

    # Pass back the image response
    return response


@visuals.route('/raw-usage')
def public_visuals_raw_usage():
    """
    Get the raw usage data for generating a react-vis
    graph in the frontend of the usage stats.

    :return:
    """

    # Get the raw usage stats
    usage = get_raw_submissions()

    # Pass back the visual data
    return success_response({
        'usage': usage
    })
