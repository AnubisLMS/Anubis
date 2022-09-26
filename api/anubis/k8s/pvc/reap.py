from kubernetes import config as k8s_config, client as k8s

from anubis.k8s.pvc.get import get_pvc_name
from anubis.models import User


def reap_user_pvc(user_id: str):
    # Load the kubernetes incluster config
    k8s_config.load_incluster_config()
    v1 = k8s.CoreV1Api()

    user: User = User.query.filter(User.id == user_id).first()

    if user is None:
        raise RuntimeError('User not found!')

    volume_name = get_pvc_name(user)

    v1.delete_namespaced_persistent_volume_claim(
        name=volume_name,
        namespace="anubis",
        body=k8s.V1DeleteOptions(
            propagation_policy="Background",

        )
    )
