import os
import pytest
import boto3
from moto import mock_aws
from src.logging import logger


@pytest.fixture(scope="session")
def moto_aws_mock():
    with mock_aws():
        os.environ['AWS_ACCESS_ID'] = "awsaccessid"
        os.environ['AWS_ACCESS_KEY'] = "awsaccesskey"
        os.environ['AWS_REGION'] = "ap-southeast-1"
        os.environ['SQS_QUEUE_NAME'] = "testing_queue"
        os.environ['SQS_RESULT_QUEUE_NAME'] = "testing_result_queue"
        os.environ['MODEL_NAME'] = "resnet18"
        sqs_client = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
        sqs_client.create_queue(QueueName=os.environ['SQS_QUEUE_NAME'])
        sqs_client.create_queue(QueueName=os.environ['SQS_RESULT_QUEUE_NAME'])
        s3_client = boto3.client('s3', region_name=os.environ['AWS_REGION'])
        s3_client.create_bucket(Bucket="testing_bucket",
                                CreateBucketConfiguration={"LocationConstraint": os.environ['AWS_REGION']})
        yield sqs_client, s3_client


@pytest.fixture(scope="session")
def namespace():
    return {}
