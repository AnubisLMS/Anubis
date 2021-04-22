import numpy as np
import pandas as pd

from anubis.models import db, AssignmentTest
from anubis.utils.visuals.queries import time_to_pass_test_sql


def get_assignment_tests_pass_times(assignment_id: str):
    assignment_tests = AssignmentTest.query.filter(
        AssignmentTest.assignment_id == assignment_id
    ).all()

    response = {}
    for assignment_test in assignment_tests:
        result = db.session.execute(time_to_pass_test_sql, {
            'assignment_id': assignment_id,
            'assignment_test_id': assignment_test.id,
        })
        data = pd.DataFrame(
            data=[x[2].total_seconds() // 3600 for x in result.fetchall()],
            columns=['duration'],
        )
        # data = data[data['duration'] != 0]
        data = data[np.abs(data.duration - data.duration.mean()) <= (3 * data.duration.std())]\
            .value_counts().to_dict()
        response[assignment_test.name] = [
            {'x': np.abs(x[0]), 'y': y, 'size': 3}
            for x, y in data.items()
        ]

    return response
