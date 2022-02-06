from flask_oauthlib.client import OAuth

from anubis.env import env

oauth = OAuth()
OAUTH_REMOTE_APP_NYU = oauth.remote_app(
    "nyu",
    base_url="https://auth.nyu.edu/oauth2/",
    authorize_url="https://auth.nyu.edu/oauth2/authorize",
    request_token_url=None,
    request_token_params={"scope": "openid"},
    access_token_url="https://auth.nyu.edu/oauth2/token",
    access_token_params={"client_id": env.OAUTH_NYU_CONSUMER_KEY},
    consumer_key=env.OAUTH_NYU_CONSUMER_KEY,
    consumer_secret=env.OAUTH_NYU_CONSUMER_SECRET,
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
