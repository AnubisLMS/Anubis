import base64
import copy
import json
import string
import traceback
import urllib.parse
from typing import Union, Tuple, Any, List, Dict, Set

from flask import request, g
from werkzeug.local import LocalProxy

from anubis.models import (
    Course,
    TAForCourse,
    ProfessorForCourse,
    Assignment,
    AssignmentRepo,
    AssignedStudentQuestion,
    AssignmentQuestion,
    AssignmentTest,
    Submission,
    TheiaSession,
    StaticFile,
    User,
    InCourse,
    LateException,
    LectureNotes,
)
from anubis.utils.auth.user import current_user
from anubis.utils.data import is_debug
from anubis.utils.exceptions import AuthenticationError, LackCourseContext
from anubis.utils.cache import cache
from anubis.utils.logging import logger


def get_course_context(full_stop: bool = True) -> Union[None, Course]:
    """
    Get the course context for the current admin user. On the anubis website
    when a user is an admin, they have a context autocomplete at the top
    with all the courses they are admins for. When they select a course,
    it sets a course context cookie.

    This function pulls that information out of the cookie, verifies
    that the user is truly an admin for that course, then returns the
    corresponding Course object.

    The full_stop option is there to save time. When it is set,
    any discrepancy found (like say if the current user is not
    an admin for the course they have set) then a LackCourseContext
    exception will be raised. When this happens, there is a high
    level wrapper that handles returns a 400 to the user saying
    they lack the proper course context / privileges.

    :param full_stop:
    :return:
    """

    def _get_course_context():
        """
        Putting this in a separate function made handling the
        full_stop option slightly easier.

        :return:
        """

        # Get the raw course cookie string
        course_raw = request.cookies.get('course', default=None)

        # If there is no cookie set, then return None
        if course_raw is None:
            return None

        # Attempt to urllib unquote, base64 decode, then json loads
        # the raw cookie. There is a lot that can go wrong here, so
        # just handle any exceptions.
        try:
            course_data = json.loads(base64.urlsafe_b64decode(
                urllib.parse.unquote(course_raw).encode()
            ))
        except Exception as e:
            # Print the exception traceback
            logger.error(traceback.format_exc())
            logger.error(str(e))
            return None

        # Get the course id from the loaded course data
        course_id = course_data.get('id', None)

        # If there was no id in the course data, then return None
        if course_id is None:
            return None

        # Verify that the current user is actually an admin for
        # this course.
        if not is_course_admin(course_id):
            if full_stop:
                raise AuthenticationError()
            return None

        # Get the course object
        course = Course.query.filter(
            Course.id == course_id,
        ).first()

        # And return it
        return course

    # Get the current course context
    if 'course_context' not in g:
        _course_context = _get_course_context()
        g.course_context = _course_context

    # If full_stop is on, then verify we got a valid context,
    # or raise a LackCourseContext.
    if g.course_context is None and full_stop:
        raise LackCourseContext()

    # Return the course context
    return g.course_context


def is_course_superuser(course_id: str, user_id: str = None) -> bool:
    """
    Use this function to verify if the current user is a superuser for
    the specified course_id. A user is a superuser for a course if they are
    a professor, or if they are a superuser.

    :param course_id:
    :param user_id:
    :return:
    """

    # Get the current user
    if user_id is None:
        user = current_user
    else:
        user = User.query.filter(User.id == user_id).first()

    # If they are a superuser, then we can just return True
    if user.is_superuser:
        return True

    # Check to see if they are a professor for the current course
    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user.id,
        ProfessorForCourse.course_id == course_id,
    ).first()

    # Return True if they are a professor for the course
    return prof is not None


def is_course_admin(course_id: str, user_id: str = None) -> bool:
    """
    Use this function to verify if the current user is an admin for
    the specified course_id. A user is an admin for a course if they are
    a ta, professor, or if they are a superuser.

    :param course_id:
    :param user_id:
    :return:
    """

    # Get the current user
    if user_id is None:
        user = current_user
    else:
        user = User.query.filter(User.id == user_id).first()

    # If they are a superuser, then just return True
    if user.is_superuser:
        return True

    # Check to see if they are a TA for the course
    ta = TAForCourse.query.filter(
        TAForCourse.owner_id == user.id,
        TAForCourse.course_id == course_id,
    ).first()

    if ta is not None:
        return True

    # Check to see if they are a professor for the course
    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user.id,
        ProfessorForCourse.course_id == course_id,
    ).first()

    if prof is not None:
        return True

    return False


def assert_course_admin(course_id: str = None):
    """
    Use this function to assert that the current user is
    an admin for the specified course. If they are not, then
    an authentication error will be raised.

    The AuthenticationError will be handled in a high level
    flask view wrapper that will return whatever string we
    put as the message for the authentication error.

    :param course_id:
    :return:
    """
    if not is_course_admin(course_id):
        raise LackCourseContext('Requires course TA permissions')


def assert_course_superuser(course_id: str = None):
    """
    Use this function to assert that the current user is
    a superuser for the specified course. If they are not, then
    an authentication error will be raised.

    The AuthenticationError will be handled in a high level
    flask view wrapper that will return whatever string we
    put as the message for the authentication error.

    :param course_id:
    :return:
    """
    if not is_course_superuser(course_id):
        raise LackCourseContext('Requires course Professor permissions')


def assert_course_context(*models: Tuple[Any]):
    """
    This function checks that all the sqlalchemy objects that are
    passed to this function are within the current course context.
    If they are not, then a LackCourseContext will be raised.

    :param models:
    :return:
    """

    # Get the current course context
    context = get_course_context()

    # Create a stack of objects to check
    object_stack = list(models)

    # This next bit of code definitely deserves an explanation. Most
    # all the sqlalchemy models have some relationship or backref
    # that leads to a course object. What I am doing here is using a
    # stack to continuously access the next backref or relationship
    # until we get to a course object.
    #
    # Since the majority of models have either an .assignment or
    # .course backref, we can simplify things a bit by iterating
    # over all the model types that have the same name for the next
    # relationship or backref to access.

    # Iterate until the stack is empty
    while len(object_stack) != 0:
        model = object_stack.pop()

        # If the model is a course, then we can actually do the context check
        if isinstance(model, Course):

            # Check that the current user is an admin for the course object
            if not is_course_admin(model.id):
                raise LackCourseContext('You cannot edit resources in this course context')

            # Verify that the course object is the same as the set context
            if model.id != context.id:
                raise LackCourseContext('Cannot view or edit resource outside course context')

        # Group together all the models that have an
        # assignment backref or relationship
        for model_type in [
            Submission,
            AssignmentTest,
            AssignmentRepo,
            AssignedStudentQuestion,
            AssignmentQuestion,
            LateException,
        ]:
            if isinstance(model, model_type):
                object_stack.append(model.assignment)
                continue

        # Group together all the models that have a course
        # backref or relationship
        for model_type in [
            Assignment,
            StaticFile,
            TheiaSession,
            LectureNotes,
        ]:
            if isinstance(model, model_type):
                object_stack.append(model.course)
                continue

        # ---------------------------------
        # If the model is a user then we need to handle it a
        # little differently. We'll just need to verify that
        # the student is in the course.
        if isinstance(model, User):

            # Get course student is in
            in_course = InCourse.query.filter(
                InCourse.owner_id == model.id,
                InCourse.course_id == context.id,
            ).first()

            # Verify that they are in the course
            if in_course is None:
                raise LackCourseContext('Student is not within this course context')


def valid_join_code(join_code: str) -> bool:
    """
    Validate code to make sure that all the characters are ok.

    :param join_code:
    :return:
    """

    # Create a valid charset from all ascii letters and numbers
    valid_chars = set(string.ascii_letters + string.digits)

    # Make sure the join code is 6 chars long, and
    # all the chars exist in the valid_chars set.
    return all(c in valid_chars for c in join_code)


@cache.memoize(timeout=60, unless=is_debug)
def get_courses(netid: str):
    """
    Get all classes a given netid is in

    :param netid:
    :return:
    """

    # Get user
    user = User.query.filter(User.netid == netid).first()

    # Get course ids
    course_ids = get_student_course_ids(user)

    # Query for classes
    classes = Course.query.filter(Course.id.in_(course_ids)).all()

    # Convert to list of data representation
    return [c.data for c in classes]


@cache.memoize(timeout=60, unless=is_debug)
def get_student_course_ids(user: User, default: str = None) -> List[str]:
    """
    Get the course ids for the courses that the user is in.

    :param user:
    :param default: 
    :return:
    """

    # Superuser
    if user.is_superuser:
        # Get all
        courses = Course.query.all()

        # List of course ids
        course_ids = list(map(lambda x: x.id, courses))

    # Regular User
    else:
        # Get all the courses the user is in
        in_courses = InCourse.query.join(Course).filter(
            InCourse.owner_id == user.id,
        ).all()

        # Build a list of course ids. If the user
        # specified a specific course, make a list
        # of only that course id.
        course_ids = list(set(in_course.course.id for in_course in in_courses))

    # If a default was specified, check
    if default is not None and default in course_ids:
        course_ids = [default]

    # Pass back list of course ids
    return course_ids


def get_user_permissions(user: User) -> Dict[str, Any]:
    """
    Get a user's `professor_for`, `ta_for`, and `admin_for` permissions

    :param user:
    :return:
    """

    # If the user is superuser, return all the permissions for every course
    if user.is_superuser:
        super_for = [
            {'id': course.id, 'name': course.name}
            for course in Course.query.all()
        ]
        return {
            "is_superuser": True,
            "is_admin": True,
            "professor_for": super_for,
            # super_for is deepcopied to avoid introducing exceptions
            # if further data processing is needed
            "ta_for": copy.deepcopy(super_for),
            "admin_for": copy.deepcopy(super_for),
        }

    professor_for = [pf.data for pf in user.professor_for_course]
    # A professor has the same permissions as a ta do
    ta_for = [taf.data for taf in user.ta_for_course] + professor_for
    # According to John's explanation in issue #115, `admin_for` should
    # actually be the same as `ta_for`. So `admin_for` now becomes a
    # redundant value and should be removed in the future
    admin_for = copy.deepcopy(ta_for)

    return {
        "is_superuser": False,
        "is_admin": len(admin_for) > 0,
        "professor_for": professor_for,
        "ta_for": ta_for,
        "admin_for": admin_for,
    }


@cache.memoize(timeout=60, unless=is_debug, source_check=True)
def get_courses_with_visuals() -> List[Dict[str, Any]]:
    """
    Get a list of the course data for courses with
    usage visuals enabled.

    :return: [
       Course.data,
       ...
    ]
    """

    # Query for courses with display_visuals on
    query = Course.query.filter(
        Course.display_visuals == True
    ).order_by(Course.course_code.desc())

    # Get the list of courses
    courses: List[Course] = query.all()

    # Break down course db objects into dictionary
    return [
        course.data for course in courses
    ]


@cache.memoize(timeout=60, unless=is_debug, source_check=True)
def get_user_admin_course_ids(user_id: str) -> Set[str]:
    admin_course_ids: Set[str] = set()

    # Check to see if they are a TA for the course
    ta: List[TAForCourse] = TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
    ).all()

    # Check to see if they are a professor for the course
    prof: List[ProfessorForCourse] = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
    ).all()

    for in_course in ta:
        admin_course_ids.add(in_course.course_id)

    for in_course in prof:
        admin_course_ids.add(in_course.course_id)

    return admin_course_ids


def get_user_course_ids(user: User) -> Tuple[Set[str], Set[str]]:
    # Get the list of course ids
    course_ids: Set[str] = set(get_student_course_ids(user))
    admin_course_ids: Set[str]

    # If they are a superuser, then just return True
    if user.is_superuser:
        admin_course_ids = set(map(lambda x: x.id, Course.query.all()))

    # Else calculate which courses they are an admin for
    else:
        admin_course_ids = get_user_admin_course_ids(user.id)

    return admin_course_ids, course_ids


@cache.memoize(timeout=3600, source_check=True, unless=is_debug)
def get_course_admin_ids(course_id: str) -> List[str]:
    """
    Get a list of course admin id values.

    * highly cached *

    :param course_id:
    :return:
    """

    # Query for the course
    course: Course = Course.query.filter(
        Course.id == course_id
    ).first()

    # If the course does not exist, then soft fail
    if course is None:
        return []

    # Query TAs
    tas: List[TAForCourse] = TAForCourse.query.filter(
        TAForCourse.course_id == course.id,
    ).all()

    # Query professors
    professors: List[ProfessorForCourse] = ProfessorForCourse.query.filter(
        ProfessorForCourse.course_id == course.id,
    ).all()

    # Generate list from the owner_id values from each list of users
    return list(map(lambda x: x.owner_id, tas)) + list(map(lambda x: x.owner_id, professors))


def get_course_users(course: Course) -> List[User]:
    """
    Get all users within the course. These are the User objects for
    each student, ta and professor in the course.

    * Assumes the InCourse table is up to date *

    :param course:
    :return:
    """
    return (
        User.query
            .join(InCourse, InCourse.owner_id == User.id)
            .filter(Course.id == course.id)
            .all()
    )


def get_course_tas(course: Course) -> List[User]:
    """
    Get all Users that are TAs for a given course.

    * Assumes the TAForCourse table is up to date *

    :param course:
    :return:
    """
    return (
        User.query
            .join(TAForCourse, TAForCourse.owner_id == User.id)
            .filter(Course.id == course.id)
            .all()
    )


def get_course_professors(course: Course) -> List[User]:
    """
    Get all Users that are Professors for a given course.

    * Assumes the ProfessorForCourse table is up to date *

    :param course:
    :return:
    """
    return (
        User.query
            .join(ProfessorForCourse, ProfessorForCourse.owner_id == User.id)
            .filter(Course.id == course.id)
            .all()
    )


def user_to_user_id_set(users: List[User]) -> Set[str]:
    """
    Convert a list of users to a set of user.ids.

    :param users:
    :return:
    """
    return set(map(lambda user: user.id, users))


course_context: Course = LocalProxy(get_course_context)
