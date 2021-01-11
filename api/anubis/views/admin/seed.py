from flask import Blueprint

from anubis.models import (
    db,
    SubmissionTestResult,
    SubmissionBuild,
    Submission,
    AssignmentRepo,
    AssignmentTest,
    InClass,
    Assignment,
    Course,
    User,
)
from anubis.utils.decorators import json_response
from anubis.utils.auth import require_admin
from anubis.utils.http import success_response
from anubis.utils.redis_queue import enqueue_webhook

seed = Blueprint("admin-seed", __name__, url_prefix="/admin/seed")


@seed.route("/")
@require_admin
@json_response
def private_seed():
    # Yeet
    SubmissionTestResult.query.delete()
    SubmissionBuild.query.delete()
    Submission.query.delete()
    AssignmentRepo.query.delete()
    AssignmentTest.query.delete()
    InClass.query.delete()
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
    ic = InClass(owner=u, class_=c)
    user_items = [u, c, ic]

    # Assignment 1 uniq
    a1 = Assignment(
        name="uniq",
        pipeline_image="registry.osiris.services/anubis/assignment/1",
        hidden=False,
        release_date="2020-08-22 23:55:00",
        due_date="2020-08-22 23:55:00",
        class_=c,
        github_classroom_url="",
        ide_enabled=True,
    )
    a1t1 = AssignmentTest(name="Long file test", assignment=a1)
    a1t2 = AssignmentTest(name="Short file test", assignment=a1)
    a1r1 = AssignmentRepo(
        owner=u,
        assignment=a1,
        repo_url="https://github.com/wabscale/xv6-public.git",
        github_username="juan-punchman",
    )
    a1s1 = Submission(
        commit="test",
        state="Waiting for resources...",
        owner=u,
        assignment=a1,
        repo=a1r1,
    )
    a1s2 = Submission(
        commit="0001",
        state="Waiting for resources...",
        owner=u,
        assignment=a1,
        repo=a1r1,
    )
    assignment_1_items = [a1, a1t1, a1t2, a1r1, a1s1, a1s2]

    # Assignment 2 tail
    a2 = Assignment(
        name="tail",
        pipeline_image="registry.osiris.services/anubis/assignment/f1295ac4",
        unique_code="f1295ac4",
        hidden=False,
        release_date="2020-09-03 23:55:00",
        due_date="2020-09-03 23:55:00",
        class_=c,
        github_classroom_url="",
        ide_enabled=True,
    )
    a2t1 = AssignmentTest(name="Hello world test", assignment=a2)
    a2t2 = AssignmentTest(name="Short file test", assignment=a2)
    a2t3 = AssignmentTest(name="Long file test", assignment=a2)
    a2r2 = AssignmentRepo(
        owner=u,
        assignment=a2,
        repo_url="https://github.com/os3224/assignment-1-spring2020.git",
        github_username="juan-punchman",
    )
    a2s1 = Submission(
        commit="2bc7f8d636365402e2d6cc2556ce814c4fcd1489",
        state="Waiting for resources...",
        owner=u,
        assignment=a2,
        repo=a1r1,
    )
    assignment_2_items = [a2, a2t1, a2t2, a2t3, a2r2, a2s1]

    # Commit
    db.session.add_all(user_items)
    db.session.add_all(assignment_1_items)
    db.session.add_all(assignment_2_items)
    db.session.commit()

    # Init models
    a1s1.init_submission_models()
    a1s2.init_submission_models()
    a2s1.init_submission_models()

    enqueue_webhook(a2s1.id)

    return success_response("seeded")
