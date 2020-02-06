from flask import request, redirect, url_for, flash, render_template, Blueprint, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from json import dumps

from ..app import db
from ..config import Config
from ..models import Submissions, Reports, Events
from ..utils import enqueue_webhook_job, log_event, send_noreply_email

from .messages import err_msg, crit_err_msg, success_msg


private = Blueprint('private', __name__, url_prefix='/private')


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

    # Notify Student (without logs)
    send_noreply_email(
        msg,
        'OS3224 - Anubis Autograder Critical Error', # email subject
        req['netid'] + '@nyu.edu',   # recipient
    )

    # Notify Admins (with logs)
    send_noreply_email(
        msg + req['error'],
        'Anubis Panic', # email subject
        Config.ADMINS,   # recipient
    )


    return {'success':True}



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

    print(req)


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

    # Notify Student
    send_noreply_email(
        msg,
        'OS3224 - Anubis Autograder Error', # email subject
        req['netid'] + '@nyu.edu',   # recipient
    )
    return {'success':True}


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
            errors=result['errors'],
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
        return dumps({
            'success': False,
            'errors': [ 'unable to process report' ]
        })

    build = submission.builds[0]
    msg=success_msg.format(
        netid=submission.netid,
        commit=submission.netid,
        assignment=submission.assignment,
        report='\n\n'.join(str(r) for r in reports),
        build=build.stdout
    )

    print(msg, flush=True)

    send_noreply_email(
        msg,
        'OS3224 - Anubis Autograder',
        submission.netid + '@nyu.edu'
    )

    return {
        'success': True
    }


@private.route('/ls')
@log_event('cli', lambda: 'ls')
def ls():
    """
    This route should hand back a json list of all submissions that are marked as
    not processed. Those submissions should be all activly enqueued or be running in tests.
    There is a chance that some of the submissions will be stale.
    """

    active = Submissions.query.filter_by(
        processed=False,
    ).all()

    res = Response(dumps([a.json for a in active], indent=2))
    res.headers['Content-Type'] = 'application/json'
    return res


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
      assignment
      commit
    }
    """
    body = request.json

    netid = body['netid']

    if 'commit' in body:
        # re-enqueue specific submission

        submission = Submissions.query.filter_by(
            netid=netid,
            commit=body['commit'],
        ).first()
    else:
        # re-enqueue last submission

        submission = Submissions.query.filter_by(
            netid=netid,
        ).order_by(desc(Submissions.timestamp)).first()

    submission.processed = False

    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {
            'success': False
        }


    enqueue_webhook_job(submission.id)

    return {
        'success': True
    }


@private.route('/stats/<assignment>')
@private.route('/stats/<assignment>/<netid>')
@log_event('cli', lambda: 'stats ' + dumps(request.json))
def stats(assignment, netid=None):
    netids = list(map(
        lambda s: s.netid,
        Submissions.query.distinct(
            Submissions.netid
        ).all()
    )) if netid is None else [netid]

    bests = {}

    for netid in netids:
        best=None
        best_count=-1
        for submission in Submissions.query.filter_by(
                assignment=assignment,
                netid=netid,
        ).all():
            correct_count = sum(map(
                lambda rep: 1 if rep.passed else 0,
                submission.reports
            ))

            if correct_count >= best_count:
                best = submission
        build = best.builds[0].json if len(best.builds) > 0 else None
        bests[netid] = {
            'submission': best.json,
            'build': build,
            'reports': [rep.json for rep in best.reports],
            'total_tests_passed': best_count
        }

    res = Response(dumps(bests, indent=2))
    res.headers['Content-Type'] = 'application/json'
    return res
