from kubernetes import client as k8s

from anubis.models import User, TheiaSession
from anubis.utils.config import get_config_str


def get_pvc_size(owner: User, theia_session: TheiaSession = None) -> str:
    if owner.is_anubis_developer:
        return get_config_str("DEVELOPER_VOLUME_SIZE", "4Gi")

    # Get home volume size from config
    if theia_session is not None and theia_session.playground:
        if theia_session.image.webtop:
            volume_size = get_config_str("WEBTOP_VOLUME_SIZE", "500Mi")
        else:
            volume_size = get_config_str("PLAYGROUND_VOLUME_SIZE", "100Mi")
    else:
        volume_size = get_config_str("THEIA_VOLUME_SIZE", "100Mi")

    return volume_size


def get_pvc_name(user: User, theia_session: TheiaSession | None = None) -> str:
    if theia_session is not None and theia_session.persistent_storage is False:
        return f"{user.netid}-{theia_session.id[:6]}-ide"

    # Overwrite the volume name to be the user's persistent volume
    return f"ide-volume-{user.netid}"


def get_user_pvc(user: User, theia_session: TheiaSession | None = None) -> tuple[str, k8s.V1PersistentVolumeClaim]:
    volume_size = get_pvc_size(user, theia_session)
    netid = user.netid

    # Overwrite the volume name to be the user's persistent volume
    theia_volume_name = get_pvc_name(user, theia_session)

    # The storage class to be used on prod is probably going to be longhorn. Regardless,
    # we'll want to be able to set this on the fly from a config value. If we default
    # to None, then the cluster default storage class will be used.
    theia_storage_class_name = get_config_str("THEIA_STORAGE_CLASS_NAME", default=None)

    # Create the persistent volume claim object. Since this is a
    # ReadWriteMany volume, the default storage class should
    # support it.
    theia_project_pvc = k8s.V1PersistentVolumeClaim(
        metadata=k8s.V1ObjectMeta(
            name=theia_volume_name,
            labels={
                "app.kubernetes.io/name": "anubis",
                "role": "session-storage",
                "netid": netid,
            },
        ),
        spec=k8s.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteMany"],
            volume_mode="Filesystem",
            storage_class_name=theia_storage_class_name,
            resources=k8s.V1ResourceRequirements(
                requests={
                    "storage": volume_size,
                }
            ),
        ),
    )

    return theia_volume_name, theia_project_pvc
