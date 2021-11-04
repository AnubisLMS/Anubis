from utils import permission_test

sample_config = [{"key": "MAX_IDES", "value": "75"}]


def test_config_admin():
    permission_test("/admin/config/list")
    permission_test(
        "/admin/config/save",
        method="post",
        json={"config": sample_config},
        fail_for=[
            "student",
            "professor",
            "ta",
        ],
    )
