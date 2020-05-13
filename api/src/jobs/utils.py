import requests


class PipelineException(Exception):
    pass


def report_error(error, submission_id):
    """
    If at any point in the build/test cycle an error occurs,
    this is the function that should be used to report
    that error to the api.

    :error str: description of error to report
    :submission_id int: id for submission (possibly null)
    """
    requests.post(
        'http://api:5000/private/report-error',
        headers={
            'Content-Type': 'application/json',
        },
        json={
            'submission_id': submission_id,
            'error': error,
        }
    )

    return PipelineException(error)


def report_panic(error, submission_id):
    """
    If there is a panic in the test pipeline (ie an unexpected,
    potentially catostrophic error) then we should use this function
    to report it. This will notify the api, which will send an email
    to the cluster admins.

    :error str: description of error to report
    :submission_id int: id for submission (possibly null)
    """
    requests.post(
        'http://api:5000/private/report-panic',
        headers={
            'Content-Type': 'application/json',
        },
        json={
            'submission_id': submission_id,
            'error': error
        }
    )

    return PipelineException(error)
