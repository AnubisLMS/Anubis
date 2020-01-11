"""
utils.py

This file contains some utility methods for reporting
"""


import json
import requests
import sys
import os


def save_results(testname, errors, stdout, passed):
    assert isinstance(name, str)
    assert isinstance(errors, list)
    assert isinstance(passed, bool)

    with open(name + '-report.json', 'w') as f:
        json.dump({
            'name': testname,
            'errors': errors,
            'passed': passed,
            'stdout': stdout,
        }, f)


def report_all(netid, assignment):
    """
    This function should load all the results into a single report, and
    send it off to the api.

    This expects the individual report jsons to already exist in the current
    directory. Those jsons should end with -report.json.

    The report should be a json with the following shape:

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
        'http://api/private/report',
        headers={
            'Content-Type': 'application/json',
        },
        json=report,
    )

