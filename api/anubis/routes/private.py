import traceback
from json import loads

from flask import request, Blueprint
from sqlalchemy.exc import IntegrityError

from anubis.models import Assignment, AssignmentQuestion, AssignedStudentQuestion
from anubis.models import Submission
from anubis.models import User
from anubis.models import db
from anubis.utils.auth import get_token
from anubis.utils.cache import cache
from anubis.utils.data import regrade_submission, is_debug
from anubis.utils.data import success_response, error_response
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.redis_queue import enqueue_webhook_rpc

private = Blueprint('private', __name__, url_prefix='/private')


def fix_dangling():
    """
    Should iterate through all dangling submissions, and see if
    student values now exist. Then enqueue them.
    """

    dangling = Submission.query.filter_by(
        studentid=None
    ).all()

    fixed = []

    for d in dangling:
        s = User.query.filter_by(
            github_username=d.github_username
        ).first()
        d.student = s
        db.session.add(d)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        if s is not None:
            fixed.append({
                'submission': d.json,
                'student': d.json,
            })
            enqueue_webhook_rpc(d.id)
    return fixed


@cache.memoize(timeout=30)
def stats_for(studentid, assignmentid):
    best = None
    best_count = -1
    for submission in Submission.query.filter_by(
    assignmentid=assignmentid,
    studentid=studentid,
    processed=True,
    ).all():
        correct_count = sum(map(
            lambda rep: 1 if rep.passed else 0,
            submission.reports
        ))

        if correct_count >= best_count:
            best = submission
    return best.id if best is not None else None


@cache.cached(timeout=30)
def get_students():
    return [s.data for s in User.query.all()]


@private.route('/')
def private_index():
    return 'super duper secret'


if is_debug():
    @private.route('/token/<netid>')
    @json_response
    def private_token_netid(netid):
        user = User.query.filter_by(netid=netid).first()
        if user is None:
            return error_response('User does not exist')
        return success_response(get_token(user.netid))


@private.route('/ls')
@log_endpoint('cli', lambda: 'ls')
@json_response
def private_ls():
    """
    This route should hand back a json list of all submissions that are marked as
    not processed. Those submissions should be all activly enqueued or be running in tests.
    There is a chance that some of the submissions will be stale.
    """

    active = Submission.query.filter(
        Submission.student_id != None,
        Submission.processed == False,
    ).all()

    return success_response({'processing': [a.data for a in active]})


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


@private.route('/student', methods=['GET', 'POST'])
@log_endpoint('cli', lambda: 'student')
@json_response
def private_student():
    """
    [{netid, github_username, first_name, last_name, email}]
    """
    if request.method == 'POST':
        body = request.json
        for student in body:
            s = User.query.filter_by(netid=student['netid']).first()
            if s is None:
                s = User(
                    netid=student['netid'],
                    github_username=student['github_username'],
                    name=student['name'] if 'name' in student else student['first_name'] + ' ' + student['last_name'],
                )
            else:
                s.github_username = student['github_username']
                s.name = student['name'] if 'name' in student else student['first_name'] + ' ' + student['last_name'],
            db.session.add(s)
            db.session.commit()
    return success_response({
        'students': list(map(
            lambda x: x.json,
            User.query.all()
        )),
        'dangling': fix_dangling()
    })


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
        netids = loads(netids)
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


@private.route('/finalquestions', methods=['GET', 'POST'])
@log_endpoint('cli', lambda: 'finalquestions')
@cache.memoize(timeout=60, unless=lambda: request.method == 'POST')
@json_response
def private_finalquestions():
    """
    This route should be used by the CLI to both get or modify / add
    existing questions. If the student final questions table is not
    populated (ie. uploading for the first time) the entire table will
    be populated with the existing questions. You will need to manually
    clear, then ret-rigger this to update student questions once they are
    populated. This is so that we don't ever overwrite a students questions
    after they are assigned them.

    response is json of shape:

    {
      data : {
        netid : {
          questions : [
            {
              id,
              content,
              solution,
              level
            },
            ...
          ],
          student : {
            id,
            netid,
            name,
            github_username
          },
          code
        },
        ...
      }
      success : true
    }

    or on failure:
    {
      success : false
      error : "..."
    }

    :return: json of shape specified above
    """

    # lets save these response messages to stay dry
    invalid_format = {
        'success': False,
        'error': 'invalid format'
    }

    unable_to_complete = {
        'success': False,
        'error': 'unable to complete'
    }

    # insert new questions and populate (if not already)
    if request.method == 'POST':
        if not (isinstance(request.json, list) and len(request.json) > 0):
            return invalid_format

        try:
            for question in request.json:
                if 'content' not in question or 'level' not in question:
                    db.session.rollback()
                    return invalid_format
                q = AssignmentQuestion.query.filter_by(content=question['content']).first()
                if q is not None:
                    # update level and solution if question exists
                    q.level = question['level']
                else:
                    q = AssignmentQuestion(
                        content=question['content'],
                        level=question['level'],
                    )
                if 'solution' in question:
                    q.solution = question['solution']

                db.session.add(q)

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            unable_to_complete['traceback'] = traceback.format_exc()
            return unable_to_complete

        r = AssignedStudentQuestion.populate()
        if not r['success']:
            return r

    return success_response({
        sfq.student.netid: sfq.data
        for sfq in AssignedStudentQuestion.query.all()
    })


@private.route('/overwritefq')
@log_endpoint('cli', lambda: 'overwritefq')
@json_response
def private_overwrite_final_question():
    """
    Use this route with extreme caution. Hitting this route will trigger all
    the data from the StudentFinalQuestion table to be repopulated with new
    values. This will not be callable from the api to avoid someone triggering
    this by accident.

    response is json of shape:

    {
      data : {
        netid : {
          questions : [
            {
              id,
              content,
              solution,
              level
            },
            ...
          ],
          student : {
            id,
            netid,
            name,
            github_username
          },
          code
        },
        ...
      }
      success : true
    }

    or on failure:
    {
      success : false
      error : "..."
    }

    :return: json of shape specified above
    """

    r = AssignedStudentQuestion.populate(overwrite=True)

    if not r['success']:
        return r

    return success_response({
        sfq.student.netid: sfq.data
        for sfq in AssignedStudentQuestion.query.all()
    })


from anubis.models import SubmissionTestResult, SubmissionBuild
from anubis.models import AssignmentTest, AssignmentRepo, InClass, Class_


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
    u = User(netid='jmc1283', github_username='juanpunchman', name='John Cunniff', is_admin=True)
    c = Class_(name='Intro to OS', class_code='CS-UY 3224', section='A', professor='Gustavo')
    ic = InClass(owner=u, class_=c)
    a = Assignment(name='Assignment1: uniq', pipeline_image="registry.osiris.services/anubis/assignment/1",
                   hidden=False, release_date='2020-08-22', due_date='2020-08-22', class_=c, github_classroom_url='')
    at1 = AssignmentTest(name='Long file test', assignment=a)
    at2 = AssignmentTest(name='Short file test', assignment=a)
    r = AssignmentRepo(owner=u, assignment=a, repo_url='https://github.com/juan-punchman/xv6-public.git')
    s1 = Submission(commit='2bc7f8d636365402e2d6cc2556ce814c4fcd1489', state='Enqueued', owner=u, assignment=a, repo=r)
    s2 = Submission(commit='0001', state='Enqueued', owner=u, assignment=a, repo=r)

    # Commit
    db.session.add_all([u, c, ic, a, at1, at2, s1, s2, r])
    db.session.commit()

    # Init models
    s1.init_submission_models()
    s2.init_submission_models()

    enqueue_webhook_rpc(s1.id)

    return {
        'u': u.data,
        'a': a.data,
        's1': s1.data,
    }