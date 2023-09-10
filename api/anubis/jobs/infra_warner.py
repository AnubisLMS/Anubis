import json
import os
import time

if 'SENTRY_DSN' in os.environ:
    del os.environ['SENTRY_DSN']

from anubis.lms.theia import get_active_theia_sessions
from anubis.utils.data import with_context
from datetime import datetime, timedelta
from kubernetes import config
from anubis.utils.email.event import send_email_event_admin
from anubis.utils.discord.webhook import send_webhook


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
            reference_id = 'idewarning'
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


def main():
    config.load_incluster_config()

    while True:
        check_cluster_ides()
        time.sleep(1)


if __name__ == "__main__":
    main()
