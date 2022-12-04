=====================
Example Configuration
=====================


.. code-block:: python
   :caption: Example configuration

    import re

    from anubis_autograde.models import Exercise, FileSystemCondition, ExistState


    exercises: list[Exercise] = [
        Exercise(
            name='helloworld',
            command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"?'),
            output_regex=re.compile(r'[Hh]ello\s[Ww]orld!?'),
        ),
        Exercise(
            name='mkdir exercise1',
            command_regex=re.compile(r'mkdir \'?"?exercise1?\'?"?'),
            filesystem_conditions=[
                FileSystemCondition(
                    path='exercise1',
                    directory=True,
                    state=ExistState.PRESENT,
                )
            ]
        ),
        Exercise(
            name='cd exercise1',
            command_regex=re.compile(r'cd \'?"?exercise1?\'?"?'),
        ),
        Exercise(
            name='pipe hello world',
            command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"? > exercise.txt'),
            filesystem_conditions=[
                FileSystemCondition(
                    path='exercise1/exercise.txt',
                    state=ExistState.PRESENT,
                    content_regex=re.compile(r'[Hh]ello\s[Ww]orld!')
                )
            ]
        ),
    ]


