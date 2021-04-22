import numpy as np
import pandas as pd

from anubis.models import db, AssignmentTest
from anubis.utils.services.cache import cache
from anubis.utils.visuals.queries import (
    time_to_pass_test_sql,
    assignment_test_fail_nosub_sql,
    assignment_test_fail_count_sql,
    assignment_test_pass_count_sql,
)
from anubis.utils.http.data import is_debug


@cache.memoize(timeout=60, unless=is_debug)
def get_assignment_visual_data(assignment_id: str):
    assignment_tests = AssignmentTest.query.filter(
        AssignmentTest.assignment_id == assignment_id
    ).all()

    response = []
    for assignment_test in assignment_tests:
        response.append({
            'title': assignment_test.name,
            'pass_time_scatter': get_assignment_tests_pass_times(assignment_test),
            'pass_count_radial': get_assignment_tests_pass_counts(assignment_test),
        })

    return response


def get_assignment_tests_pass_times(assignment_test: AssignmentTest):
    result = db.session.execute(time_to_pass_test_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    data = pd.DataFrame(
        data=[x[2].total_seconds() // 3600 for x in result.fetchall()],
        columns=['duration'],
    )
    # data = data[data['duration'] != 0]
    data = data[np.abs(data.duration - data.duration.mean()) <= (3 * data.duration.std())] \
        .value_counts().to_dict()

    return [
        {'x': np.abs(x[0]), 'y': y, 'size': 3}
        for x, y in data.items()
    ]


def get_assignment_tests_pass_counts(assignment_test: AssignmentTest):
    result = db.session.execute(assignment_test_fail_nosub_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    n = result.fetchone()[0]
    nosub_count = int(n if n is not None else 0)

    result = db.session.execute(assignment_test_fail_count_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    n = result.fetchone()[0]
    fail_count = int(n if n is not None else 0)

    result = db.session.execute(assignment_test_pass_count_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    n = result.fetchone()[0]
    pass_count = int(n if n is not None else 0)

    return [
        {'label': 'no submission', 'theta': nosub_count, 'color': 'grey'},
        {'label': 'test failed', 'theta': fail_count, 'color': 'red'},
        {'label': 'test passed', 'theta': pass_count, 'color': 'green'},
    ]
