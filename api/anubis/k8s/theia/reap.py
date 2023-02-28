from datetime import timedelta, datetime

from kubernetes import client as k8s, config as k8s_config

from anubis.ide.reap import mark_session_ended
from anubis.k8s.theia.get import list_theia_pods
from anubis.k8s.theia.update import update_theia_pod_cluster_addresses
from anubis.lms.courses import get_active_courses, get_course_admin_ids
from anubis.models import TheiaSession, db, Course
from anubis.utils.config import get_config_int
from anubis.utils.logging import logger
from anubis.lms.reserve import get_active_reserved_sessions


def reap_stale_theia_sessions(*_):
    """
    Reap any and all stale sessions either in the database or
    in kubernetes. This function should be run periodically in
    the reap job to ensure that the state in the database matches
    what is running in the cluster and vice versa.

    :param _:
    :return:
    """

    # Load the incluster config
    k8s_config.load_incluster_config()

    # Log the event
    logger.info("Clearing stale theia sessions")

    # Get the list of active pods
    theia_pods = list_theia_pods()

    # Update the records for pod ip addresses
    update_theia_pod_cluster_addresses(theia_pods)

    # Check that all theia sessions have not
    # reached the global timeout.
    reap_old_theia_sessions(theia_pods)

    # Make sure that database entries marked
    # as active have pods and pods have active
    # database entries.
    reap_stale_theia_k8s_resources(theia_pods)

    db.session.commit()


def reap_theia_session_k8s_resources(theia_session_id: str):
    """
    Mark a theia session kubernetes resources for deletion. This really
    just means, delete the pod and the pvc for the session.

    :param theia_session_id:
    :return:
    """
    v1 = k8s.CoreV1Api()

    # Log the reap
    logger.info("Reaping TheiaSession {}".format(theia_session_id))

    # Mark the pod for deletion by a label selector
    v1.delete_collection_namespaced_pod(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=anubis,role=theia-session,session={}".format(
            theia_session_id,
        ),
        propagation_policy="Background",
    )


def reap_old_theia_sessions(theia_pods: k8s.V1PodList):
    """
    Check that all the active pods have not reached the
    maximum lifetime of a theia session.

    :param theia_pods:
    :return:
    """

    # Get stale timeout hours
    theia_stale_timeout_hours = get_config_int("THEIA_STALE_TIMEOUT_HOURS", default=6)
    theia_stale_timeout = timedelta(hours=theia_stale_timeout_hours)

    # Iterate through all active
    for n, pod in enumerate(theia_pods.items):

        # Get the theia session id from the pod labels
        session_id = pod.metadata.labels["session"]

        # Get the database entry for the theia session
        theia_session: TheiaSession = TheiaSession.query.filter(TheiaSession.id == session_id).first()

        # Make sure we have a session to work on
        if theia_session is None:
            continue

        if datetime.now() <= theia_session.created + theia_stale_timeout:
            logger.info(f"NOT reaping session {theia_session.id}: age ok")
            continue

        # Reap the session
        reap_theia_session(theia_session, commit=False)

        # Batch commits in size of 5
        if n % 5 == 0:
            db.session.commit()


def reap_theia_session(theia_session: TheiaSession, commit: bool = True):
    """
    Reap the given theia session. This is a two step process where
    we first mark the k8s resources for deletion, then
    mark the database entry as ended and inactive.

    :param theia_session:
    :param commit:
    :return:
    """

    # Mark the session resources in kubernetes for deletion.
    # The call to delete the theia session resources will be
    # backgrounded. That is that the session resources will only
    # have been marked for deletion when this function returns.
    reap_theia_session_k8s_resources(theia_session.id)

    # Update the database entry for the session. set the end time,
    # and active to False.
    mark_session_ended(theia_session)

    if theia_session.submission_id:
        from anubis.lms.shell_autograde import close_shell_autograde_ide_submission

        close_shell_autograde_ide_submission(theia_session)

    # Commit the changes to the database entry
    if commit:
        db.session.commit()


def reap_theia_session_by_id(theia_session_id: str):
    """
    Reap the theia session identified by id. This will mark the theia
    session resources in kubernetes for deletion, then mark the database
    entry for the session as inactive.

    :param theia_session_id:
    :return:
    """

    # Load incluster kubernetes config
    k8s_config.load_incluster_config()

    # Log the reap
    logger.info("Attempting to reap theia session {}".format(theia_session_id))

    # Find the theia session in the database
    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
    ).first()

    # Make sure that we have a record for this session
    if theia_session is None:
        logger.error("Could not find theia session {} when attempting to delete".format(theia_session_id))
        return

    # Reap the session
    reap_theia_session(theia_session)


def reap_theia_sessions_in_course(course_id: str):
    """
    Reap all theia sessions within a specific course. This will
    kick everyone off their IDEs.

    There may be many database entries that this function updates
    so we will batch commits to help speed things up, while
    keeping things relatively consistent in the cluster.

    :param course_id:
    :return:
    """

    # Load the incluster config
    k8s_config.load_incluster_config()

    # Lof the reap
    logger.info(f"Clearing theia sessions course_id={course_id}")

    # Find all theia sessions in the database that are
    # marked as active.
    theia_sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.course_id == course_id,
    ).all()

    # Iterate through all active theia sessions in the database, deleting and
    # updating as we go.
    for n, theia_session in enumerate(theia_sessions):
        # Reap the session
        reap_theia_session(theia_session, commit=False)

        # Batch commits in size of 5
        if n % 5 == 0:
            db.session.commit()

    db.session.commit()


def reap_theia_playgrounds_all():
    """
    Reap all theia sessions within anubis playgrounds. This will
    kick everyone off their IDEs.

    There may be many database entries that this function updates
    so we will batch commits to help speed things up, while
    keeping things relatively consistent in the cluster.

    :return:
    """

    # Load the incluster config
    k8s_config.load_incluster_config()

    # Lof the reap
    logger.info(f"Clearing theia sessions playgrounds")

    # Find all theia sessions in the database that are
    # marked as active.
    theia_sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.playground == True,
    ).all()

    # Iterate through all active theia sessions in the database, deleting and
    # updating as we go.
    for n, theia_session in enumerate(theia_sessions):
        # Reap the session
        reap_theia_session(theia_session, commit=False)

        # Batch commits in size of 5
        if n % 5 == 0:
            db.session.commit()

    db.session.commit()


def reap_stale_theia_k8s_resources(theia_pods: k8s.V1PodList):
    """
    Checks that all active Theia Sessions have active pods.

    Will mark pods for deletion if they are marked as not active in db.
    Will mark db sessions as not active if they do not have a pod.

    The intent of this function is that it is called every few minutes
    to fix any inconsistencies in what is in the database, and k8s. For
    example, if there is a theia pod that still exists for a theia session
    that has been marked as inactive in the database, this function will
    figure that out and delete the "stale" pod.

    :param theia_pods:
    :return:
    """

    # Log the event
    logger.info("Checking active ActiveTheia sessions")

    # Get the theia timeout config value
    standard_theia_timeout = get_config_int("THEIA_STALE_PROXY_MINUTES", default=10)
    admin_theia_timeout = get_config_int("THEIA_ADMIN_STALE_PROXY_MINUTES", default=60)

    # Get list of all courses
    courses: list[Course] = get_active_courses()

    active_db_sessions: list[TheiaSession] = []

    # Iterate over all courses
    for course in courses:
        print("filtering stale ides for course {} - {}".format(course.name, course.course_code))

        # Get a list of (heavily cached) admin id strings
        course_admin_ids = get_course_admin_ids(course.id)
        print("course_admin_ids", course.name, course_admin_ids, sep=" :: ")

        # Build query for theia active sessions within the course
        query = TheiaSession.query.filter(
            # Get sessions marked as active
            TheiaSession.active == True,
            # Only consider sessions that have had some
            # time to have their k8s resources requested.
            TheiaSession.k8s_requested == True,
            # Only consider sessions that are a part of
            # this course.
            TheiaSession.course_id == course.id,
        )

        # Get a list of the standard (student) theia sessions that are active
        standard_active_db_theia_sessions: list[TheiaSession] = query.filter(
            # Filter out admin users (only students in the course)
            ~TheiaSession.owner_id.in_(course_admin_ids),
            # Filter for sessions that have had a proxy in the last 10 minutes
            TheiaSession.last_proxy >= datetime.now() - timedelta(minutes=standard_theia_timeout),
        ).all()

        # Get a list of the admin (professor/ta) theia sessions that are active
        admin_active_db_theia_sessions: list[TheiaSession] = query.filter(
            # Filter for admin users (only professors+tas)
            TheiaSession.owner_id.in_(course_admin_ids),
            # Filter for sessions that have had a proxy in the last 60 minutes
            TheiaSession.last_proxy >= datetime.now() - timedelta(minutes=admin_theia_timeout),
        ).all()

        # Build list of all the active theia ides (in the database)
        # from the standard and admin sessions.
        active_db_sessions.extend(standard_active_db_theia_sessions)
        active_db_sessions.extend(admin_active_db_theia_sessions)

    # Make sure to cover theia sessions that do not have a set
    # course as well. Hold these course-less ides to the
    # standard timeout.
    no_course_db_active_sessions: list[TheiaSession] = TheiaSession.query.filter(
        # Get sessions marked as active
        TheiaSession.active == True,
        # Only consider sessions that have had some
        # time to have their k8s resources requested.
        TheiaSession.k8s_requested == True,
        # Course-less theia session
        TheiaSession.course_id == None,
        # Filter for sessions that have had a proxy in the last 10 minutes
        TheiaSession.last_proxy >= datetime.now() - timedelta(minutes=standard_theia_timeout),
    ).all()

    # Print the course-less ides to the screen
    print("no-course ides", no_course_db_active_sessions, sep=" :: ")

    # Add the no-course theia sessions to the active db sessions list
    active_db_sessions.extend(no_course_db_active_sessions)

    # Build set of active pod session ids
    active_pod_ids = set()
    for pod in theia_pods.items:
        active_pod_ids.add(pod.metadata.labels["session"])
    print('active_pod_ids', active_pod_ids)

    # Build set of active db session ids
    active_db_ids = set()
    for active_db_session in active_db_sessions:
        active_db_ids.add(active_db_session.id)

    # Figure out reserved session IDs
    reserved_sessions = get_active_reserved_sessions()
    reserved_session_ids = set(reserved_session.id for reserved_session in reserved_sessions)

    # Union with reserved
    active_db_ids = active_db_ids.union(reserved_session_ids)
    print('active_db_ids', active_db_ids)

    # Figure out which ones don't match and need to be updated.
    # (not including sessions reserved)
    stale_pods_ids = active_pod_ids.difference(active_db_ids)
    stale_db_ids = active_db_ids.difference(active_pod_ids)

    # Log which stale pods we need to clean up
    if len(stale_pods_ids) > 0:
        logger.info("Found stale theia pods to reap: {}".format(str(list(stale_pods_ids))))

    # Log the stale database entries we need to cleanup
    if len(stale_db_ids) > 0:
        logger.info("Found stale theia database entries: {}".format(str(list(stale_db_ids))))

    # Reap theia sessions

    # for stale_pod_id in stale_pods_ids:
    #     if stale_pod_id in reserved_session_ids:
    #         continue
    #     logger.info(f'Reaping stale pod session-id: {stale_pod_id}')
    #     reap_theia_session_by_id(stale_pod_id)
    #
    # # Update database entries
    # TheiaSession.query.filter(
    #     TheiaSession.id.in_(list(stale_db_ids.difference(reserved_session_ids))),
    # ).update({TheiaSession.active: False}, False)
    #
    # # Commit any and all changes to the database
    # db.session.commit()
