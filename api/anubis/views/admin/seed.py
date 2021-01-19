import random
import string
from datetime import datetime, timedelta

from flask import Blueprint

from anubis.models import (
    db,
    SubmissionTestResult,
    SubmissionBuild,
    Submission,
    AssignmentRepo,
    AssignmentTest,
    InCourse,
    Assignment,
    Course,
    User,
    TheiaSession,
    AssignmentQuestion,
    AssignedStudentQuestion,
)
from anubis.utils.auth import require_admin
from anubis.utils.decorators import json_response
from anubis.utils.http import success_response
from anubis.utils.data import rand
from anubis.utils.questions import assign_questions

seed = Blueprint("admin-seed", __name__, url_prefix="/admin/seed")


def randstr(n=10):
    return rand()[:n]


def randnetid():
    return "".join(random.choice(string.ascii_lowercase) for _ in range(3)) + "".join(
        random.choice(string.digits) for _ in range(random.randint(2, 4))
    )


def create_assignment(course, users):
    # Assignment 1 uniq
    assignment = Assignment(
        name="uniq",
        pipeline_image="registry.osiris.services/anubis/assignment/1",
        hidden=False,
        release_date=datetime.now() - timedelta(hours=2),
        due_date=datetime.now() + timedelta(hours=2),
        grace_date=datetime.now() + timedelta(hours=3),
        course=course,
        github_classroom_url="",
        ide_enabled=True,
    )

    for i in range(random.randint(2, 4)):
        b, c = random.randint(1, 5), random.randint(1, 5)
        assignment_question = AssignmentQuestion(
            question=f"What is {c} + {b}?",
            solution=f"{c+b}",
            sequence=i,
            code_question=False,
            assignment=assignment,
        )
        db.session.add(assignment_question)

    tests = []
    for i in range(random.randint(1, 5)):
        tests.append(AssignmentTest(name=f"test {i}", assignment=assignment))

    submissions = []
    repos = []
    theia_sessions = []
    for user in users:
        repos.append(
            AssignmentRepo(
                owner=user,
                assignment=assignment,
                repo_url="https://github.com/wabscale/xv6-public.git",
                github_username=user.github_username,
            )
        )

        for _ in range(2):
            theia_sessions.append(
                TheiaSession(
                    owner=user,
                    assignment=assignment,
                    repo_url=repos[-1].repo_url,
                    active=False,
                    ended=datetime.now(),
                    state="state",
                    cluster_address="127.0.0.1",
                )
            )
        theia_sessions.append(
            TheiaSession(
                owner=user,
                assignment=assignment,
                repo_url=repos[-1].repo_url,
                active=True,
                state="state",
                cluster_address="127.0.0.1",
            )
        )

        if random.randint(0, 3) != 0:
            for i in range(random.randint(1, 10)):
                submissions.append(
                    Submission(
                        commit=randstr(),
                        state="Waiting for resources...",
                        owner=user,
                        assignment=assignment,
                        repo=repos[-1],
                    )
                )

    db.session.add_all(tests)
    db.session.add_all(submissions)
    db.session.add_all(theia_sessions)
    db.session.add_all(repos)
    db.session.add(assignment)

    return assignment, tests, submissions, repos


def create_students(n=10):
    students = []
    for i in range(random.randint(n // 2, n)):
        students.append(
            User(
                netid=randnetid(),
                github_username=randstr(),
                name=f"first last {i}",
                is_admin=False,
                is_superuser=False,
            )
        )
    db.session.add_all(students)
    return students


def create_course(users):
    course = Course(
        name="Intro to OS", course_code="CS-UY 3224", section="A", professor="Gustavo"
    )
    db.session.add(course)

    for user in users:
        db.session.add(InCourse(owner=user, course=course))

    return course


@seed.route("/")
@require_admin(unless_debug=True)
@json_response
def private_seed():
    # Yeet
    TheiaSession.query.delete()
    AssignedStudentQuestion.query.delete()
    AssignmentQuestion.query.delete()
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
    me = User(
        netid="jmc1283",
        github_username="wabscale",
        name="John Cunniff",
        is_admin=True,
        is_superuser=True,
    )
    db.session.add(me)

    students = create_students(130) + [me]
    course = create_course(students)
    assignment, _, submissions, _ = create_assignment(course, students)

    db.session.commit()

    # Init models
    for submission in submissions:
        submission.init_submission_models()
        submission.processed = random.randint(0, 1) == 1
        db.session.commit()

    assign_questions(assignment)

    return success_response("seeded")
