import dataclasses
import enum
import re


class FileSystemState(str, enum.Enum):
    PRESENT = 'PRESENT'
    ABSENT = 'ABSENT'


@dataclasses.dataclass
class FileSystemCondition:
    path: str
    directory: bool = False
    state: FileSystemState = FileSystemState.PRESENT
    content: str = None
    content_regex: re.Pattern = None


@dataclasses.dataclass
class Exercise:
    name: str = None
    win_message: str = 'Congrats! You did the exercise by typing {user_command}'
    command_regex: re.Pattern = None
    output_regex: re.Pattern = None
    complete: bool = False
    filesystem_conditions: list[FileSystemCondition] = None

    def __str__(self):
        name = self.name
        return f'<Exercise {name=}>'

    def __repr__(self):
        return str(self)


@dataclasses.dataclass
class UserState:
    exercise_name: str
    command: str
    output: str
    cwd: str
