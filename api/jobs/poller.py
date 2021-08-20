from anubis.utils.data import db, TheiaSession
from anubis.utils.lms.theia import get_theia_pod_name
from kubernetes import client
from datetime import datetime, timedelta

from anubis.utils.services.logger import logger


def poller():
    v1 = client.CoreV1Api()
    theia_sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.clusterip == None,
        TheiaSession.created > datetime.now() - timedelta(minutes=10),
    ).all()

    for session in theia_sessions:
        # Get the name of the pod
        pod_name = get_theia_pod_name(session.session_id)
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
                    "session_id": session.session_id,
                    "netid": session.owner.netid,
                },
            )

            # Log the success
            logger.info("Theia session started {}".format(pod_name))

            db.session.commit()


if __name__ == "__main__":
    print(f"Running poller job - {datetime.now()}")
    poller()