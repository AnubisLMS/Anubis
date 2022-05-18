import numpy as np
import pandas as pd
from datetime import datetime

from anubis.models import TheiaSession, Assignment


def get_theia_sessions(course_id: str = None, start: datetime = None) -> pd.DataFrame:
    """
    Get all theia session objects, and throw them into a dataframe

    When ``course_id`` is None will return playground sessions.

    :return:
    """

    filters = []

    if start is not None:
        filters.append(TheiaSession.created >= start)

    # Get all the theia session sqlalchemy objects
    if course_id is not None:
        raw_theia_sessions = TheiaSession.query.join(Assignment).filter(
            Assignment.course_id == course_id,
            *filters,
        ).all()
    else:
        raw_theia_sessions = TheiaSession.query.filter(
            TheiaSession.playground == True,
            *filters,
        ).all()

    # Specify which columns we want
    columns = ["id", "owner_id", "assignment_id", "image_id", "created", "ended"]

    # Build a dataframe of from the columns we pull out of each theia session object
    theia_sessions = pd.DataFrame(
        data=list(
            map(
                lambda x: ({column: getattr(x, column) for column in columns}),
                raw_theia_sessions,
            )
        ),
        columns=columns,
    )

    # Round the timestamps to the nearest hour
    theia_sessions["created"] = theia_sessions["created"].apply(lambda date: pd.to_datetime(date).round("H"))
    theia_sessions["ended"] = theia_sessions["ended"].apply(lambda date: pd.to_datetime(date).round("H"))

    # Add a duration column
    if len(theia_sessions) > 0:
        # Get the duration from subtracting the end from the start time, and converting to minutes
        theia_sessions["duration"] = theia_sessions[["ended", "created"]].apply(
            lambda row: (row[0] - row[1]).seconds / 60, axis=1
        )

    # The apply breaks if there are no rows, so make it empty in that case
    else:
        theia_sessions["duration"] = []

    # Drop outliers based on duration
    theia_sessions = theia_sessions[
        np.abs(theia_sessions.duration - theia_sessions.duration.mean()) <= (3 * theia_sessions.duration.std())
        ]

    return theia_sessions
