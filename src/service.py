from datetime import datetime as dt

import os
from dotenv import load_dotenv

from src.image_model import ImageClassifierModel
from src.aws_tools import SQSManager, S3Manager
from src.schemas import SQSSendMessage, SQSMessage
from src.logging import logger

load_dotenv()


def initialize_aws_clients() -> tuple[SQSManager, SQSManager]:
    """
    Function to generate AWS managers instances

    Returns:
        s3 (S3Manager): S3 bucket for storing images
        sqs (SQSManager): SQS queue for polling messages
        result_sqs (SQSManager): SQS queue for sending message after successful run
    """
    logger.info("Initialize AWS clients")
    try:
        sqs = SQSManager(os.environ['SQS_QUEUE_NAME'])
        result_sqs = SQSManager(os.environ['SQS_RESULT_QUEUE_NAME'])
        return sqs, result_sqs
    except Exception as e:
        logger.error(f"Failed to initialize SQS classes. Error: {e}")


def message_polling(sqs: SQSManager, max_number: int, long_poll_time: int) -> dict[str, SQSMessage]:
    """
    Function for polling message from SQS and handle logging

    Args:
        sqs (SQSManager): SQS queue for polling messages
        max_number (int): max number of messages to poll
        long_poll_time (int): long polling time

    Returns:
        dict with str for key and SQSMessage for value
    """
    logger.info(f"Polling SQS queue {os.environ['SQS_QUEUE_NAME']} for image processing request")
    try:
        messages = sqs.get_sqs_messages(max_number, long_poll_time)
        logger.info(f"Got {len(messages.values())} image processing requests")
        if len(messages.values()) > 0:
            return messages
    except Exception as e:
        logger.error(f"Failed to poll sqs messages. Error: {e}")


def aws_image_process(sqs: SQSManager, result_sqs: SQSManager, messages: dict[str, SQSMessage]):
    """
    Function to handle overall image classification pipeline

    Args:
        sqs (SQSManager): SQS queue for polling messages
        result_sqs (SQSManager): SQS queue for sending message after successful run
        messages (dict with SQSMessage for value): dict containing messages polled from SQS
    """
    file_paths = []
    for mess in messages.values():
        logger.info(f"""Retrieving image {mess.body['key']} from bucket: {mess.body['bucket']}""")
        try:
            s3 = S3Manager(mess.body['bucket'])
            file_path = s3.get_file(mess.body['key'])
            file_paths.append({'file_path': file_path, 'bucket': mess.body['bucket'], 'key': mess.body['key']})
        except Exception as e:
            logger.error(f"Failed to retrieve {mess.body['key']} from bucket: {mess.body['bucket']}. Error: {e}")
            continue

    if len(file_paths) > 0:
        logger.info(f"Running model {os.environ['MODEL_NAME']} to classify {len(file_paths)} images")
        try:
            img_classifier = ImageClassifierModel(os.environ['MODEL_NAME'])
            start_time = dt.now()
            classifications = img_classifier.classify_image_batch([f['file_path'] for f in file_paths])

            logger.info(f"Model took {dt.now() - start_time} to finish")
        except Exception as e:
            logger.error(f"Failed to run classification model. Error: {e}")
            return None

        try:
            logger.info("Clearing locally saved images")
            S3Manager.clear_files([f['file_path'] for f in file_paths])
            logger.info("Done")
            logger.info("Deleting sqs messages")
            sqs.delete_sqs_messages(messages)
            logger.info("Done")
        except Exception as e:
            logger.error(f"Failed to clean up after classification {e}")

        logger.info(f"Sending result to {os.environ['SQS_RESULT_QUEUE_NAME']} SQS Queue")
        result_mess = []
        for i, file in enumerate(file_paths):
            try:
                result_mess.append(SQSSendMessage(**{"status": "completed", "bucket": file['bucket'],
                                                     "key": file['key'], "result": classifications[i]}))
                logger.info(f"Result for {file['key']} in {file['bucket']}: {classifications[i]}")
            except Exception as e:
                logger.error(f"Failed to send result from bucket: {file['bucket']}, key: {file['key']} to {os.environ['SQS_RESULT_QUEUE_NAME']}. Error: {e}")
        if len(result_mess) > 0:
            result_sqs.send_sqs_messages(result_mess)
            logger.info(f"Successfully sent the result(s) to {os.environ['SQS_RESULT_QUEUE_NAME']}")
        else:
            logger.error(f"Failed to send any result to {os.environ['SQS_RESULT_QUEUE_NAME']}")
    else:
        logger.error(f"Failed to retrieve any file from S3")
