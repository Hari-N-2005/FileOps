"""
File Watcher Module
Monitors directories for file changes and triggers processing
"""

import os
import time
from pathlib import Path
from typing import Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events"""
    
    def __init__(self, callback: Callable, stable_time: int = 2, logger=None):
        """
        Initialize file change handler
        
        Args:
            callback: Function to call when a file is ready for processing
            stable_time: Time in seconds to wait before processing (ensures file is complete)
            logger: Logger instance
        """
        super().__init__()
        self.callback = callback
        self.stable_time = stable_time
        self.logger = logger
        self.pending_files = {}  # Track files waiting to be processed
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if self.logger:
            self.logger.debug(f"File detected: {file_path}")
        
        # Add to pending files with timestamp
        self.pending_files[file_path] = time.time()
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Update timestamp for pending file
        if file_path in self.pending_files:
            self.pending_files[file_path] = time.time()
    
    def check_stable_files(self) -> None:
        """Check for files that have been stable for the required time"""
        current_time = time.time()
        files_to_process = []
        
        for file_path, timestamp in list(self.pending_files.items()):
            # Check if file has been stable for required time
            if current_time - timestamp >= self.stable_time:
                # Verify file still exists and is accessible
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        # Try to open the file to ensure it's not locked
                        with open(file_path, 'rb') as f:
                            pass
                        files_to_process.append(file_path)
                    except (IOError, PermissionError) as e:
                        if self.logger:
                            self.logger.debug(f"File not ready yet: {file_path} - {e}")
                        # Reset timestamp to try again later
                        self.pending_files[file_path] = current_time
                else:
                    # File no longer exists, remove from pending
                    del self.pending_files[file_path]
        
        # Process stable files
        for file_path in files_to_process:
            if self.logger:
                self.logger.debug(f"Processing stable file: {file_path}")
            
            try:
                self.callback(file_path)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            finally:
                # Remove from pending files
                if file_path in self.pending_files:
                    del self.pending_files[file_path]


class FileWatcher:
    """Watches directories for file changes"""
    
    def __init__(self, directories: List[str], callback: Callable, 
                 stable_time: int = 2, logger=None):
        """
        Initialize file watcher
        
        Args:
            directories: List of directories to watch
            callback: Function to call when a file is ready for processing
            stable_time: Time to wait before processing new files
            logger: Logger instance
        """
        self.directories = directories
        self.callback = callback
        self.stable_time = stable_time
        self.logger = logger
        self.observer = Observer()
        self.event_handler = FileChangeHandler(callback, stable_time, logger)
        self.running = False
    
    def start(self) -> None:
        """Start watching directories"""
        if self.running:
            if self.logger:
                self.logger.warning("File watcher is already running")
            return
        
        for directory in self.directories:
            if not os.path.exists(directory):
                if self.logger:
                    self.logger.warning(f"Directory does not exist: {directory}")
                continue
            
            if not os.path.isdir(directory):
                if self.logger:
                    self.logger.warning(f"Path is not a directory: {directory}")
                continue
            
            self.observer.schedule(self.event_handler, directory, recursive=False)
            if self.logger:
                self.logger.info(f"Watching directory: {directory}")
        
        self.observer.start()
        self.running = True
        
        if self.logger:
            self.logger.info("File watcher started")
    
    def stop(self) -> None:
        """Stop watching directories"""
        if not self.running:
            return
        
        self.observer.stop()
        self.observer.join(timeout=5)
        self.running = False
        
        if self.logger:
            self.logger.info("File watcher stopped")
    
    def check_pending_files(self) -> None:
        """Check for files that are ready to be processed"""
        self.event_handler.check_stable_files()
    
    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self.running
