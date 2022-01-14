import pytest
import dataclasses

from typing import Callable, List, Sequence

from anubis.assignment import utils

@dataclasses.dataclass
class CompareTestFixture:
    comp_func: Callable[[Sequence[str], Sequence[str], bool], bool]
    matched: bool
    actual: List[str]
    expected: List[str]
    case_sensitive: bool = True

@pytest.fixture
def compare_test_fixtures() -> List[CompareTestFixture]:
    return [CompareTestFixture(
        comp_func=utils.test_lines,
        matched=True,
        actual=["asd", "qwe", "123"],
        expected=["asd", "qwe", "123"],
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["asdf", "qwe", "123"],
        expected=["asd", "qwe", "123"],
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=True,
        actual=["AsD", "QwE", "123"],
        expected=["aSd", "qWe", "123"],
        case_sensitive=False,
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["AsD", "QwEd", "123"],
        expected=["aSd", "qWee", "123"],
        case_sensitive=False,
    ), CompareTestFixture(
        comp_func=utils.search_lines,
        matched=True,
        actual=["asd", "qwe", "debugging", "123"],
        expected=["asd", "qwe", "123"],
    ), CompareTestFixture(
        comp_func=utils.search_lines,
        matched=False,
        actual=["asd", "qwe", "123"],
        expected=["asd", "qwe", "debugging", "123"],
    )]

def test_compare_func(compare_test_fixtures: List[CompareTestFixture]):
    for fixture in compare_test_fixtures:
        matched = fixture.comp_func(fixture.actual, fixture.expected, fixture.case_sensitive)
        assert matched == fixture.matched
