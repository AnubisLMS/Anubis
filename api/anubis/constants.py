THEIA_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "750m", "memory": "500Mi"},
        "limits": {"cpu": "1.5", "memory": "750Mi"},
    },
}
