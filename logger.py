import logging

def setup_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)

    # Set the default logging level
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler('project.log')

    # Set level for file handler
    file_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger
