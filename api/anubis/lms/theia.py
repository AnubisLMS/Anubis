import json
from datetime import datetime, timedelta

from anubis.models import TheiaSession
from anubis.utils.config import get_config_int
from anubis.utils.data import with_context
from anubis.utils.discord.webhook import send_webhook
from anubis.utils.email.event import send_email_event_admin


def get_active_theia_sessions(minutes: int = None) -> list[TheiaSession]:
    if minutes is None:
        theia_active_minutes_window: int = get_config_int('THEIA_ACTIVE_MINUTES_WINDOW', default=15)

    # Get all theia sessions within the last 10 minutes that are
    # active and don't have cluster_address
    theia_sessions: list[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.created > datetime.now() - timedelta(minutes=theia_active_minutes_window),
    ).all()

    return theia_sessions


@with_context
def check_cluster_ides():
    sessions = get_active_theia_sessions()
    now = datetime.now()

    for session in sessions:
        # Check for age
        age = now - session.created

        # Check if it is old
        old = age > timedelta(minutes=2)

        # Check for running
        running = session.state == 'Running'

        # Check for
        if old and not running:
            reference_id = 'ide_warning'
            state = session.state

            # Send email warning
            send_email_event_admin(
                reference_id,
                reference_id,
                reference_id,
                context={
                    'age':     age,
                    'now':     datetime.now(),
                    'session': json.dumps(session.data, indent=2),
                    'state':   state,
                }
            )

            # Send webhook
            send_webhook(f'Failed to start IDE within time :: {state}')
