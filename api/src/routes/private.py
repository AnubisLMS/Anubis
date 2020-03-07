from flask import request, redirect, url_for, flash, render_template, Blueprint, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from json import dumps
from datetime import datetime
from pytz import timezone
import dateutil.parser

from ..app import db
from ..config import Config
from ..models import Submissions, Reports, Student, Assignment
from ..utils import enqueue_webhook_job, log_event, send_noreply_email, esindex, jsonify

from .messages import err_msg, crit_err_msg, success_msg


private = Blueprint('private', __name__, url_prefix='/private')


def fix_dangling():
    """
    Should iterate through all dangling submissions, and see if
    student values now exist. Then enqueue them.
    """

    dangling=Submissions.query.filter_by(
        studentid=None
    ).all()

    fixed=[]

    for d in dangling:
        s=Student.query.filter_by(
            github_username=d.github_username
        ).first()
        d.student=s
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
    submission=Submissions.query.filter_by(
        id=req['submission_id'],
    ).first()

    submission.processed=True
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        print('ERROR unable to mark submission as processed, continuing to report the panic - {}'.format(submission.id))
        db.session.rollback()


    msg=crit_err_msg.format(
        netid=submission.netid,
        assignment=submission.assignment,
        commit=submission.commit,
    )

    esindex(
        'email',
        type='panic',
        msg=msg,
        submission=submission.id,
        assignment=submission.assignment.name,
        netid=submission.netid,
    )

    # Notify Student (without logs)
    send_noreply_email(
        msg,
        'OS3224 - Anubis Autograder Critical Error', # email subject
        submission.netid + '@nyu.edu',   # recipient
    )

    # Notify Admins (with logs)
    send_noreply_email(
        msg + req['error'],
        'Anubis Panic', # email subject
        Config.ADMINS,   # recipient
    )


    return jsonify({'success':True})



@private.route('/report-error', methods=['POST'])
@log_event('error-report', lambda: 'error was report from worker ' + dumps(request.json))
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
    submission=Submissions.query.filter_by(
        id=req['submission_id'],
    ).first()

    submission.processed=True
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        print('ERROR unable to mark submission as processed, continuing to report the error')
        db.session.rollback()

    msg=err_msg.format(
        netid=submission.netid,
        assignment=submission.assignment,
        commit=submission.commit,
        error=req['error'],
    )

    esindex(
        'email',
        type='error',
        msg=msg,
        submission=submission.id,
        assignment=submission.assignment.name,
        netid=submission.netid,
    )

    # Notify Student
    send_noreply_email(
        msg,
        'OS3224 - Anubis Autograder Error', # email subject
        submission.netid + '@nyu.edu',   # recipient
    )
    return jsonify({'success':True})


@private.route('/report', methods=['POST'])
@log_event('report', lambda: 'report from worker submitted for {}'.format(request.json['netid']))
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
    report=request.json

    submission=Submissions.query.filter_by(
        id=report['submission_id']
    ).first()


    submission.processed=True
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        print('ERROR unable to mark submission as processed {}'.format(submission.id))
        db.session.rollback()

    reports=[
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
        return jsonify({
            'success': False,
            'errors': [ 'unable to process report' ]
        })

    build = submission.builds[0]
    msg=success_msg.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment,
        report='\n\n'.join(str(r) for r in reports),
        test_logs=submission.tests[0].stdout,
        build=build.stdout,
    )

    esindex(
        'email',
        type='submission',
        msg=msg,
        submission=submission.id,
        assignment=submission.assignment.name,
        netid=submission.netid,
    )

    send_noreply_email(
        msg,
        'OS3224 - Anubis Autograder',
        submission.netid + '@nyu.edu'
    )

    return jsonify({
        'success': True
    })


@private.route('/ls')
@log_event('cli', lambda: 'ls')
def ls():
    """
    This route should hand back a json list of all submissions that are marked as
    not processed. Those submissions should be all activly enqueued or be running in tests.
    There is a chance that some of the submissions will be stale.
    """

    active = Submissions.query.filter(
        Submissions.studentid!=None,
        Submissions.processed==False,
    ).all()

    return jsonify([a.json for a in active])


@private.route('/dangling')
@log_event('cli', lambda: 'dangling')
def dangling():
    """
    This route should hand back a json list of all submissions that are dangling.
    Dangling being that we have no netid to match to the github username that
    submitted the assignment.
    """

    dangling = Submissions.query.filter(
        Submissions.studentid==None,
    ).all()
    dangling = [a.json for a in dangling]

    return jsonify({
        "success": True,
        "data": {
            "dangling": dangling,
            "count": len(dangling)
        }
    })


@private.route('/restart', methods=['POST'])
@log_event('cli', lambda: 'restart')
def restart():
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
    body = request.json

    netid = body['netid']

    student = Student.query.filter_by(netid=netid).first()
    if student is None:
        return jsonify({
            'success': False,
            'errors': ['Student does not exist']
        })

    if 'commit' in body:
        # re-enqueue specific submission

        submission = Submissions.query.filter_by(
            studentid=student.id,
            commit=body['commit'],
        ).first()
    else:
        # re-enqueue last submission

        submission = Submissions.query.filter_by(
            studentid=student.id,
        ).order_by(desc(Submissions.timestamp)).first()

    submission.processed = False
    reports = submission.reports
    builds = submission.builds

    for report in reports:
        db.session.delete(report)
    for build in builds:
        db.session.delete(build)

    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {
            'success': False
        }


    enqueue_webhook_job(submission.id)

    return jsonify({
        'success': True
    })


@private.route('/student', methods=['GET', 'POST'])
@log_event('cli', lambda: 'student')
def handle_student():
    """
    [{netid, github_username, first_name, last_name, email}]
    """
    if request.method == 'POST':
        body = request.json
        for student in body:
            s=Student.query.filter_by(netid=student['netid']).first()
            if s is None:
                s=Student(
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
                return jsonify({'success': False, 'errors': ['integ error']})
    return jsonify({
        'success': True,
        'data': list(map(
            lambda x: x.json,
            Student.query.all()
        )),
        'dangling': fix_dangling()
    })


@private.route('/fix-dangling')
@log_event('cli', lambda: 'fix-dangling')
def fix_dangling_route():
    return jsonify(fix_dangling())


@private.route('/assignment', methods=['POST'])
@log_event('cli', lambda: 'assignment')
def handle_assignment():
    """
    body = {
      action
      data {
        name
        due_date
        grace_date
      }
    }
    """
    data=request.json
    action=data['action']
    data=data['data']
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
            return jsonify({
                'success': False,
                'error': ['unable to commit']
            })
        return jsonify({
            'success': True,
            'msg': 'assignment created',
            'data': a.json
        })
    elif action == 'modify':
        a = Assignment.query.filter_by(name=data['name']).first()
        if a is None:
            return jsonify({
                'success': False,
                'error': ['assignment does not exist']
            })

        a.due_date=dateutil.parser.parse(data['due_date'], ignoretz=False),
        a.grace_date=dateutil.parser.parse(data['grace_date'], ignoretz=False)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': ['unable to delete']
            })

        return jsonify({
            'success': True,
            'msg': 'Assignment updated',
            'data': a.json,
        })
    elif action == 'ls':
        assignments = Assignment.query.all()
        return jsonify({
            'success': True,
            'data': list(map(lambda x: x.json, assignments))
        })
    return jsonify({
        'success': False,
        'error': ['invalid action']
    })


@private.route('/stats/<assignment_name>')
@private.route('/stats/<assignment_name>/<netid>')
@log_event('cli', lambda: 'stats')
def stats(assignment_name, netid=None):
    students = list(
        Student.query.all()
    ) if netid is None else [
        Student.query.filter_by(
            netid=netid
        ).first()
    ]

    bests = {}
    eastern = timezone('US/Eastern')

    assignment = Assignment.query.filter_by(name=assignment_name).first()
    if assignment is None:
        return jsonify({
            'success': False,
            'error': ['assignment does not exist']
        })

    for student in students:
        if student is None:
            return jsonify({
                "success": False,
                "erorr":"student does not exist",
            })
        best=None
        best_count=-1
        for submission in Submissions.query.filter_by(
                assignment=assignment,
                studentid=student.id,
                processed=True,
        ).all():
            correct_count = sum(map(
                lambda rep: 1 if rep.passed else 0,
                submission.reports
            ))

            if correct_count >= best_count:
                best = submission
        if best is None:
            # no submission
            bests[student.netid] = None
        else:
            build = len(best.builds) > 0
            best_count = sum(map(lambda x: 1 if x.passed else 0, best.reports))
            late = 'past due' if assignment.due_date < submission.timestamp else False
            late = 'past grace' if assignment.grace_date < submission.timestamp else late
            bests[student.netid] = {
                'submission': best.json,
                'builds': build,
                'reports': [rep.json for rep in best.reports],
                'total_tests_passed': best_count,
                'repo_url': best.repo,
                'late': late
            }
    return jsonify({
        "success": True,
        "data": bests
    })
