"""
Logging System
Provides centralized logging with file rotation and console output
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional


class AutomationLogger:
    """Centralized logging system for automation engine"""
    
    def __init__(self, log_file: str = "logs/automation.log", 
                 level: str = "INFO",
                 max_size_mb: int = 10,
                 backup_count: int = 5):
        """
        Initialize logging system
        
        Args:
            log_file: Path to log file
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            max_size_mb: Maximum log file size in MB before rotation
            backup_count: Number of backup log files to keep
        """
        self.log_file = log_file
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        
        # Create logs directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger("AutomationEngine")
        self.logger.setLevel(self.level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_size_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info)
    
    def log_file_operation(self, operation: str, source: str, destination: Optional[str] = None, 
                          status: str = "SUCCESS") -> None:
        """
        Log file operation with structured format
        
        Args:
            operation: Type of operation (MOVE, COPY, DELETE, etc.)
            source: Source file path
            destination: Destination path (optional)
            status: Operation status (SUCCESS, FAILED, etc.)
        """
        if destination:
            message = f"[{operation}] {status} | {source} -> {destination}"
        else:
            message = f"[{operation}] {status} | {source}"
        
        if status == "SUCCESS":
            self.info(message)
        else:
            self.error(message)
    
    def log_backup_operation(self, backup_type: str, sources: list, destination: str,
                            files_count: int, status: str = "SUCCESS") -> None:
        """
        Log backup operation
        
        Args:
            backup_type: Type of backup (FULL, INCREMENTAL)
            sources: List of source directories
            destination: Backup destination
            files_count: Number of files backed up
            status: Operation status
        """
        message = (f"[BACKUP-{backup_type}] {status} | "
                  f"Sources: {', '.join(sources)} | "
                  f"Destination: {destination} | "
                  f"Files: {files_count}")
        
        if status == "SUCCESS":
            self.info(message)
        else:
            self.error(message)
    
    def log_engine_status(self, status: str, message: str = "") -> None:
        """
        Log engine status changes
        
        Args:
            status: Status type (STARTED, STOPPED, ERROR)
            message: Additional message
        """
        full_message = f"[ENGINE-{status}]"
        if message:
            full_message += f" {message}"
        
        if status == "ERROR":
            self.error(full_message)
        else:
            self.info(full_message)


# Singleton instance
_logger_instance: Optional[AutomationLogger] = None


def get_logger(log_file: str = "logs/automation.log",
               level: str = "INFO",
               max_size_mb: int = 10,
               backup_count: int = 5) -> AutomationLogger:
    """
    Get singleton logger instance
    
    Args:
        log_file: Path to log file
        level: Logging level
        max_size_mb: Maximum log file size in MB
        backup_count: Number of backup log files
        
    Returns:
        AutomationLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AutomationLogger(log_file, level, max_size_mb, backup_count)
    return _logger_instance


def init_logger_from_config(config: dict) -> AutomationLogger:
    """
    Initialize logger from configuration dictionary
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        AutomationLogger instance
    """
    return get_logger(
        log_file=config.get('log_file', 'logs/automation.log'),
        level=config.get('level', 'INFO'),
        max_size_mb=config.get('max_size_mb', 10),
        backup_count=config.get('backup_count', 5)
    )
