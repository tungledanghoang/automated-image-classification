import os
import json

from src.service import aws_image_process, initialize_aws_clients, message_polling
from src.aws_tools import SQSManager, S3Manager


def test_main_service(moto_aws_mock):
    sqs_client, s3_client = moto_aws_mock
    queue_url = sqs_client.get_queue_url(QueueName=os.environ['SQS_QUEUE_NAME'])['QueueUrl']
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"bucket": "testing_bucket", "key": "kitchen.jpg"})
    )
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"bucket": "testing_bucket", "key": "living_room.jpg"})
    )
    s3_client.upload_file("tests/images/kitchen.jpg", "testing_bucket", "kitchen.jpg")
    s3_client.upload_file("tests/images/living_room.jpg", "testing_bucket", "living_room.jpg")
    sqs, result_sqs = initialize_aws_clients()
    messages = message_polling(sqs, 2, 5)
    aws_image_process(sqs, result_sqs, messages)

    sqs = SQSManager(os.environ['SQS_RESULT_QUEUE_NAME'])
    messages = sqs.get_sqs_messages(10)
    assert len(list(messages.values())) == 2
    for message in messages.values():
        assert message.body["status"] == "completed"
        assert message.body["bucket"] == "testing_bucket"
        assert message.body["key"] in ["kitchen.jpg", "living_room.jpg"]
