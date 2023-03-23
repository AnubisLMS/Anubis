import json
from dataclasses import asdict

import requests
from flask import current_app
from retry import retry

from anubis_autograde.logging import log
from anubis_autograde.models import Exercise, UserState
from anubis_autograde.utils import colorize_render, skip_if_not_prod

pipeline_url: str = 'http://anubis-pipeline-api:5000'


@retry(tries=3)
def _pipeline_api_request(endpoint: str, body: dict = None, query: dict = None, method: str = 'post'):
    url = f'{pipeline_url}/{endpoint}/{current_app.config["SUBMISSION_ID"]}'
    log.info(f'pipeline request: {url}')
    query = query or dict()
    query = {'token': current_app.config["TOKEN"], **query}
    if method == 'post':
        response = requests.post(
            url,
            params=query,
            headers={'Content-Type': 'application/json'},
            json=body,
            timeout=5,
        )
    elif method == 'get':
        response = requests.get(
            url,
            params=query,
            timeout=5,
        )
    else:
        raise
    log.info(f'response.text = {response.text}')
    assert response.status_code == 200


@skip_if_not_prod
def pipeline_initialize_submission_status():
    _pipeline_api_request(
        'pipeline/report/state',
        {'state': "Assignment run in IDE."},
        {'processed': '0'}
    )


@skip_if_not_prod
def pipeline_finalize_submission_status():
    _pipeline_api_request(
        'pipeline/report/state',
        {'state': 'Submitted!'},
        {'processed': '1'}
    )


@skip_if_not_prod
def pipeline_reset_submission_status():
    _pipeline_api_request(
        'pipeline/reset',
        method='get'
    )


@skip_if_not_prod
def pipeline_forward_exercise_status(
    exercise: Exercise,
    user_state: UserState,
):
    _pipeline_api_request(
        'pipeline/report/test',
        {
            'test_name':   exercise.name,
            'passed':      exercise.complete,
            'message':     colorize_render(
                exercise.win_message,
                user_state=user_state,
            ),
            'output_type': 'shell_exercise',
            'output':      json.dumps({
                'exercise':   repr(exercise),
                'user_state': asdict(user_state),
            }),
        }
    )
