from datetime import datetime, timedelta

import pytest

from anubis.ide.initialize import initialize_ide_for_assignment
from anubis.lms.reserve import get_active_reserves, is_session_reserved, reserve_ide_for_students
from anubis.models import (
    db,
    ReservedIDETime,
    Assignment,
    User,
    Course,
InCourse,
TheiaSession,
Submission
)
from utils import with_context, create_user


def assignment_query(name: str = 'CS-UY 3224 Assignment 4'):
    return Assignment.query.filter(
        Assignment.github_repo_required == False,
        Assignment.name == name
    )


@pytest.fixture(scope="session")
@with_context
def assignment_id():
    assignment = assignment_query().first()
    return assignment.id


@pytest.fixture(scope="session")
@with_context
def course_id():
    assignment = assignment_query().first()
    return assignment.course.id


@pytest.fixture(scope="session")
@with_context
def active_reserve_id(assignment_id, course_id):
    now = datetime.now()
    r = ReservedIDETime(
        assignment_id=assignment_id,
        course_id=course_id,
        start=now + timedelta(minutes=45),
        end=now + timedelta(minutes=120),
    )
    db.session.add(r)
    db.session.commit()
    return r.id


@pytest.fixture(scope="session")
@with_context
def inactive_reserve_id(assignment_id, course_id):
    now = datetime.now()
    r = ReservedIDETime(
        assignment_id=assignment_id,
        course_id=course_id,
        start=now + timedelta(minutes=75),
        end=now + timedelta(minutes=120),
    )
    db.session.add(r)
    db.session.commit()
    return r.id


def create_assignment_ide(user: User, reserved: bool = True):
    if reserved:
        assignment = assignment_query().first()
    else:
        assignment = assignment_query('CS-UY 3224 Assignment 2').first()
    assert assignment is not None
    return initialize_ide_for_assignment(user, assignment)


@with_context
def test_get_active_reserved(active_reserve_id):
    get_active_reserves()


@with_context
def test_active_reserved(active_reserve_id):
    active_reserves = get_active_reserves()
    assert len(active_reserves) >= 1
    assert any(r.id == active_reserve_id for r in active_reserves)


@with_context
def test_inactive_reserved(inactive_reserve_id):
    active_reserves = get_active_reserves()
    assert len(active_reserves) >= 1
    assert all(r.id != inactive_reserve_id for r in active_reserves)


@with_context
def test_is_reserved_active(active_reserve_id):
    netid, _, __ = create_user()
    user: User = User.query.filter(User.netid == netid).first()
    theia_session = create_assignment_ide(user)

    assert is_session_reserved(theia_session)


@with_context
def test_is_reserved_inactive(active_reserve_id):
    netid, _, __ = create_user()
    user: User = User.query.filter(User.netid == netid).first()
    theia_session = create_assignment_ide(user, reserved=False)

    assert not is_session_reserved(theia_session)


@with_context
def test_reserve_ide_for_students(active_reserve_id):
    reserve: ReservedIDETime = ReservedIDETime.query.filter(ReservedIDETime.id == active_reserve_id).first()
    course: Course = reserve.course
    assignment: Assignment = reserve.assignment
    students: list[User] = User.query.join(InCourse).filter(InCourse.course_id == course.id).all()

    # Make sure that students have all inactive IDEs
    for student in students:
        TheiaSession.query.filter(
            TheiaSession.owner_id == student.id,
        ).update({'active': False})
    db.session.commit()

    # Run reserve
    reserve_ide_for_students(reserve)

    db.session.flush()

    # Verify IDEs for each student
    for student in students:
        ide: TheiaSession = TheiaSession.query.filter(
            TheiaSession.active == True,
            TheiaSession.owner_id == student.id
        ).first()

        # Verify IDE exists, submission exists & is autograde
        assert ide is not None
        assert ide.submission_id is not None
        assert ide.autograde == True

        # Verify submission was created
        submission: Submission = ide.submission
        assert submission.assignment_id == assignment.id

        # Verify reserved
        assert is_session_reserved(ide)