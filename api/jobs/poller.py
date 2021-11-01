import time
from typing import List
from datetime import datetime, timedelta

from kubernetes import config

from anubis.models import TheiaSession
from anubis.utils.data import with_context
from anubis.k8s.theia import update_theia_session


@with_context
def poller():
    """
    Poll Database for sessions created within the last 10 minutes
    if they are active and dont have a cluster_address.

    If the session is running match the pod to the cluster_address

    If the session has failed, update the session to failed.
    """
    # Get all theia sessions within the last 10 minutes that are 
    # active and dont have cluster_address
    theia_sessions: List[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.cluster_address == None,
        TheiaSession.created > datetime.now() - timedelta(minutes=10),
    ).all()

    for session in theia_sessions:
        # Try to update the session info
        update_theia_session(session)


if __name__ == "__main__":
    config.load_incluster_config()

    while True:
        poller()
        time.sleep(1)
