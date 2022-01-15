from flask import Blueprint

from anubis.models import (
    db, ForumPost, ForumCategory, ForumPostInCategory, ForumPostUpvote, ForumPostComment, ForumPostViewed
)
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.http.decorators import json_response, json_endpoint

forums_ = Blueprint("public-forums", __name__, url_prefix="/public/forums")


@forums_.put('/post')
@require_user()
@json_endpoint([])
def public_put_forum_post():
    db, ForumPost, ForumCategory, ForumPostInCategory, ForumPostUpvote, ForumPostComment, ForumPostViewed
    current_user
    json_response
