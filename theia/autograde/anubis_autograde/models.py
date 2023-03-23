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
    directory_fail_message: str = None

    state: ExistState = ExistState.PRESENT
    state_fail_message: str = None

    content: str = None
    content_fail_message: str = None

    content_regex: re.Pattern = None
    content_regex_fail_message: str = None


@dataclasses.dataclass
class EnvVarCondition:
    name: str

    # Value regex
    value_regex: re.Pattern = None
    value_regex_fail_message: str = None

    # State
    state: ExistState = ExistState.PRESENT
    state_fail_message: str = None


@dataclasses.dataclass
class Exercise:
    name: str = None

    # Exercise related jinja2 templates
    start_message: str = None
    win_message: str = 'Congrats! You did the exercise by typing {{ user_state.command }}'
    fail_message: str = None
    hint_message: str = None

    # Number of failed commands before getting hint
    fail_to_hint_message_count: int = 2

    # Number of failed commands before getting start message
    fail_to_exercise_start_message_count: int = 4

    # Number of failed commands before getting start message
    fail_to_assignment_start_message_count: int = 16

    # User command regex
    command_regex: re.Pattern = None
    command_regex_fail_message: str = None

    # User output regex
    output_regex: re.Pattern = None
    output_regex_fail_message: str = None

    # User vwd regex
    cwd_regex: re.Pattern = None
    cwd_regex_fail_message: str = None

    # Filesystem related conditions
    filesystem_conditions: typing.List[FileSystemCondition] = None

    # Environment variable conditions
    env_var_conditions: typing.List[EnvVarCondition] = None

    # Eject function. Use with care.
    eject_function: typing.Callable[['Exercise', UserState], bool] = None

    complete: bool = False # internal use only
    failures: int = 0  # internal use only

    def __str__(self):
        name = self.name
        return f'<Exercise name={name}>'

    def __repr__(self):
        return str(self)
