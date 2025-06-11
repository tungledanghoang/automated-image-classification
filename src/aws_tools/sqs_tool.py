import os
import boto3
import json
from typing import List

from src.schemas import SQSMessage, SQSSendMessage
from src.logging import logger


class SQSManager:
    """
    Simple class providing methods for getting SQS messages and deleting them from queue
    """
    def __init__(self, queue_name: str):
        self.sqs = boto3.client('sqs', aws_access_key_id=os.environ['AWS_ACCESS_ID'],
                                aws_secret_access_key=os.environ['AWS_ACCESS_KEY'],
                                region_name=os.environ['AWS_REGION'])
        self.queue_url = [url for url in self.sqs.list_queues()['QueueUrls'] if queue_name in url][0]
        if len(self.queue_url) == 0:
            raise ValueError(f"SQS queue {queue_name} does not exist")
        self.receipt_handles = []

    def get_sqs_messages(self, max_number: int = 10, long_poll_time: int = 5) -> dict[str, SQSMessage]:
        """
        Get SQS messages from queue

        Args:
            max_number (int): max number of messages to get from queue at once
            long_poll_time (int): long polling time

        Returns:
            dict with key being message id and value being a dict containing
            message body, sent timestamp and receipt handle
        """
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_number,
            AttributeNames=[
                'SentTimestamp'
            ],
            MessageAttributeNames=[
                'All'
            ],
            WaitTimeSeconds=long_poll_time
        )
        messages_res = response.get('Messages', [])
        messages_dict = {}

        # When polling messages from SQS, it is possible that there will be duplicates
        # therefore it is necessary to filter out the duplicates, keeping only the last unique
        # message polled, as they will have the receipt handle needed for deleting messages
        for message in messages_res:
            message_id = message['MessageId']
            data = {'body': json.loads(message['Body']),
                    'timestamp': int(message['Attributes']['SentTimestamp']),
                    'receipt_handle': message['ReceiptHandle']}
            if message['MessageId'] not in messages_dict.keys():
                messages_dict[message_id] = SQSMessage(**data)
            elif messages_dict[message_id]['timestamp'] < data['timestamp']:
                messages_dict[message_id] = SQSMessage(**data)
        return messages_dict

    def send_sqs_messages(self, messages: List[SQSSendMessage]):
        for message in messages:
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(dict(message))
            )

    def delete_sqs_messages(self, messages_dict: dict[str, SQSMessage]):
        """
        Delete SQS messages pulled so far from queue

        Args:
            messages_dict (dict): dict with key being message id and value being
            a dict containing message body, sent timestamp and receipt handle
        """
        for message in messages_dict.values():
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message.receipt_handle
            )
