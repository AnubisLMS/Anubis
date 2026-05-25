from flask_oauthlib.client import OAuth

from anubis.env import env

oauth = OAuth()

ENTRA_TENANT_ID = env.OAUTH_ENTRA_TENANT_ID
ENTRA_AUTHORITY = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}"
ENTRA_AUTHORIZE_URL = f"{ENTRA_AUTHORITY}/oauth2/v2.0/authorize"
ENTRA_TOKEN_URL = f"{ENTRA_AUTHORITY}/oauth2/v2.0/token"

OAUTH_REMOTE_APP_ENTRA = oauth.remote_app(
    "entra",
    base_url="https://graph.microsoft.com/",
    authorize_url=ENTRA_AUTHORIZE_URL,
    request_token_url=None,
    request_token_params={"scope": "openid profile email User.Read"},
    access_token_url=ENTRA_TOKEN_URL,
    access_token_params={"client_id": env.OAUTH_ENTRA_CLIENT_ID},
    access_token_method="POST",
    consumer_key=env.OAUTH_ENTRA_CLIENT_ID,
    consumer_secret=env.OAUTH_ENTRA_CLIENT_SECRET,
)

OAUTH_REMOTE_APP_GITHUB = oauth.remote_app(
    "github",
    base_url="https://github.com/login/oauth/",
    authorize_url="https://github.com/login/oauth/authorize",
    request_token_url=None,
    request_token_params={"scope": "read:user"},
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params={
        "client_id": env.OAUTH_GITHUB_CONSUMER_KEY,
        "client_secret": env.OAUTH_GITHUB_CONSUMER_SECRET,
    },
    consumer_key=env.OAUTH_GITHUB_CONSUMER_KEY,
    consumer_secret=env.OAUTH_GITHUB_CONSUMER_SECRET,
)
