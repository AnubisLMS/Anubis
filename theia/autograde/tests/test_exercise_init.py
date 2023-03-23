class TestExerciseGenerate:

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
