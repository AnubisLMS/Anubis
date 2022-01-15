from typing import List
from anubis.models import (
    db,
    User,
    Course,
    InCourse,
    ForumPost,
    ForumCategory,
    ForumPostInCategory,
    ForumPostUpvote,
    ForumPostComment,
    ForumPostViewed,
)
from anubis.utils.auth.user import current_user
from anubis.utils.http import req_assert


def verify_post_owner(post_id: str) -> ForumPost:
    post: ForumPost = ForumPost.query.filter(
        ForumPost.id == post_id,
        ForumPost.owner_id == current_user.id,
    ).first()
    req_assert(post is not None, message='Post does not exist')

    return post


def verify_post(post_id: str) -> ForumPost:
    post: ForumPost = ForumPost.query.filter(
        ForumPost.id == post_id,
    ).first()
    req_assert(post is not None, message='Post does not exist')

    return post


def get_post_comments(post: ForumPost) -> List[ForumPostComment]:
    comments: List[ForumPostComment] = ForumPostComment.query.filter(
        ForumPostComment.post_id == post.id,
    ).all()
    return comments

