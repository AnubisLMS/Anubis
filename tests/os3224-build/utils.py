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

