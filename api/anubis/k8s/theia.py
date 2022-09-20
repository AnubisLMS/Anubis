import base64
import json
import traceback
from datetime import datetime, timedelta

from kubernetes import client as k8s, config as k8s_config

from anubis.constants import THEIA_DEFAULT_OPTIONS, WEBTOP_DEFAULT_OPTIONS
from anubis.github.parse import parse_github_repo_name
from anubis.ide.reap import mark_session_ended
from anubis.k8s.pvc import get_user_pvc
from anubis.lms.courses import get_active_courses
from anubis.lms.courses import get_course_admin_ids
from anubis.models import Course, TheiaSession, Assignment, db
from anubis.utils.auth.token import create_token
from anubis.utils.config import get_config_int
from anubis.utils.data import is_debug
from anubis.utils.logging import logger


def create_theia_k8s_pod_pvc(
    theia_session: TheiaSession,
    skip_debug_check: bool = False
) -> tuple[k8s.V1Pod, k8s.V1PersistentVolumeClaim | None]:
    """
    Create the python kubernetes objects for a theia session. This is
    basically building the yaml for the theia session pod and pvc. There is
    a great deal of variation in what the pod will look like based
    on the options provided in the theia session database entry.

    :param theia_session:
    :param skip_debug_check:
    :return:
    """

    # Get the owner of the theia session's netid
    netid = theia_session.owner.netid

    # Construct the theia pod name
    pod_name = get_theia_pod_name(theia_session)

    # list of container objects
    pod_containers = []

    # list of volumes
    pod_volumes = []

    # Extra env to add to the theia pod containers
    sidecar_extra_env: list[k8s.V1EnvVar] = []
    theia_extra_env: list[k8s.V1EnvVar] = []
    init_extra_env: list[k8s.V1EnvVar] = []

    # Get the set repo url for this session. If the assignment has github repos disabled,
    # then default to an empty string.
    repo_url = theia_session.repo_url or ""
    repo_name = parse_github_repo_name(repo_url)
    webtop = theia_session.image.webtop

    # Get the theia session options
    if not theia_session.image.webtop:
        limits = theia_session.resources.get("limits", THEIA_DEFAULT_OPTIONS['resources']['limits'])
        requests = theia_session.resources.get("requests", THEIA_DEFAULT_OPTIONS['resources']['requests'])
        admin = theia_session.admin
        autosave = theia_session.autosave
        credentials = theia_session.credentials
        persistent_storage = theia_session.persistent_storage

    else:
        limits = theia_session.resources.get("limits", WEBTOP_DEFAULT_OPTIONS['resources']['limits'])
        requests = theia_session.resources.get("requests", WEBTOP_DEFAULT_OPTIONS['resources']['requests'])
        admin = False
        autosave = False
        credentials = False
        privileged = False
        persistent_storage = True

    # Put assignment name in theia container environment
    if theia_session.assignment_id is not None:
        assignment: Assignment = theia_session.assignment
        theia_extra_env.append(k8s.V1EnvVar(
            name="ANUBIS_ASSIGNMENT_NAME",
            value=assignment.name,
        ))

    # Value for if the git secret should be included in the init and sidecar
    # containers (for provisioning and autosave).
    include_git_secret: bool = True

    # Value for if the docker secret should be included in the admin
    # theia container. Default to the value of privileged.
    include_docker_secret: bool = admin

    # If we are in debug mode, then check if the git secret is available. If it is
    # not available, then we'll need to not include it in the init and sidecar
    # containers. It is then up to those containers to handle the missing git
    # credentials.
    if not skip_debug_check and is_debug():

        # Load the kubernetes incluster config
        k8s_config.load_incluster_config()
        v1 = k8s.CoreV1Api()

        # Determine if the git secret should be included
        try:
            # Attempt to read the git secret from the anubis namespace.
            # This will throw k8s.exceptions.ApiException(404) if
            # the secret is not available.
            git_secret: k8s.V1Secret = v1.read_namespaced_secret("git", "anubis")

            # Decode git token
            git_token = base64.b64decode(git_secret.data["token"].encode()).decode("utf-8", "ignore")

            # If git token is DEBUG, then we should not pass it to the init and sidecar
            if git_token == "DEBUG":
                include_git_secret = False
                autosave = False

        # Catch kubernetes.k8s.exceptions.ApiException
        except k8s.exceptions.ApiException as e:
            # If we 404ed, then the secret is not there.
            if e.status == 404:
                include_git_secret = False
                autosave = False

        # Determine if the docker config json secret should be included (for admin ide)
        try:
            # Attempt to read the anubis secret from the anubis namespace.
            # This will throw k8s.exceptions.ApiException(404) if
            # the secret is not available.
            anubis_secret: k8s.V1Secret = v1.read_namespaced_secret("anubis-registry", "anubis")

            # Decode git token
            docker_config_json = base64.b64decode(anubis_secret.data[".dockerconfigjson"].encode()).decode(
                "utf-8", "ignore"
            )

            # If git token is DEBUG, then we should not pass it to the init and sidecar
            if docker_config_json == "DEBUG":
                include_docker_secret = False

        # Catch kubernetes.k8s.exceptions.ApiException
        except k8s.exceptions.ApiException as e:
            # If we 404ed, then the secret is not there.
            if e.status == 404:
                include_docker_secret = False

    # Construct the PVC name from the theia pod name
    theia_volume_name = f"{netid}-{theia_session.id[:6]}-ide"

    # Volume Mounts
    theia_volume_mounts = []
    sidecar_volume_mounts = []

    # If persistent storage is enabled for this assignment, then we should create a pvc
    if persistent_storage:
        # Overwrite the volume name to be the user's persistent volume
        theia_volume_name, theia_project_pvc = get_user_pvc(theia_session.owner, theia_session)

        # Append the PVC to the volume list
        pod_volumes.append(
            k8s.V1Volume(
                name=theia_volume_name,
                persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                    claim_name=theia_volume_name,
                ),
            )
        )

    # If the assignment does not have persistent volumes enabled, then create a blank
    # "empty-dir" volume. This skips the allocation of the pvc.
    else:
        theia_project_pvc = None
        pod_volumes.append(k8s.V1Volume(name=theia_volume_name))

    # If the git secret should be included, then we add them to the
    # sidecar and init envs here.
    if include_git_secret:
        # Add git cred to sidecar
        sidecar_extra_env.append(
            # Add the git credentials secret to the container. The entrypoint
            # processes for this container will read this credential and drop
            # it where it needs to.
            k8s.V1EnvVar(
                name="GIT_CRED",
                value_from=k8s.V1EnvVarSource(
                    secret_key_ref=k8s.V1SecretKeySelector(name="git", key="credentials")
                ),
            ),
        )

        # Add git cred to init
        init_extra_env.append(
            # Add the git credentials secret to the container. The entrypoint
            # processes for this container will read this credential and drop
            # it where it needs to.
            k8s.V1EnvVar(
                name="GIT_CRED",
                value_from=k8s.V1EnvVarSource(
                    secret_key_ref=k8s.V1SecretKeySelector(name="git", key="credentials")
                ),
            ),
        )

    # If the theia_session is marked as an admin session, then we can turn on any
    # admin features in the IDE by passing in the proper ADMIN environment variables.
    if admin:

        # Add ANUBIS_ADMIN=ON to theia container and sidecar container
        anubis_admin_env = k8s.V1EnvVar(name="ANUBIS_ADMIN", value="ON")
        sidecar_extra_env.append(anubis_admin_env)
        theia_extra_env.append(anubis_admin_env)

        # If this session belongs to a course, then add the assignment
        # tests repo environment variable to both theia container and
        # sidecar container
        if theia_session.course_id:
            anubis_assignment_tests_repo_env = k8s.V1EnvVar(
                name="ANUBIS_ASSIGNMENT_TESTS_REPO",
                value=theia_session.course.autograde_tests_repo,
            )
            theia_extra_env.append(anubis_assignment_tests_repo_env)
            sidecar_extra_env.append(anubis_assignment_tests_repo_env)

    ##################################################################################
    # INIT CONTAINER

    # Create the init container. This will clone the initial repo onto
    # the shared volume.
    init_container = k8s.V1Container(
        name=f"theia-init",
        image="registry.digitalocean.com/anubis/theia-init",
        image_pull_policy="IfNotPresent",
        env=[
            # Git repo to clone
            k8s.V1EnvVar(name="GIT_REPO", value=repo_url),
            # Add extra env if there is any
            *init_extra_env,
        ],
        volume_mounts=[
            k8s.V1VolumeMount(
                mount_path="/out",
                name=theia_volume_name,
            )
        ],
    )

    ##################################################################################
    # SIDECAR CONTAINER

    if not webtop:
        sidecar_volume_mounts.append(k8s.V1VolumeMount(
            mount_path="/home/anubis",
            name=theia_volume_name,
        ))

    # Sidecar container where anything that the student should not see exists.
    # The main purpose for this container is to keep the git credentials separate
    # from the student environment. The shared /home/project volume is used to share
    # the repo between these two containers.
    sidecar_container = k8s.V1Container(
        name="sidecar",
        image="registry.digitalocean.com/anubis/theia-sidecar",
        image_pull_policy="IfNotPresent",
        env=[
            # set the AUTOSAVE environment variable to ON or OFF. If the variable
            # is set to false, then the autosave loop will be skipped.
            k8s.V1EnvVar(
                name="AUTOSAVE",
                value="ON" if autosave else "OFF",
            ),
            # set netid for commit messages
            k8s.V1EnvVar(
                name="NETID",
                value=netid,
            ),
            k8s.V1EnvVar(name="GIT_REPO", value=repo_url),
            *sidecar_extra_env,
        ],
        # Add a security context to disable privilege escalation
        security_context=k8s.V1SecurityContext(
            allow_privilege_escalation=False,
            run_as_non_root=True,
            run_as_user=1001,
        ),
        # Add the shared volume mount to /home/project
        volume_mounts=sidecar_volume_mounts,
    )

    ##################################################################################
    # DOCKERD CONTAINER

    if theia_session.docker:
        certs_volume = k8s.V1Volume(name="dockerd-certs", empty_dir={})
        certs_volume_mount = k8s.V1VolumeMount(name="dockerd-certs", mount_path="/certs")

        pod_volumes.append(certs_volume)
        theia_volume_mounts.append(certs_volume_mount)

        theia_extra_env.append(k8s.V1EnvVar(name="ANUBIS_RUN_DOCKERD", value="1"))

        dockerd_container = k8s.V1Container(
            name="dockerd",
            image="registry.digitalocean.com/anubis/theia-dockerd",
            image_pull_policy="IfNotPresent",
            env=[
                k8s.V1EnvVar(name="ANUBIS_RUN_DOCKERD", value="1")
            ],
            # Add a security context to disable privilege escalation
            security_context=k8s.V1SecurityContext(
                allow_privilege_escalation=True,
                run_as_non_root=True,
                run_as_user=1001,
                privileged=True,  # Hardcode privileged as it is required for docker (even rootless)
            ),
            # Add the shared certs volume
            volume_mounts=[
                certs_volume_mount
            ],
        )

        pod_containers.append(dockerd_container)

    ##################################################################################
    # THEIA CONTAINER

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
        theia_extra_env.append(
            k8s.V1EnvVar(
                name="INCLUSTER",
                value=base64.b64encode(token.encode()).decode(),
            )
        )

        if theia_session.course_id is not None:
            # Include COURSE_CONTEXT environment variable as urlsafe_base64
            # value. THis needs to be urlsafe because of the way the course
            # context cookie is loaded from a request (see get_course_context
            # function in anubis.lms.courses for more details)
            theia_extra_env.append(
                k8s.V1EnvVar(
                    name="COURSE_CONTEXT",
                    value=base64.urlsafe_b64encode(
                        json.dumps(
                            {
                                "id":          theia_session.course.id,
                                "name":        theia_session.course.name,
                                "course_code": theia_session.course.course_code,
                            }
                        ).encode()
                    ).decode(),
                )
            )

    # Only set course code env var if it is available for this session
    if theia_session.course_id is not None:
        # set the course code to be the course code for the course
        # that this theia session belongs to.
        theia_extra_env.append(
            k8s.V1EnvVar(
                name="COURSE_CODE",
                value=theia_session.course.course_code,
            )
        )

    # Figure out which uid to use
    theia_user_id = 1001
    if webtop:
        theia_user_id = 0

    # Initialize theia volume mounts array with
    # the project volume mount
    theia_volume_mounts.append(
        k8s.V1VolumeMount(
            mount_path="/home/anubis",
            name=theia_volume_name,
        )
    )

    # If privileged, add docker config file to pod as a volume
    if admin and include_docker_secret:
        pod_volumes.append(
            k8s.V1Volume(
                name="docker-config",
                secret=k8s.V1SecretVolumeSource(
                    default_mode=0o644,
                    secret_name="anubis-registry",
                    items=[k8s.V1KeyToPath(key=".dockerconfigjson", path="config.json")],
                ),
            )
        )
        theia_volume_mounts.append(
            k8s.V1VolumeMount(
                mount_path="/docker",
                name="docker-config",
            )
        )

    if webtop:
        pod_volumes.append(
            k8s.V1Volume(
                name="dshm",
                empty_dir=k8s.V1EmptyDirVolumeSource(
                    medium="Memory"
                )
            )
        )
        theia_volume_mounts.append(
            k8s.V1VolumeMount(
                mount_path="/dev/shm",
                name="dshm",
            )
        )

    theia_image = theia_session.image.image
    theia_image_tag = theia_session.image.default_tag or "latest"
    if theia_session.image_tag is not None:
        theia_image_tag = theia_session.image_tag.tag

    # Create the main theia container. This is where the theia server runs, and
    # where the student will have a shell on.
    theia_container = k8s.V1Container(
        name="theia",
        image_pull_policy="IfNotPresent",
        ports=[
            k8s.V1ContainerPort(container_port=5000),
            # Optional proxy ports
            *(k8s.V1ContainerPort(container_port=8000 + i, protocol="TCP") for i in range(11)),
            *(k8s.V1ContainerPort(container_port=8000 + i, protocol="UDP") for i in range(11)),
        ],
        # Use the theia image that was specified in the database. If this is
        # a student session, this should be the theia image that is default either
        # for the course, or for the specific assignment.
        image=f"{theia_image}:{theia_image_tag}",
        # Add environment
        env=[
            # set the AUTOSAVE environment variable to ON or OFF
            # depending on if autosave is enabled for the session.
            k8s.V1EnvVar(
                name="AUTOSAVE",
                value="ON" if autosave else "OFF",
            ),
            # setting the repo name makes some of the initialization
            # a little easier.
            k8s.V1EnvVar(
                name="REPO_NAME",
                value=repo_name,
            ),
            # Add any extra env if it was specified.
            *theia_extra_env,
        ],
        # set the resource limits and requests
        resources=k8s.V1ResourceRequirements(
            limits=limits,
            requests=requests,
        ),
        # setup the shared volume where the student
        # repo exists.
        volume_mounts=theia_volume_mounts,
        # Startup probe is the way that kubernetes can
        # check to see if the theia has started correctly.
        # The pod will not be marked as ready until the
        # webserver has started and the startup probe has
        # succeeded.
        startup_probe=k8s.V1Probe(
            http_get=k8s.V1HTTPGetAction(
                path="/",
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
        security_context=k8s.V1SecurityContext(
            allow_privilege_escalation=webtop,
            privileged=False,
            run_as_user=theia_user_id,
        ),
    )

    ##################################################################################
    # POD

    # Add the main theia container, and the sidecar
    # to the containers list.
    pod_containers.append(theia_container)
    pod_containers.append(sidecar_container)

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
        extra_labels["network-policy"] = theia_session.network_policy or "os-student"

        # set up the pod DNS to be pointed to cloudflare 1.1.1.1 instead
        # of the internal kubernetes dns.
        spec_extra["dns_policy"] = "None"
        spec_extra["dns_config"] = k8s.V1PodDNSConfig(nameservers=["1.1.1.1"])

    # If the network is not locked, then we still need to apply
    # the admin policy. The gist of this policy is that the pod
    # can only connect to the api within the cluster, and anything
    # outside of the cluster.
    else:
        extra_labels["network-policy"] = "admin"

    # Create pod object
    pod = k8s.V1Pod(
        metadata=k8s.V1ObjectMeta(
            name=pod_name,
            labels={
                "app.kubernetes.io/name": "anubis",
                "component":              "theia-session",
                "role":                   "theia-session",
                "netid":                  netid,
                "session":                theia_session.id,
                **extra_labels,
            },
        ),
        spec=k8s.V1PodSpec(
            # set the hostname here so that the terminals on the
            # IDEs will be theia@anubis-ide instead of some ugly
            # container hash.
            hostname="anubis-ide",
            # set the init container
            init_containers=[init_container],
            # set the containers list
            containers=pod_containers,
            # Add the shared Volume(s)
            volumes=pod_volumes,
            # Minimal service account with no extra permissions
            service_account_name='theia-ide',
            # Disable service information from being injected into the environment
            enable_service_links=False,
            # Don't mount service account tokens
            automount_service_account_token=False,
            # Add any extra things in the spec (depending on the
            # options set for the session)
            **spec_extra,
        ),
    )

    return pod, theia_project_pvc


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


def list_theia_pods() -> k8s.V1PodList:
    """
    Get a list of all theia pods that are currently active within the
    kubernetes cluster. This list may not match exactly what is marked
    as active in the database.

    :return:
    """
    v1 = k8s.CoreV1Api()

    # list pods by label selector
    pods = v1.list_namespaced_pod(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=anubis,role=theia-session",
    )

    return pods


def active_theia_pod_count() -> int:
    """
    Get the number of currently active theia pods in
    the kubernetes cluster.

    :return:
    """

    return len(list_theia_pods().items)


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

        # If the session is younger than 6 hours old, continue
        if datetime.now() <= theia_session.created + theia_stale_timeout:
            logger.info(f"NOT reaping session {theia_session.id}")
            continue

        # Reap the session
        reap_theia_session(theia_session, commit=False)

        # Batch commits in size of 5
        if n % 5 == 0:
            db.session.commit()


def fix_stale_theia_resources(theia_pods: k8s.V1PodList):
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

    print("active_db_sessions", active_db_sessions)

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
        logger.info("Found stale theia pods to reap: {}".format(str(list(stale_pods_ids))))

    # Log the stale database entries we need to cleanup
    if len(stale_db_ids) > 0:
        logger.info("Found stale theia database entries: {}".format(str(list(stale_db_ids))))

    # Reap theia sessions

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

    # Update the database entry for the session. set the end time,
    # and active to False.
    mark_session_ended(theia_session)

    # Commit the changes to the database entry
    if commit:
        db.session.commit()


def update_theia_session(session: TheiaSession):
    # Load the kubernetes incluster config
    v1 = k8s.CoreV1Api()

    # Get the name of the pod
    pod_name = get_theia_pod_name(session)

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

    # Update the session state from the pod status
    if pod.status.phase == "Pending":

        # Boolean to indicate if volume has attached
        volume_attached: bool = False

        # If storage volume needs to be attached, we should check
        # in the events for the pod if it has been attached.
        if session.persistent_storage:
            # Get event list for ide pod
            events: k8s.CoreV1Eventlist = v1.list_namespaced_event(
                "anubis", field_selector=f"involvedObject.name={pod_name}"
            )

            # Iterate through events
            for event in events.items:
                event: k8s.CoreV1Event

                # attachdetach-controller starts success messages like
                # this when volume has attached
                if "AttachVolume.Attach succeeded" in event.message:
                    volume_attached = True
                    break

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


def get_theia_pod_name(theia_session: TheiaSession) -> str:
    return f"theia-{theia_session.owner.netid}-{theia_session.id}"


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
    fix_stale_theia_resources(theia_pods)

    db.session.commit()
