from anubis.models import User, InCourse, Course
from anubis.utils.cache import cache
from anubis.utils.data import is_debug


@cache.cached(timeout=5, unless=is_debug)
def get_students(course_code=None):
    filters = []
    if course_code is not None:
        filters = [Course.course_code == course_code]
    return [
        s.data
        for s in User.query.join(InCourse).join(Course).filter(
            *filters
        ).all()
    ]


@cache.cached(timeout=5, unless=is_debug)
def get_students_in_class(class_id, offset=None, limit=None):
    if offset is not None and limit is not None:
        return [
            u.data
            for u in User.query.join(InCourse).join(Course).filter(
                Course.id == class_id,
                InCourse.owner_id == User.id,
            ).limit(limit).offset(offset).all()
        ]

    return [
        u.data
        for u in User.query.join(InCourse).join(Course).filter(
            Course.id == class_id,
            InCourse.owner_id == User.id,
        ).all()
    ]


