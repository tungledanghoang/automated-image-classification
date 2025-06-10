import os
import pytest

from src.service import aws_image_process
from src.aws_tools import SQSManager, S3Manager


def test_main_service(moto_aws_mock):
    sqs_client, s3_client = moto_aws_mock
    queue_url = sqs_client.get_queue_url(QueueName=os.environ['SQS_QUEUE_NAME'])['QueueUrl']
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="kitchen.jpg"
    )
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="living_room.jpg"
    )
    s3_client.upload_file("tests/images/kitchen.jpg", os.environ['S3_BUCKET_NAME'], "kitchen.jpg")
    s3_client.upload_file("tests/images/living_room.jpg", os.environ['S3_BUCKET_NAME'], "living_room.jpg")
    aws_image_process()

    sqs = SQSManager(os.environ['SQS_RESULT_QUEUE_NAME'])
    messages = sqs.get_sqs_messages(10)
    for message in messages.values():
        assert (f"Original message: kitchen.jpg. Classification result:" in message.body) | (f"Original message: living_room.jpg. Classification result:" in message.body)
