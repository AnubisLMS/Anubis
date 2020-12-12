import os
import time
from datetime import datetime

from kubernetes import config, client

from anubis.models import db, Config, TheiaSession
from anubis.utils.logger import logger


def get_theia_pod_name(theia_session: TheiaSession) -> str:
    return "theia-{}-{}".format(theia_session.owner.netid, theia_session.id)


def create_theia_pod_obj(theia_session: TheiaSession):
    name = get_theia_pod_name(theia_session)

    # PVC
    volume_name = name + '-volume'
    pvc = client.V1PersistentVolumeClaim(
        metadata=client.V1ObjectMeta(
            name=volume_name,
            labels={"app": "theia", "role": "storage"}
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=['ReadWriteMany'],
            volume_mode="Filesystem",
            resources=client.V1ResourceRequirements(
                requests={
                    "storage": "100M",
                }
            )
        )
    )

    # Init container
    init_container = client.V1Container(
        name="theia-init-{}-{}".format(theia_session.owner.netid, theia_session.id),
        image="registry.osiris.services/anubis/theia-init:latest",
        image_pull_policy=os.environ.get('IMAGE_PULL_POLICY', default='Always'),
        env=[
            client.V1EnvVar(name="GIT_REPO", value=theia_session.repo.repo_url),
            client.V1EnvVar(name="GIT_CRED",
                            value_from=client.V1EnvVarSource(
                                secret_key_ref=client.V1SecretKeySelector(
                                    name='git',
                                    key='credentials'
                                ))),
        ],
        volume_mounts=[
            client.V1VolumeMount(
                mount_path='/out',
                name=volume_name,
            )
        ]
    )

    # Theia container
    theia_container = client.V1Container(
        name="theia",
        image="registry.osiris.services/anubis/theia:latest",
        image_pull_policy=os.environ.get('IMAGE_PULL_POLICY', default='Always'),
        ports=[client.V1ContainerPort(container_port=3000)],
        resources=client.V1ResourceRequirements(
            limits={'cpu': '2', 'memory': '500Mi'},
            requests={'cpu': '500m', 'memory': '250Mi'},
        ),
        volume_mounts=[
            client.V1VolumeMount(
                mount_path='/home/project',
                name=volume_name,
            )
        ]
    )

    # Create pod
    pod = client.V1Pod(
        spec=client.V1PodSpec(
            init_containers=[init_container],
            containers=[theia_container],
            volumes=[client.V1Volume(name=volume_name)],
        ),
        metadata=client.V1ObjectMeta(
            name="theia-{}-{}".format(theia_session.owner.netid, theia_session.id),
            labels={
                "app": "theia",
                "role": "theia-session",
                "netid": theia_session.owner.netid,
                "session": str(theia_session.id),
            }
        )
    )

    return pod, pvc


def initialize_theia_session(theia_session_id: int):
    from anubis.app import create_app

    app = create_app()
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    logger.info('Initializing theia session {}'.format(theia_session_id), extra={
        'Initializing theia session': theia_session_id,
    })

    with app.app_context():
        max_ides = Config.query.filter(Config.key == "MAX_IDES").first()
        max_ides = int(max_ides.value) if max_ides is not None else 10
        theia_session = TheiaSession.query.filter(
            TheiaSession.id == theia_session_id,
        ).first()

        if theia_session is None:
            logger.error('Unable to find theia session rpc.initialize_theia_session', extra={
                'theia_session_id': theia_session_id,
            })
            return

        logger.debug('Found theia_session {}'.format(theia_session_id), extra={'submission': theia_session.data})

        # Create pod, and pvc object
        pod, pvc = create_theia_pod_obj(theia_session)

        # Log
        logger.info('creating theia pod: ' + pod.to_str())

        # Send to kube api
        v1.create_namespaced_persistent_volume_claim(namespace='anubis', body=pvc)
        v1.create_namespaced_pod(namespace='anubis', body=pod)

        # Wait for it to have started, then update theia_session state
        name = get_theia_pod_name(theia_session)
        while True:
            pod: client.V1Pod = v1.read_namespaced_pod(
                name=name,
                namespace='anubis',
            )

            if pod.status.phase == 'Pending':
                time.sleep(1)

            if pod.status.phase == 'Running':
                theia_session.cluster_address = pod.status.pod_ip
                theia_session.state = 'Running'
                logger.info('Theia session started {}'.format(name))
                break

            if pod.status.phase == 'Failed':
                theia_session.active = False
                theia_session.state = 'Failed'
                logger.error('Theia session failed {}'.format(name))
                break

        db.session.commit()


def clear_theia_sessions(*_):
    from anubis.app import create_app

    app = create_app()
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    logger.info('Clearing theia sessions')

    with app.app_context():
        theia_sessions = TheiaSession.query.filter(
            TheiaSession.active == True,
        ).all()

        # Delete the pods
        v1.delete_collection_namespaced_pod(
            namespace='anubis',
            label_selector='app=theia',
            propagation_policy='Background'
        )

        for n, theia_session in enumerate(theia_sessions):
            # Get pod name
            name = get_theia_pod_name(theia_session)

            if theia_session.active:
                # Log deletion
                logger.info('deleting theia session pod: {}'.format(name),
                            extra={'session': theia_session.data})
                # Update the database row
                theia_session.active = False
                theia_session.state = 'Ended'
                theia_session.ended = datetime.now()

            # Batch commits in size of 5
            if n % 5 == 0:
                db.session.commit()

        pods = v1.list_namespaced_pod('anubis', label_selector="app=theia,role=theia-session")
        for pod in pods.items:
            v1.delete_namespaced_pod(pod.metadata.name, namespace='anubis')

        db.session.commit()
