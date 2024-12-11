import logging
import requests
from datetime import datetime
import time

LOGS_PATH = f"data/logs/search.log"
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler for logging to a file
file_handler = logging.FileHandler(LOGS_PATH)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

# Create a console handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def fetch_data(url):
    """ """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
