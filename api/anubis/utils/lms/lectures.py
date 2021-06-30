from typing import Optional, List

from anubis.utils.services.cache import cache
from anubis.models import User, LectureNotes
from anubis.utils.data import is_debug
from anubis.utils.lms.courses import get_student_course_ids


@cache.memoize(timeout=10, unless=is_debug, source_check=True)
def get_lecture_notes(user_id: str, course_id: Optional[str] = None):

    # Load user
    user = User.query.filter(User.id == user_id).first()

    # Verify user exists
    if user is None:
        return None

    # Get the list of course ids
    course_ids = get_student_course_ids(user, default=course_id)

    # Build a list of all the LectureNotes visible
    # to this user for each of the courses they are in.
    lecture_notes: List[LectureNotes] = LectureNotes.query.filter(
        LectureNotes.course_id.in_(course_ids),
        LectureNotes.hidden == False,
    ).order_by(LectureNotes.post_time.desc()).all()

    # Pass back the raw data
    return [lecture_note.data for lecture_note in lecture_notes]
