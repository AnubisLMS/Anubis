"""
Program:

1. Checks for any updates to class assignments
2. updates the class google calendar accordingly

Implementation:

 - Keep track of list of assignments
 - Every midnight, get updated list of all assignments and compare to previous list
 - Handled changes:
    - if inserted, create a new event
    - if deleted, delete an event

**Not sure if anubis has an "alter due date" functionality**
"""

from datetime import datetime, timedelta
from typing import Callable

from anubis.constants import REAPER_TXT
from anubis.lms.assignments import get_active_assignments
from anubis.lms.courses import get_course_users, get_active_courses, get_active_assigments
from anubis.models import Assignment, Course, User
from anubis.utils.data import with_context
from anubis.utils.logging import logger
import anubis.jobs.calendar_jobs # Need: list of assignemts per course, insert event/delete event to a specific calendar

now = datetime.now()

# Given a class id/name for input, returns a dictionary of updates (insert, time change, or deletion)

course_list = get_active_courses()
assignment_list = get_active_assignments() # current anubis assignments state

# create dictionary with courses as keys indexing lists of their assignments
course_assignment_list = {}
for course in course_list:
    course_assignment_mapping[course.id] = []
    for assignment in assignment_list:
        if course.id == assignment.course_id:
            course_assignment_mapping[course.id].append(assignment)

# get list of assignments per course

new_assignmnets = []
deleted_assignments = []

def check_assignment_updates_for_class():

    # FOR EACH course calendar, loop through returned calendar list of courses
    # compare assignment lists with respective course in course_assignment_list dictionary
    # append new assignments to new_assignments
    # append deleted_assignments to deleted_assignments

    return 0

def insert_assignments():

    # loop through new_assignments
    # use insert_assignment function to insert assignment to calendar
    
    return 0

def delete_assignment():
    
    # loop through deleted_assignments
    # use delete_assignment function to delete assignment from calendar
    return 0

    









