import os
import pytest
from src.aws_tools import SQSManager


@pytest.fixture(scope="module")
def sqs(moto_aws_mock):
    sqs_client, _ = moto_aws_mock
    queue_url = sqs_client.get_queue_url(QueueName=os.environ['SQS_QUEUE_NAME'])['QueueUrl']
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="First sqs message"
    )
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="Second sqs message"
    )
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="Third sqs message"
    )
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="Fourth sqs message"
    )
    sqs_manager = SQSManager(queue_name=os.environ['SQS_QUEUE_NAME'])
    return sqs_manager


def test_sqs_get_message(sqs, namespace):
    messages = sqs.get_sqs_messages(10)
    messages_body = [message.body for message in messages.values()]
    namespace['sqs_messages'] = messages
    assert "First sqs message" in messages_body
    assert "Second sqs message" in messages_body
    assert "Third sqs message" in messages_body
    assert "Fourth sqs message" in messages_body


def test_sqs_delete_message(sqs, namespace):
    sqs.delete_sqs_messages(namespace['sqs_messages'])
    second_poll = sqs.get_sqs_messages(10)
    assert len(second_poll.values()) == 0


def test_sqs_send_message(sqs):
    sqs.send_sqs_messages(["Testing message send"])
    res = sqs.get_sqs_messages(1)
    assert list(res.values())[0].body == "Testing message send"
