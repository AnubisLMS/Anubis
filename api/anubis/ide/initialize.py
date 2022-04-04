from kubernetes import config, client

from anubis.k8s.theia import create_theia_k8s_pod_pvc
from anubis.models import TheiaSession, db
from anubis.utils.auth.user import current_user
from anubis.utils.config import get_config_int
from anubis.utils.logging import logger


def initialize_theia_session(theia_session_id: str):
    """
    Create the kube resources for a theia session. Will update
    database entry to reflect that the session has been initialized.

    After creating the theia session kubernetes resources, this
    function will wait up to 60 seconds for the session resources
    to come out of "Pending". We do this so that we can capture the
    pod cluster ip address. Without setting this IP address, there
    is no way for the theia proxy to direct traffic to the session.
    If it reaches 60 seconds, we cut our loses and return. The reaper
    job that fires every 5 minutes will be on the lookout for sessions
    that have been initialized but are missing cluster ip addresses
    and update them accordingly.

    :param theia_session_id:
    :return:
    """

    # Load the kubernetes incluster config
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    # Log the initialization event
    logger.info(
        "Initializing theia session {}".format(theia_session_id),
        extra={
            "Initializing theia session": theia_session_id,
        },
    )

    # Calculate the maximum IDEs that are allowed to exist at any given time
    max_ides = get_config_int("THEIA_MAX_SESSIONS", default=50)

    # Check to ses how many theia sessions are marked as active in the database. If that
    # count exceeds the artificial limit of IDEs, then we need to re-enqueue this job.
    if (
        TheiaSession.query.filter(
            TheiaSession.active == True,
            TheiaSession.state != "Initializing",
        ).count()
        >= max_ides
    ):
        from anubis.rpc.enqueue import enqueue_ide_initialize

        # If there are too many active pods, recycle the job through the queue.
        logger.info(
            "Maximum IDEs currently running. Re-enqueuing session_id={} initialized request".format(theia_session_id)
        )

        # Re-enqueue this initialization job, then return
        enqueue_ide_initialize(theia_session_id)
        return

    # Get the theia session
    theia_session = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
    ).first()

    # Confirm that the theia session exists.
    if theia_session is None:
        # Log the error if there was one, then return
        logger.error(
            "Unable to find theia session rpc.initialize_theia_session",
            extra={"theia_session_id": theia_session_id},
        )
        return

    # Log the event
    logger.info(
        "Found theia_session to init {}".format(theia_session_id),
        extra={"submission": theia_session.data},
    )

    # Create pod, and pvc object from the options specified for the
    # theia session.
    pod, pvc = create_theia_k8s_pod_pvc(theia_session)

    # Log the creation of the pod
    logger.info("creating theia pod: " + pod.to_str())

    # If a pvc is necessary (for persistent volume assignments)
    if pvc is not None:
        # Create the PVC if it did not already exist
        try:
            # This function will throw a 404 client.exceptions.ApiException
            # if the pvc does not exist
            v1.read_namespaced_persistent_volume_claim(namespace="anubis", name=pvc.metadata.name)
            logger.info(f"PVC for user already exists: {pvc.metadata.name}")

        # Catch the exception thrown if the pvc does not exist
        except client.exceptions.ApiException:
            logger.info(f"PVC for user does not exist (Creating): {pvc.metadata.name}")
            v1.create_namespaced_persistent_volume_claim(namespace="anubis", body=pvc)

    # Send the pod to the kubernetes api. Ask to create
    # these resources under the anubis namespace. These actions are by default
    # backgrounded. That means that these functions will almost certainly return
    # before the resources have actually been created and initialized.
    v1.create_namespaced_pod(namespace="anubis", body=pod)

    # Mark theia session as k8s resources requested
    theia_session.k8s_requested = True

    # Commit any and all changes that have been made
    # in the database up to this point.
    db.session.commit()


def initialize_ide(
    # Required
    image_id: str,
    # Optional / settings
    image_tag_id: str = None,
    assignment_id: str = None,
    course_id: str = None,
    repo_url: str = "",
    playground: bool = False,
    network_locked: bool = True,
    network_policy: str = "os-student",
    autosave: bool = True,
    persistent_storage: bool = True,
    resources: dict = None,
    # Admin fields
    admin: bool = False,
    privileged: bool = False,
    credentials: bool = False,
) -> TheiaSession:
    from anubis.rpc.enqueue import enqueue_ide_initialize

    # Create a new session
    session = TheiaSession(
        owner_id=current_user.id,
        active=True,
        state="Initializing",
        # Required
        image_id=image_id,
        # Options / settings
        image_tag_id=image_tag_id,
        assignment_id=assignment_id,
        course_id=course_id,
        repo_url=repo_url,
        playground=playground,
        network_locked=network_locked,
        network_policy=network_policy,
        persistent_storage=persistent_storage,
        autosave=autosave,
        resources=resources,
        # Admin Options
        admin=admin,
        privileged=privileged,
        credentials=credentials,
    )
    db.session.add(session)
    db.session.commit()

    # Send kube resource initialization rpc job
    enqueue_ide_initialize(session.id)

    # Redirect to proxy
    return session
