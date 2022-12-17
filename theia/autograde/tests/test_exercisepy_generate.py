import os
import pathlib

import pytest

from anubis_autograde.exercise.run import run_exercise_init


@pytest.mark.parametrize('args', [['exercise-init']])
class TestExerciseGenerate:
    @pytest.fixture()
    def exercise_py(self, pytester, parser, args) -> pathlib.Path:
        parser.parse_args(args)
        run_exercise_init(args)
        exercise_py = (pytester.path / 'exercise.py')
        assert exercise_py.exists()
        return exercise_py

    @pytest.fixture()
    def exercise(self, exercise_py):
        os.chdir(exercise_py.parent)
        import exercise
        assert exercise
        return exercise

    def test_exercise_py_gen(self, exercise_py):
        pass

    def test_exercise_py_importable(self, exercise):
        pass

    def test_exercise_py_valid_items(self, exercise):
        assert exercise.start_message
        assert exercise.end_message
        assert exercise.exercises
        assert len(exercise.exercises) == 4

    def test_exercise_py_valid_names(self, exercise):
        assert exercise.exercises[0].name == 'helloworld'
        assert exercise.exercises[1].name == 'mkdir exercise1'
        assert exercise.exercises[2].name == 'cd exercise1'
        assert exercise.exercises[3].name == 'pipe hello world'
