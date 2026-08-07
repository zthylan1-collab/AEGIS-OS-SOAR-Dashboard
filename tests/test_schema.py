import pytest

from event_pipeline.schema import validate_event


def test_valid_event_passes():
    event = {
        "event_id": "123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2026-08-06T10:00:00Z",
        "cloud_provider": "aws",
        "user": "admin@example.com",
        "action": "IAM:ConsoleLoginFailure",
        "source_ip": "1.2.3.4",
        "severity": "HIGH",
        "details": {},
    }
    validate_event(event)  # لا يجب أن يرفع استثناء


def test_invalid_event_raises():
    with pytest.raises(Exception):
        validate_event({"event_id": "ناقص الحقول"})