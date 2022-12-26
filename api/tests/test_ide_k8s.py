from kubernetes.client import V1Container

from anubis.constants import THEIA_DEFAULT_NETWORK_POLICY, THEIA_SHELL_AUTOGRADE_NETWORK_POLICY
from anubis.constants import THEIA_DEFAULT_OPTIONS
from anubis.k8s.theia.create import create_theia_k8s_pod_pvc
from anubis.models import db, TheiaSession
from anubis.utils.config import set_config_value
from utils import Session, with_context, create_repo


def adjust_assignment_theia_options(assignment_id, options):
    from anubis.models import Assignment, db
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    assignment.theia_options = options
    db.session.commit()


@with_context
def test_playground_k8s():
    set_config_value('THEIA_STORAGE_CLASS_NAME', 'longhorn')
    s = Session("student", new=True)
    r = s.get("/public/playgrounds/active")
    assert r == {"active": False}
    r = s.get("/public/playgrounds/images")
    assert r['images']
    image_id = r['images'][0]['id']
    r = s.post(f"/public/playgrounds/initialize/{image_id}")
    ide_id = r['session']['id']

    db.session.flush()
    db.session.commit()

    ide = TheiaSession.query.filter(TheiaSession.id == ide_id).first()
    pod, pvc = create_theia_k8s_pod_pvc(ide, skip_debug_check=True)

    # Assert pvc things
    assert pvc.spec.access_modes == ['ReadWriteMany']
    assert pvc.spec.storage_class_name == 'longhorn'
    assert pvc.metadata.name == f'ide-volume-{s.netid}'

    # Assert pod things
    assert pod.metadata.labels['app.kubernetes.io/name'] == 'anubis'
    assert pod.metadata.labels['network-policy'] == THEIA_DEFAULT_NETWORK_POLICY
    assert pod.metadata.labels['role'] == 'theia-session'
    assert pod.metadata.labels['session'] == ide_id
    assert pod.metadata.labels['netid'] == s.netid
    assert pod.metadata.name == f'theia-{s.netid}-{ide_id}'

    assert pod.spec.hostname == 'anubis-ide'
    assert pod.spec.dns_config.nameservers == ['1.1.1.1']
    assert pod.spec.dns_policy == 'None'

    ###########################################
    # Verify init container

    assert len(pod.spec.init_containers) == 1
    init_container: V1Container = pod.spec.init_containers[0]

    # Verify env
    init_env = {env.name: env.value for env in init_container.env}
    assert init_env == {'GIT_REPO': '', 'GIT_CRED': None}

    # Verify image
    assert init_container.image == 'registry.digitalocean.com/anubis/theia-init'
    assert init_container.name == 'theia-init'
    assert len(init_container.volume_mounts) == 1
    assert init_container.volume_mounts[0].mount_path == '/home/anubis'
    assert init_container.volume_mounts[0].name == f'ide-volume-{s.netid}'

    theia_container: V1Container = None
    autosave_container: V1Container = None
    for container in pod.spec.containers:
        match container.name:
            case 'theia':
                theia_container = container
            case 'autosave':
                autosave_container = container
            case _:
                assert False  # Unknown container

    # Verify we found
    assert theia_container
    assert autosave_container

    ###########################################
    # Verify theia container

    # Check env
    theia_env = {env.name: env.value for env in theia_container.env}
    assert theia_env == {'AUTOSAVE': 'OFF', 'REPO_NAME': ''}

    # Check ports
    theia_ports = {port.container_port for port in theia_container.ports}
    assert theia_ports == {5000}.union(set(range(8000, 8011)))

    # Check security context
    assert theia_container.security_context.allow_privilege_escalation is False
    assert theia_container.security_context.privileged is False
    assert theia_container.security_context.run_as_user == 1001

    # Check resources
    assert theia_container.resources.limits == THEIA_DEFAULT_OPTIONS['resources']['limits']
    assert theia_container.resources.requests == THEIA_DEFAULT_OPTIONS['resources']['requests']

    # Verify volume
    assert len(theia_container.volume_mounts) == 2
    assert theia_container.volume_mounts[0].mount_path == '/log'
    assert theia_container.volume_mounts[0].name == f'log'
    assert theia_container.volume_mounts[0].read_only is None
    assert theia_container.volume_mounts[1].mount_path == '/home/anubis'
    assert theia_container.volume_mounts[1].name == f'ide-volume-{s.netid}'
    assert theia_container.volume_mounts[1].read_only is None

    ###########################################
    # Verify autosave container

    # Check env
    autosave_env = {env.name: env.value for env in autosave_container.env}
    assert autosave_env == {'AUTOSAVE': 'OFF', 'NETID': s.netid, 'GIT_CRED': None, 'GIT_REPO': '', }

    # Check ports
    assert autosave_container.ports is None

    # Check security context
    assert autosave_container.security_context.allow_privilege_escalation is False
    assert autosave_container.security_context.privileged is None
    assert autosave_container.security_context.run_as_user == 1001

    # Verify volume
    assert len(autosave_container.volume_mounts) == 2
    assert autosave_container.volume_mounts[0].mount_path == '/log'
    assert autosave_container.volume_mounts[0].name == f'log'
    assert autosave_container.volume_mounts[0].read_only is None
    assert autosave_container.volume_mounts[1].mount_path == '/home/anubis'
    assert autosave_container.volume_mounts[1].name == f'ide-volume-{s.netid}'
    assert autosave_container.volume_mounts[1].read_only is None


@with_context
def test_assignment_ide_k8s():
    s = Session("student", new=True)
    assignments = s.get("/public/assignments/list")["assignments"]
    for a in assignments:
        if a["github_repo_required"] and '0' in a['name']:
            assignment_id = a["id"]
            break
    else:
        assert False  # Break if assignment not found
    adjust_assignment_theia_options(assignment_id, {
        'persistent_storage': False,
        'resources':          {},
        'network_policy':     THEIA_DEFAULT_NETWORK_POLICY,
    })
    r = s.get(f"/public/ide/active/{assignment_id}")
    assert r == {"active": False}
    create_repo(s, assignment_id)
    r = s.post(f"/public/ide/initialize/{assignment_id}", json={})
    ide_id = r['session']['id']

    db.session.flush()
    db.session.commit()

    ide: TheiaSession = TheiaSession.query.filter(TheiaSession.id == ide_id).first()

    assert ide.autosave is True
    assert ide.playground is False
    assert ide.admin is False
    assert ide.docker is False
    assert ide.persistent_storage is False
    assert ide.repo_url == 'https://github.com/AnubisLMS/xv6'

    pod, pvc = create_theia_k8s_pod_pvc(ide, skip_debug_check=True)

    # Assert pvc things
    assert pvc is None

    # Assert pod things
    assert pod.metadata.labels['app.kubernetes.io/name'] == 'anubis'
    assert pod.metadata.labels['network-policy'] == THEIA_DEFAULT_NETWORK_POLICY
    assert pod.metadata.labels['role'] == 'theia-session'
    assert pod.metadata.labels['session'] == ide_id
    assert pod.metadata.labels['netid'] == s.netid
    assert pod.metadata.name == f'theia-{s.netid}-{ide_id}'

    assert pod.spec.hostname == 'anubis-ide'
    assert pod.spec.dns_config.nameservers == ['1.1.1.1']
    assert pod.spec.dns_policy == 'None'

    ###########################################
    # Verify init container

    assert len(pod.spec.init_containers) == 1
    init_container: V1Container = pod.spec.init_containers[0]

    # Verify env
    init_env = {env.name: env.value for env in init_container.env}
    assert init_env == {'GIT_REPO': 'https://github.com/AnubisLMS/xv6', 'GIT_CRED': None}

    # Verify image
    assert init_container.image == 'registry.digitalocean.com/anubis/theia-init'
    assert init_container.name == 'theia-init'
    assert len(init_container.volume_mounts) == 1
    assert init_container.volume_mounts[0].mount_path == '/home/anubis'

    theia_container: V1Container = None
    autosave_container: V1Container = None
    for container in pod.spec.containers:
        match container.name:
            case 'theia':
                theia_container = container
            case 'autosave':
                autosave_container = container
            case _:
                assert False  # Unknown container

    # Verify we found
    assert theia_container
    assert autosave_container

    ###########################################
    # Verify theia container

    # Check env
    theia_env = {env.name: env.value for env in theia_container.env}
    assert theia_env['AUTOSAVE'] == 'ON'
    assert theia_env['REPO_NAME'] == 'xv6'
    assert theia_env['ANUBIS_ASSIGNMENT_NAME']
    assert theia_env['COURSE_CODE'] == 'CS-UY 3224'

    # Check ports
    theia_ports = {port.container_port for port in theia_container.ports}
    assert theia_ports == {5000}.union(set(range(8000, 8011)))

    # Check security context
    assert theia_container.security_context.allow_privilege_escalation is False
    assert theia_container.security_context.privileged is False
    assert theia_container.security_context.run_as_user == 1001

    # Check resources
    assert theia_container.resources.limits == THEIA_DEFAULT_OPTIONS['resources']['limits']
    assert theia_container.resources.requests == THEIA_DEFAULT_OPTIONS['resources']['requests']

    # Verify volume
    assert len(theia_container.volume_mounts) == 2
    assert theia_container.volume_mounts[0].mount_path == '/log'
    assert theia_container.volume_mounts[0].read_only is None
    assert theia_container.volume_mounts[1].mount_path == '/home/anubis'
    assert theia_container.volume_mounts[1].read_only is None

    ###########################################
    # Verify autosave container

    # Check env
    autosave_env = {env.name: env.value for env in autosave_container.env}
    assert autosave_env == {'AUTOSAVE': 'ON', 'NETID': s.netid, 'GIT_CRED': None,
                            'GIT_REPO': 'https://github.com/AnubisLMS/xv6'}

    # Check ports
    assert autosave_container.ports is None

    # Check security context
    assert autosave_container.security_context.allow_privilege_escalation is False
    assert autosave_container.security_context.privileged is None
    assert autosave_container.security_context.run_as_user == 1001

    # Verify volume
    assert len(autosave_container.volume_mounts) == 2
    assert autosave_container.volume_mounts[0].mount_path == '/log'
    assert autosave_container.volume_mounts[0].read_only is None
    assert autosave_container.volume_mounts[1].mount_path == '/home/anubis'
    assert autosave_container.volume_mounts[1].read_only is None


@with_context
def test_shell_assignment_ide_k8s():
    s = Session("student", new=True)
    assignments = s.get("/public/assignments/list")["assignments"]
    for a in assignments:
        if '4' in a['name']:
            assignment_id = a["id"]
            break
    else:
        assert False  # Break if assignment not found
    adjust_assignment_theia_options(assignment_id, {
        'persistent_storage': False,
        'resources':          {},
        'autosave':           False,
        'network_policy':     THEIA_SHELL_AUTOGRADE_NETWORK_POLICY,
        'network_dns_locked': False,
    })
    r = s.get(f"/public/ide/active/{assignment_id}")
    assert r == {"active": False}
    create_repo(s, assignment_id)
    r = s.post(f"/public/ide/initialize/{assignment_id}", json={})
    ide_id = r['session']['id']
    # check_shell_assignment_ide(s, ide_id)

    ide: TheiaSession = TheiaSession.query.filter(TheiaSession.id == ide_id).first()

    assert ide.autosave is False
    assert ide.playground is False
    assert ide.admin is False
    assert ide.docker is False
    assert ide.persistent_storage is False
    assert ide.repo_url == ''

    pod, pvc = create_theia_k8s_pod_pvc(ide, skip_debug_check=True)

    # Assert pvc things
    assert pvc is None

    # Assert pod things
    assert pod.metadata.labels['app.kubernetes.io/name'] == 'anubis'
    assert pod.metadata.labels['network-policy'] == THEIA_SHELL_AUTOGRADE_NETWORK_POLICY
    assert pod.metadata.labels['shell-autograde'] == 'ON'
    assert pod.metadata.labels['role'] == 'theia-session'
    assert pod.metadata.labels['session'] == ide_id
    assert pod.metadata.labels['netid'] == s.netid
    assert pod.metadata.name == f'theia-{s.netid}-{ide_id}'

    assert pod.spec.hostname == 'anubis-ide'
    assert pod.spec.dns_config

    ###########################################
    # Verify init container

    assert len(pod.spec.init_containers) == 1
    init_container: V1Container = pod.spec.init_containers[0]

    # Verify env
    init_env = {env.name: env.value for env in init_container.env}
    assert init_env == {'GIT_REPO': '', 'GIT_CRED': None}

    # Verify image
    assert init_container.image == 'registry.digitalocean.com/anubis/theia-init'
    assert init_container.name == 'theia-init'
    assert len(init_container.volume_mounts) == 1
    assert init_container.volume_mounts[0].mount_path == '/home/anubis'

    theia_container: V1Container = None
    autosave_container: V1Container = None
    autograde_container: V1Container = None
    for container in pod.spec.containers:
        match container.name:
            case 'theia':
                theia_container = container
            case 'autosave':
                autosave_container = container
            case 'autograde':
                autograde_container = container
            case _:
                assert False  # Unknown container

    # Verify we found
    assert theia_container
    assert autosave_container

    ###########################################
    # Verify theia container

    # Check env
    theia_env = {env.name: env.value for env in theia_container.env}
    assert theia_env['AUTOSAVE'] == 'OFF'
    assert theia_env['REPO_NAME'] == ''
    assert theia_env['ANUBIS_ASSIGNMENT_NAME']
    assert theia_env['COURSE_CODE'] == 'CS-UY 3224'

    # Check ports
    theia_ports = {port.container_port for port in theia_container.ports}
    assert theia_ports == {5000}.union(set(range(8000, 8011)))

    # Check security context
    assert theia_container.security_context.allow_privilege_escalation is False
    assert theia_container.security_context.privileged is False
    assert theia_container.security_context.run_as_user == 1001

    # Check resources
    assert theia_container.resources.limits == THEIA_DEFAULT_OPTIONS['resources']['limits']
    assert theia_container.resources.requests == THEIA_DEFAULT_OPTIONS['resources']['requests']

    # Verify volume
    assert len(theia_container.volume_mounts) == 2
    assert theia_container.volume_mounts[0].mount_path == '/log'
    assert theia_container.volume_mounts[0].read_only is None
    assert theia_container.volume_mounts[1].mount_path == '/home/anubis'
    assert theia_container.volume_mounts[1].read_only is None

    ###########################################
    # Verify autosave container

    # Check env
    autosave_env = {env.name: env.value for env in autosave_container.env}
    assert autosave_env == {'AUTOSAVE': 'OFF', 'NETID': s.netid, 'GIT_CRED': None, 'GIT_REPO': ''}

    # Check ports
    assert autosave_container.ports is None

    # Check security context
    assert autosave_container.security_context.allow_privilege_escalation is False
    assert autosave_container.security_context.privileged is None
    assert autosave_container.security_context.run_as_user == 1001

    # Verify volume
    assert len(autosave_container.volume_mounts) == 2
    assert autosave_container.volume_mounts[0].mount_path == '/log'
    assert autosave_container.volume_mounts[0].read_only is None
    assert autosave_container.volume_mounts[1].mount_path == '/home/anubis'
    assert autosave_container.volume_mounts[1].read_only is None

    ###########################################
    # Verify autograde container

    # Check env
    autograde_env = {env.name: env.value for env in autograde_container.env}
    assert autograde_env['EXERCISE_PY']
    assert autograde_env['NETID']
    assert autograde_env['SUBMISSION_ID']
    assert 'GIT_GRED' not in autograde_env

    # Check ports
    assert autograde_container.ports is None

    # Check security context
    assert autograde_container.security_context.allow_privilege_escalation is False
    assert autograde_container.security_context.privileged is False
    assert autograde_container.security_context.run_as_user == 1001

    # Verify volume
    assert len(autograde_container.volume_mounts) == 2
    assert autograde_container.volume_mounts[0].mount_path == '/log'
    assert autograde_container.volume_mounts[0].read_only is None
    assert autograde_container.volume_mounts[1].mount_path == '/home/anubis'
    assert autograde_container.volume_mounts[1].read_only is None
