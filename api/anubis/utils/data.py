from email.mime.text import MIMEText
from json import dumps
from os import environ
from smtplib import SMTP
from typing import List, Union, Dict, Tuple
from parse import parse

from flask import Response

from anubis.config import config
from anubis.models import User, Class_, InClass, Assignment, Submission, AssignmentRepo, AssignedStudentQuestion
from anubis.models import db
from anubis.utils.auth import load_user
from anubis.utils.cache import cache
from anubis.utils.redis_queue import enqueue_webhook_rpc


def is_debug() -> bool:
    """
    Returns true if the app is running in debug mode

    :return:
    """
    return config.DEBUG


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


def bulk_regrade_submission(submissions):
    """
    Regrade a batch of submissions
    :param submissions:
    :return:
    """
    response = []
    for submission in submissions:
        response.append(regrade_submission(submission))
    return response


def regrade_submission(submission):
    """
    Regrade a submission

    :param submission: Union[Submissions, int]
    :return: dict response
    """

    if isinstance(submission, int):
        submission = Submission.query.filter_by(id=submission).first()
        if submission is None:
            return error_response('could not find submission')

    if not submission.processed:
        return error_response('submission currently being processed')

    submission.processed = False
    submission.state = 'Waiting for resources...'
    submission.init_submission_models()

    enqueue_webhook_rpc(submission.id)

    return success_response({'message': 'regrade started'})


def jsonify(data, status_code=200):
    """
    Wrap a data response to set proper headers for json
    """
    res = Response(dumps(data))
    res.status_code = status_code
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = 'https://nyu.cool' \
        if not environ.get('DEBUG', False) \
        else 'https://localhost'
    return res


def error_response(error_message: str) -> dict:
    """
    Form an error REST api response dict.

    :param error_message: string error message
    :return:
    """
    return {
        'success': False,
        'error': error_message,
        'data': None,
    }


def success_response(data: Union[dict, str, None]) -> dict:
    """
    Form a success REST api response dict.

    :param data:
    :return:
    """
    return {
        'success': True,
        'error': None,
        'data': data,
    }


def send_noreply_email(message: str, subject: str, recipient: str):
    """
    Use this function to send a noreply email to a user (ie student).

    * This will only work on the computer that has the dns pointed to it (ie the server)

    If you set up the dns with namecheap, you can really easily just set
    the email dns setting to private email. Once that is set, it configures
    all the spf stuff for you. Doing to MX and spf records by hand are super
    annoying.

    eg:
    send_noreply_email('this is the message', 'this is the subject', 'netid@nyu.edu')

    :msg str: email body or message to send
    :subject str: subject for email
    :to str: recipient of email (should be their nyu email)
    """

    if environ.get('DEBUG', False):
        return print(message, subject, recipient, flush=True)

    message = MIMEText(message, "plain")
    message["Subject"] = subject

    message["From"] = "noreply@anubis.osiris.services"
    message["To"] = recipient

    s = SMTP("smtp")
    s.send_message(message)
    s.quit()


def notify(user: User, message: str, subject: str):
    """
    Send a noreply email to a user.

    :param user:
    :param message:
    :param subject:
    :return:
    """
    recipient = '{netid}@nyu.edu'.format(netid=user.netid)
    send_noreply_email(message, subject, recipient)


def fix_dangling():
    """
    Try to connect repos that do not have an owner.

    :return:
    """
    fixed = []

    dangling_repos = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == None
    ).all()
    for dr in dangling_repos:
        owner = User.query.filter(
            User.github_username == dr.github_username
        ).first()

        if owner is not None:
            dr.owner_id = owner.id
            db.session.add_all((dr, owner))
            db.session.commit()

            for s in dr.submissions:
                s.owner_id = owner.id
                db.session.add(s)
                db.session.commit()
                fixed.append(s.data)
                enqueue_webhook_rpc(s.id)

    dangling_submissions = Submission.query.filter(
        Submission.owner_id == None
    ).all()
    for s in dangling_submissions:
        dr = AssignmentRepo.query.filter(
            AssignmentRepo.id == s.assignment_repo_id
        ).first()

        owner = User.query.filter(
            User.github_username == dr.github_username
        ).first()

        if owner is not None:
            dr.owner_id = owner.id
            db.session.add_all((dr, owner))
            db.session.commit()

            s.owner_id = owner.id
            db.session.add(s)
            db.session.commit()
            fixed.append(s.data)
            enqueue_webhook_rpc(s.id)

    return fixed


@cache.memoize(timeout=300, unless=is_debug)
def stats_for(student_id, assignment_id):
    best = None
    best_count = -1
    for submission in Submission.query.filter(
    Submission.assignment_id == assignment_id,
    Submission.owner_id == student_id,
    Submission.processed == True,
    ).order_by(Submission.last_updated.desc()).all():
        correct_count = sum(map(lambda result: 1 if result.passed else 0, submission.test_results))

        if correct_count >= best_count:
            best_count = correct_count
            best = submission
    return best.id if best is not None else None


@cache.cached(timeout=60 * 60)
def get_students(class_name: str = 'Intro. to Operating Systems'):
    return [s.data for s in User.query.join(InClass).join(Class_).filter(
        Class_.name == class_name,
    ).all()]


@cache.cached(timeout=60 * 60)
def get_students_in_class(class_id):
    return [c.data for c in User.query.join(InClass).join(Class_).filter(
        Class_.id == class_id,
        InClass.owner_id == User.id,
    ).all()]


@cache.memoize(timeout=60 * 60, unless=is_debug)
def bulk_stats(assignment_id, netids=None):
    bests = {}

    assignment = Assignment.query.filter_by(name=assignment_id).first() or Assignment.query.filter_by(
        id=assignment_id).first()
    if assignment is None:
        return error_response('assignment does not exist')

    students = get_students_in_class(assignment.class_id)
    if netids is not None:
        students = filter(
            lambda x: x['netid'] in netids,
            students
        )

    for student in students:
        submission_id = stats_for(student['id'], assignment.id)
        netid = student['netid']
        if submission_id is None:
            # no submission
            bests[netid] = 'No successful submissions'
        else:
            submission = Submission.query.filter(
                Submission.id == submission_id
            ).first()
            repo_path = parse('https://github.com/{}', submission.repo.repo_url)[0]
            best_count = sum(map(lambda x: 1 if x.passed else 0, submission.test_results))
            late = 'past due' if assignment.due_date < submission.created else False
            late = 'past grace' if assignment.grace_date < submission.created else late
            bests[netid] = {
                'submission': submission.data,
                'build': submission.build.stat_data,
                'test_results': [submission_test_result.stat_data for submission_test_result in
                                 submission.test_results],
                'total_tests_passed': best_count,
                'master': 'https://github.com/{}'.format(repo_path),
                'commits': 'https://github.com/{}/commits/master'.format(repo_path),
                'commit_tree': 'https://github.com/{}/tree/{}'.format(repo_path, submission.commit),
                'late': late
            }

    return bests


def _verify_data_shape(data, shape, path=None) -> Tuple[bool, Union[str, None]]:
    """
    _verify_data_shape(
      {'data': []},
      {'data': list}
    ) == (True, None)

    _verify_data_shape(
      {'data': ''},
      {'data': list}
    ) == (False, '.data')

    _verify_data_shape(
      {'data': '', 'empty': 10},
      {'data': list}
    ) == (False, '.data')

    This function is what handles the data shape verification. You can use this function, or
    the decorator on uploaded data to verify its use before usage. You can basically write out
    what the shape should look like. This function supports nested dictionaries.

    Here, we will return a tuple of a boolean indicating success or failure, and a error string.
    If there was an error validating a given field, the error string will be a path to the
    unvalidated field. An example would be:

    _verify_data_shape(
      {'data': ''},
      {'data': list}
    ) -> (False, '.data')

    :return: success as bool, error path
    """

    if path is None:
        path = ""

    if shape is dict or shape is list:  # Free, just need a match
        if isinstance(data, shape):
            return True, None
        return False, path

    # Verify if data is constant
    for _t in [int, str, float]:
        if isinstance(data, _t):
            return (True, None) if shape == _t else (False, path)

    if isinstance(data, dict):  # Verify dict keys
        for s_key, s_value in shape.items():

            # Verify key is included
            if s_key not in data:
                return False, path + "." + s_key

            # Supported basic types
            for _t in [int, str, float]:

                # Check free strings are strings and lists
                if s_value is _t:
                    if not isinstance(data[s_key], s_value):
                        return False, path + "." + s_key

                # Check explicit strings and lists
                elif isinstance(s_value, _t):
                    if not isinstance(data[s_key], type(s_value)):
                        return False, path + "." + s_key

            # Recurse on other dicts
            if isinstance(s_value, dict):

                # Free dict ( no need to verify more )
                if s_value == dict:
                    return True, None

                # Explicit Dict ( need to recurse )
                elif isinstance(s_value, dict):
                    # Recurse on dict
                    r, e = _verify_data_shape(data[s_key], s_value, path + "." + s_key)

                    if r is False:
                        return r, e

                # Type s_value was not dict ( type mismatch )
                else:
                    return False, path + "." + s_key

            # Recurse on lists
            if isinstance(s_value, list):
                # Free list ( no need to verify more )
                if s_value == list:
                    return True, None

                # Explicit list ( need to recurse )
                elif isinstance(s_value, list):

                    # If we have a type specified in the list,
                    # we should iterate, then recurse on the
                    # elements of the data. Otherwise there's
                    # nothing to do.
                    if len(s_value) == 1:
                        s_value = s_value[0]

                        for item in data[s_key]:
                            # Recurse on list item
                            r, e = _verify_data_shape(
                                item, s_value, path + ".[" + s_key + "]"
                            )

                            if r is False:
                                return r, e

                # Type s_value was not dict ( type mismatch )
                else:
                    return False, path + "." + s_key

            if s_value is list or s_value is dict:
                if isinstance(data[s_key], s_value):
                    return True, None
                return (
                    False,
                    path + ".[" + s_key + "]"
                    if s_value is list
                    else path + "." + s_key + "",
                )

    return True, None


def split_chunks(lst, n):
    """
    Split lst into list of lists size n.

    :return: list of lists
    """
    _chunks = []
    for i in range(0, len(lst), n):
        _chunks.append(lst[i:i + n])
    return _chunks
