import numpy as np
import pandas as pd
from typing import List, Any, Union, Dict

from anubis.models import db, AssignmentTest
from anubis.utils.data import is_debug
from anubis.utils.services.cache import cache
from anubis.utils.visuals.queries import (
    time_to_pass_test_sql,
    assignment_test_fail_nosub_sql,
    assignment_test_fail_count_sql,
    assignment_test_pass_count_sql,
)


@cache.memoize(timeout=60, unless=is_debug)
def get_admin_assignment_visual_data(assignment_id: str) -> List[Dict[str, Any]]:
    """
    Get the admin visual data for an assignment. Visual data is generated
    for each assignment test that is part of the assignment.

    :param assignment_id:
    :return:
    """

    # Get all the assignment tests for the specified assignment
    assignment_tests = AssignmentTest.query.filter(
        AssignmentTest.assignment_id == assignment_id
    ).all()

    # Build a list of visual data for each assignment test
    response = []
    for assignment_test in assignment_tests:
        response.append({
            'title': assignment_test.name,
            'pass_time_scatter': get_assignment_tests_pass_times(assignment_test),
            'pass_count_radial': get_assignment_tests_pass_counts(assignment_test),
        })

    return response


def get_assignment_tests_pass_times(assignment_test: AssignmentTest):
    """
    Calculate the amount of time it took each student in the class
    to get their test to pass. This is measured as the time between
    their first submission for the assignment and the first submission
    that passed the specific test.

    :param assignment_test:
    :return:
    """

    # Run the very long query to generate the list of netids and timedetlas
    result = db.session.execute(time_to_pass_test_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })

    # Build a dataframe of the durations, converted to hours
    df = pd.DataFrame(
        data=[x[2].total_seconds() // 3600 for x in result.fetchall()],
        columns=['duration'],
    )

    # Drop outlier values (> 3 sigma)
    df = df[np.abs(df.duration - df.duration.mean()) <= (3 * df.duration.std())] \
        .value_counts().to_dict()

    # Return the x and y plot data for the scatter visual
    return [
        {'x': np.abs(x[0]), 'y': y, 'size': 3}
        for x, y in df.items()
    ]


def get_assignment_tests_pass_counts(assignment_test: AssignmentTest):
    """
    Get the number of students that had:
    - no submission
    - passed the test
    - failed the test
    for the specified test.

    The data from this function is turned into the pass counts
    radial donut on the autograde page.

    :param assignment_test:
    :return:
    """

    # Run a query to find the number of students with no submission
    result = db.session.execute(assignment_test_fail_nosub_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    n = result.fetchone()[0]
    nosub_count = int(n if n is not None else 0)

    # Run a query to find the number of students that failed the test
    result = db.session.execute(assignment_test_fail_count_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    n = result.fetchone()[0]
    fail_count = int(n if n is not None else 0)

    # Run a query to find the number of students that passed the test
    result = db.session.execute(assignment_test_pass_count_sql, {
        'assignment_id': assignment_test.assignment_id,
        'assignment_test_id': assignment_test.id,
    })
    n = result.fetchone()[0]
    pass_count = int(n if n is not None else 0)

    # Format the response to fit what the frontend is expecting
    return [
        {'label': 'no submission', 'theta': nosub_count, 'color': 'grey'},
        {'label': 'test failed', 'theta': fail_count, 'color': 'red'},
        {'label': 'test passed', 'theta': pass_count, 'color': 'green'},
    ]
