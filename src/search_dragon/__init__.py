import logging
import requests
from datetime import datetime
import time

LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Create a console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

    # Add handlers to the logger
    logger.addHandler(console_handler)


def fetch_data(url):
    """ """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
