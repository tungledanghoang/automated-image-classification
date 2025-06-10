import os
from dotenv import load_dotenv
from typing import List

from src.models import ImageClassifierModel
from src.aws_tools import SQSManager, S3Manager

load_dotenv()


def aws_image_process():
    """
    Function to handle overall image classification pipeline

    Returns:
        classification results from the image model
    """
    s3 = S3Manager(os.environ['S3_BUCKET_NAME'])
    sqs = SQSManager(os.environ['SQS_QUEUE_NAME'])
    result_sqs = SQSManager(os.environ['SQS_RESULT_QUEUE_NAME'])

    messages = sqs.get_sqs_messages(10)
    messages_body = [message.body for message in messages.values()]

    file_paths = s3.get_files(messages_body)

    img_classifier = ImageClassifierModel("resnet50")
    classifications = img_classifier.classify_image_batch(file_paths)

    s3.clear_files(file_paths)
    sqs.delete_sqs_messages(messages)

    result_mess = []
    for i, mess in enumerate(messages_body):
        result_mess.append(f"Original message: {mess}. Classification result: {classifications[i]}")
    result_sqs.send_sqs_messages(result_mess)
