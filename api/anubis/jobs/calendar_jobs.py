##Possible behaviours

#If an assignment event is created and then immediate edited, it might end up in the update_events at the same time as create_events
#Since this is implemented 


from datetime import datetime, timedelta
from typing import Callable

from anubis.constants import REAPER_TXT
from anubis.lms.assignments import get_active_assignments
from anubis.lms.courses import get_course_users
from anubis.models import Assignment, Course, User
from anubis.utils.data import with_context
#TODO: wait for event wrapper from pinhan
# from anubis.utils.email.event import send_email_event
from anubis.utils.logging import logger

now = datetime.now()

create_events = [
    {
        'condition': lambda assignment: now - timedelta(days=1) < assignment.release_date < now,
        'reference_type': 'assigment_release',
        'template_key': 'assignment_release',
    },
]

#TODO: add update_events as well 
# need to add a field to assignment smthg like last_modified and cal_event_id, check with TEO

def _create_assignment_condition_calendar(
    recent_assigments: list[Assignment],
    condition: Callable[[Assignment], bool],
    template_key: str,
    reference_type: str
):
    for assignment in recent_assignments:
        logger.info(f'{assignment=}')
        course: Course = assignment.course
        students: list[User] = get_course_users(course)

        logger.info(f'Inspecting assignment {reference_type=} {assignment.name=} {assignment.course.course_code=}')

        #TODO: Add calendar preference check for the assignment, same as gmail

        if not condition(assignment):
            logger.info(f'Condition not met for assignment, skipping')
            continue

        else:
            logger.info(f'Condition met, sending emails')

        logger.info(f'students = {students}')
        for student in students:
            context = {
                'user':       student,
                'assignment': assignment,
                'course':     course,
            }

            #TODO: Add calendar preference check for students, same as gmail

            logger.debug(f'Sending email for user based off preferences user_id={student.id}')

            #TODO: Pipeline into the google api wrapper, same as gmail


def calendar_jobs():
    recent_assignments = get_active_assigments()
    logger.info(f'recent_assigments = {str(recent_assignments)}')


    for event in create_events:
        _create_assignment_condition_calendar(
            recent_assigments,
            event['condition'],
            event['template_key'],
            event['reference_type'],
        )

if __name__ == "__main__":
    print(REAPER_TXT)

    calendar_jobs()