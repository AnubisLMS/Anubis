import requests
import json
import os

def report_all(netid, assignment, submission_id):
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
    """

    

    reports = []
    for filename in os.listdir('.'):
        if filename.endswith('-report.json'):
            reports.append(json.load(open(filename)))

    report = {
        'netid': netid,
        'assignment': assignment,
        'reports': reports,
    }

    requests.post(
        'http://api:5000/private/report',
        headers={
            'Content-Type': 'application/json',
        },
        json=report,
    )

