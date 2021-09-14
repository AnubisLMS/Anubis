from utils import Session, create_repo


def test_repos_public():
    s = Session('student', new=True)

    s.get('/public/repos')
    repos = s.get('/public/repos/list')['repos']
    assert len(repos) == 0

    create_repo(s)

    repos = s.get('/public/repos/list')['repos']
    assert len(repos) == 1
    repos = s.get('/public/repos/')['repos']
    assert len(repos) == 1
