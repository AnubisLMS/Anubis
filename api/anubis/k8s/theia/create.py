import base64
import json

from kubernetes import client as k8s, config as k8s_config

from anubis.constants import (
    THEIA_DEFAULT_OPTIONS,
    WEBTOP_DEFAULT_OPTIONS,
    THEIA_VALID_NETWORK_POLICIES,
    THEIA_DEFAULT_NETWORK_POLICY
)
from anubis.github.parse import parse_github_repo_name
from anubis.k8s.pvc.get import get_user_pvc
from anubis.k8s.theia.get import get_theia_pod_name, get_theia_node_selector
from anubis.lms.shell_autograde import get_exercise_py_text, resume_submission
from anubis.models import TheiaSession, Assignment
from anubis.utils.auth.token import create_token
from anubis.utils.data import is_debug


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

    # Extra labels to be applied to the pod
    pod_labels_extra = {}

    # Anything extra in the pod spec to be added
    pod_spec_extra = {}

    # list of container objects
    pod_containers = []

    # list of volumes
    pod_volumes = []

    # Extra env to add to the theia pod containers
    autosave_extra_env: list[k8s.V1EnvVar] = []
    theia_extra_env: list[k8s.V1EnvVar] = []
    init_extra_env: list[k8s.V1EnvVar] = []

    shared_log_volume = k8s.V1Volume(name="log", empty_dir={})
    shared_log_volume_mount = k8s.V1VolumeMount(name="log", mount_path="/log")
    pod_volumes.append(shared_log_volume)

    # Get the set repo url for this session. If the assignment has github repos disabled,
    # then default to an empty string.
    repo_url = theia_session.repo_url or ""
    repo_name = parse_github_repo_name(repo_url)
    webtop = theia_session.image.webtop if theia_session.image else False

    # Figure out which uid to use
    default_theia_user_id = 1001
    theia_user_id = default_theia_user_id if not webtop else 0

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
        persistent_storage = True

    # Put assignment name in theia container environment
    if theia_session.assignment_id is not None:
        assignment: Assignment = theia_session.assignment
        theia_extra_env.append(k8s.V1EnvVar(
            name="ANUBIS_ASSIGNMENT_NAME",
            value=assignment.name,
        ))

    # Value for if the git secret should be included in the init and autosave sidecar
    # containers (for provisioning and autosave).
    include_git_secret: bool = True

    # Value for if the docker secret should be included in the admin
    # theia container. Default to the value of privileged.
    include_docker_secret: bool = admin

    # If we are in debug mode, then check if the git secret is available. If it is
    # not available, then we'll need to not include it in the init and autosave sidecar
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

            # If git token is DEBUG, then we should not pass it to the init and autosave sidecar
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

            # If git token is DEBUG, then we should not pass it to the init and autosave sidecar
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
    ide_volume_mounts: list[k8s.V1VolumeMount] = []
    autosave_volume_mounts: list[k8s.V1VolumeMount] = []

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
    # autosave sidecar and init envs here.
    if include_git_secret:
        # Add git cred to autosave sidecar
        autosave_extra_env.append(
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

        # Add ANUBIS_ADMIN=ON to theia container and autosave sidecar container
        anubis_admin_env = k8s.V1EnvVar(name="ANUBIS_ADMIN", value="ON")
        autosave_extra_env.append(anubis_admin_env)
        theia_extra_env.append(anubis_admin_env)

        # If this session belongs to a course, then add the assignment
        # tests repo environment variable to both theia container and
        # autosave sidecar container
        if theia_session.course_id:
            anubis_assignment_tests_repo_env = k8s.V1EnvVar(
                name="ANUBIS_ASSIGNMENT_TESTS_REPO",
                value=theia_session.course.autograde_tests_repo,
            )
            theia_extra_env.append(anubis_assignment_tests_repo_env)
            autosave_extra_env.append(anubis_assignment_tests_repo_env)

    # Initialize theia volume mounts array with
    # the project volume mount
    ide_volume_mounts.append(
        k8s.V1VolumeMount(
            mount_path="/home/anubis",
            name=theia_volume_name,
        )
    )

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
        volume_mounts=[*ide_volume_mounts],
    )

    ##################################################################################
    # AUTOSAVE SIDECAR CONTAINER

    if not webtop:
        autosave_volume_mounts.append(k8s.V1VolumeMount(
            mount_path="/home/anubis",
            name=theia_volume_name,
        ))

    # Autosave container where anything that the student should not see exists.
    # The main purpose for this container is to keep the git credentials separate
    # from the student environment. The shared /home/project volume is used to share
    # the repo between these two containers.
    autosave_container = k8s.V1Container(
        name="autosave",
        image="registry.digitalocean.com/anubis/theia-autosave",
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
            *autosave_extra_env,
        ],
        # Add a security context to disable privilege escalation
        security_context=k8s.V1SecurityContext(
            allow_privilege_escalation=False,
            run_as_non_root=True,
            run_as_user=1001,
        ),
        # Add the shared volume mount to /home/project
        volume_mounts=[
            shared_log_volume_mount,
            *autosave_volume_mounts
        ],
    )

    ##################################################################################
    # DOCKERD CONTAINER

    if theia_session.docker:
        certs_volume = k8s.V1Volume(name="dockerd-certs", empty_dir={})
        certs_volume_mount = k8s.V1VolumeMount(name="dockerd-certs", mount_path="/certs")

        pod_volumes.append(certs_volume)
        ide_volume_mounts.append(certs_volume_mount)

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
                shared_log_volume_mount,
                *ide_volume_mounts,
            ],
        )

        pod_containers.append(dockerd_container)

    ##################################################################################
    # AUTOGRADE CONTAINER

    if theia_session.autograde:

        # Submission may not be created. Skip handling this for now
        submission = theia_session.submission

        autograde_container = k8s.V1Container(
            name="autograde",
            image="registry.digitalocean.com/anubis/theia-autograde",
            image_pull_policy="IfNotPresent",
            env=[
                k8s.V1EnvVar(name="NETID", value=netid),
                k8s.V1EnvVar(name="TOKEN", value=submission.token),
                k8s.V1EnvVar(name="SUBMISSION_ID", value=submission.id),
                k8s.V1EnvVar(name="EXERCISE_PY", value=get_exercise_py_text(theia_session.assignment)),
                k8s.V1EnvVar(name="RESUME", value=resume_submission(submission)),
            ],
            volume_mounts=[
                shared_log_volume_mount,
                *ide_volume_mounts,
            ],

            # Add startup probe to make sure that the bashrc is generated before IDE can be accessed.
            # This ensures that any shell in IDE can only exist after bashrc is created.
            startup_probe=k8s.V1Probe(
                _exec=k8s.V1ExecAction(command=['stat', '/home/anubis/.bashrc']),
                failure_threshold=60,
                period_seconds=1,
                initial_delay_seconds=0,
            ),
            security_context=k8s.V1SecurityContext(
                allow_privilege_escalation=False,
                privileged=False,
                run_as_user=default_theia_user_id,
            ),
        )

        pod_labels_extra["shell-autograde"] = 'ON'

        theia_extra_env.append(
            k8s.V1EnvVar(
                name="ANUBIS_SHELL_AUTOGRADE",
                value="1",
            )
        )

        pod_containers.append(autograde_container)

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
        ide_volume_mounts.append(
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
        ide_volume_mounts.append(
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
        volume_mounts=[
            shared_log_volume_mount,
            *ide_volume_mounts
        ],
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

    # Add the main theia container, and the autosave sidecar
    # to the containers list.
    pod_containers.append(theia_container)
    pod_containers.append(autosave_container)

    # All IDEs must have a network policy attached to them. This section reads the network
    # policy specified for the IDE, and verifies it is in the set of acceptable network policy
    # names ( defined in anubis/constants.py ). If the policy is not valid, fallback to the default.
    network_policy = theia_session.network_policy \
        if theia_session.network_policy in THEIA_VALID_NETWORK_POLICIES \
        else THEIA_DEFAULT_NETWORK_POLICY

    # This label will enable the student network policy to be
    # applied to this container. The gist of this policy is that
    # students will only be able to connect to github.
    pod_labels_extra["network-policy"] = network_policy

    # If network locked, then set the network policy to student
    # and dns to 1.1.1.1
    if theia_session.network_dns_locked:
        # set up the pod DNS to be pointed to cloudflare 1.1.1.1 instead
        # of the internal kubernetes dns.
        pod_spec_extra["dns_policy"] = "None"
        pod_spec_extra["dns_config"] = k8s.V1PodDNSConfig(nameservers=["1.1.1.1"])

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
                **pod_labels_extra,
            },
        ),
        spec=k8s.V1PodSpec(
            # set the hostname here so that the terminals on the
            # IDEs will be theia@anubis-ide instead of some ugly
            # container hash.
            hostname="anubis-ide",
            # set node selector
            node_selector=get_theia_node_selector(),
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
            **pod_spec_extra,
        ),
    )

    return pod, theia_project_pvc
