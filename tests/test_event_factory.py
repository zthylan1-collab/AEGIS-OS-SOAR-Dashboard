from event_pipeline.mock_producer import generate_mock_event


def test_generated_event_has_required_fields():
    event = generate_mock_event()
    for field in ["event_id", "timestamp", "cloud_provider", "user", "action", "source_ip", "severity"]:
        assert field in event