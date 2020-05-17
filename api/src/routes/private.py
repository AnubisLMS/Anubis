from json import dumps, loads

import dateutil.parser
from flask import request, Blueprint
from sqlalchemy.exc import IntegrityError
import traceback

from .messages import err_msg, crit_err_msg, success_msg
from ..app import db, cache
from ..config import Config
from ..models import Submissions, Reports, Student, Assignment, Errors, FinalQuestions, StudentFinalQuestions
from ..utils import enqueue_webhook_job, log_event, send_noreply_email, esindex, json, regrade_submission

private = Blueprint('private', __name__, url_prefix='/private')


def fix_dangling():
    """
    Should iterate through all dangling submissions, and see if
    student values now exist. Then enqueue them.
    """

    dangling = Submissions.query.filter_by(
        studentid=None
    ).all()

    fixed = []

    for d in dangling:
        s = Student.query.filter_by(
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
                'student': s.json,
            })
            enqueue_webhook_job(d.id)
    return fixed


@private.route('/')
def index():
    return 'super duper secret'


@private.route('/report-panic', methods=['POST'])
@log_event('panic-report', lambda: 'panic was report from worker ' + dumps(request.json))
@json
def handle_report_panic():
    """
    This route will only be hit when there is a panic reported from a worker.
    The difference between an error and a panic is that a panic is an unexpected error.
    This could potentially mean that something in the pipeline is broken. This route
    will notify the admins of the error. We will also let the student know there was an
    error (not showing them the logs).

    request.json = {
      submission_id : int - database id for submission that was processed
      error         : str - description of error encountered
    }
    """

    req = request.json
    submission = Submissions.query.filter_by(
        id=req['submission_id'],
    ).first()

    submission.processed = True
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        print('ERROR unable to mark submission as processed, continuing to report the panic - {}'.format(
            submission.id
        ))
        db.session.rollback()

    msg = crit_err_msg.format(
        netid=submission.netid,
        assignment=submission.assignment,
        commit=submission.commit,
    )

    e = Errors(
        message=msg,
        submission=submission,
    )

    db.session.add(e)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    esindex(
        'email',
        type='panic',
        msg=msg,
        submission=submission.id,
        assignment=submission.assignment.name,
        netid=submission.netid,
    )

    # Notify Admins (with logs)
    send_noreply_email(
        msg + req['error'],
        'Anubis Panic',  # email subject
        Config.ADMINS,  # recipient
    )

    esindex(
        index='submission',
        processed=1,
        error=2,
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment.name,
        report=str(req['error']),
        passed=0
    )

    return {'success': True}


@private.route('/report-error', methods=['POST'])
@log_event('error-report', lambda: 'error was report from worker ' + dumps(request.json))
@json
def handle_report_error():
    """
    If at any point, a worker in the rq cluster encounters an error
    with grading an assignment, the worker should report to this endpoint.
    This does not necessarily mean that something is broken in the cluster.
    errors could include:

    - Clone errors
    - Build errors
    - Various docker errors

    The body of the post request should fit the shape:

    request.json = {
      submission_id : int - database id for submission that was processed
      error         : str - description of error encountered
    }

    When this route is hit, we should mearly report the error back to the student
    through a noreply email.
    """
    req = request.json
    submission = Submissions.query.filter_by(
        id=req['submission_id'],
    ).first()

    submission.processed = True
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        print('ERROR unable to mark submission as processed, continuing to report the error')
        db.session.rollback()

    msg = err_msg.format(
        netid=submission.netid,
        assignment=submission.assignment,
        commit=submission.commit,
        error=req['error'],
    )

    esindex(
        index='submission',
        processed=1,
        error=1,
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment.name,
        report=str(req['error']),
        passed=0
    )

    e = Errors(
        message=msg,
        submission=submission,
    )

    db.session.add(e)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return {
        'success': True
    }


@private.route('/report', methods=['POST'])
@log_event('report', lambda: 'report from worker submitted for {}'.format(request.json['netid']))
@json
def handle_report():
    """
    TODO redocument and reformat this

    This endpoint should only ever be hit by the rq workers. This is where
    they should be posting report jsons. We should document the results,
    then notify the student.

    The report json should follow this structure:

    report = {
      netid: str
      assignment: str
      results: [
        testname: str
        errors: str
        passed: true
      ]
    }
    """
    report = request.json

    submission = Submissions.query.filter_by(
        id=report['submission_id']
    ).first()

    submission.processed = True
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        print('ERROR unable to mark submission as processed {}'.format(submission.id))
        db.session.rollback()

    reports = [
        Reports(
            testname=result['name'],
            errors=dumps(result['errors']),
            passed=result['passed'],
            submission=submission,
        )
        for result in report['reports']
    ]

    try:
        for result in reports:
            db.session.add(result)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print('ERROR unable to process report for {}'.format(report['netid']))
        return {
            'success': False,
            'errors': ['unable to process report']
        }

    build = submission.builds[0]
    msg = success_msg.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment,
        report='\n\n'.join(str(r) for r in reports),
        test_logs=submission.tests[0].stdout,
        build=build.stdout,
    )

    esindex(
        index='submission',
        processed=1,
        error=0,
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment.name,
        report='\n\n'.join(str(r) for r in reports),
        passed=sum(1 if r.passed else 0 for r in reports)
    )

    return {
        'success': True
    }


@private.route('/ls')
@log_event('cli', lambda: 'ls')
@json
def ls():
    """
    This route should hand back a json list of all submissions that are marked as
    not processed. Those submissions should be all activly enqueued or be running in tests.
    There is a chance that some of the submissions will be stale.
    """

    active = Submissions.query.filter(
        Submissions.studentid != None,
        Submissions.processed == False,
    ).all()

    return [a.json for a in active]


@private.route('/dangling')
@log_event('cli', lambda: 'dangling')
@json
def dangling():
    """
    This route should hand back a json list of all submissions that are dangling.
    Dangling being that we have no netid to match to the github username that
    submitted the assignment.
    """

    dangling = Submissions.query.filter(
        Submissions.studentid == None,
    ).all()
    dangling = [a.json for a in dangling]

    return {
        "success": True,
        "data": {
            "dangling": dangling,
            "count": len(dangling)
        }
    }


@private.route('/regrade/<assignment_name>')
@log_event('cli', lambda: 'regrade')
@json
def regrade_all(assignment_name):
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
        return {
            'success': False,
            'error': ['cant find assignment']
        }

    submission = Submissions.query.filter_by(
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

    return {
        'success': True,
        'data': response
    }


@private.route('/student', methods=['GET', 'POST'])
@log_event('cli', lambda: 'student')
@json
def handle_student():
    """
    [{netid, github_username, first_name, last_name, email}]
    """
    if request.method == 'POST':
        body = request.json
        for student in body:
            s = Student.query.filter_by(netid=student['netid']).first()
            if s is None:
                s = Student(
                    netid=student['netid'],
                    github_username=student['github_username'],
                    name=student['name'] if 'name' in student else student['first_name'] + ' ' + student['last_name'],
                )
            else:
                s.github_username = student['github_username']
                s.name = student['name'] if 'name' in student else student['first_name'] + ' ' + student['last_name'],
            db.session.add(s)
            try:
                db.session.commit()
            except IntegrityError as e:
                print('integ err')
                return {
                    'success': False,
                    'errors': ['integ error']
                }
    return {
        'success': True,
        'data': list(map(
            lambda x: x.json,
            Student.query.all()
        )),
        'dangling': fix_dangling()
    }


@private.route('/fix-dangling')
@log_event('cli', lambda: 'fix-dangling')
@json
def fix_dangling_route():
    return fix_dangling()


@private.route('/assignment', methods=['POST'])
@log_event('cli', lambda: 'assignment')
@json
def handle_assignment():
    """
    This route is a catchall endpoint for creating, modifying or listing assignment data.
    Anubis needs assignment metadata for the due dates and grace dates of assignments. This
    endpoint should be hit by the api to create and modify those values. All timezones should
    be EST. The dateutil parser is used for paring datetime values, so the accepted datetime
    format is quite flexable.

    body = {
      action
      data {
        name
        due_date
        grace_date
      }
    }
    """
    data = request.json
    action = data['action']
    data = data['data']
    if action == 'add':
        a = Assignment(
            name=data['name'],
            due_date=dateutil.parser.parse(data['due_date'], ignoretz=False),
            grace_date=dateutil.parser.parse(data['grace_date'], ignoretz=False)
        )
        db.session.add(a)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {
                'success': False,
                'error': ['unable to commit']
            }
        return {
            'success': True,
            'msg': 'assignment created',
            'data': a.json
        }
    elif action == 'modify':
        a = Assignment.query.filter_by(name=data['name']).first()
        if a is None:
            return {
                'success': False,
                'error': ['assignment does not exist']
            }

        a.due_date = dateutil.parser.parse(data['due_date'], ignoretz=False),
        a.grace_date = dateutil.parser.parse(data['grace_date'], ignoretz=False)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {
                'success': False,
                'error': ['unable to delete']
            }

        return {
            'success': True,
            'msg': 'Assignment updated',
            'data': a.json,
        }
    elif action == 'ls':
        assignments = Assignment.query.all()
        return {
            'success': True,
            'data': list(map(lambda x: x.json, assignments))
        }
    return {
        'success': False,
        'error': ['invalid action']
    }


@cache.memoize(timeout=30)
def stats_for(studentid, assignmentid):
    best = None
    best_count = -1
    for submission in Submissions.query.filter_by(
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
    return [s.json for s in Student.query.all()]


@private.route('/stats/<assignment_name>')
@private.route('/stats/<assignment_name>/<netid>')
@log_event('cli', lambda: 'stats')
@cache.memoize(timeout=60, unless=lambda: request.args.get('netids', None) is not None)
@json
def stats(assignment_name, netid=None):
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
        return {
            'success': False,
            'error': ['assignment does not exist']
        }

    for student in students:
        submissionid = stats_for(student['id'], assignment.id)
        netid = student['netid']
        if submissionid is None:
            # no submission
            bests[netid] = None
        else:
            submission = Submissions.query.filter_by(
                id=submissionid
            ).first()
            build = len(submission.builds) > 0
            best_count = sum(map(lambda x: 1 if x.passed else 0, submission.reports))
            late = 'past due' if assignment.due_date < submission.timestamp else False
            late = 'past grace' if assignment.grace_date < submission.timestamp else late
            bests[netid] = {
                'submission': submission.json,
                'builds': build,
                'reports': [rep.json for rep in submission.reports],
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
    return {
        "success": True,
        "data": bests
    }


@private.route('/finalquestions', methods=['GET', 'POST'])
@log_event('cli', lambda: 'finalquestions')
@cache.memoize(timeout=60, unless=lambda: request.method == 'POST')
@json
def priv_finalquestions():
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
                print(question, flush=True, )
                if 'content' not in question or 'level' not in question:
                    db.session.rollback()
                    return invalid_format
                q = FinalQuestions.query.filter_by(content=question['content']).first()
                if q is not None:
                    # update level and solution if question exists
                    q.level = question['level']
                else:
                    q = FinalQuestions(
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

        r = StudentFinalQuestions.populate()
        if not r['success']:
            return r

    return {
        'data': {
            sfq.student.netid: sfq.json
            for sfq in StudentFinalQuestions.query.all()
        },
        'success': True
    }


@private.route('/overwritefq')
@log_event('cli', lambda: 'overwritefq')
@json
def priv_overwritefq():
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

    r = StudentFinalQuestions.populate(overwrite=True)

    if not r['success']:
        return r

    return {
        'data': {
            sfq.student.netid: sfq.json
            for sfq in StudentFinalQuestions.query.all()
        },
        'success': True
    }
