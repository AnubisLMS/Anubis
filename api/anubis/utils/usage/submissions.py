from typing import Any

import pandas as pd

from anubis.models import Submission, Assignment
from anubis.utils.cache import cache


def get_submissions(course_id: str) -> pd.DataFrame:
    """
    Get all submissions from visible assignments, and put them in a dataframe

    :return:
    """
    # Get the submission sqlalchemy objects
    raw_submissions = (
        Submission.query.join(Assignment)
            .filter(
            Assignment.hidden == False,
            Assignment.course_id == course_id,
        )
            .all()
    )

    # Specify which columns we want
    columns = ["id", "owner_id", "assignment_id", "processed", "created"]

    # Build a dataframe of from the columns we pull out of each submission object
    submissions = pd.DataFrame(
        data=list(
            map(
                lambda x: ({column: getattr(x, column) for column in columns}),
                raw_submissions,
            )
        ),
        columns=columns,
    )

    # Round the submission timestamps to the nearest hour
    submissions["created"] = submissions["created"].apply(lambda date: pd.to_datetime(date).round("H"))

    return submissions


@cache.memoize(timeout=360)
def get_raw_submissions() -> list[dict[str, Any]]:
    submissions_df = get_submissions()
    data = (
        submissions_df.groupby(["assignment_id", "created"])["id"]
            .count()
            .reset_index()
            .rename(columns={"id": "count"})
            .to_dict()
    )
    data["created"] = {k: str(v) for k, v in data["created"].items()}

    assignment_ids = list(set(data["assignment_id"].values()))
    response = {}

    for assignment_id in assignment_ids:
        assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
        response[assignment_id] = {
            "data": [],
            "name": assignment.name,
            "release_date": str(assignment.release_date),
            "due_date": str(assignment.due_date),
        }

    for index, assignment_id in data["assignment_id"].items():
        response[assignment_id]["data"].append(
            {
                "x": data["created"][index],
                "y": data["count"][index],
                "label": f"{data['created'][index]} {data['count'][index]}",
            }
        )

    return list(response.values())
