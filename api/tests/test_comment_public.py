from datetime import datetime, timedelta

from utils import Session, with_context


def create_post(s: Session) -> str:
    course_id = s.course_id
    # Create post
    data = s.post_json('/public/forums/post', json={
        'course_id': course_id,
        'title': 'title1',
        'content': 'content1',
        'visible_to_students': True,
        'anonymous': False,
    })
    assert data
    assert data['post']['id']
    post1_id = data['post']['id']

    return post1_id


def test_comment_create():
    s: Session = Session()
    post_id = create_post(s)

    # Create comment
    data = s.post_json(f'/public/forums/post/{post_id}/comment', json={
        'content': 'content1',
        'anonymous': False,
    })
    assert data
    assert data['comment']['content'] == 'content1'
    assert data['comment']['thread_start'] is True
    assert data['comment']['approved_by'] is None
    assert data['comment']['display_name'] == s.name
    comment_id = data['comment']['id']

    data = s.get(f'/public/forums/post/comment/{comment_id}')
    assert data['comment']['content'] == 'content1'
    assert data['comment']['thread_start'] is True
    assert data['comment']['approved_by'] is None
    assert data['comment']['display_name'] == s.name


def test_comment_edit():
    s: Session = Session()
    post_id = create_post(s)

    # Create comment
    data = s.post_json(f'/public/forums/post/{post_id}/comment', json={
        'content': 'content1',
        'anonymous': False,
    })
    assert data
    assert data['comment']['content'] == 'content1'
    assert data['comment']['thread_start'] is True
    assert data['comment']['approved_by'] is None
    assert data['comment']['display_name'] == s.name
    comment_id = data['comment']['id']

    # Edit comment
    data = s.patch_json(f'/public/forums/post/comment/{comment_id}', json={
        'content': 'content2',
        'anonymous': True,
    })
    assert data
    assert data['comment']['content'] == 'content2'
    assert data['comment']['thread_start'] is True
    assert data['comment']['approved_by'] is None
    assert data['comment']['display_name'] == 'Anonymous'

    # Get comment
    data = s.get(f'/public/forums/post/comment/{comment_id}')
    assert data['comment']['content'] == 'content2'
    assert data['comment']['thread_start'] is True
    assert data['comment']['approved_by'] is None
    assert data['comment']['display_name'] == 'Anonymous'


def test_comment_thread():
    s: Session = Session()
    post_id = create_post(s)

    # Create first comment
    data = s.post_json(f'/public/forums/post/{post_id}/comment', json={
        'content': 'content1',
        'anonymous': False,
    })
    comment1_id = data['comment']['id']

    # Create comment
    data = s.post_json(f'/public/forums/post/{post_id}/comment/{comment1_id}', json={
        'content': 'content2',
        'anonymous': False,
    })
    assert data
    assert data['comment']['content'] == 'content2'
    assert data['comment']['thread_start'] == False
    assert data['comment']['approved_by'] is None
    assert data['comment']['display_name'] == s.name
    comment2_id = data['comment']['id']

    # Get full post
    data = s.get(f'/public/forums/post/{post_id}')
    assert data
    assert len(data['post']['comments'])
    assert all(comment['id'] in [comment1_id, comment2_id] for comment in data['post']['comments'])






