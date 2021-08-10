import base64
import os
from datetime import datetime
from typing import Tuple

from kubernetes import client

from anubis.models import TheiaSession, db
from anubis.utils.auth.token import create_token
from anubis.utils.lms.theia import get_theia_pod_name, mark_session_ended
from anubis.utils.services.logger import logger


def create_theia_k8s_pod_pvc(theia_session: TheiaSession) -> Tuple[client.V1Pod, client.V1PersistentVolumeClaim]:
    """
    Create the python kubernetes objects for a theia session. This is
    basically building the yaml for the theia session pod and pvc. There is
    a great deal of variation in what the pod will look like based
    on the options provided in the theia session database entry.

    :param theia_session:
    :return:
    """

    # Get the owner of the theia session's netid
    netid = theia_session.owner.netid

    # Construct the theia pod name
    name = get_theia_pod_name(theia_session)

    # List of container objects
    containers = []

    # Get the set repo url for this session. If the assignment has github repos disabled,
    # then default to an empty string.
    repo_url = theia_session.repo_url or ''

    # Get the theia session options
    limits = theia_session.options.get('limits', {"cpu": "2", "memory": "500Mi"})
    requests = theia_session.options.get('requests', {"cpu": "250m", "memory": "100Mi"})
    autosave = theia_session.options.get('autosave', True)
    credentials = theia_session.options.get('credentials', False)

    # Construct the PVC name from the theia pod name
    volume_name = netid + "-volume"

    # Create the persistent volume claim object. Since this is a
    # ReadWriteMany volume, the default storage class should
    # support it.
    pvc = client.V1PersistentVolumeClaim(

        metadata=client.V1ObjectMeta(
            name=volume_name,
            labels={
                "app.kubernetes.io/name": "anubis",
                "role": "session-storage",
                "netid": netid,
            },
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteMany"],
            volume_mode="Filesystem",
            resources=client.V1ResourceRequirements(
                requests={
                    "storage": "250Mi",
                }
            ),
        ),
    )

    # Create the init container. This will clone the initial repo onto
    # the shared volume.
    init_container = client.V1Container(
        name=f"theia-init",
        image="registry.digitalocean.com/anubis/theia-init:latest",
        image_pull_policy="IfNotPresent",
        env=[
            client.V1EnvVar(name="GIT_REPO", value=repo_url),
            client.V1EnvVar(
                name="GIT_CRED",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="git", key="credentials"
                    )
                ),
            ),
        ],
        volume_mounts=[
            client.V1VolumeMount(
                mount_path="/out",
                name=volume_name,
            )
        ],
    )

    # Extra env to add to the main theia server container
    extra_env = []

    # If this is an admin IDE session, then we should add a token
    # for the anubis cli to be able to authenticate to the anubis
    # api.
    if credentials:
        # Create a token for the session owner
        token = create_token(theia_session.owner.netid)

        # Create the INCLUSTER environment variable as the base64
        # encoded token. This token should be picked up by the
        # theia init process to initialize the anubis cli with
        # the token.
        extra_env.append(client.V1EnvVar(
            name='INCLUSTER',
            value=base64.b64encode(token.encode()).decode(),
        ))

    user_id = 1001
    if theia_session.privileged:
        user_id = 0

    # Create the main theia container. This is where the theia server runs, and
    # where the student will have a shell on.
    theia_container = client.V1Container(
        name="theia",
        image_pull_policy=os.environ.get("IMAGE_PULL_POLICY", default="Always"),
        ports=[client.V1ContainerPort(container_port=5000)],

        # Use the theia image that was specified in the database. If this is
        # a student session, this should be the theia image that is default either
        # for the course, or for the specific assignment.
        image=theia_session.image,

        # Add environment
        env=[
            # Set the AUTOSAVE environment variable to ON or OFF
            # depending on if autosave is enabled for the session.
            client.V1EnvVar(
                name='AUTOSAVE',
                value='ON' if autosave else 'OFF',
            ),

            # Set the course code to be the course code for the course
            # that this theia session belongs to.
            client.V1EnvVar(
                name='COURSE_CODE',
                value=theia_session.course.course_code,
            ),

            # Add any extra env if it was specified.
            *extra_env,
        ],

        # Set the resource limits and requests
        resources=client.V1ResourceRequirements(
            limits=limits,
            requests=requests,
        ),

        # Setup the shared volume where the student
        # repo exists.
        volume_mounts=[
            client.V1VolumeMount(
                mount_path="/home/anubis",
                name=volume_name,
            )
        ],

        # Startup probe is the way that kubernetes can
        # check to see if the theia has started correctly.
        # The pod will not be marked as ready until the
        # webserver has started and the startup probe has
        # succeeded.
        startup_probe=client.V1Probe(
            http_get=client.V1HTTPGetAction(
                path='/',
                port=5000,
            ),
            initial_delay_seconds=3,
            period_seconds=1,
            failure_threshold=60,
            success_threshold=1,
        ),

        # If the session should be privileged, set it here. Privileged
        # containers should only exist for the management IDEs so that
        # docker can run.
        security_context=client.V1SecurityContext(
            allow_privilege_escalation=theia_session.privileged,
            privileged=theia_session.privileged,
            run_as_user=user_id,
        ),
    )

    # Sidecar container where anything that the student should not see exists.
    # The main purpose for this container is to keep the git credentials separate
    # from the student environment. The shared /home/project volume is used to share
    # the repo between these two containers.
    sidecar_container = client.V1Container(
        name="sidecar",
        image="registry.digitalocean.com/anubis/theia-sidecar:latest",
        image_pull_policy=os.environ.get("IMAGE_PULL_POLICY", default="Always"),

        env=[
            # Add the git credentials secret to the container. The entrypoint
            # processes for this container will read this credential and drop
            # it where it needs to.
            client.V1EnvVar(
                name="GIT_CRED",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="git", key="credentials"
                    )
                ),
            ),

            # Set the AUTOSAVE environment variable to ON or OFF. If the variable
            # is set to false, then the autosave loop will be skipped.
            client.V1EnvVar(
                name='AUTOSAVE',
                value='ON' if autosave else 'OFF',
            ),
        ],

        # Add a security context to disable privilege escalation
        security_context=client.V1SecurityContext(
            allow_privilege_escalation=False,
            run_as_non_root=True,
            run_as_user=1001,
        ),

        # Add the shared volume mount to /home/project
        volume_mounts=[
            client.V1VolumeMount(
                mount_path="/home/anubis",
                name=volume_name,
            )
        ],
    )

    # Add the main theia container, and the sidecar
    # to the containers list.
    containers.append(theia_container)
    containers.append(sidecar_container)

    # Extra labels to be applied to the pod
    extra_labels = {}

    # Anything extra in the pod spec to be added
    spec_extra = {}

    # If network locked, then set the network policy to student
    # and dns to 1.1.1.1
    if theia_session.network_locked:

        # This label will enable the student network policy to be
        # applied to this container. The gist of this policy is that
        # students will only be able to connect to github.
        extra_labels["network-policy"] = "student"

        # Set up the pod DNS to be pointed to cloudflare 1.1.1.1 instead
        # of the internal kubernetes dns.
        spec_extra['dns_policy'] = "None"
        spec_extra["dns_config"] = client.V1PodDNSConfig(nameservers=["1.1.1.1"])

    # If the network is not locked, then we still need to apply
    # the admin policy. The gist of this policy is that the pod
    # can only connect to the api within the cluster, and anything
    # outside of the cluster.
    else:
        extra_labels["network-policy"] = "admin"

    # Create pod object
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(

            name=name,
            labels={
                "app.kubernetes.io/name": "theia",
                "role": "theia-session",
                "netid": theia_session.owner.netid,
                "session": theia_session.id,
                **extra_labels,
            },
        ),

        spec=client.V1PodSpec(

            # Set the hostname here so that the terminals on the
            # IDEs will be theia@anubis-ide instead of some ugly
            # container hash.
            hostname='anubis-ide',

            # Set the init container
            init_containers=[init_container],

            # Set the containers list
            containers=containers,

            # Add the shared Volume
            volumes=[
                client.V1Volume(
                    name=volume_name,
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=volume_name,
                    )
                )
            ],

            # Add any extra things in the spec (depending on the
            # options set for the session)
            **spec_extra
        ),
    )

    return pod, pvc


def reap_theia_session_k8s_resources(theia_session_id: str):
    """
    Mark a theia session kubernetes resources for deletion. This really
    just means, delete the pod and the pvc for the session.

    :param theia_session_id:
    :return:
    """
    v1 = client.CoreV1Api()

    # Log the reap
    logger.info("Reaping TheiaSession {}".format(theia_session_id))

    # Mark the pod for deletion by a label selector
    v1.delete_collection_namespaced_pod(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=theia,role=theia-session,session={}".format(
            theia_session_id,
        ),
        propagation_policy="Background",
    )


def list_theia_pods() -> client.V1PodList:
    """
    Get a list of all theia pods that are currently active within the
    kubernetes cluster. This list may not match exactly what is marked
    as active in the database.

    :return:
    """
    v1 = client.CoreV1Api()

    # List pods by label selector
    pods = v1.list_namespaced_pod(
        namespace="anubis", label_selector="app.kubernetes.io/name=theia,role=theia-session"
    )

    return pods


def active_theia_pod_count() -> int:
    """
    Get the number of currently active theia pods in
    the kubernetes cluster.

    :return:
    """

    return len(list_theia_pods().items)


def update_theia_pod_cluster_addresses(theia_pods: client.V1PodList):
    """
    Iterate through all theia pods, updating the pod cluster
    addresses in the databse as we go.

    :param theia_pods:
    :return:
    """

    # Iterate through all active
    for n, pod in enumerate(theia_pods.items):
        # Get the session id from the pod labels
        session_id = pod.metadata.labels["session"]

        # Get the database entry for the theia session
        theia_session: TheiaSession = TheiaSession.query.filter(
            TheiaSession.id == session_id
        ).first()

        # Make sure we have a session to work on
        if theia_session is None:
            continue

        # Update the theia session record in the database with
        # the pod cluster address.
        theia_session.cluster_address = pod.status.pod_ip

    # Commit any and all changes
    db.session.commit()


def reap_old_theia_sessions(theia_pods: client.V1PodList):
    """
    Check that all the active pods have not reached the
    maximum lifetime of a theia session.

    :param theia_pods:
    :return:
    """
    # Get the app config
    from anubis.config import config as _config

    # Iterate through all active
    for n, pod in enumerate(theia_pods.items):

        # Get the theia session id from the pod labels
        session_id = pod.metadata.labels["session"]

        # Get the database entry for the theia session
        theia_session: TheiaSession = TheiaSession.query.filter(
            TheiaSession.id == session_id
        ).first()

        # Make sure we have a session to work on
        if theia_session is None:
            continue

        # If the session is younger than 6 hours old, continue
        if datetime.now() <= theia_session.created + _config.THEIA_TIMEOUT:
            logger.info(f'NOT reaping session {theia_session.id}')
            continue

        # Reap the session
        reap_theia_session(theia_session, commit=False)

        # Batch commits in size of 5
        if n % 5 == 0:
            db.session.commit()


def fix_stale_theia_resources(theia_pods: client.V1PodList):
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

    # Get active pods and db rows
    active_db_sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
    ).all()

    # Build set of active pod session ids
    active_pod_ids = set()
    for pod in theia_pods.items:
        active_pod_ids.add(pod.metadata.labels["session"])

    # Build set of active db session ids
    active_db_ids = set()
    for active_db_session in active_db_sessions:
        active_db_ids.add(active_db_session.id)

    # Figure out which ones don't match
    # and need to be updated.
    stale_pods_ids = active_pod_ids - active_db_ids
    stale_db_ids = active_db_ids - active_pod_ids

    # Log which stale pods we need to clean up
    if len(stale_pods_ids) > 0:
        logger.info(
            "Found stale theia pods to reap: {}".format(str(list(stale_pods_ids)))
        )

    # Log the stale database entries we need to cleanup
    if len(stale_db_ids) > 0:
        logger.info(
            "Found stale theia database entries: {}".format(str(list(stale_db_ids)))
        )

    # Reap theia sessions
    from anubis.rpc.theia import reap_theia_session_by_id
    for stale_pod_id in stale_pods_ids:
        reap_theia_session_by_id(stale_pod_id)

    # Update database entries
    TheiaSession.query.filter(
        TheiaSession.id.in_(list(stale_db_ids)),
    ).update({TheiaSession.active: False}, False)

    # Commit any and all changes to the database
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

    # Update the database entry for the session. Set the end time,
    # and active to False.
    mark_session_ended(theia_session)

    # Commit the changes to the database entry
    if commit:
        db.session.commit()
