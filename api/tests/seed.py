import os
import requests

os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DISABLE_ELK'] = '1'

from anubis.app import create_app
from anubis.models import db, User, InClass, Class_
from anubis.models import Assignment, AssignmentRepo, AssignmentTest
from anubis.models import Submission, SubmissionTestResult, SubmissionBuild
import json


def get(path, token=None, params=None) -> dict:
    headers = {}
    if token is not None:
        headers['token'] = token
    if params is None:
        params = {}
    response = requests.get('http://localhost:5000' + path, headers=headers, params=params)
    print('path={} params={} data={}\n'.format(path, params, json.dumps(response.json(), indent=2)))
    return response.json()


app = create_app()

with app.app_context():
    # Create
    db.create_all()

    # Yeet
    SubmissionTestResult.query.delete()
    SubmissionBuild.query.delete()
    Submission.query.delete()
    AssignmentRepo.query.delete()
    AssignmentTest.query.delete()
    InClass.query.delete()
    Assignment.query.delete()
    Class_.query.delete()
    User.query.delete()
    db.session.commit()

    # Create
    u = User(netid='jmc1283', github_username='juanpunchman', name='John Cunniff', is_admin=True)
    c = Class_(name='Intro to OS', class_code='CS-UY 3224', section='A', professor='Gustavo')
    ic = InClass(owner=u, class_=c)
    a = Assignment(name='Assignment1: uniq', hidden=False, release_date='2020-08-22', due_date='2020-08-22', class_=c)
    at1 = AssignmentTest(name='Long file test', assignment=a)
    at2 = AssignmentTest(name='Short file test', assignment=a)
    r = AssignmentRepo(owner=u, assignment=a, repo_url='git@github.com/os3224/final')
    s1 = Submission(commit='0000', state='Enqueued', owner=u, assignment=a)
    s2 = Submission(commit='0001', state='Enqueued', owner=u, assignment=a)

    # Commit
    db.session.add_all([u, c, ic, a, at1, at2, s1, s2, r])
    db.session.commit()

    # Init models
    s1.init_submission_models()
    s2.init_submission_models()



token = get('/private/token/jmc1283')['data']

# whoami
get('/public/whoami')
get('/public/whoami', token=token)

# Test class endpoint
get('/public/classes', token=token)

# Test assignment endpoint
get('/public/assignments', token=token)
get('/public/assignments', token=token, params={'class': 'Intro to OS'})

# Test submissions endpoint
get('/public/submissions', token=token)
get('/public/submissions', token=token, params={'class': 'Intro to OS'})
get('/public/submissions', token=token, params={'assignment': 'Assignment1: uniq'})
get('/public/submissions', token=token, params={'class': 'Intro to OS', 'assignment': 'Assignment1: uniq'})

# Test submission endpoint
get('/public/submission/0000', token=token)
get('/public/submission/0001', token=token)
get('/public/submission/0003', token=token)
