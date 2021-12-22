from datetime import datetime
from random import choice, randint
from string import ascii_letters as letters
from typing import List


class MockCourse():
    def __init__(self):
        self.name = "".join(choice(letters) for i in range(randint(15, 33)))
        self.course_code = "CS-GY " + "".join(
            str(randint(0, 9)) for i in range(4)
        )
        self.id = randint(0, 99)
        self.professor_display_name = "J. Smith"


class MockIDE():
    def __init__(self):
        self.created = datetime.now()
        self.created = self.created.replace(hour=abs(self.created.hour - randint(1, 5)))
        self.last_proxy = datetime.now()
        self.last_proxy = self.last_proxy.replace(
            minute=abs(self.last_proxy.minute - randint(1, 5))
        )
        self.id = randint(10000000, 99999999)


def mock_course_user_count(course: MockCourse) -> int:
    return randint(1, 200)


def mock_course_ides_opened(course: MockCourse) -> int:
    return randint(1, 9999)


def mock_courses() -> List[MockCourse]:
    return [MockCourse() for i in range(randint(3, 10))]


def mock_active_ides(desired: int = 0) -> List[MockIDE]:
    num_ides = desired if desired else randint(5, 52)
    return [MockIDE() for i in range(num_ides)]
