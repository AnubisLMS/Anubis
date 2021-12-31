import sys
from typing import List

import google.oauth2.credentials
import googleapiclient.discovery
import kubernetes.client
import kubernetes.config
from googleapiclient.discovery import build

from anubis.k8s.google import get_google_secret, get_google_credentials
from anubis.utils.exceptions import GoogleCredentialsException


def assert_google_credentials(google_credentials: google.oauth2.credentials.Credentials):
    # If we don't have credentials, then we can not communicate with the Google api.
    # Exit with error if google_creds is None at this point. Exiting with 1 will
    # make the pod fail which we can set up alerts for later.
    if google_credentials is None:
        raise GoogleCredentialsException('MISSING GOOGLE API CREDENTIALS')

    # The token can expire or be disabled. In these cases, then there is nothing
    # more we can do. Exit with an error.
    if not google_credentials.valid:
        raise GoogleCredentialsException('GOOGLE API CREDENTIALS INVALID')


def build_google_service(
    secret_name: str,
    google_api: str,
    google_api_version: str,
    scopes: List[str],
) -> googleapiclient.discovery.Resource:
    """
    Build the Google service object for interacting with gmail/calendar apis.

    :param secret_name:
    :param google_api:
    :param google_api_version:
    :param scopes:
    :return:
    """

    # Setup Kubernetes incluster client
    kubernetes.config.load_incluster_config()

    # Get CoreV1Api object
    v1 = kubernetes.client.CoreV1Api()

    # Get kubernetes credentials secret object
    secret = get_google_secret(v1, secret_name)

    # Use credentials secret and turn it into a Google credentials
    # object for building the Google service object
    google_credentials = get_google_credentials(v1, secret, scopes)

    # Assert that the Google credentials are valid and usable. Otherwise,
    # this will raise a GoogleCredentialsException
    assert_google_credentials(google_credentials)

    # Create the Google service object using Google credentials
    service = build(google_api, google_api_version, credentials=google_credentials)
    service: googleapiclient.discovery.Resource

    return service
