import logging
import os
from logging.handlers import RotatingFileHandler

from csstuning.config import config_loader


def setup_logger(name, log_dir=None, log_file_name="log.txt", level=logging.INFO, max_bytes=1048576, backup_count=3):
    """Setup a logger with file and stream handlers."""
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # Set the default log directory from the config if not provided
    if log_dir is None:
        log_dir = config_loader.get_config().get("general", "logs_dir")

    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Complete log file path
    log_file = os.path.join(log_dir, log_file_name)

    # Logger setup
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File Handler
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

# Example Usage
logger = setup_logger("logger", level=logging.DEBUG)