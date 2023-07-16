from datetime import datetime, timedelta

from utils import Session, with_context


def test_post_create():
    s: Session = Session()
    course_id = s.course_id

    # Create post
    data = s.post_json('/public/forum/post', json={
        'course_id': course_id,
        'title': 'title1',
        'content': 'content1',
        'visible_to_students': True,
        'anonymous': False,
    })
    assert data
    assert data['post']['id']
    post1_id = data['post']['id']

    # Get post
    data = s.get(f'/public/forum/post/{post1_id}')
    assert data
    assert data['post']['title'] == 'title1'
    assert data['post']['content'] == 'content1'


def test_post_create_edit():
    s: Session = Session()
    course_id = s.course_id

    # Create post
    data = s.post_json('/public/forum/post', json={
        'course_id': course_id,
        'title': 'title1',
        'content': 'content1',
        'visible_to_students': True,
        'anonymous': False,
    })
    assert data
    assert data['post']['id']
    post1_id = data['post']['id']

    # Get post
    data = s.get(f'/public/forum/post/{post1_id}')
    assert data
    assert data['post']['title'] == 'title1'
    assert data['post']['content'] == 'content1'

    # Edit post
    data = s.patch_json(f'/public/forum/post/{post1_id}', {
        'title': 'title2',
        'content': 'content2',
        'visible_to_students': True,
        'anonymous': False,
    })
    assert data
    assert data['post']['title'] == 'title2'
    assert data['post']['content'] == 'content2'

    # Get edited post
    data = s.get(f'/public/forum/post/{post1_id}')
    assert data
    assert data['post']['title'] == 'title2'
    assert data['post']['content'] == 'content2'


def test_post_create_anon():
    s: Session = Session()
    s2: Session = Session()
    course_id = s.course_id

    # Create post
    data = s.post_json('/public/forum/post', json={
        'course_id': course_id,
        'title': 'title1',
        'content': 'content1',
        'visible_to_students': True,
        'anonymous': True,
    })
    assert data
    assert data['post']['id']
    post1_id = data['post']['id']

    # Get post as other student
    data = s2.get(f'/public/forum/post/{post1_id}')
    assert data
    assert data['post']['title'] == 'title1'
    assert data['post']['content'] == 'content1'
    assert data['post']['display_name'] == 'Anonymous'


def test_post_delete():
    s: Session = Session()
    course_id = s.course_id

    # Create post
    data = s.post_json('/public/forum/post', json={
        'course_id': course_id,
        'title': 'title3',
        'content': 'content3',
        'visible_to_students': True,
        'anonymous': False,
    })
    assert data
    assert data['post']['id']
    post1_id = data['post']['id']

    # Get post
    data = s.get(f'/public/forum/post/{post1_id}')
    assert data
    assert data['post']['title'] == 'title3'
    assert data['post']['content'] == 'content3'

    # Delete post
    data = s.delete(f'/public/forum/post/{post1_id}')
    assert data
    assert data['status'] == 'Post deleted'

    # Get post
    s.get(f'/public/forum/post/{post1_id}', should_fail=True)

