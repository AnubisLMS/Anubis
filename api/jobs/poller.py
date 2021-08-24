import time
import traceback
from typing import List
from datetime import datetime, timedelta

from kubernetes import config, client

from anubis.models import db, TheiaSession
from anubis.utils.data import with_context
from anubis.utils.lms.theia import get_theia_pod_name
from anubis.utils.services.logger import logger


@with_context
def poller():
    """
    Poll Database for sessions created within the last 10 minutes
    if they are active and dont have a cluster_address.

    If the session is running match the pod to the cluster_address

    If the session has failed, update the session to failed.
    """

    # Load the kubernetes incluster config
    v1 = client.CoreV1Api()

    # Get all theia sessions within the last 10 minutes that are 
    # active and dont have cluster_address
    theia_sessions: List[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.cluster_address == None,
        TheiaSession.created > datetime.now() - timedelta(minutes=10),
    ).all()

    for session in theia_sessions:
        try:
            # Get the name of the pod
            pod_name = get_theia_pod_name(session)

            # Get the pod information from the kubernetes api
            pod: client.V1Pod = v1.read_namespaced_pod(
                namespace="anubis",
                name=pod_name,
            )

            # If the pod has failed. There are more than a few ways that
            # the pod could have failed. If we reach this, then we should
            # just mark the theia session as failed, then let the reaper
            # job clean up the kubernetes resources at a later date.
            if pod.status.phase == "Failed":
                # Set cluster address and state
                session.active = False
                session.state = "Failed"

                # Log the failure
                logger.error("Theia session failed {}".format(pod_name))

                db.session.commit()

            # If the pod is marked as running. The pod is marked as
            # running when the main containers have started
            if pod.status.phase == "Running":
                # Set the cluster address and state
                session.cluster_address = pod.status.pod_ip
                session.state = "Running"

                # Index the event
                logger.info(
                    "theia",
                    extra={
                        "event": "session-init",
                        "session_id": session.id,
                        "netid": session.owner.netid,
                    },
                )

                # Log the success
                logger.info("Theia session started {}".format(pod_name))

                db.session.commit()

        except client.exceptions.ApiException as e:
            if e.status == 404:
                continue
            logger.error(traceback.format_exc())
            logger.error('continuing')


if __name__ == "__main__":
    config.load_incluster_config()

    while True:
        poller()
        time.sleep(1)
