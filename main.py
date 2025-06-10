from src.logging import logger
from src.service import aws_image_process, initialize_aws_clients


if __name__ == "__main__":
    logger.info("_______Starting service_______")
    clients = initialize_aws_clients()
    if clients is not None:
        sqs, result_sqs = clients
        while True:
            aws_image_process(sqs, result_sqs)
    logger.info("_______Service shutdown_______")
