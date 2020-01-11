from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError
from json import dumps

from ..app import db
from ..models import Submissions, Results, Events

private = Blueprint('private', __name__, url_prefix='/private')


def notify_student(submission):
    """
    TODO: implement email mechanism for reporting results to students
    """


@private.route('/')
def index():
    return 'super secret'


@private.route('/report', methods=['POST'])
@log_event('REPORT', lambda: 'report from worker submitted for {}'.format(request.json['netid']))
def handle_report():
    """
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
        stdout: str
        passed: true
      ]
    }
    """
    report=request.json

    submission=Submissions(
        netid=report['netid'],
    )

    results=[
        Results(
            testname=result['testname'],
            stdout=result['stdout'],
            errors=result['errors'],
            passed=result['passed'],
            submission=submission,
        )
        for result in report['results']
    ]


    try:
        db.session.add(submission)
        for result in results:
            db.session.add(results)
        db.session.commit()
    except IntegrityError as e:
        print('ERROR unable to process report for {}'.format(report['netid']))
        return dumps({
            'success': False,
            'errors': [ 'unable to process report' ]
        })

    notify_student(submission)

    return dumps({
        'success': True
    })
