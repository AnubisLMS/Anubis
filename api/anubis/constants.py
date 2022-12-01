# Standard IDE variables
THEIA_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "750m", "memory": "500Mi"},
        "limits": {"cpu": "1.5", "memory": "750Mi"},
    },
}

# Developer IDE variables
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

# Webtop IDE variables
WEBTOP_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "1000m", "memory": "1Gi"},
        "limits": {"cpu": "3000m", "memory": "4Gi"},
    },
}

# Autograde IDE related variables
AUTOGRADE_IDE_DEFAULT_IMAGE = "registry.digitalocean.com/anubis/theia-jepst-test"

# NYU specific variables
NYU_DOMAIN = 'anubis.osiris.services'

# Database Variables
DB_COLLATION = "utf8mb4_general_ci"
DB_CHARSET = "utf8mb4"

# Google Gmail variables
EMAIL_FROM = "noreply@anubis-lms.io"
GOOGLE_GMAIL_CREDS_SECRET = "google-gmail-creds"
GOOGLE_GMAIL_CREDS_SCOPES = ['https://www.googleapis.com/auth/gmail.send']


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
