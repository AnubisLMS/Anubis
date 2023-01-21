from kubernetes import config, client as k8s
from anubis.utils.logging import logger

from anubis.models import User


def create_user_pvc(user: User, pvc: k8s.V1PersistentVolumeClaim):
    """
    Create a PVC for a user.

    :param user: The user to create the PVC for.
    :param pvc: The PVC to create.

    :return: None
    """
    config.load_incluster_config()

    v1 = k8s.CoreV1Api()

    try:
        v1.read_namespaced_persistent_volume_claim(namespace="anubis", name=pvc.metadata.name)
        logger.info(f"PVC for user {user.id} already exists")
    except k8s.ApiException:
        # If the pvc does not exist then create one
        v1.create_namespaced_persistent_volume_claim(namespace="anubis", body=pvc)
        logger.info(f"Created PVC for user {user.id}")
