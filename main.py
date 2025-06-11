import threading

from src.logging import logger
from src.service import aws_image_process, initialize_aws_clients, message_polling


if __name__ == "__main__":
    logger.info("_______Starting service_______")
    clients = initialize_aws_clients()
    if clients is not None:
        sqs, result_sqs = clients
        while True:
            messages = message_polling(sqs, 4, 20)
            if messages is not None:
                t = threading.Thread(target=aws_image_process, args=(sqs, result_sqs, messages), daemon=True)
                t.start()
    logger.info("_______Service shutdown_______")
