from typing import List
from flask import Blueprint

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
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http import req_assert, success_response, error_response
from anubis.utils.auth.user import verify_in_course
from anubis.lms.forum import verify_post_owner, get_post_comments, verify_post

forums_ = Blueprint("public-forums", __name__, url_prefix="/public/forums")


@forums_.get('/<string:course_id>')
@require_user()
@json_response
def public_forum_list(course_id: str):
    course: Course = verify_in_course(course_id)

    posts: List[ForumPost] = ForumPost.query.filter(
        ForumPost.course_id == course.id,
        ForumPost.visible_to_students == True,
    ).order_by(ForumPost.created.desc()).all()

    return success_response({
        'posts': [
            post.data for post in posts
        ]
    })


@forums_.put('/post')
@require_user()
@json_endpoint([
    ('course_id', str),
    ('title', str),
    ('content', str),
    ('visible_to_students', bool),
    ('anonymous', bool),
])
def public_put_forum_post(
    course_id: str,
    title: str,
    content: str,
    visible_to_students: bool,
    anonymous: bool,
):
    course = verify_in_course(course_id)

    post = ForumPost(
        owner_id=current_user.id,
        course_id=course.id,
        visible_to_students=visible_to_students,
        pinned=False,
        anonymous=anonymous,
        seen_count=0,
        title=title,
        content=content,
    )
    db.session.add(post)
    db.session.commit()

    return success_response({
        'post': post.data,
        'status': 'Post created',
    })


@forums_.patch('/post/<string:post_id>')
@require_user()
@json_endpoint([
    ('title', str),
    ('content', str),
    ('visible_to_students', bool),
    ('anonymous', bool),
])
def public_patch_forum_post(
    post_id: str,
    title: str,
    content: str,
    visible_to_students: bool,
    anonymous: bool,
):
    post = verify_post_owner(post_id)

    post.title = title
    post.content = content
    post.visible_to_students = visible_to_students
    post.anonymous = anonymous

    db.session.add(post)
    db.session.commit()

    return success_response({
        'post': post.data,
        'status': 'Post updated',
    })


@forums_.delete('/post/<string:post_id>')
@require_user()
def public_delete_forum_post(post_id: str):
    post: ForumPost = verify_post_owner(post_id)

    db.session.delete(post)
    db.session.commit()

    return success_response({
        'status': 'Post deleted',
        'variant': 'warning'
    })


@forums_.put('/post/seen_<string:post_id>')
@require_user()
def public_put_forum_post_seen(post_id: str):
    post: ForumPost = verify_post(post_id)

    post.seen_count += 1

    viewed: ForumPostViewed = ForumPostViewed.query.filter(
        ForumPostViewed.post_id == post.id,
        ForumPostViewed.owner_id == current_user.id,
    ).first()
    if viewed is None:
        viewed = ForumPostViewed(
            post_id=post.id,
            owner_id=current_user.id,
        )
        db.session.add(viewed)

    db.session.commit()

    return success_response({
        'status': 'Post deleted',
        'variant': 'warning'
    })
