from utils import Session, with_context, create_repo


@with_context
def adjust_assignment_theia_options(assignment_id, options):
    from anubis.models import Assignment, db
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    assignment.theia_options = options
    db.session.commit()


@with_context
def set_longhorn():
    from anubis.utils.config import set_config_value
    set_config_value('THEIA_STORAGE_CLASS_NAME', 'longhorn')


def test_playground_k8s():
    from anubis.k8s.theia import create_theia_k8s_pod_pvc

    set_longhorn()

    s = Session("student", new=True)
    r = s.get("/public/playgrounds/active")
    assert r == {"active": False}

    r = s.get("/public/playgrounds/images")
    assert r['images']
    image_id = r['images'][0]['id']

    r = s.post(f"/public/playgrounds/initialize/{image_id}")
    ide_id = r['session']['id']

    @with_context
    def _check_playground(_ide_id):
        from anubis.models import TheiaSession
        from kubernetes.client import V1Container
        from anubis.constants import THEIA_DEFAULT_OPTIONS

        ide = TheiaSession.query.filter(TheiaSession.id == _ide_id).first()
        pod, pvc = create_theia_k8s_pod_pvc(ide, skip_debug_check=True)

        # Assert pvc things
        assert pvc.spec.access_modes == ['ReadWriteMany']
        assert pvc.spec.storage_class_name == 'longhorn'
        assert pvc.metadata.name == f'ide-volume-{s.netid}'

        # Assert pod things
        assert pod.metadata.labels['app.kubernetes.io/name'] == 'anubis'
        assert pod.metadata.labels['network-policy'] == 'os-student'
        assert pod.metadata.labels['role'] == 'theia-session'
        assert pod.metadata.labels['session'] == _ide_id
        assert pod.metadata.labels['netid'] == s.netid
        assert pod.metadata.name == f'theia-{s.netid}-{_ide_id}'

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
        assert init_container.volume_mounts[0].mount_path == '/out'
        assert init_container.volume_mounts[0].name == f'ide-volume-{s.netid}'

        theia_container: V1Container = None
        sidecar_container: V1Container = None
        for container in pod.spec.containers:
            if container.name == 'theia':
                theia_container = container
            elif container.name == 'sidecar':
                sidecar_container = container

        # Verify we found
        assert theia_container
        assert sidecar_container

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
        assert len(theia_container.volume_mounts) == 1
        assert theia_container.volume_mounts[0].mount_path == '/home/anubis'
        assert theia_container.volume_mounts[0].name == f'ide-volume-{s.netid}'
        assert theia_container.volume_mounts[0].read_only is None

        ###########################################
        # Verify sidecar container

        # Check env
        sidecar_env = {env.name: env.value for env in sidecar_container.env}
        assert sidecar_env == {'AUTOSAVE': 'OFF', 'NETID': s.netid, 'GIT_CRED': None, 'GIT_REPO': '',}

        # Check ports
        assert sidecar_container.ports is None

        # Check security context
        assert sidecar_container.security_context.allow_privilege_escalation is False
        assert sidecar_container.security_context.privileged is None
        assert sidecar_container.security_context.run_as_user == 1001

        # Verify volume
        assert len(sidecar_container.volume_mounts) == 1
        assert sidecar_container.volume_mounts[0].mount_path == '/home/anubis'
        assert sidecar_container.volume_mounts[0].name == f'ide-volume-{s.netid}'
        assert sidecar_container.volume_mounts[0].read_only is None

    _check_playground(ide_id)


def test_assignment_ide_k8s():
    from anubis.k8s.theia import create_theia_k8s_pod_pvc
    s = Session("student", new=True)

    assignments = s.get("/public/assignments/list")["assignments"]
    assignment_id = None
    for a in assignments:
        if a["github_repo_required"]:
            assignment_id = a["id"]
            break

    adjust_assignment_theia_options(assignment_id, {
        'persistent_storage': False,
        'resources': {},
        'network-policy': 'os-student',
    })

    r = s.get(f"/public/ide/active/{assignment_id}")
    assert r == {"active": False}

    create_repo(s, assignment_id)

    r = s.post(f"/public/ide/initialize/{assignment_id}")
    ide_id = r['session']['id']

    @with_context
    def _check_assignment_ide(_ide_id):
        from anubis.models import TheiaSession
        from kubernetes.client import V1Container
        from anubis.constants import THEIA_DEFAULT_OPTIONS

        ide: TheiaSession = TheiaSession.query.filter(TheiaSession.id == _ide_id).first()

        assert ide.autosave is True
        assert ide.playground is False
        assert ide.admin is False
        assert ide.privileged is False
        assert ide.persistent_storage is False
        assert ide.repo_url == 'https://github.com/AnubisLMS/xv6'

        pod, pvc = create_theia_k8s_pod_pvc(ide, skip_debug_check=True)

        # Assert pvc things
        assert pvc is None

        # Assert pod things
        assert pod.metadata.labels['app.kubernetes.io/name'] == 'anubis'
        assert pod.metadata.labels['network-policy'] == 'os-student'
        assert pod.metadata.labels['role'] == 'theia-session'
        assert pod.metadata.labels['session'] == _ide_id
        assert pod.metadata.labels['netid'] == s.netid
        assert pod.metadata.name == f'theia-{s.netid}-{_ide_id}'

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
        assert init_container.volume_mounts[0].mount_path == '/out'

        theia_container: V1Container = None
        sidecar_container: V1Container = None
        for container in pod.spec.containers:
            if container.name == 'theia':
                theia_container = container
            elif container.name == 'sidecar':
                sidecar_container = container

        # Verify we found
        assert theia_container
        assert sidecar_container

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
        assert len(theia_container.volume_mounts) == 1
        assert theia_container.volume_mounts[0].mount_path == '/home/anubis'
        assert theia_container.volume_mounts[0].read_only is None

        ###########################################
        # Verify sidecar container

        # Check env
        sidecar_env = {env.name: env.value for env in sidecar_container.env}
        assert sidecar_env == {'AUTOSAVE': 'ON', 'NETID': s.netid, 'GIT_CRED': None, 'GIT_REPO': 'https://github.com/AnubisLMS/xv6'}

        # Check ports
        assert sidecar_container.ports is None

        # Check security context
        assert sidecar_container.security_context.allow_privilege_escalation is False
        assert sidecar_container.security_context.privileged is None
        assert sidecar_container.security_context.run_as_user == 1001

        # Verify volume
        assert len(sidecar_container.volume_mounts) == 1
        assert sidecar_container.volume_mounts[0].mount_path == '/home/anubis'
        assert sidecar_container.volume_mounts[0].read_only is None

    _check_assignment_ide(ide_id)
