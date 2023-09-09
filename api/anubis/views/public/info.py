from flask import Blueprint

from anubis.utils.auth.http import require_user
from anubis.utils.config import get_config_dict
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response

info_ = Blueprint("public-info", __name__, url_prefix="/public/info")


@info_.get('/discord')
@require_user()
@json_response
def public_info_discord():
    discord_info = get_config_dict('DISCORD_INFO', {})
    return success_response(discord_info)
