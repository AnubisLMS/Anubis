from datetime import datetime, timedelta

import pytest

from anubis.ide.initialize import initialize_ide_for_assignment
from anubis.lms.reserve import get_active_reserves, is_session_reserved
from anubis.models import db, ReservedIDETime, Assignment, User
from utils import with_context, create_user


def assignment_query():
    return Assignment.query.filter(Assignment.github_repo_required == False)


@pytest.fixture(scope="session")
@with_context
def assignment_id():
    assignment = assignment_query().order_by(Assignment.id).first()
    return assignment.id


@pytest.fixture(scope="session")
@with_context
def course_id():
    assignment = assignment_query().order_by(Assignment.id).first()
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
        assignment = assignment_query().order_by(Assignment.id).first()
    else:
        assignment = assignment_query().order_by(Assignment.id.desc()).first()
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
