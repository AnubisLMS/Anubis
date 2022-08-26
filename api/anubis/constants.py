THEIA_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "750m", "memory": "500Mi"},
        "limits": {"cpu": "1.5", "memory": "750Mi"},
    },
}

WEBTOP_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "1", "memory": "1Gi"},
        "limits": {"cpu": "3", "memory": "4Gi"},
    },
}
DB_COLLATION = "utf8mb4_general_ci"
DB_CHARSET = "utf8mb4"

EMAIL_FROM = "noreply@anubis-lms.io"
