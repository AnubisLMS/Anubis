import requests
import argparse
import json
import os


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('netid', help='')
    parser.add_argument('assignment', help='')
    parser.add_argument('submission_id', help='')
    return parser.parse_args()


def report_results(netid, assignment, submission_id):
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
    os.chdir('/mnt/submission/')

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


def main():
    args = parse_args()
    report_results(
        args.netid,
        args.assignment,
        args.submission_id
    )

if __name__ == '__main__':
    main()
