"""
File Organizer Module
Moves and organizes files based on rules
"""

import os
import shutil
from pathlib import Path
from typing import Optional


class FileOrganizer:
    """Handles file organization operations"""
    
    def __init__(self, logger=None):
        """
        Initialize file organizer
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
    
    def move_file(self, source: str, destination_dir: str) -> bool:
        """
        Move file to destination directory
        
        Args:
            source: Source file path
            destination_dir: Destination directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate source file
            if not os.path.exists(source):
                if self.logger:
                    self.logger.error(f"Source file does not exist: {source}")
                return False
            
            if not os.path.isfile(source):
                if self.logger:
                    self.logger.error(f"Source is not a file: {source}")
                return False
            
            # Create destination directory if needed
            Path(destination_dir).mkdir(parents=True, exist_ok=True)
            
            # Get filename and construct destination path
            filename = Path(source).name
            destination = os.path.join(destination_dir, filename)
            
            # Handle duplicate filenames
            destination = self._handle_duplicate(destination)
            
            # Move the file
            shutil.move(source, destination)
            
            if self.logger:
                self.logger.log_file_operation("MOVE", source, destination, "SUCCESS")
            
            return True
            
        except PermissionError as e:
            if self.logger:
                self.logger.error(f"Permission denied moving file: {source} - {e}")
            return False
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error moving file {source}: {e}", exc_info=True)
            return False
    
    def copy_file(self, source: str, destination_dir: str) -> bool:
        """
        Copy file to destination directory
        
        Args:
            source: Source file path
            destination_dir: Destination directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate source file
            if not os.path.exists(source):
                if self.logger:
                    self.logger.error(f"Source file does not exist: {source}")
                return False
            
            if not os.path.isfile(source):
                if self.logger:
                    self.logger.error(f"Source is not a file: {source}")
                return False
            
            # Create destination directory if needed
            Path(destination_dir).mkdir(parents=True, exist_ok=True)
            
            # Get filename and construct destination path
            filename = Path(source).name
            destination = os.path.join(destination_dir, filename)
            
            # Handle duplicate filenames
            destination = self._handle_duplicate(destination)
            
            # Copy the file
            shutil.copy2(source, destination)
            
            if self.logger:
                self.logger.log_file_operation("COPY", source, destination, "SUCCESS")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error copying file {source}: {e}", exc_info=True)
            return False
    
    def _handle_duplicate(self, file_path: str) -> str:
        """
        Handle duplicate filenames by adding a counter
        
        Args:
            file_path: Original file path
            
        Returns:
            Modified file path if duplicate exists
        """
        if not os.path.exists(file_path):
            return file_path
        
        path = Path(file_path)
        directory = path.parent
        stem = path.stem
        extension = path.suffix
        
        counter = 1
        while True:
            new_filename = f"{stem} ({counter}){extension}"
            new_path = directory / new_filename
            
            if not new_path.exists():
                if self.logger:
                    self.logger.debug(f"Duplicate detected, renaming to: {new_filename}")
                return str(new_path)
            
            counter += 1
            
            # Safety check to prevent infinite loop
            if counter > 1000:
                if self.logger:
                    self.logger.error(f"Too many duplicates for: {file_path}")
                return file_path
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                if self.logger:
                    self.logger.warning(f"File does not exist: {file_path}")
                return False
            
            os.remove(file_path)
            
            if self.logger:
                self.logger.log_file_operation("DELETE", file_path, None, "SUCCESS")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            path = Path(file_path)
            
            return {
                'name': path.name,
                'extension': path.suffix,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'directory': str(path.parent)
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting file info for {file_path}: {e}")
            return None
