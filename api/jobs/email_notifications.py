from datetime import datetime, timedelta
from typing import Callable

import googleapiclient.discovery

from anubis.google.service import build_google_service
from anubis.lms.assignments import get_active_assignment
from anubis.lms.courses import get_course_users
from anubis.models import Assignment, Course, User
from anubis.utils.data import with_context
from anubis.utils.email.event import send_email_event
from anubis.utils.logging import logger

now = datetime.now()

events = [
    {
        'condition':      lambda assignment: now - timedelta(days=1) < assignment.release_date < now,
        'reference_type': 'assignment_release',
        'template_key':   'assignment_release',
    },
    {
        'condition':      lambda assignment: now < assignment.due_date < now + timedelta(days=1),
        'reference_type': 'assignment_deadline',
        'template_key':   'assignment_deadline',
    },
]


def _send_assignment_condition_email_notifications(
    service: googleapiclient.discovery.Resource,
    recent_assignments: list[Assignment],
    condition: Callable[[Assignment], bool],
    template_key: str,
    reference_type: str
):
    for assignment in recent_assignments:
        course: Course = assignment.course
        students: list[User] = get_course_users(course)

        logger.info(f'Inspecting reference_type={reference_type} assignment_id={assignment.id} course_id={assignment.course_id} ')

        if not condition(assignment):
            logger.info(f'Condition not met for assignment, skipping')
            return

        else:
            logger.info(f'Condition met, sending email')

        logger.info(f'students = {students}')
        for student in students:
            context = {
                'user':       student,
                'assignment': assignment,
                'course':     course,
            }

            send_email_event(
                service,
                student,
                assignment.id,
                reference_type,
                template_key,
                context,
            )


@with_context
def email_notifications():
    recent_assignments = get_active_assignment()
    logger.info(f'recent_assignments = {str(recent_assignments)}')

    service = build_google_service(
        'google-gmail-creds',
        'gmail',
        'v1',
        ['https://www.googleapis.com/auth/gmail.send']
    )

    for event in events:
        _send_assignment_condition_email_notifications(
            service,
            recent_assignments,
            event['condition'],
            event['template_key'],
            event['reference_type'],
        )


if __name__ == "__main__":
    print("")
    print("""
             ___
            /   \\\\
       /\\\\ | . . \\\\
     ////\\\\|     ||
   ////   \\\\\\ ___//\\
  ///      \\\\      \\
 ///       |\\\\      |     
//         | \\\\  \\   \\    
/          |  \\\\  \\   \\   
           |   \\\\ /   /   
           |    \\/   /    
           |     \\\\/|     
           |      \\\\|     
           |       \\\\     
           |        |     
           |_________\\  

""")
    email_notifications()
