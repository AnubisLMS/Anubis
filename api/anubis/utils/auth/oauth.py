from flask_oauthlib.client import OAuth

from anubis.config import config

oauth = OAuth()
OAUTH_REMOTE_APP = oauth.remote_app(
    "nyu",
    base_url="https://auth.nyu.edu/oauth2/",
    authorize_url="https://auth.nyu.edu/oauth2/authorize",
    request_token_url=None,
    request_token_params={"scope": "openid"},
    access_token_url="https://auth.nyu.edu/oauth2/token",
    access_token_params={"client_id": config.OAUTH_CONSUMER_KEY},
    consumer_key=config.OAUTH_CONSUMER_KEY,
    consumer_secret=config.OAUTH_CONSUMER_SECRET,
)

OAUTH_REMOTE_APP_GITHUB = oauth.remote_app(
    "github",
    base_url="https://github.com/login/oauth/",
    authorize_url="https://github.com/login/oauth/authorize",
    request_token_url=None,
    request_token_params={
        "client_id": config.OAUTH_GITHUB_CLIENT_KEY,
        "scope": "read:user"
    },
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params={
        "client_id": config.OAUTH_GITHUB_CLIENT_KEY,
        "client_secret": config.OAUTH_GITHUB_CLIENT_SECRET,
    },
    consumer_key=config.OAUTH_GITHUB_CLIENT_KEY,
    consumer_secret=config.OAUTH_GITHUB_CLIENT_SECRET,
)