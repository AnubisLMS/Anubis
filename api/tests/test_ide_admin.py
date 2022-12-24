from utils import permission_test

settings_sample = {
    "network_dns_locked": False,
    "privileged": True,
    "repo_url": "https://github.com/os3224/anubis-assignment-tests",
    "options": '{"limits": {"cpu": "4", "memory": "4Gi"}}',
}


def test_ide_admin():
    permission_test("/admin/ide/initialize", method="post", json={"settings": settings_sample})
    permission_test("/admin/ide/active")
    permission_test("/admin/ide/list")
    permission_test("/admin/ide/reap-all")
