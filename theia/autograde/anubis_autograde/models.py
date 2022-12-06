import dataclasses
import enum
import re
import typing


@dataclasses.dataclass
class UserState:
    exercise_name: str
    command: str
    output: str
    cwd: str
    environ: typing.Dict[str, str]


class ExistState(str, enum.Enum):
    """
    PRESENT = 'PRESENT'
    ABSENT = 'ABSENT'
    """
    PRESENT = 'PRESENT'
    ABSENT = 'ABSENT'


@dataclasses.dataclass
class FileSystemCondition:
    path: str
    directory: bool = False
    state: ExistState = ExistState.PRESENT
    content: str = None
    content_regex: re.Pattern = None


@dataclasses.dataclass
class EnvVarCondition:
    name: str
    value_regex: re.Pattern = None
    state: ExistState = ExistState.PRESENT


@dataclasses.dataclass
class Exercise:
    name: str = None
    complete: bool = False
    start_message: str = None
    win_message: str = 'Congrats! You did the exercise by typing {{ user_state.command }}'
    fail_message: str = None
    hint_message: str = None
    fail_to_hint_message_count: int = 2
    fail_to_start_message_count: int = 8
    command_regex: re.Pattern = None
    output_regex: re.Pattern = None
    cwd_regex: re.Pattern = None
    filesystem_conditions: typing.List[FileSystemCondition] = None
    env_var_conditions: typing.List[EnvVarCondition] = None
    eject_function: typing.Callable[['Exercise', UserState], bool] = None

    failures: int = 0  # internal use only

    def __str__(self):
        name = self.name
        return f'<Exercise name={name}>'

    def __repr__(self):
        return str(self)
