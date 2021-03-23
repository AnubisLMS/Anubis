import numpy as np
import pandas as pd
from datetime import datetime
from io import BytesIO

from anubis.models import Assignment, Submission, TheiaSession
from anubis.utils.cache import cache
from anubis.utils.data import is_debug


def get_submissions() -> pd.DataFrame:
    raw_submissions = Submission.query.all()
    columns = ['id', 'owner_id', 'assignment_id', 'processed', 'created']
    submissions = pd.DataFrame(
        data=list(map(lambda x: ({
            column: getattr(x, column)
            for column in columns
        }), raw_submissions)),
        columns=columns
    )
    submissions['created'] = submissions['created'].apply(lambda date: pd.to_datetime(date).round('H'))
    return submissions


def get_theia_sessions() -> pd.DataFrame:
    raw_theia_sessions = TheiaSession.query.all()
    columns = ['id', 'owner_id', 'assignment_id', 'created', 'ended']
    theia_sessions = pd.DataFrame(
        data=list(map(lambda x: ({
            column: getattr(x, column)
            for column in columns
        }), raw_theia_sessions)),
        columns=columns
    )
    theia_sessions['created'] = theia_sessions['created'].apply(lambda date: pd.to_datetime(date).round('H'))
    theia_sessions['ended'] = theia_sessions['ended'].apply(lambda date: pd.to_datetime(date).round('H'))
    theia_sessions['duration'] = theia_sessions[['ended', 'created']].apply(
        lambda row: (row[0] - row[1]).seconds / 60, axis=1)
    theia_sessions = theia_sessions[
        np.abs(theia_sessions.duration - theia_sessions.duration.mean()) <= (3 * theia_sessions.duration.std())
    ]  # Drop outliers based on duration
    return theia_sessions


@cache.cached(timeout=300, unless=is_debug)
def get_usage_plot():
    import matplotlib.pyplot as plt

    assignments = Assignment.query.filter(
        Assignment.hidden == False,
        Assignment.release_date >= datetime.now(),
    ).all()
    submissions = get_submissions()
    theia_sessions = get_theia_sessions()

    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    # assignment release line
    for assignment in assignments:
        axs[0].axvline(x=assignment.release_date.date(), color='red', label=f'{assignment.name} release')
        axs[1].axvline(x=assignment.release_date.date(), color='red', label=f'{assignment.name} release')

    # submissions over hour line
    submissions.groupby(['assignment_id', 'created'])['id'] \
        .count().reset_index().rename(columns={'id': 'count'}).groupby('assignment_id') \
        .plot(x='created', y='count', label='submissions', ax=axs[0])

    # ides over hour line
    theia_sessions.groupby(['assignment_id', 'created'])['id'] \
        .count().reset_index().rename(columns={'id': 'count'}).groupby('assignment_id') \
        .plot(x='created', y='count', label='IDE sessions', color='green', ax=axs[1])

    axs[0].legend(loc='upper center')
    axs[0].set(title='Anubis usage over time', ylabel='count')
    axs[0].grid(True)

    axs[1].legend(loc='upper center')
    axs[1].set(ylabel='count')
    axs[1].grid(True)

    file_bytes = BytesIO()

    fig.tight_layout()
    fig.patch.set_facecolor('white')
    plt.savefig(file_bytes)

    file_bytes.seek(0)

    return file_bytes.read()
