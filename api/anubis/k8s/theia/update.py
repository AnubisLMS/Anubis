import traceback
from datetime import datetime, timedelta

from kubernetes import client as k8s

from anubis.k8s.theia.create import create_k8s_resources_for_ide
from anubis.k8s.theia.get import get_theia_pod_name
from anubis.lms.theia import get_active_theia_sessions
from anubis.models import TheiaSession, db
from anubis.utils.logging import logger
from anubis.utils.redis import create_redis_lock


def update_theia_pod_cluster_addresses(theia_pods: k8s.V1PodList):
    """
    Iterate through all theia pods, updating the pod cluster
    addresses in the database as we go.

    :param theia_pods:
    :return:
    """

    # Iterate through all active
    for n, pod in enumerate(theia_pods.items):
        # Get the session id from the pod labels
        session_id = pod.metadata.labels["session"]

        # Get the database entry for the theia session
        theia_session: TheiaSession = TheiaSession.query.filter(TheiaSession.id == session_id).first()

        # Make sure we have a session to work on
        if theia_session is None:
            continue

        # Update the theia session record in the database with
        # the pod cluster address.
        theia_session.cluster_address = pod.status.pod_ip

    # Commit any and all changes
    db.session.commit()


def update_all_theia_sessions():
    """
    Poll Database for sessions created within the last 10 minutes
    if they are active and dont have a cluster_address.

    If the session is running match the pod to the cluster_address

    If the session has failed, update the session to failed.
    """

    # Go through all active sessions
    for session in get_active_theia_sessions():

        # Synchronize session resource
        lock = create_redis_lock(f'theia-session-{session.id}')
        if not lock.acquire(blocking=False):
            continue

        # Try to update the session info
        update_theia_session(session)

        # Release lock
        lock.release()


def update_theia_session(session: TheiaSession):
    # Load the kubernetes incluster config
    v1 = k8s.CoreV1Api()

    # Get the name of the pod
    pod_name = get_theia_pod_name(session)

    # Get age of session
    age: timedelta = datetime.now() - session.created

    try:
        # If the pod has not been created yet, then a 404 will be thrown.
        # Skip logging if that is the case.
        # Get the pod information from the kubernetes api
        pod: k8s.V1Pod = v1.read_namespaced_pod(
            namespace="anubis",
            name=pod_name,
        )

    except k8s.exceptions.ApiException as e:

        # If the status code is 404, then it has not been created yet
        if e.status == 404:
            if session.state != "Waiting for IDE to be scheduled...":
                session.state = "Waiting for IDE to be scheduled..."
                db.session.commit()
            return

        # Error
        logger.error(traceback.format_exc())
        logger.error("continuing")
        return

    # Consider pod aged out if it has been 3 minutes without passing
    if age > timedelta(minutes=3) and pod.status.phase != 'Running':

        # Mark k8s_requested as False before deleting
        session.k8s_requested = False

        try:
            # Delete existing k8s resources for session
            from anubis.k8s.theia.reap import reap_theia_session_k8s_resources
            reap_theia_session_k8s_resources(session.id)
        except k8s.exceptions.ApiException as e:
            logger.error(f'Failed to delete aged out session {e} {session}\n{traceback.format_exc()}')
            return

        try:
            # Re-create theia session
            create_k8s_resources_for_ide(session)
        except k8s.exceptions.ApiException as e:
            logger.error(f'Failed to re-create aged out session {e} {session}\n{traceback.format_exc()}')
            return

        # Commit changes to session.k8s_requested
        db.session.commit()
        return

    # Update the session state from the pod status
    if pod.status.phase == "Pending":

        # Boolean to indicate if volume has attached
        volume_attached: bool = False
        scheduled: bool = False
        scaling: bool = False

        # Get event list for ide pod
        events: k8s.CoreV1Eventlist = v1.list_namespaced_event(
            "anubis", field_selector=f"involvedObject.name={pod_name}"
        )

        # Iterate through events
        for event in events.items:
            event: k8s.CoreV1Event

            # If scheduled, then there will be a "Scheduled" event
            if 'Scheduled' in event.reason:
                scheduled = True
                continue

            # 0/10 nodes are available: 10 Insufficient cpu, 2 Insufficient memory.
            if 'FailedScheduling' in event.reason and 'Insufficient' in event.message:
                scaling = True
                continue

            # attachdetach-controller starts success messages like
            # this when volume has attached
            if "AttachVolume.Attach succeeded" in event.message:
                volume_attached = True
                break

        if not scheduled and scaling:
            session.state = "We are adding more servers to handle your IDE. Give us a minute..."

        # If storage volume needs to be attached, we should check
        # in the events for the pod if it has been attached.
        elif scheduled and session.persistent_storage:
            # If we are expecting a volume, but it has not been attached, then
            # we should set the status message to state such
            if session.persistent_storage and not volume_attached:
                session.state = "Waiting for Persistent Volume to attach..."

        # State that the ide server has not yet started
        else:
            session.state = "Waiting for IDE server to start..."

        db.session.commit()

    # If the pod has failed. There are more than a few ways that
    # the pod could have failed. If we reach this, then we should
    # just mark the theia session as failed, then let the reaper
    # job clean up the kubernetes resources at a later date.
    if pod.status.phase == "Failed":
        # set cluster address and state
        session.active = False
        session.state = "Failed"

        # Log the failure
        logger.error("Theia session failed {}".format(pod_name))

        db.session.commit()

    # If the pod is marked as running. The pod is marked as
    # running when the main containers have started
    if pod.status.phase == "Running":
        # set the cluster address and state
        session.cluster_address = pod.status.pod_ip
        session.state = "Running"

        # Index the event
        logger.info(
            "theia",
            extra={
                "event":      "session-init",
                "session_id": session.id,
                "netid":      session.owner.netid,
            },
        )

        # Log the success
        logger.info("Theia session started {}".format(pod_name))

        db.session.commit()
