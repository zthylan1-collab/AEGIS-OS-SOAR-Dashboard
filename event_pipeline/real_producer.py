#!/usr/bin/env python3
"""Producer حقيقي: يجلب أحداث CloudTrail من AWS ويرسلها إلى Redpanda"""
import argparse
import logging
import time
from datetime import datetime

from cloud_connectors.aws_connector import AWSConnector
from config.settings import settings
from event_pipeline.producer import get_producer, send_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("real_producer")

CRITICAL_ACTIONS = {
    "CloudTrail:StopLogging", "S3:DeleteBucket", "IAM:AttachUserPolicy",
    "RDS:DeleteDatabase", "S3:PutBucketPolicy",
}
HIGH_ACTIONS = {
    "IAM:ConsoleLoginFailure", "EC2:AuthorizeSecurityGroupIngress",
    "IAM:CreateAccessKey", "S3:PutBucketAcl",
}


def infer_severity(action: str) -> str:
    if action in CRITICAL_ACTIONS:
        return "CRITICAL"
    if action in HIGH_ACTIONS:
        return "HIGH"
    if action.endswith("Failure") or action.endswith("Denied"):
        return "MEDIUM"
    return "LOW"


def make_json_safe(obj):
    """تحويل أي كائن (datetime, dict, list) إلى صيغة JSON قابلة للتسلسل"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_safe(i) for i in obj]
    return obj


def format_event(raw: dict) -> dict:
    return {
        "event_id": str(raw.get("EventId")),
        "timestamp": raw.get("EventTime", datetime.now()).isoformat(),
        "cloud_provider": "aws",
        "user": raw.get("Username"),
        "resource": raw.get("Resources", [{}])[0].get("ResourceName") if raw.get("Resources") else None,
        "action": raw.get("EventName"),
        "source_ip": raw.get("SourceIPAddress"),
        "severity": infer_severity(raw.get("EventName", "")),
        "details": make_json_safe(raw),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=60, help="الجلب كل N ثانية")
    parser.add_argument("--once", action="store_true", help="جلب مرة واحدة ثم الخروج")
    args = parser.parse_args()

    connector = AWSConnector(use_localstack=False)
    producer = get_producer()

    while True:
        events = connector.get_cloudtrail_events()
        log.info(f"تم جلب {len(events)} حدث من CloudTrail")
        for raw in events:
            send_event(producer, settings.RAW_EVENTS_TOPIC, format_event(raw))
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()