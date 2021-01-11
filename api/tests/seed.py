import json
from anubis.models import Submission, SubmissionTestResult, SubmissionBuild
from anubis.models import Assignment, AssignmentRepo, AssignmentTest
from anubis.models import db, User, InCourse, Course
from anubis.app import create_app
import os
import requests

os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DISABLE_ELK"] = "1"
os.environ["DEBUG"] = "1"


def get(path, token=None, params=None, headers=None) -> dict:
    if headers is None:
        headers = {}
    if token is not None:
        headers["token"] = token
    if params is None:
        params = {}
    response = requests.get(
        "http://localhost:5000" + path, headers=headers, params=params
    )
    print(
        "path={} params={} data={}\n".format(
            path, params, json.dumps(response.json(), indent=2)
        )
    )
    return response.json()


def post(path, data, token=None, params=None, headers=None) -> dict:
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    if token is not None:
        headers["token"] = token
    if params is None:
        params = {}
    response = requests.post(
        "http://localhost:5000" + path, headers=headers, params=params, json=data
    )
    print(
        "path={} params={} data={}\n".format(
            path, params, json.dumps(response.json(), indent=2)
        )
    )
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
    InCourse.query.delete()
    Assignment.query.delete()
    Course.query.delete()
    User.query.delete()
    db.session.commit()

    # Create
    u = User(
        netid="jmc1283",
        github_username="juan-punchman",
        name="John Cunniff",
        is_admin=True,
    )
    c = Course(
        name="Intro to OS", class_code="CS-UY 3224", section="A", professor="Gustavo"
    )
    ic = InCourse(owner=u, class_=c)
    a = Assignment(
        name="Assignment1: uniq",
        unique_code="abc123",
        pipeline_image="registry.osiris.services/anubis/assignment/1",
        hidden=False,
        release_date="2020-08-22",
        due_date="2020-08-22",
        class_=c,
    )
    at1 = AssignmentTest(name="Long file test", assignment=a)
    at2 = AssignmentTest(name="Short file test", assignment=a)
    r = AssignmentRepo(
        owner=u,
        assignment=a,
        repo_url="https://github.com/juan-punchman/xv6-public.git",
    )
    s1 = Submission(
        commit="2bc7f8d636365402e2d6cc2556ce814c4fcd1489",
        state="Enqueued",
        owner=u,
        assignment=a,
        repo=r,
    )
    s2 = Submission(commit="0001", state="Enqueued", owner=u, assignment=a, repo=r)

    # Commit
    db.session.add_all([u, c, ic, a, at1, at2, s1, s2, r])
    db.session.commit()

    # Init models
    s1.init_submission_models()
    s2.init_submission_models()


token = get("/private/token/jmc1283")["data"]

# whoami
get("/public/whoami")
get("/public/whoami", token=token)

# Test class endpoint
get("/public/classes", token=token)

# Test assignment endpoint
get("/public/assignments", token=token)
get("/public/assignments", token=token, params={"class": "Intro to OS"})

# Test submissions endpoint
get("/public/submissions", token=token)
get("/public/submissions", token=token, params={"class": "Intro to OS"})
get("/public/submissions", token=token, params={"assignment": "Assignment1: uniq"})
get(
    "/public/submissions",
    token=token,
    params={"class": "Intro to OS", "assignment": "Assignment1: uniq"},
)

# Test submission endpoint
get("/public/submission/0000", token=token)
get("/public/submission/0001", token=token)
get("/public/submission/0003", token=token)


webhook = json.load(open(os.path.join(os.path.dirname(__file__), "webhook2.json")))
post("/public/webhook", data=webhook, headers={"X-GitHub-Event": "push"})
