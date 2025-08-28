import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

class TempDirManager:
    """A context manager for creating and cleaning up temporary directories."""
    
    def __init__(self, prefix: Optional[str] = None, base_dir: Optional[str] = None):
        """Initialize the TempDirManager.
        
        Args:
            prefix (str, optional): Prefix for the temporary directory name
            base_dir (str, optional): Base directory to create temp dir in. If None, uses system temp dir.
        """
        self.prefix = prefix
        self.base_dir = base_dir
        self.temp_dir = None
        
    def __enter__(self) -> str:
        """Create and return the path to a temporary directory."""
        self.temp_dir = tempfile.mkdtemp(prefix=self.prefix, dir=self.base_dir)
        return self.temp_dir
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir) 