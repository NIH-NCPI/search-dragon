import subprocess
import logging
import time

def set_logging_config(log_file):

    LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

    # Create a console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
