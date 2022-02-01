import pytest

from dataclasses import dataclass, field
from typing import Callable, List, Sequence, Tuple

from anubis.assignment import utils

@dataclass
class CompareTestFixture:
    comp_func: Callable[[Sequence[str], Sequence[str], bool], Tuple[bool, List[str]]]
    matched: bool
    actual: List[str]
    expected: List[str]
    diff: List[str] = field(default_factory=list)
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
        diff=['--- ', '+++ ', '@@ -1,3 +1,3 @@', '-asd', '+asdf', ' qwe', ' 123'],
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
        diff=['--- ', '+++ ', '@@ -1,3 +1,3 @@', " asd", "-qwee", "+qwed", " 123"],
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
        diff=[],
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["asd", "qww"],
        expected=["asd", "qww", "123A"],
        diff=['--- ', '+++ ', '@@ -1,3 +1,2 @@', " asd", " qww", "-123A"],
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["asd", "qww"],
        expected=["asd", "qww", "123A"],
        diff=['--- ', '+++ ', '@@ -1,3 +1,2 @@', " asd", " qww", "-123a"],
        case_sensitive=False,
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["asd", "qww", "fgff", "kasd", "asdasd"],
        expected=["asd", "qww", "fgff", "kasd", "asdasd", "123A"],
        diff=['--- ', '+++ ', '@@ -3,4 +3,3 @@', " fgff", " kasd", " asdasd", "-123A"],
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["a", "b"],
        expected=["a", "b", "c"],
        diff=['--- ', '+++ ', '@@ -1,3 +1,2 @@', " a", " b", "-c"],
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["exec test failed"],
        expected=["sample 1", "sample 2", "sample 3", "sample 4", "sample 5", "sample 6", "sample 7"],
        diff=["--- ", "+++ ", "@@ -1,7 +1 @@", "-sample 1", "-sample 2", "-sample 3", "-sample 4", "-sample 5", "-sample 6", "-sample 7", "+exec test failed"]
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["sample 1", "sample 2", "exec test failed"],
        expected=["sample 1", "sample 2", "sample 3", "sample 4", "sample 5", "sample 6", "sample 7"],
        diff=["--- ", "+++ ", "@@ -1,7 +1,3 @@", " sample 1", " sample 2", "-sample 3", "-sample 4", "-sample 5", "-sample 6", "-sample 7", "+exec test failed"]
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["sample 1", "sample 2", "sample 3", "sample 4", "sample 5", "sample 6", "sample 7"],
        expected=["sample 1", "sample 2", "sample x"],
        diff=["--- ", "+++ ", "@@ -1,3 +1,7 @@", " sample 1", " sample 2", "-sample x", "+sample 3", "+sample 4", "+sample 5", "+sample 6", "+sample 7"]
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=True,
        actual=["asd\n"],
        expected=["asd"],
        diff=[]
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=[],
        expected=["bar"],
        diff=["--- ", "+++ ", "@@ -1 +0,0 @@", "-bar"]
    ), CompareTestFixture(
        comp_func=utils.test_lines,
        matched=False,
        actual=["my broken for loop" for _ in range(2000)],
        expected=["foo", "bar"],
        # 1000 is the default cutoff for the length of the context
        # We make sure that excessively long output produced by
        # student code will not go into the difflib.unified_diff function
        diff=["--- ", "+++ ", "@@ -1,2 +1,1000 @@", "-foo", "-bar"] + ["+my broken for loop" for _ in range(1000)]
    )]

def test_compare_func(compare_test_fixtures: List[CompareTestFixture]):
    for fixture in compare_test_fixtures:
        matched, diff = fixture.comp_func(fixture.actual, fixture.expected, fixture.case_sensitive)
        assert matched == fixture.matched
        assert not matched or (matched and len(fixture.diff) == 0)
        assert diff == fixture.diff
