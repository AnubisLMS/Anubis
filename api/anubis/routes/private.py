import json
import traceback
from typing import List

from dateutil.parser import parse as date_parse, ParserError
from flask import request, Blueprint, Response
from sqlalchemy import or_, and_

from anubis.models import Assignment
from anubis.models import Submission
from anubis.models import User
from anubis.models import db
from anubis.utils.auth import get_token
from anubis.utils.cache import cache
from anubis.utils.data import regrade_submission, is_debug
from anubis.utils.data import success_response, error_response
from anubis.utils.decorators import json_response, json_endpoint
from anubis.utils.elastic import log_endpoint
from anubis.utils.redis_queue import enqueue_webhook_rpc
from anubis.utils.logger import logger
from anubis.utils.data import fix_dangling

private = Blueprint('private', __name__, url_prefix='/private')


@cache.memoize(timeout=30)
def stats_for(student_id, assignment_id):
    # TODO rewrite this
    raise


@cache.cached(timeout=30)
def get_students():
    return [s.data for s in User.query.all()]


@private.route('/')
def private_index():
    return 'super duper secret'


if is_debug():
    @private.route('/token/<netid>')
    def private_token_netid(netid):
        user = User.query.filter_by(netid=netid).first()
        if user is None:
            return error_response('User does not exist')
        res = Response(json.dumps(success_response(get_token(user.netid))), headers={'Content-Type': 'application/json'})
        res.set_cookie('token', get_token(user.netid), httponly=True)
        return res


@private.route('/assignment/sync', methods=['POST'])
@log_endpoint('cli', lambda: 'assignment-sync')
@json_endpoint(required_fields=[('assignment', dict), ('tests', list)])
def private_assignment_sync(assignment_data: dict, tests: List[str]):
    logger.debug("/private/assignment/sync meta: {}".format(json.dumps(assignment_data, indent=2)))
    logger.debug("/private/assignment/sync tests: {}".format(json.dumps(tests, indent=2)))
    # Find the assignment
    a = Assignment.query.filter(
        Assignment.unique_code == assignment_data['unique_code']
    ).first()

    # Attempt to find the class
    c = Class_.query.filter(
        or_(Class_.name == assignment_data["class"],
            Class_.class_code == assignment_data["class"])
    ).first()
    if c is None:
        return error_response('Unable to find class')

    # Check if it exists
    if a is None:
        a = Assignment(unique_code=assignment_data['unique_code'])

    # Update fields
    a.name = assignment_data['name']
    a.hidden = assignment_data['hidden']
    a.description = assignment_data['description']
    a.pipeline_image = assignment_data['pipeline_image']
    a.class_ = c
    try:
        a.release_date = date_parse(assignment_data['date']['release'])
        a.due_date = date_parse(assignment_data['date']['due'])
        a.grace_date = date_parse(assignment_data['date']['grace'])
    except ParserError:
        logger.error(traceback.format_exc())
        return error_response('Unable to parse datetime'), 406

    db.session.add(a)
    db.session.commit()

    for i in AssignmentTest.query.filter(
    and_(AssignmentTest.assignment_id == a.id,
         AssignmentTest.name.notin_(tests))
    ).all():
        db.session.delete(i)
    db.session.commit()

    for test_name in tests:
        at = AssignmentTest.query.filter(
            Assignment.id == a.id,
            AssignmentTest.name == test_name,
        ).join(Assignment).first()
        
        if at is None:
            at = AssignmentTest(assignment=a, name=test_name)
            db.session.add(at)
            db.session.commit()

    return success_response({
        'assignment': a.data,
    })


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
        Submission.student_id == None,
    ).all()
    dangling = [a.data for a in dangling]

    return success_response({
        "dangling": dangling,
        "count": len(dangling)
    })


@private.route('/regrade/<assignment_name>')
@log_endpoint('cli', lambda: 'regrade')
@json_response
def private_regrade_assignment(assignment_name):
    """
    This route is used to restart / re-enqueue jobs.

    TODO verify fields that this endpoint is processing

    body = {
      netid
    }

    body = {
      netid
      commit
    }
    """
    assignment = Assignment.query.filter_by(
        name=assignment_name
    ).first()

    if assignment is None:
        return error_response('cant find assignment')

    submission = Submission.query.filter_by(
        assignment=assignment
    ).all()

    response = []

    for s in submission:
        res = regrade_submission(s)
        response.append({
            'submission': s.id,
            'commit': s.commit,
            'netid': s.netid,
            'success': res['success'],
        })

    return success_response({'submissions': response})


@private.route('/fix-dangling')
@log_endpoint('cli', lambda: 'fix-dangling')
@json_response
def private_fix_dangling():
    return fix_dangling()


@private.route('/stats/<assignment_name>')
@private.route('/stats/<assignment_name>/<netid>')
@log_endpoint('cli', lambda: 'stats')
@cache.memoize(timeout=60, unless=lambda: request.args.get('netids', None) is not None)
@json_response
def private_stats_assignment(assignment_name, netid=None):
    netids = request.args.get('netids', None)

    if netids is not None:
        netids = json.loads(netids)
    elif netid is not None:
        netids = [netid]
    else:
        netids = list(map(lambda x: x['netid'], get_students()))

    students = get_students()
    students = filter(
        lambda x: x['netid'] in netids,
        students
    )

    bests = {}

    assignment = Assignment.query.filter_by(name=assignment_name).first()
    if assignment is None:
        return error_response('assignment does not exist')

    for student in students:
        submissionid = stats_for(student['id'], assignment.id)
        netid = student['netid']
        if submissionid is None:
            # no submission
            bests[netid] = None
        else:
            submission = Submission.query.filter_by(
                id=submissionid
            ).first()
            build = len(submission.builds) > 0
            best_count = sum(map(lambda x: 1 if x.passed else 0, submission.reports))
            late = 'past due' if assignment.due_date < submission.timestamp else False
            late = 'past grace' if assignment.grace_date < submission.timestamp else late
            bests[netid] = {
                'submission': submission.data,
                'builds': build,
                'reports': [rep.data for rep in submission.reports],
                'total_tests_passed': best_count,
                'repo_url': submission.repo,
                'master': 'https://github.com/{}'.format(
                    submission.repo[submission.repo.index(':') + 1:-len('.git')],
                ),
                'commit_tree': 'https://github.com/{}/tree/{}'.format(
                    submission.repo[submission.repo.index(':') + 1:-len('.git')],
                    submission.commit
                ),
                'late': late
            }
    return success_response({'stats': bests})


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
        a1r1 = AssignmentRepo(owner=u, assignment=a1, repo_url='https://github.com/juan-punchman/xv6-public.git')
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
        a2r2 = AssignmentRepo(owner=u, assignment=a2, repo_url='https://github.com/os3224/assignment-1-spring2020.git')
        a2s1 = Submission(commit='2bc7f8d636365402e2d6cc2556ce814c4fcd1489', state='Waiting for resources...', owner=u, assignment=a2,
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

        enqueue_webhook_rpc(a2s1.id)

        return success_response('seeded')
