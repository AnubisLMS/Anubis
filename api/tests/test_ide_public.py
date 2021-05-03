from utils import Session, create_repo


def test_ide_public():
    s = Session('student', new=True)
    s.get('/public/ide/available')
    assignments = s.get('/public/assignments/list')['assignments']
    assignment_id = assignments[0]['id']

    s.get(f'/public/ide/active/{assignment_id}')
    active = s.get(f'/public/ide/active/{assignment_id}')['active']
    assert active is None

    s.get(f'/public/ide/initialize/{assignment_id}', should_fail=True)

    create_repo(s, assignment_id)

    resp = s.get(f'/public/ide/initialize/{assignment_id}')
    assert resp['session'] is not None
    assert resp['active']
    session_id = resp['session']['id']

    active = s.get(f'/public/ide/active/{assignment_id}')['active']
    assert active is not None

    s.get(f'/public/ide/poll/{session_id}')
    s.get(f'/public/ide/poll/{session_id}')
    s.get(f'/public/ide/poll/{session_id}')
    s.get(f'/public/ide/redirect-url/{session_id}')

    s.get(f'/public/ide/stop/{session_id}')

    resp = s.get(f'/public/ide/active/{assignment_id}')
    assert not resp['active']
    assert 'session' not in resp
