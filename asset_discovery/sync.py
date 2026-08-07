#!/usr/bin/env python3
"""مزامنة الأصول (EC2 + S3 + IAM) من السحابة إلى PostgreSQL"""
import argparse
import logging
from datetime import datetime, timezone

from cloud_connectors.aws_connector import AWSConnector
from database.models import Asset, SessionLocal, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("asset_sync")


def upsert_asset(db, asset_id, name, asset_type, provider, region, details):
    db.merge(Asset(
        id=asset_id,
        name=name,
        type=asset_type,
        cloud_provider=provider,
        region=region,
        details=details,
        last_seen=datetime.now(timezone.utc),
    ))


def sync_aws(db, connector: AWSConnector) -> int:
    count = 0
    for vm in connector.list_ec2_instances():
        upsert_asset(db, vm["id"], vm["id"], "EC2", "aws", "us-east-1", vm)
        count += 1
    for bucket in connector.list_s3_buckets():
        upsert_asset(db, f"s3:{bucket['name']}", bucket["name"], "S3", "aws", "us-east-1", bucket)
        count += 1
    for user in connector.list_iam_users():
        upsert_asset(db, f"iam:{user['name']}", user["name"], "IAM", "aws", "us-east-1", user)
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["localstack", "aws"], default="localstack")
    args = parser.parse_args()

    init_db()
    connector = AWSConnector(use_localstack=(args.env == "localstack"))
    db = SessionLocal()
    try:
        count = sync_aws(db, connector)
        db.commit()
        log.info(f"✅ تمت مزامنة {count} أصل إلى PostgreSQL")
    finally:
        db.close()


if __name__ == "__main__":
    main()