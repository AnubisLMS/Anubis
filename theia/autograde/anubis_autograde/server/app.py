from flask import Flask

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.exercise.verify import run_exercise
from anubis_autograde.utils import text_response, reject_handler, user_state_from_request
from flask import Flask

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.exercise.verify import run_exercise
from anubis_autograde.utils import text_response, reject_handler, user_state_from_request

app = Flask(__name__)


@app.get('/status')
@text_response
def status():
    output = 'Exercise Status:\n'
    for exercise in get_exercises():
        output += f'`-> name:     {exercise.name}\n'
        output += f'    complete: {exercise.complete}\n'
    return output


@app.post('/submit')
@text_response
@reject_handler
def submit():
    # Get options from the form
    user_state = user_state_from_request()
    exercise = run_exercise(user_state)

    return exercise.win_message.format(
        user_exercise_name=user_state.exercise_name,
        user_command=user_state.command,
        user_output=user_state.output,
    )
