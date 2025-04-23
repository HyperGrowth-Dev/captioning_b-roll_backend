import os
import logging
from pathlib import Path

def setup_logging(logger_name: str, log_file: str = None):
    """Configure logging for the application.
    
    Args:
        logger_name (str): Name of the logger
        log_file (str, optional): Path to log file. If None, logs only to console.
    """
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        ensure_directory(os.path.dirname(log_file))
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    logger.info("Logging initialized")
    return logger

def ensure_directory(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True) 