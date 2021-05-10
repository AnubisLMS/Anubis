from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any

import numpy as np
import pandas as pd

from anubis.models import Assignment, Submission, TheiaSession
from anubis.utils.data import is_debug
from anubis.utils.services.cache import cache


def get_submissions() -> pd.DataFrame:
    """
    Get all submissions from visible assignments, and put them in a dataframe

    :return:
    """
    # Get the submission sqlalchemy objects
    raw_submissions = Submission.query.join(Assignment).filter(Assignment.hidden == False).all()

    # Specify which columns we want
    columns = ['id', 'owner_id', 'assignment_id', 'processed', 'created']

    # Build a dataframe of from the columns we pull out of each submission object
    submissions = pd.DataFrame(
        data=list(map(lambda x: ({
            column: getattr(x, column)
            for column in columns
        }), raw_submissions)),
        columns=columns
    )

    # Round the submission timestamps to the nearest hour
    submissions['created'] = submissions['created'].apply(lambda date: pd.to_datetime(date).round('H'))

    return submissions


def get_theia_sessions() -> pd.DataFrame:
    """
    Get all theia session objects, and throw them into a dataframe

    :return:
    """

    # Get all the theia session sqlalchemy objects
    raw_theia_sessions = TheiaSession.query.all()

    # Specify which columns we want
    columns = ['id', 'owner_id', 'assignment_id', 'created', 'ended']

    # Build a dataframe of from the columns we pull out of each theia session object
    theia_sessions = pd.DataFrame(
        data=list(map(lambda x: ({
            column: getattr(x, column)
            for column in columns
        }), raw_theia_sessions)),
        columns=columns
    )

    # Round the timestamps to the nearest hour
    theia_sessions['created'] = theia_sessions['created'].apply(lambda date: pd.to_datetime(date).round('H'))
    theia_sessions['ended'] = theia_sessions['ended'].apply(lambda date: pd.to_datetime(date).round('H'))

    # Add a duration column
    if len(theia_sessions) > 0:
        # Get the duration from subtracting the end from the start time, and converting to minutes
        theia_sessions['duration'] = theia_sessions[['ended', 'created']].apply(
            lambda row: (row[0] - row[1]).seconds / 60, axis=1)

    # The apply breaks if there are no rows, so make it empty in that case
    else:
        theia_sessions['duration'] = []

    # Drop outliers based on duration
    theia_sessions = theia_sessions[
        np.abs(theia_sessions.duration - theia_sessions.duration.mean()) <= (3 * theia_sessions.duration.std())
    ]

    return theia_sessions


@cache.memoize(timeout=360)
def get_raw_submissions() -> List[Dict[str, Any]]:
    submissions_df = get_submissions()
    data = submissions_df.groupby(['assignment_id', 'created'])['id'].count() \
        .reset_index().rename(columns={'id': 'count'}).to_dict()
    data['created'] = {k: str(v) for k, v in data['created'].items()}

    assignment_ids = list(set(data['assignment_id'].values()))
    response = {}

    for assignment_id in assignment_ids:
        assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
        response[assignment_id] = {
            'data': [],
            'name': assignment.name,
            'release_date': str(assignment.release_date),
            'due_date': str(assignment.due_date),
        }

    for index, assignment_id in data['assignment_id'].items():
        response[assignment_id]['data'].append({
            'x': data['created'][index],
            'y': data['count'][index],
            'label': f"{data['created'][index]} {data['count'][index]}",
        })

    return list(response.values())


# def theia_propagate_usage(df: pd.DataFrame) -> pd.DataFrame:
#     # df.reset_index(inplace=True)
#     df.set_index('created', inplace=True, drop=True)
#     for created in df.index:
#         count = df.loc[created]['count']
#         assignment_id = df.loc[created]['assignment_id']
#         for i in range(1, 7):
#             idx = pd.to_datetime(created + timedelta(hours=i))
#             if idx in df.index:
#                 logger.info(df.loc[idx])
#                 df.loc[idx]['count'] += count
#             else:
#                 df.append(pd.DataFrame(
#                     [[assignment_id, count]],
#                     index=[idx],
#                     columns=df.columns,
#                 ))
#                 logger.info(df.loc[idx])
#         break
#     return df


@cache.memoize(timeout=420, unless=is_debug)
def get_usage_plot():
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    assignments = Assignment.query.filter(
        Assignment.hidden == False,
        Assignment.release_date <= datetime.now(),
    ).all()
    submissions = get_submissions()
    theia_sessions = get_theia_sessions()

    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    legend_handles0 = []
    legend_handles1 = []

    # submissions over hour line
    submissions.groupby(['assignment_id', 'created'])['id'] \
        .count().reset_index().rename(columns={'id': 'count'}).groupby('assignment_id') \
        .plot(x='created', label=None, ax=axs[0])

    # ides over hour line
    theia_sessions.groupby(['assignment_id', 'created'])['id'] \
        .count().reset_index().rename(columns={'id': 'count'}).groupby('assignment_id') \
        .plot(x='created', label=None, ax=axs[1])

    # assignment release line
    for color, assignment in zip(mcolors.TABLEAU_COLORS, assignments):
        legend_handles0.append(
            axs[0].axvline(
                x=assignment.due_date,
                color=color,
                linestyle='dotted',
                label=f'{assignment.name}',
            )
        )
        legend_handles1.append(
            axs[1].axvline(
                x=assignment.due_date,
                color=color,
                linestyle='dotted',
                label=f'{assignment.name}',
            )
        )

    utcnow = datetime.utcnow().replace(microsecond=0)

    axs[0].text(
        0.97, 0.9, f'Generated {utcnow} UTC',
        transform=axs[0].transAxes, fontsize=12, color='gray', alpha=0.5,
        ha='right', va='center',
    )
    axs[0].legend(handles=legend_handles0, loc='upper left')
    axs[0].set(title='Submissions over time', xlabel='time', ylabel='count')
    axs[0].grid(True)

    axs[1].text(
        0.97, 0.9, f'Generated {utcnow} UTC',
        transform=axs[1].transAxes, fontsize=12, color='gray', alpha=0.5,
        ha='right', va='center',
    )
    axs[1].legend(handles=legend_handles1, loc='upper left')
    axs[1].set(title='Cloud IDEs over time', xlabel='time', ylabel='count')
    axs[1].grid(True)

    file_bytes = BytesIO()

    fig.tight_layout()
    fig.patch.set_facecolor('white')
    plt.savefig(file_bytes)

    file_bytes.seek(0)

    return file_bytes.read()
