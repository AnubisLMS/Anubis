import requests
import json
import os


class PipelineException(Exception):
    pass


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
    requests.post(
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

    return PipelineException(error)



