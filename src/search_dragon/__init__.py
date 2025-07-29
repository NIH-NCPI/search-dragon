import logging
from rich.logging import RichHandler

LOGGING_FORMAT = "%(message)s"

_logger = None
def logger(logid="", loglevel=logging.INFO, logformat=LOGGING_FORMAT, console_handler=None, filename=None):
    """Establish a singleton logger that can be reused by multiple components. 
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(logid)

        if filename is not None:
            logging.basicConfig(filename=filename, encoding='utf-8', level=loglevel)

        _logger.setLevel(loglevel)

        # Create a console handler for logging to the console
        if not _logger.handlers:
            if filename is None and console_handler is None:
                console_handler = logging.StreamHandler()
                
            if console_handler:
                console_handler.setLevel(loglevel)
                console_handler.setFormatter(logging.Formatter(logformat))

                # Add handlers to the logger
                _logger.addHandler(console_handler)
    return _logger
        