from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError
from json import dumps

from ..app import db
from ..models import Submissions, Reports, Events
from ..utils import log_event, send_noreply_email
private = Blueprint('private', __name__, url_prefix='/private')


def notify_student(submission):
    """
    TODO: implement email mechanism for reporting results to students
    """


@private.route('/')
def index():
    return 'super duper secret'


@private.route('/report-error', methods=['POST'])
@log_event('ERROR-REPORT', lambda: 'error report from worker ' + dumps(request.json))
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
      netid         : str - netid of student
      assignment    : str - name of assignment
      submission_id : int - database id for submission that was processed
      error         : str - description of error encountered
    }

    When this route is hit, we should mearly report the error back to the student
    through a noreply email.
    """
    req = request.json
    print(dumps(body, indent=2), flush=True)

    msg = """
    There was an error in grading your recent OS3224 submission.

    netid: {netid}
    assignment: {assignment}
    error: {error}
    """.format(
        netid=req['netid'],
        assignment=req['assignment'],
        error=req['error'],
    )

    send_noreply_email(
        msg,
        'OS3224 - Autograder Error', # email subject
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

    submission=Submissions(
        netid=report['netid'],
    )

    results=[
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
        for result in results:
            db.session.add(result)
        db.session.commit()
    except IntegrityError as e:
        print('ERROR unable to process report for {}'.format(report['netid']))
        return dumps({
            'success': False,
            'errors': [ 'unable to process report' ]
        })

    notify_student(submission)

    return {
        'success': True
    }
