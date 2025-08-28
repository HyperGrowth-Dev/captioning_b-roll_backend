import os
import logging
import tempfile
import shutil
from typing import Optional
from contextlib import contextmanager

def setup_logging(logger_name: str, log_file: str = None) -> logging.Logger:
    """Configure logging with console handler only (uses main app.log)"""
    # Create a new logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # Only add console handler - main app.log will capture all output
    console_handler = logging.StreamHandler()
    
    # Create formatter and add it to handler
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_format)
    
    # Add handler to the logger
    logger.addHandler(console_handler)
    
    logger.info("Logging initialized")
    return logger

def ensure_directory(directory: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    os.makedirs(directory, exist_ok=True)
