THEIA_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "750m", "memory": "500Mi"},
        "limits": {"cpu": "1.5", "memory": "750Mi"},
    },
}

DEVELOPER_DEFAULT_IMAGE = "registry.digitalocean.com/anubis/theia-base"
DEVELOPER_DEFAULT_OPTIONS = {
    "autosave": False,
    "persistent_storage": True,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "2000m", "memory": "4Gi"},
        "limits": {"cpu": "4000m", "memory": "6Gi"},
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

NYU_DOMAIN = 'anubis.osiris.services'


REAPER_TXT = """

             ___
            /   \\\\
       /\\\\ | . . \\\\
     ////\\\\|     ||
   ////   \\\\\\ ___//\\
  ///      \\\\      \\
 ///       |\\\\      |     
//         | \\\\  \\   \\    
/          |  \\\\  \\   \\   
           |   \\\\ /   /   
           |    \\/   /    
           |     \\\\/|     
           |      \\\\|     
           |       \\\\     
           |        |     
           |_________\\  

"""