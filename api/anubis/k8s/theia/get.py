from kubernetes import client as k8s

from anubis.models import TheiaSession


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


def get_theia_pod_name(theia_session: TheiaSession) -> str:
    return f"theia-{theia_session.owner.netid}-{theia_session.id}"
