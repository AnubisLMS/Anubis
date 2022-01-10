import base64
import json
from typing import List, Optional

import google.oauth2
import kubernetes.client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def get_google_secret(v1: kubernetes.client.CoreV1Api, secret_name: str) -> kubernetes.client.V1Secret:
    # Read credential token from kubernetes api.
    secret = v1.read_namespaced_secret(secret_name, "anubis")
    secret: kubernetes.client.V1Secret
    return secret


def get_google_credentials(
    v1: kubernetes.client.CoreV1Api,
    secret: kubernetes.client.V1Secret,
    scopes: List[str],
) -> Optional[google.oauth2.credentials.Credentials]:
    token = json.loads(base64.b64decode(secret.data["token.json"].encode()).decode())

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    google_creds = Credentials.from_authorized_user_info(token, scopes)

    if google_creds and google_creds.expired and google_creds.refresh_token:
        google_creds.refresh(Request())

        # Otherwise, we are reliant on the k8s api being available to
        # patch the token.json object in the secret resource.
        secret.data["token.json"] = base64.b64encode(google_creds.to_json().encode()).decode()
        v1.patch_namespaced_secret(secret.metadata.name, "anubis", secret)

    return google_creds
