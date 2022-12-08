import os
import traceback
from typing import Any

import requests

from anubis.utils.logging import logger


def get_github_token() -> str | None:
    # Get GITHUB token from environment
    token = os.environ.get("GITHUB_TOKEN", None)

    # If we could not get the token, log and return None
    if token is None:
        logger.error("MISSING GITHUB_TOKEN")
        return None

    return token


def github_rest(url, body=None, method: str = "get", api_domain: str = "api.github.com", accept: str = "application/vnd.github.v3+json") -> dict | bytes | None:
    # Get the github api token
    token = get_github_token()

    url = f'https://{api_domain}' + url
    headers = {
        "Accept": accept,
        "Authorization": f"token {token}",
    }

    req_function = {
        "put": requests.put,
        "get": requests.get,
        "del": requests.delete,
        "delete": requests.delete,
    }[method.lower()]

    r = None
    try:
        if body is not None:
            r: requests.Response = req_function(url, headers=headers, json=body)
        else:
            r: requests.Response = req_function(url, headers=headers)
        is_json = 'application/json' in r.headers.get('Content-Type')
        if is_json:
            if r.status_code == 204:
                return dict()
            return r.json()
        else:
            return r.content
    except Exception as e:
        if r is not None and isinstance(r, requests.Response):
            logger.error(str(r))
            logger.error(r.content)
        logger.error(traceback.format_exc())
        logger.error(f"Request to github api Failed {e}")
        return None


def github_graphql(query: str, variables: dict[str, Any] = None) -> dict[str, Any] | None:
    # Default values for variables
    if variables is None:
        variables = dict()

    token = get_github_token()

    # set up request options
    url = "https://api.github.com/graphql"
    json = {"query": query, "variables": variables}
    headers = {"Authorization": "token %s" % token}

    # Make the graph request over http
    try:
        r = requests.post(url=url, json=json, headers=headers)
        return r.json()["data"]
    except KeyError as e:
        logger.error(traceback.format_exc())
        logger.error(r.content)
        return None
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Request to github api Failed {e}")
        return None
