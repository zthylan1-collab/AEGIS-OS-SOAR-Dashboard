import os

import pytest

from cloud_connectors.aws_connector import AWSConnector

pytestmark = pytest.mark.skipif(
    os.getenv("AEGIS_RUN_LOCALSTACK_TESTS", "0") == "0",
    reason="يتطلب LocalStack شغالاً — فعّله بـ: AEGIS_RUN_LOCALSTACK_TESTS=1",
)


def test_localstack_ec2_returns_list():
    conn = AWSConnector(use_localstack=True)
    assert isinstance(conn.list_ec2_instances(), list)