import requests
import json
import os


def report_error(error, netid, assignment, submission_id):
    """
    If at any point in the build/test cycle an error occurs,
    this is the function that should be used to report
    that error to the api.

    :error str: description of error to report
    :netid str: netid of student
    :assignment str: name of assignment
    :submission_id int: id for submission (possibly null)
    """
    return requests.post(
        'http://api:5000/private/report-error',
        headers={
            'Content-Type': 'application/json',
        },
        json={
            'netid':netid,
            'assignment': assignment,
            'submission_id': submission_id,
            'error': error
        }
    )



def report_results(working_dir, netid, assignment, submission_id):
    """
    This function should load all the results into a single report, and
    send it off to the api.

    This expects the individual report jsons to already exist in the current
    directory. Those jsons should end with -report.json.

    The report should be a json with the following shape:

    report = {
      netid: str
      assignment: str
      submission_id: int
      results: [
        testname: str
        errors: str
        stdout: str
        passed: true
      ]
    }

    :working_dir str: path to where report jsons are
    :netid str: netid of student
    :assignment str: name of assignement
    :submisssion_id: id of submission
    """

    old_working_dir=os.getcwd()
    os.chdir(working_dir)

    reports = []
    for filename in os.listdir('.'):
        if filename.endswith('-report.json'):
            reports.append(json.load(open(filename)))

    report = {
        'netid': netid,
        'assignment': assignment,
        'reports': reports,
    }

    res = requests.post(
        'http://api:5000/private/report',
        headers={
            'Content-Type': 'application/json',
        },
        json=report,
    )

    if res.status_code != 200 or not res.json['success']:
        os.chdir(old_working_dir)
        print('Error reporting to api')
        return False

    os.chdir(old_working_dir)

    return res.json


