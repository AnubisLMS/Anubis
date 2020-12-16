from datetime import datetime
from typing import Union, List, Dict

from anubis.models import Class_, InClass, User, Assignment, Submission, AssignedStudentQuestion
from anubis.utils.auth import load_user
from anubis.utils.cache import cache
from anubis.utils.data import is_debug


@cache.memoize(timeout=60, unless=is_debug)
def get_classes(netid: str):
    """
    Get all classes a given netid is in

    :param netid:
    :return:
    """
    # Query for classes
    classes = Class_.query.join(InClass).join(User).filter(
        User.netid == netid
    ).all()

    # Convert to list of data representation
    return [c.data for c in classes]


@cache.memoize(timeout=60, unless=is_debug)
def get_assignments(netid: str, class_name=None) -> Union[List[Dict[str, str]], None]:
    """
    Get all the current assignments for a netid. Optionally specify a class_name
    to filter by class.

    :param netid: netid of user
    :param class_name: optional class name
    :return: List[Assignment.data]
    """
    # Load user
    user = load_user(netid)

    # Verify user exists
    if user is None:
        return None

    filters = []
    if class_name is not None:
        filters.append(Class_.name == class_name)

    assignments = Assignment.query.join(Class_).join(InClass).join(User).filter(
        User.netid == netid,
        Assignment.hidden == False,
        Assignment.release_date <= datetime.now(),
        *filters
    ).order_by(Assignment.due_date.desc()).all()

    a = [a.data for a in assignments]
    for assignment_data in a:
        assignment_data['has_submission'] = Submission.query.join(User).join(Assignment).filter(
            Assignment.id == assignment_data['id'],
            User.netid == netid,
        ).first() is not None

    return a


@cache.memoize(timeout=3, unless=is_debug)
def get_submissions(netid: str, class_name=None, assignment_name=None, assignment_id=None) -> Union[
    List[Dict[str, str]], None]:
    """
    Get all submissions for a given netid. Cache the results. Optionally specify
    a class_name and / or assignment_name for additional filtering.

    :param netid: netid of student
    :param class_name: name of class
    :param assignment_id: id of assignment
    :param assignment_name: name of assignment
    :return:
    """
    # Load user
    user = load_user(netid)

    # Verify user exists
    if user is None:
        return None

    # Build filters
    filters = []
    if class_name is not None:
        filters.append(Class_.name == class_name)
    if assignment_name is not None:
        filters.append(Assignment.name == assignment_name)
    if assignment_id is not None:
        filters.append(Assignment.id == assignment_id)

    owner = User.query.filter(User.netid == netid).first()
    submissions = Submission.query.join(Assignment).join(Class_).join(InClass).join(User).filter(
        Submission.owner_id == owner.id,
        *filters
    ).all()

    return [s.full_data for s in submissions]


@cache.memoize(timeout=60 * 60, unless=is_debug)
def get_assigned_questions(assignment_id: int, user_id: int):
    # Get assigned questions
    assigned_questions = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.assignment_id == assignment_id,
        AssignedStudentQuestion.owner_id == user_id,
    ).all()

    return [
        assigned_question.data
        for assigned_question in assigned_questions
    ]