"""
utils.py

This file contains some utility methods for reporting
"""


import json

def save_results(name, errors, passed):
    assert isinstance(name, str)
    assert isinstance(errors, list) or errors is None
    assert isinstance(passed, bool)

    with open('/mnt/submission/' + name + '-report.json', 'w') as f:
        json.dump({
            'name': name,
            'errors': errors,
            'passed': passed,
        }, f)

