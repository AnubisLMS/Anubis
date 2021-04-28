import base64
import json
import traceback
import urllib.parse
from typing import Union

from flask import request

from anubis.models import Course, TAForCourse, ProfessorForCourse
from anubis.utils.services.logger import logger
from anubis.utils.users.auth import LackCourseContext, current_user, AuthenticationError


def get_visible_courses():
    user = current_user()

    if user.is_superuser:
        return Course.query.all(), []

    ta_for = TAForCourse.query.filter(
        TAForCourse.owner_id == user.id,
    ).all()
    prof_for = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user.id
    ).all()

    ta_for_course_ids = list(map(lambda _x: _x.course_id, ta_for))
    prof_for_course_ids = list(map(lambda _x: _x.course_id, prof_for))

    ta_courses = Course.query.filter(Course.id.in_(ta_for_course_ids)).all()
    prof_courses = Course.query.filter(Course.id.in_(prof_for_course_ids)).all()

    return prof_courses, ta_courses


def get_course_context(full_stop: bool = True) -> Union[None, Course]:
    def _get_course_context():
        course_raw = request.cookies.get('course', default=None)
        if course_raw is None:
            return None

        try:
            course_data = json.loads(base64.urlsafe_b64decode(
                urllib.parse.unquote(course_raw).encode()
            ))
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.info(str(e))
            return None

        course_id = course_data.get('id', None)
        if course_id is None:
            return None

        if not is_course_admin(course_id):
            return None

        course = Course.query.filter(
            Course.id == course_id,
        ).first()

        return course

    context = _get_course_context()
    if context is None and full_stop:
        raise LackCourseContext()
    return context


def is_course_superuser(course_id: str) -> bool:
    user = current_user()
    if user.is_superuser:
        return True

    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user.id,
        TAForCourse.course_id == course_id,
    ).first()

    return prof is not None


def is_course_admin(course_id: str) -> bool:
    user = current_user()
    if user.is_superuser:
        return True

    ta = TAForCourse.query.filter(
        TAForCourse.owner_id == user.id,
        TAForCourse.course_id == course_id,
    ).first()
    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user.id,
        TAForCourse.course_id == course_id,
    ).first()

    return ta is not None or prof is not None


def assert_course_admin(course_id: str = None):
    if not is_course_admin(course_id):
        raise AuthenticationError('Admin privileges missing')


def assert_course_superuser(course_id: str = None):
    if not is_course_superuser(course_id):
        raise AuthenticationError('Admin privileges missing')


def assert_course_context(*expressions):
    if not all(expressions):
        raise LackCourseContext()