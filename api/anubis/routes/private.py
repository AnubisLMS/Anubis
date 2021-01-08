import json
import traceback
from typing import List, Dict

from dateutil.parser import parse as date_parse, ParserError
from flask import request, Blueprint, Response
from sqlalchemy import or_, and_

from anubis.models import Assignment
from anubis.models import db, User, Submission
from anubis.rpc.batch import rpc_bulk_regrade
from anubis.rpc.theia import reap_all_theia_sessions
from anubis.utils.auth import get_token
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.data import split_chunks
from anubis.utils.data import success_response, error_response
from anubis.utils.decorators import json_response, json_endpoint, load_from_id
from anubis.utils.elastic import log_endpoint
from anubis.utils.logger import logger
from anubis.utils.redis_queue import enqueue_webhook, rpc_enqueue
from anubis.utils.students import get_students, bulk_stats
from anubis.utils.questions import hard_reset_questions, assign_questions, get_assigned_questions, get_all_questions
from anubis.utils.submissions import fix_dangling
from anubis.utils.assignments import assignment_sync

private = Blueprint('private', __name__, url_prefix='/private')


@private.route('/')
def private_index():
    return 'super duper secret'


@private.route('/token/<netid>')
def private_token_netid(netid):
    """
    For debugging, you can use this to sign in as the given user.

    :param netid:
    :return:
    """
    user = User.query.filter_by(netid=netid).first()
    if user is None:
        return error_response('User does not exist')
    token = get_token(user.netid)
    res = Response(json.dumps(success_response(token)), headers={'Content-Type': 'application/json'})
    res.set_cookie('token', token, httponly=True)
    return res


@private.route('/assignment/<int:id>/questions/get/<string:netid>')
@log_endpoint('cli', lambda: 'question get')
@load_from_id(Assignment, verify_owner=False)
@json_response
def private_assignment_id_questions_get_netid(assignment: Assignment, netid: str):
    """
    Get questions assigned to a given student.

    :param assignment:
    :param netid:
    :return:
    """
    user = User.query.filter_by(netid=netid).first()
    if user is None:
        return error_response('user not found')

    return success_response({
        'netid': user.netid,
        'questions': get_assigned_questions(assignment.id, user.id)
    })


@private.route('/questions/hard-reset/<string:unique_code>')
@log_endpoint('cli', lambda: 'question hard reset')
@json_response
def private_questions_hard_reset_unique_code(unique_code: str):
    """
    This endpoint should be used very sparingly. When this is hit,
    assuming the assignment exists, it will delete all questions
    for the given assignment. This is potentially very destructive,
    because you will not be able to get the question assignments
    back without a database backup.

    * If you chose to use this half way into an assignment without
    being able to reset, you will need to assign new questions to
    students! *

    If you end up needing to re-assign questions, this has the
    potential to create a great deal of confusion among students.

    ** Be careful with this one **

    :param unique_code:
    :return:
    """
    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response('Unable to find assignment')

    # Hard reset questions
    hard_reset_questions(assignment)

    return success_response({
        'status': 'questions deleted'
    })


@private.route('/questions/get/<string:unique_code>')
@log_endpoint('cli', lambda: 'questions get')
@json_response
def private_questions_get_unique_code(unique_code: str):
    """
    Get all questions for the given assignment.

    :param unique_code:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response('Unable to find assignment')

    return get_all_questions(assignment)


@private.route('/questions/assign/<string:unique_code>')
@log_endpoint('cli', lambda: 'question assign')
@json_response
def private_questions_assign_unique_code(unique_code: str):
    """
    Assign questions that have been created. This action will only run once.
    Once a question is assigned to a student, the only way to change it is
    by manually editing the database. This is by design to reduce confusion.

    Questions must already be created to use this.

    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response('Unable to find assignment')

    # Assign the questions
    assigned_questions = assign_questions(assignment)

    # Pass back the response
    return success_response({'assigned': assigned_questions})


@private.route('/assignment/sync', methods=['POST'])
@log_endpoint('cli', lambda: 'assignment-sync')
@json_endpoint(required_fields=[('assignment', dict)])
def private_assignment_sync(assignment_data: dict):
    """
    Sync assignment data from the CLI. This should be used to create and update assignment data.

    body = {
      "assignment": {
        "name": "{name}",
        "class": "CS-UY 3224",
        "hidden": true,
        "github_classroom_url": "",
        "unique_code": "{code}",
        "pipeline_image": "registry.osiris.services/anubis/assignment/{code}",
        "date": {
          "release": "{now}",
          "due": "{week_from_now}",
          "grace": "{week_from_now}"
        },
        "description": "This is a very long description that encompases the entire assignment\n",
        "questions": [
          {
            "sequence": 1,
            "questions": [
              {
                "q": "What is 3*4?",
                "a": "12"
              },
              {
                "q": "What is 3*2",
                "a": "6"
              }
            ]
          },
          {
            "sequence": 2,
            "questions": [
              {
                "q": "What is sqrt(144)?",
                "a": "12"
              }
            ]
          }
        ]
      }
    }

    response = {
      assignment : {}
      questions: {
        accepted: [ ... ]
        ignored: [ ... ]
        rejected: [ ... ]
      }
    }

    :param assignment_data:
    :param test_data:
    :param question_data:
    :return:
    """

    # Create or update assignment
    message, success = assignment_sync(assignment_data)

    # If there was an error, pass it back
    if not success:
        return error_response(message), 406

    # Return
    return success_response(message)


@private.route('/dangling')
@log_endpoint('cli', lambda: 'dangling')
@json_response
def private_dangling():
    """
    This route should hand back a json list of all submissions that are dangling.
    Dangling being that we have no netid to match to the github username that
    submitted the assignment.
    """

    dangling = Submission.query.filter(
        Submission.owner_id == None,
    ).all()
    dangling = [a.data for a in dangling]

    return success_response({
        "dangling": dangling,
        "count": len(dangling)
    })


@private.route('/reset-dangling')
@log_endpoint('reset-dangling', lambda: 'reset-dangling')
@json_response
def private_reset_dangling():
    resets = []
    for s in Submission.query.filter_by(owner_id=None).all():
        s.init_submission_models()
        resets.append(s.data)
    return success_response({'reset': resets})


@private.route('/regrade-submission/<commit>')
@log_endpoint('cli', lambda: 'regrade-commit')
@json_response
def private_regrade_submission(commit):
    """
    Regrade a specific submission via the unique commit hash.

    :param commit:
    :return:
    """

    # Find the submission
    s = Submission.query.filter(
        Submission.commit == commit,
        Submission.owner_id != None,
    ).first()
    if s is None:
        return error_response('not found')

    # Reset submission in database
    s.init_submission_models()

    # Enqueue the submission pipeline
    enqueue_webhook(s.id)

    # Return status
    return success_response({
        'submission': s.data,
        'user': s.owner.data
    })


@private.route('/regrade/<assignment_name>')
@log_endpoint('cli', lambda: 'regrade')
@json_response
def private_regrade_assignment(assignment_name):
    """
    This route is used to restart / re-enqueue jobs.

    The work required for this is potentially very IO entinsive
    on the database. We basically need to load the entire submission
    history out of the database, reset each, then re-enqueue them
    for processing. This makes resetting a single assignment actually
    very time consuming. For this we need to be a bit smart about how to
    handle this.

    We will split all submissions for the given assignment into
    chunks of 100. We can then push each of those chunks as a
    bulk_regrade job to the rpc workers.

    This solution isn't the fastest, but it gets the job done.

    :param assignment_name: name of assignment to regrade
    :return:
    """

    # Find the assignment
    assignment = Assignment.query.filter_by(
        name=assignment_name
    ).first()
    if assignment is None:
        return error_response('cant find assignment')

    # Get all submissions that have an owner (not dangling)
    submissions = Submission.query.filter(
        Submission.assignment_id == assignment.id,
        Submission.owner_id != None
    ).all()

    # Split the submissions into bite sized chunks
    submission_ids = [s.id for s in submissions]
    submission_chunks = split_chunks(submission_ids, 100)

    # Enqueue each chunk as a job for the rpc workers
    for chunk in submission_chunks:
        rpc_enqueue(rpc_bulk_regrade, chunk)

    # Pass back the enqueued status
    return success_response({'status': 'chunks enqueued'})


@private.route('/fix-dangling')
@log_endpoint('cli', lambda: 'fix-dangling')
@json_response
def private_fix_dangling():
    """
    Attempt to fix dangling. A dangling submission is one we can't match
    to a user. We can only see the github username when someone pushes.
    If we cant match that username to a user at that time, we create a
    dangling submission. That is a submission that has no owner. We create
    a submission in the database, but do not process it. Once we have
    the student github username, we'll need to check to see if
    we can find dangling submissions by them. That situation is what
    this endpoint is for.

    We go through all the existing dangling submissions and attempt to
    find a user for which the github username matches.

    :return:
    """
    return fix_dangling()


@private.route('/stats/<assignment_id>')
@private.route('/stats/<assignment_id>/<netid>')
@log_endpoint('cli', lambda: 'stats')
@json_response
def private_stats_assignment(assignment_id, netid=None):
    """
    Calculate result statistics for an assignment. This endpoint is
    potentially very IO and computationally expensive. We basically
    need to load the entire submission history out of the database
    for the given assignment, then do calculations per user. For
    this reason, much of the individual computations here are quite
    heavily cached.

    * Due to how heavily cached the stats calculations are, once cached
    they will not be updated until there is a cache bust after the
    timeout. *

    :param assignment_id:
    :param netid:
    :return:
    """
    netids = request.args.get('netids', None)
    force = request.args.get('force', False)

    if force is not False:
        cache.clear()

    if netids is not None:
        netids = json.loads(netids)
    elif netid is not None:
        netids = [netid]
    else:
        netids = list(map(lambda x: x['netid'], get_students()))

    bests = bulk_stats(assignment_id, netids)
    return success_response({'stats': bests})


@private.route('/submission/<int:id>')
@log_endpoint('cli', lambda: 'submission-stats')
@load_from_id(Submission, verify_owner=False)
@json_response
def private_submission_stats_id(submission: Submission):
    """
    Get absolutely everything we have for specific submission.

    * This is can be a lot of data *

    :param submission:
    :return:
    """

    return success_response({
        'student': submission.owner.data,
        'submission': submission.full_data,
        'assignment': submission.assignment.data,
        'questions': get_assigned_questions(submission.assignment.id, submission.owner.id),
        'class': submission.assignment.class_.data,
    })


@private.route('/ide/clear')
@log_endpoint('cli', lambda: 'clear-ide')
@json_response
def private_ide_clear():
    """
    Enqueue a job for the rpc workers to reap all the active
    theia submissions. They will end all active sessions in the
    database, then schedule all the kube resources for deletion.

    :return:
    """
    rpc_enqueue(reap_all_theia_sessions, tuple())

    return success_response({'state': 'enqueued'})


from anubis.models import SubmissionTestResult, SubmissionBuild
from anubis.models import AssignmentTest, AssignmentRepo, InClass, Class_

if is_debug():
    @private.route('/seed')
    @json_response
    def private_seed():
        # Yeet
        SubmissionTestResult.query.delete()
        SubmissionBuild.query.delete()
        Submission.query.delete()
        AssignmentRepo.query.delete()
        AssignmentTest.query.delete()
        InClass.query.delete()
        Assignment.query.delete()
        Class_.query.delete()
        User.query.delete()
        db.session.commit()

        # Create
        u = User(netid='jmc1283', github_username='juan-punchman', name='John Cunniff', is_admin=True)
        c = Class_(name='Intro to OS', class_code='CS-UY 3224', section='A', professor='Gustavo')
        ic = InClass(owner=u, class_=c)
        user_items = [u, c, ic]

        # Assignment 1 uniq
        a1 = Assignment(name='uniq', pipeline_image="registry.osiris.services/anubis/assignment/1",
                        hidden=False, release_date='2020-08-22 23:55:00', due_date='2020-08-22 23:55:00', class_=c,
                        github_classroom_url='')
        a1t1 = AssignmentTest(name='Long file test', assignment=a1)
        a1t2 = AssignmentTest(name='Short file test', assignment=a1)
        a1r1 = AssignmentRepo(owner=u, assignment=a1, repo_url='https://github.com/juan-punchman/xv6-public.git',
                              github_username='juan-punchman')
        a1s1 = Submission(commit='test', state='Waiting for resources...', owner=u, assignment=a1,
                          repo=a1r1)
        a1s2 = Submission(commit='0001', state='Waiting for resources...', owner=u, assignment=a1, repo=a1r1)
        assignment_1_items = [a1, a1t1, a1t2, a1r1, a1s1, a1s2]

        # Assignment 2 tail
        a2 = Assignment(name='tail', pipeline_image="registry.osiris.services/anubis/assignment/f1295ac4",
                        unique_code='f1295ac4',
                        hidden=False, release_date='2020-09-03 23:55:00', due_date='2020-09-03 23:55:00', class_=c,
                        github_classroom_url='')
        a2t1 = AssignmentTest(name='Hello world test', assignment=a2)
        a2t2 = AssignmentTest(name='Short file test', assignment=a2)
        a2t3 = AssignmentTest(name='Long file test', assignment=a2)
        a2r2 = AssignmentRepo(owner=u, assignment=a2, repo_url='https://github.com/os3224/assignment-1-spring2020.git',
                              github_username='juan-punchman')
        a2s1 = Submission(commit='2bc7f8d636365402e2d6cc2556ce814c4fcd1489', state='Waiting for resources...', owner=u,
                          assignment=a2,
                          repo=a1r1)
        assignment_2_items = [a2, a2t1, a2t2, a2t3, a2r2, a2s1]

        # Commit
        db.session.add_all(user_items)
        db.session.add_all(assignment_1_items)
        db.session.add_all(assignment_2_items)
        db.session.commit()

        # Init models
        a1s1.init_submission_models()
        a1s2.init_submission_models()
        a2s1.init_submission_models()

        enqueue_webhook(a2s1.id)

        return success_response('seeded')
