import logging

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

