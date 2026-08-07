#!/usr/bin/env python3
"""ينشئ موارد وهمية في LocalStack ويولّد أحداث CloudTrail فعلية"""
import boto3

from config.settings import settings

REGION = "us-east-1"
session = boto3.Session(aws_access_key_id="test", aws_secret_access_key="test", region_name=REGION)

ec2 = session.client("ec2", endpoint_url=settings.LOCALSTACK_ENDPOINT)
s3 = session.client("s3", endpoint_url=settings.LOCALSTACK_ENDPOINT)
iam = session.client("iam", endpoint_url=settings.LOCALSTACK_ENDPOINT)
ct = session.client("cloudtrail", endpoint_url=settings.LOCALSTACK_ENDPOINT)

# 1) خادم وهمي
ec2.run_instances(ImageId="ami-0a1b2c3d4e5f6a7b8", MinCount=1, MaxCount=1, InstanceType="t3.micro")
print("✅ EC2 instance")

# 2) سلة S3
s3.create_bucket(Bucket="aegis-demo-bucket")
print("✅ S3 bucket")

# 3) مستخدم IAM
iam.create_user(UserName="demo-analyst")
print("✅ IAM user")

# 4) تفعيل CloudTrail حتى يُسجل الأحداث
ct.create_trail(Name="aegis-trail", S3BucketName="aegis-demo-bucket", IsMultiRegionTrail=True)
ct.start_logging(Name="aegis-trail")
print("✅ CloudTrail trail + logging")

# 5) توليد نشاط يُسجل في CloudTrail
s3.put_bucket_versioning(Bucket="aegis-demo-bucket", VersioningConfiguration={"Status": "Enabled"})
iam.create_access_key(UserName="demo-analyst")
print("✅ تم توليد أحداث قابلة للجلب")