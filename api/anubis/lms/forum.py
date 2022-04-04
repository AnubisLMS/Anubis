from anubis.models import (
    ForumPost,
    ForumPostComment,
)
from anubis.utils.auth.user import current_user
from anubis.utils.http import req_assert


def verify_post(post_id: str) -> ForumPost:
    post: ForumPost = ForumPost.query.filter(
        ForumPost.id == post_id,
    ).first()
    req_assert(post is not None, message='Post does not exist')
    return post


def verify_post_owner(post_id: str) -> ForumPost:
    post: ForumPost = verify_post(post_id)
    req_assert(post.owner_id == current_user.id, message='Post does not exist')
    return post


def verify_post_comment(comment_id: str) -> ForumPostComment:
    comment: ForumPostComment = ForumPostComment.query.filter(
        ForumPostComment.id == comment_id,
    ).first()
    req_assert(comment is not None, message='Comment does not exist')
    return comment


def verify_post_comment_owner(comment_id: str) -> ForumPostComment:
    comment: ForumPostComment = verify_post_comment(comment_id)
    req_assert(comment.owner_id == current_user.id, message='Comment does not exist')
    return comment


def get_post_comments(post: ForumPost) -> list[ForumPostComment]:
    comments: list[ForumPostComment] = ForumPostComment.query.filter(
        ForumPostComment.post_id == post.id,
    ).all()
    return comments


def get_post_comments_data(post: ForumPost) -> list[dict]:
    comments: list[ForumPostComment] = post.comments

    def _full_comment(comment: ForumPostComment) -> dict:
        data = comment.data
        data['children'] = [
            _comment.data
            for _comment in comments
            if _comment.parent_id == comment.id
        ]
        return data

    return [
        _full_comment(comment)
        for comment in comments
        if comment.thread_start is True
    ]
