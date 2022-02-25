from typing import Dict, List

from anubis.models import Course, InCourse, User
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug, source_check=True)
def get_students(course_id: str = None) -> List[Dict[str, dict]]:
    """
    Get students by course code. If no course code is specified,
    then all courses will be considered.

    * This response is cached for up to 60 seconds *

    :param course_id:
    :return:
    """

    # List of sqlalchemy filters
    if course_id is not None:
        users = User.query.join(InCourse).filter(InCourse.course_id == course_id).all()
    else:
        users = User.query.all()

    # Get all users, and break them into their data props
    return [s.data for s in users]


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
            for u in User.query.join(InCourse)
                .join(Course)
                .filter(
                Course.id == course_id,
                InCourse.owner_id == User.id,
            )
                .order_by(User.name.desc())
                .limit(limit)
                .offset(offset)
                .all()
        ]

    # Get the users, and break them into their data props
    return [
        u.data
        for u in User.query.join(InCourse)
            .join(Course)
            .filter(
            Course.id == course_id,
            InCourse.owner_id == User.id,
        )
            .order_by(User.name.desc())
            .all()
    ]
