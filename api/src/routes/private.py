from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError
from json import dumps

from ..app import db
from ..config import Config
from ..models import Submissions, Reports, Events
from ..utils import log_event, send_noreply_email

from .messages import err_msg, crit_err_msg, success_msg


private = Blueprint('private', __name__, url_prefix='/private')


@private.route('/')
def index():
    return 'super duper secret'


@private.route('/report-error', methods=['POST'])
@log_event('PANIC-REPORT', lambda: 'panic was report from worker ' + dumps(request.json))
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



@private.route('/report-panic', methods=['POST'])
@log_event('ERROR-REPORT', lambda: 'error was report from worker ' + dumps(request.json))
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
@log_event('REPORT', lambda: 'report from worker submitted for {}'.format(request.json['netid']))
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

    print(dumps(report, indent=2), flush=True)

    submission=Submissions.query.filter_by(
        id=report['submission_id']
    ).first()

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
        db.session.add(submission)
        for result in reports:
            db.session.add(result)
        db.session.commit()
    except IntegrityError as e:
        print('ERROR unable to process report for {}'.format(report['netid']))
        return dumps({
            'success': False,
            'errors': [ 'unable to process report' ]
        })


    send_noreply_email(
        success_msg.format(
            netid=submission.netid,
            commit=submission.netid,
            assignment=submission.assignment,
            report='\n\n'.join(str(r) for r in reports)
        ),
        'OS3224 - Anubis Autograder',
        submission.netid + '@nyu.edu'
    )

    return {
        'success': True
    }
