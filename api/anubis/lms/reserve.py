import traceback
from datetime import datetime, timedelta

from anubis.ide.initialize import initialize_ide_for_assignment
from anubis.models import ReservedIDETime, TheiaSession, Course, InCourse, Assignment, User
from anubis.utils.exceptions import AssertError
from anubis.utils.logging import logger
from anubis.utils.redis import create_redis_lock


def get_active_reserves() -> list[ReservedIDETime]:
    now = datetime.now()
    return ReservedIDETime.query.filter(
        ReservedIDETime.start < now + timedelta(hours=1),
        ReservedIDETime.end > now,
    ).all()


def is_session_reserved(theia_session: TheiaSession) -> bool:
    if theia_session.assignment_id is None or theia_session.playground:
        return False

    now = datetime.now()
    return ReservedIDETime.query.filter(
        ReservedIDETime.start < now + timedelta(hours=1),
        ReservedIDETime.end > now,
        ReservedIDETime.assignment_id == theia_session.assignment_id,
    ).first() is not None


def get_active_reserved_sessions() -> list[TheiaSession]:
    active_reserves = get_active_reserves()
    assignment_ids = list(set(active_reserve.assignment_id for active_reserve in active_reserves))
    return TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.assignment_id.in_(assignment_ids),
    ).all()


def check_for_ide_resources(user: User, assignment: Assignment) -> TheiaSession | None:
    return TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.owner_id == user.id,
        TheiaSession.assignment_id == assignment.id
    ).first()


def reserve_ide_for_student(student: User, assignment: Assignment) -> TheiaSession:
    session = check_for_ide_resources(student, assignment)
    if session is not None:
        logger.info(f'Found existing session for {student}, skipping')
        return session

    logger.info(f'Initializing ide for {student}')

    try:
        return initialize_ide_for_assignment(student, assignment)
    except AssertError:
        logger.warning(f'{traceback.format_exc()}\nFailed to initialize IDE for {student}')


def reserve_ide_for_students(reserve: ReservedIDETime):
    course: Course = reserve.course
    assignment: Assignment = reserve.assignment
    students: list[User] = User.query.join(InCourse).join(Course).filter(
        Course.id == course.id,
        InCourse.owner_id == User.id,
    ).all()
    logger.info(f'Running reserve for {assignment}')

    lock = create_redis_lock(f'reserve-ide-{assignment.id}', auto_release_time=60.0)
    if not lock.acquire(blocking=False):
        logger.info(f'Failed to acquire lock, returning')
        return

    for student in students:
        reserve_ide_for_student(student, assignment)


def reserve_sync():
    active_reserves = get_active_reserves()

    for active_reserve in active_reserves:
        reserve_ide_for_students(active_reserve)
