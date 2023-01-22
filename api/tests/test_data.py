import pytest

from anubis.utils.data import verify_data_shape


@pytest.mark.parametrize("students", [
    [{'netid': 'abc123', 'name': 'x y z'}],
    [{'netid': 'abc123', 'name': 'x y z'}, {'netid': 'abc123', 'name': 'x y z'}]
])
def test_verify_shape(students):
    passed, error_msg = verify_data_shape(students, [{"netid": str, "name": str}])
    assert passed
    assert error_msg is None


@pytest.mark.parametrize("students,error", [
    ([{'netid': 'abc123', 'name': 1}], '.[0].name'),
    ([{'netid': 'abc123', 'name': 'x y z'}, {'netid': 'abc123', 'name': None}], '.[1].name'),
    ([{'netid': 'abc123', 'name': 'x y z'}, {'netid': 123, 'name': 'x y z'}], '.[1].netid')
])
def test_verify_shape_fail(students, error):
    passed, error_msg = verify_data_shape(students, [{"netid": str, "name": str}])
    assert not passed
    assert error_msg == error
