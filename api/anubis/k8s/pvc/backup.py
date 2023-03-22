import json
from dataclasses import dataclass
from datetime import datetime

from dateutil.parser import parse as date_parse
from kubernetes import client as k8s

from anubis.k8s.pvc.get import get_pvc_name
from anubis.models import User
from anubis.utils.cache import cache
from anubis.utils.data import is_job, is_debug
from anubis.utils.datetime import convert_to_local
from anubis.utils.logging import logger


@dataclass
class LonghornBackup:
    pv_name: str
    pv_status: str
    pvc_name: str
    namespace: str
    access_mode: str
    backup_name: str
    backup_at: datetime
    size: int


@cache.memoize(timeout=-1, unless=is_debug, forced_update=is_job)
def list_all_backups() -> list[LonghornBackup]:
    custom_object_api = k8s.CustomObjectsApi()
    r = custom_object_api.list_cluster_custom_object('longhorn.io', 'v1beta2', 'backups')

    backups: list[LonghornBackup] = []

    for backup in r.get('items', []):
        status: dict = backup.get('status', dict()) or dict()
        metadata: dict = backup.get('metadata', dict()) or dict()
        status_labels: dict = status.get('labels', dict()) or dict()
        k8s_status: dict = json.loads(status_labels.get('KubernetesStatus', '{}'))

        if len(status_labels) == 0 or len(k8s_status) == 0:
            logger.warning(f'labels or status empty for backup {backup=}')
            continue

        if status.get('progress', 0) != 100:
            logger.warning(f'backup not ready {backup=}')
            continue

        backup = LonghornBackup(
            pv_name=k8s_status['pvName'],
            pv_status=k8s_status['pvStatus'],
            pvc_name=k8s_status['pvcName'],
            namespace=k8s_status['namespace'],
            access_mode=status_labels['longhorn.io/volume-access-mode'],
            backup_name=metadata['name'],
            backup_at=convert_to_local(date_parse(status['snapshotCreatedAt'])),
            size=status['size']
        )
        backups.append(backup)

    return backups


def list_user_backups(user: User) -> list[LonghornBackup]:
    backups = list_all_backups
    pvc_name = get_pvc_name(user)

    return list(filter(lambda backup: backup.pvc_name == pvc_name, backups))




