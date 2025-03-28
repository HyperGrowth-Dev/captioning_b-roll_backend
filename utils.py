import os
import logging
import tempfile
import shutil
from typing import Optional
from contextlib import contextmanager

def setup_logging(logger_name: str, log_file: str) -> logging.Logger:
    """Configure logging with both file and console handlers"""
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Configure logging
    log_file_path = os.path.join('output', log_file)
    
    # Create a new logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file_path)
    console_handler = logging.StreamHandler()
    
    # Create formatters and add it to handlers
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Logging initialized")
    return logger

def ensure_directory(directory: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    os.makedirs(directory, exist_ok=True)

class TempDirManager:
    """Manages temporary directories for the application"""
    def __init__(self, base_dir: str = 'temp'):
        self.base_dir = base_dir
        self.current_dir = None
        self.temp_dirs = []  # Initialize the list to store temp directories
        ensure_directory(base_dir)
    
    def create_temp_dir(self, prefix='temp_'):
        """Create a new temporary directory and return its path"""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup(self) -> None:
        """Clean up the current temporary directory"""
        if self.current_dir and os.path.exists(self.current_dir):
            shutil.rmtree(self.current_dir)
            self.current_dir = None
    
    def cleanup_all(self) -> None:
        """Clean up all temporary directories"""
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
            ensure_directory(self.base_dir)
        self.current_dir = None 