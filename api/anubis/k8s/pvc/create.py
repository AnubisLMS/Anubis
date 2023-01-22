from kubernetes import config, client as k8s

from anubis.models import User
from anubis.utils.logging import logger


def create_user_pvc(user: User | str, pvc: k8s.V1PersistentVolumeClaim):
    """
    Create a PVC for a user.

    :param user: The user to create the PVC for.
    :param pvc: The PVC to create.

    :return: None
    """
    config.load_incluster_config()
    v1 = k8s.CoreV1Api()

    if isinstance(user, str):
        user: User = User.query.filter(User.id == user).first()

    try:
        v1.read_namespaced_persistent_volume_claim(namespace="anubis", name=pvc.metadata.name)
        logger.warning(f"PVC for user {user.id} already exists")
    except k8s.ApiException:
        # If the pvc does not exist then create one
        v1.create_namespaced_persistent_volume_claim(namespace="anubis", body=pvc)
        logger.info(f"Created PVC for user {user.id}")
