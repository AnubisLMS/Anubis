from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError
from json import dumps

from ..app import db
from ..models import Submissions, Reports, Events
from ..utils import log_event
private = Blueprint('private', __name__, url_prefix='/private')


def notify_student(submission):
    """
    TODO: implement email mechanism for reporting results to students
    """


@private.route('/')
def index():
    return 'super secret'


@private.route('/report-error', methods=['POST'])
@log_event('ERROR-REPORT', lambda: 'error report from worker submitted')
def handle_report_error():
    print(dumps(request.json, indent=2), flush=True)
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
