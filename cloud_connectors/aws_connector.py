"""موصل AWS: يعمل مع LocalStack أو السحابة الحقيقية"""
import os
from datetime import datetime, timedelta, timezone

import boto3

from config.settings import settings


class AWSConnector:
    def __init__(self, use_localstack: bool = True):
        if use_localstack:
            self.endpoint_url = settings.LOCALSTACK_ENDPOINT
            self.aws_access_key = "test"
            self.aws_secret_key = "test"
        else:
            self.endpoint_url = None
            self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.session = boto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region,
        )

    def _client(self, service: str):
        return self.session.client(service, endpoint_url=self.endpoint_url)

    def get_cloudtrail_events(self, hours_back: int = 1) -> list:
        """أحداث CloudTrail — في LocalStack يرجع ما تم توليده بعد تفعيل الـ trail"""
        client = self._client("cloudtrail")
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        try:
            response = client.lookup_events(StartTime=start_time, EndTime=end_time, MaxResults=50)
            return response.get("Events", [])
        except Exception as exc:
            print(f"⚠️ خطأ في جلب أحداث CloudTrail: {exc}")
            return []

    def list_ec2_instances(self) -> list:
        client = self._client("ec2")
        instances = []
        try:
            for reservation in client.describe_instances().get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instances.append({
                        "id": instance["InstanceId"],
                        "type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                        "private_ip": instance.get("PrivateIpAddress"),
                        "public_ip": instance.get("PublicIpAddress"),
                    })
        except Exception as exc:
            print(f"⚠️ خطأ في جلب EC2: {exc}")
        return instances

    def list_s3_buckets(self) -> list:
        client = self._client("s3")
        try:
            return [{"name": b["Name"]} for b in client.list_buckets().get("Buckets", [])]
        except Exception as exc:
            print(f"⚠️ خطأ في جلب S3: {exc}")
            return []

    def list_iam_users(self) -> list:
        client = self._client("iam")
        try:
            return [{"name": u["UserName"]} for u in client.list_users().get("Users", [])]
        except Exception as exc:
            print(f"⚠️ خطأ في جلب IAM: {exc}")
            return []