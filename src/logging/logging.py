import logging
from logging import FileHandler

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler = FileHandler(filename="log.txt")
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
