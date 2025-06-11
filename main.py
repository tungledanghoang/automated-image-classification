import threading
import signal

from src.logging import logger
from src.service import aws_image_process, initialize_aws_clients, message_polling


class GracefulExit:
    def __init__(self):
        self.terminate = False
        signal.signal(signal.SIGTERM, self.signal_terminate)

    def signal_terminate(self, signum, frame):
        self.terminate = True


if __name__ == "__main__":
    logger.info("_______Starting service_______")
    g = GracefulExit()
    clients = initialize_aws_clients()
    if clients is not None:
        sqs, result_sqs = clients
        while not g.terminate:
            messages = message_polling(sqs, 4, 20)
            if messages is not None:
                t = threading.Thread(target=aws_image_process, args=(sqs, result_sqs, messages), daemon=True)
                t.start()
    logger.info("_______Service shutdown_______")
