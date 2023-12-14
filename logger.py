import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


formatter = logging.Formatter('%(asctime)s-%(levelname)s-ssg_logging-%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

LOGGER.addHandler(stream_handler)

file_handler = logging.FileHandler('ssg.log')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)
