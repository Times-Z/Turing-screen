import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('app.log', mode='w'),
        logging.StreamHandler()
    ],
    datefmt='%H:%M:%S')

logger = logging.getLogger('monitoring')
logger.setLevel(logging.DEBUG)
