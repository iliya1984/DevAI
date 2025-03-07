import logging

def configure_logger():
    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger

logger = configure_logger()