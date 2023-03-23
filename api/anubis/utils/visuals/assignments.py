from typing import Any

import numpy as np
import pandas as pd

from anubis.lms.submissions import get_submission_tests
from anubis.lms.autograde import bulk_autograde
from anubis.models import Assignment, AssignmentTest, Submission, TheiaSession, User, db
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job
from anubis.utils.visuals.queries import (
    assignment_test_fail_count_sql,
    assignment_test_fail_nosub_sql,
    assignment_test_pass_count_sql,
    time_to_pass_test_sql,
)


@cache.memoize(timeout=60, unless=is_debug)
def get_admin_assignment_visual_data(assignment_id: str) -> list[dict[str, Any]]:
    """
    Get the admin visual data for an assignment. Visual data is generated
    for each assignment test that is part of the assignment.

    :param assignment_id:
    :return:
    """

    # Get all the assignment tests for the specified assignment
    assignment_tests = AssignmentTest.query.filter(AssignmentTest.assignment_id == assignment_id).all()

    # Build a list of visual data for each assignment test
    response = []
    for assignment_test in assignment_tests:
        response.append(
            {
                "title": assignment_test.name,
                "pass_time_scatter": get_assignment_tests_pass_times(assignment_test),
                "pass_count_radial": get_assignment_tests_pass_counts(assignment_test),
            }
        )

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
    result = db.session.execute(
        time_to_pass_test_sql,
        {
            "assignment_id": assignment_test.assignment_id,
            "assignment_test_id": assignment_test.id,
        },
    )

    # Build a dataframe of the durations, converted to hours
    df = pd.DataFrame(
        data=[x[2].total_seconds() // 3600 for x in result.fetchall()],
        columns=["duration"],
    )

    # Drop outlier values (> 3 sigma)
    df = df[np.abs(df.duration - df.duration.mean()) <= (3 * df.duration.std())].value_counts().to_dict()

    # Return the x and y plot data for the scatter visual
    return [{"x": np.abs(x[0]), "y": y, "size": 3} for x, y in df.items()]


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
    result = db.session.execute(
        assignment_test_fail_nosub_sql,
        {
            "assignment_id": assignment_test.assignment_id,
            "assignment_test_id": assignment_test.id,
        },
    )
    n = result.fetchone()[0]
    nosub_count = int(n if n is not None else 0)

    # Run a query to find the number of students that failed the test
    result = db.session.execute(
        assignment_test_fail_count_sql,
        {
            "assignment_id": assignment_test.assignment_id,
            "assignment_test_id": assignment_test.id,
        },
    )
    n = result.fetchone()[0]
    fail_count = int(n if n is not None else 0)

    # Run a query to find the number of students that passed the test
    result = db.session.execute(
        assignment_test_pass_count_sql,
        {
            "assignment_id": assignment_test.assignment_id,
            "assignment_test_id": assignment_test.id,
        },
    )
    n = result.fetchone()[0]
    pass_count = int(n if n is not None else 0)

    # Format the response to fit what the frontend is expecting
    return [
        {"label": "no submission", "theta": nosub_count, "color": "grey"},
        {"label": "test failed", "theta": fail_count, "color": "red"},
        {"label": "test passed", "theta": pass_count, "color": "green"},
    ]


@cache.memoize(timeout=60, unless=is_debug, source_check=True)
def get_assignment_history(assignment_id, netid):
    """

    :param assignment_id:
    :param netid:
    :return:
    """

    assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    other = User.query.filter(User.netid == netid).first()

    db_theia_sessions = TheiaSession.query.filter(
        TheiaSession.owner_id == other.id, TheiaSession.assignment_id == assignment.id
    ).all()

    db_submissions = (
        Submission.query.filter(
            Submission.assignment_id == assignment.id,
            Submission.owner_id == other.id,
        )
            .order_by(Submission.created.desc())
            .all()
    )

    test_count = len(assignment.full_data["tests"])

    test_results = []
    build_results = []
    for db_submission in db_submissions:
        created = db_submission.created.replace(microsecond=0, second=0)
        build_passed = 1 if db_submission.build.passed else 0
        tests_passed = sum(
            map(
                lambda test: (1 if test["result"]["passed"] else 0),
                get_submission_tests(db_submission),
            )
        )

        test_results.append(
            {
                "x": str(created),
                "y": tests_passed,
                "total": test_count,
                "label": f"{tests_passed}/{test_count} tests passed",
            }
        )

        build_results.append(
            {
                "x": str(created),
                "y": build_passed,
                "label": "build passed" if build_passed == 1 else "build failed",
            }
        )

    return {
        "submissions": {
            "test_results": test_results,
            "build_results": build_results,
        },
        "dates": {
            "release_date": [{"x": str(assignment.release_date), "y": test_count}],
            "due_date": [{"x": str(assignment.due_date), "y": test_count}],
            "grace_date": [{"x": str(assignment.grace_date), "y": test_count}],
        },
    }


@cache.memoize(timeout=-1, source_check=True, forced_update=is_job)
def get_assignment_sundial(assignment_id):
    """
    Get the sundial data for a specific assignment. The basic breakdown of
    this data is:

    submission -> test -> {passed, failed}

    :param assignment_id:
    :return:
    """

    # Get the assignment
    assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    # Create base sundial
    sundial = {
        "children": [
            # Build Passed
            {
                "name": "build passed",
                "hex": "#8b0eea",
                "children": [
                    {
                        "name": test.name,
                        "hex": "#004080",
                        "children": [
                            # Test Passed
                            {"name": "passed", "hex": "#008000", "value": 0},
                            # Test Failed
                            {"name": "failed", "hex": "#800000", "value": 0},
                        ],
                    }
                    for test in assignment.tests
                ],
            },
            # Build Failed
            {
                "name": "build failed",
                "hex": "#f00",
                "value": 0,
            },
            # No Submission
            {
                "name": "no submission",
                "hex": "#808080",
                "value": 0,
            },
        ]
    }

    # Get the autograde results for the entire assignment. This
    # function call is cached.
    autograde_results = bulk_autograde(assignment_id, offset=0, limit=300)

    # Count the number of build and no submissions to
    # insert into the name label.
    build_passed = 0
    build_failed = 0
    no_submission = 0

    # Go through all the autograde results
    for result in autograde_results:

        # If there was no submission, then increment no submission
        if result["submission"] is None:
            no_submission += 1
            sundial["children"][2]["value"] += 1
            continue

        # If the build passed, go through the tests
        if result["build_passed"]:
            build_passed += 1

            # set of tests passed names
            tests_passed = set(result["tests_passed_names"])

            for index in range(len(sundial["children"][0]["children"])):
                # Get the test name
                test_name = sundial["children"][0]["children"][index]["name"]

                # If this student passed this test, then increment the tests passed value
                if test_name in tests_passed:
                    sundial["children"][0]["children"][index]["children"][0]["value"] += 1

                # If this student failed this test, then increment the tests failed value
                else:
                    sundial["children"][0]["children"][index]["children"][1]["value"] += 1

            continue

        # If the build failed, then skip the tests
        if not result["build_passed"]:
            # If the student failed the build, then we increment the failed build value
            build_failed += 1
            sundial["children"][1]["value"] += 1

            continue

    # Update the title for the high level names
    sundial["children"][0]["name"] = f"{build_passed} builds passed"
    sundial["children"][1]["name"] = f"{build_failed} builds failed"
    sundial["children"][2]["name"] = f"{no_submission} no submissions"

    # Update the title for the individual tests
    for test in sundial["children"][0]["children"]:
        passed = test["children"][0]
        failed = test["children"][1]
        passed_value = passed["value"]
        failed_value = failed["value"]

        passed["name"] = f"{passed_value} passed"
        failed["name"] = f"{failed_value} failed"

    return sundial
