from event_pipeline.real_producer import infer_severity


def test_critical_action():
    assert infer_severity("CloudTrail:StopLogging") == "CRITICAL"


def test_default_low():
    assert infer_severity("S3:GetObject") == "LOW"