import json
from dataclasses import asdict

import requests
from flask import current_app

from anubis_autograde.models import Exercise, UserState
from anubis_autograde.utils import colorize_render, skip_if_debug
from anubis_autograde.logging import log

pipeline_url: str = 'http://anubis-pipeline-api:5000'


def _pipeline_api_request(endpoint: str, body: dict, query: dict = None):
    url = f'{pipeline_url}/{endpoint}/{current_app.config["SUBMISSION_ID"]}'
    log.info(f'pipeline request: {url}')
    query = query or dict()
    requests.post(
        url,
        args={'token': current_app.config["TOKEN"], **query},
        json=body
    )


@skip_if_debug
def initialize_submission_status():
    _pipeline_api_request(
        'report/state',
        {'state': 'Assignment running in IDE.'},
        {'processed': '0'}
    )


@skip_if_debug
def finalize_submission_status():
    _pipeline_api_request(
        'report/state',
        {'state': 'Submitted!'},
        {'processed': '1'}
    )


@skip_if_debug
def forward_exercise_status(
    exercise: Exercise,
    user_state: UserState,
):
    _pipeline_api_request(
        'report/test',
        {
            'test_name':   exercise.name,
            'passed':      exercise.complete,
            'message':     colorize_render(
                exercise.win_message,
                user_state=user_state,
            ),
            'output_type': 'shell_exercise',
            'output':      json.dumps({
                'exercise':   asdict(exercise),
                'user_state': asdict(user_state),
            }),
        }
    )
