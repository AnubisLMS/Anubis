from typing import List, Dict

from anubis.models import User, InCourse, Course
from anubis.utils.services.cache import cache
from anubis.utils.http.data import is_debug


@cache.memoize(timeout=60, unless=is_debug)
def get_students(course_code: str = None) -> List[Dict[str, dict]]:
    """
    Get students by course code. If no course code is specified,
    then all courses will be considered.

    * This response is cached for up to 60 seconds *

    :param course_code:
    :return:
    """

    # List of sqlalchemy filters
    filters = []

    # If a course code is specified, then add it to the filter
    if course_code is not None:
        filters = [Course.course_code == course_code]

    # Get all users, and break them into their data props
    return [
        s.data
        for s in User.query.join(InCourse).join(Course).filter(
            *filters
        ).all()
    ]


@cache.memoize(timeout=60, unless=is_debug)
def get_students_in_class(course_id, offset=None, limit=None):
    """
    Similar to the get_students function, this function
    gets all the students in a particular course. This function
    takes the course_id instead of the course code.

    * optionally accepts a offset and limit for the query *
    * This response is cached for up to 60 seconds *

    :param course_id:
    :param offset:
    :param limit:
    :return:
    """

    # If a limit and offset was specified, then use them
    # in the query.
    if offset is not None and limit is not None:
        # Get the users, and break them into their data props
        return [
            u.data
            for u in User.query.join(InCourse).join(Course).filter(
                Course.id == course_id,
                InCourse.owner_id == User.id,
            ).order_by(User.name.desc()).limit(limit).offset(offset).all()
        ]

    # Get the users, and break them into their data props
    return [
        u.data
        for u in User.query.join(InCourse).join(Course).filter(
            Course.id == course_id,
            InCourse.owner_id == User.id,
        ).order_by(User.name.desc()).all()
    ]
