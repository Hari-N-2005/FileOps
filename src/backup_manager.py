"""
Backup System
Handles scheduled backups of important directories
"""

import os
import shutil
import schedule
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any


class BackupManager:
    """Manages backup operations"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """
        Initialize backup manager
        
        Args:
            config: Backup configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.is_scheduled = False
        self.last_backup_time = None
    
    def perform_backup(self) -> bool:
        """
        Perform backup according to configuration
        
        Returns:
            True if successful, False otherwise
        """
        if not self.config.get('enabled', False):
            if self.logger:
                self.logger.info("Backup is disabled in configuration")
            return False
        
        backup_type = self.config.get('type', 'incremental')
        source_directories = self.config.get('source_directories', [])
        destination = self.config.get('destination')
        
        if not source_directories:
            if self.logger:
                self.logger.error("No source directories configured for backup")
            return False
        
        if not destination:
            if self.logger:
                self.logger.error("No destination configured for backup")
            return False
        
        if self.logger:
            self.logger.info(f"Starting {backup_type} backup...")
        
        try:
            # Create timestamped backup folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = Path(destination) / f"backup_{timestamp}"
            backup_folder.mkdir(parents=True, exist_ok=True)
            
            total_files = 0
            
            # Backup each source directory
            for source_dir in source_directories:
                if not os.path.exists(source_dir):
                    if self.logger:
                        self.logger.warning(f"Source directory does not exist: {source_dir}")
                    continue
                
                # Get directory name for backup
                dir_name = Path(source_dir).name
                backup_dest = backup_folder / dir_name
                
                if backup_type == 'full':
                    files_copied = self._full_backup(source_dir, str(backup_dest))
                else:  # incremental
                    files_copied = self._incremental_backup(source_dir, str(backup_dest))
                
                total_files += files_copied
                
                if self.logger:
                    self.logger.info(f"Backed up {files_copied} files from {source_dir}")
            
            # Log backup completion
            if self.logger:
                self.logger.log_backup_operation(
                    backup_type.upper(),
                    source_directories,
                    str(backup_folder),
                    total_files,
                    "SUCCESS"
                )
            
            self.last_backup_time = datetime.now()
            
            # Clean old backups based on retention policy
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Backup failed: {e}", exc_info=True)
                self.logger.log_backup_operation(
                    backup_type.upper(),
                    source_directories,
                    destination,
                    0,
                    "FAILED"
                )
            return False
    
    def _full_backup(self, source: str, destination: str) -> int:
        """
        Perform full backup of directory
        
        Args:
            source: Source directory
            destination: Destination directory
            
        Returns:
            Number of files copied
        """
        files_copied = 0
        
        try:
            # Use shutil.copytree for full directory copy
            shutil.copytree(source, destination, dirs_exist_ok=True)
            
            # Count files
            for root, dirs, files in os.walk(destination):
                files_copied += len(files)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during full backup of {source}: {e}")
        
        return files_copied
    
    def _incremental_backup(self, source: str, destination: str) -> int:
        """
        Perform incremental backup (only modified files)
        
        Args:
            source: Source directory
            destination: Destination directory
            
        Returns:
            Number of files copied
        """
        files_copied = 0
        
        try:
            Path(destination).mkdir(parents=True, exist_ok=True)
            
            # Get last backup time (or 24 hours ago if no previous backup)
            if self.last_backup_time:
                cutoff_time = self.last_backup_time.timestamp()
            else:
                cutoff_time = (datetime.now() - timedelta(days=1)).timestamp()
            
            # Walk through source directory
            for root, dirs, files in os.walk(source):
                for file in files:
                    source_file = os.path.join(root, file)
                    
                    # Check if file was modified since last backup
                    try:
                        mtime = os.path.getmtime(source_file)
                        
                        if mtime > cutoff_time:
                            # Calculate relative path and destination
                            rel_path = os.path.relpath(source_file, source)
                            dest_file = os.path.join(destination, rel_path)
                            
                            # Create destination directory if needed
                            Path(dest_file).parent.mkdir(parents=True, exist_ok=True)
                            
                            # Copy file
                            shutil.copy2(source_file, dest_file)
                            files_copied += 1
                    
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"Could not backup file {source_file}: {e}")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during incremental backup of {source}: {e}")
        
        return files_copied
    
    def _cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy"""
        retention_days = self.config.get('retention_days', 0)
        
        if retention_days == 0:
            return  # Keep all backups
        
        destination = Path(self.config.get('destination'))
        
        if not destination.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            # Find all backup folders
            for backup_dir in destination.glob('backup_*'):
                if backup_dir.is_dir():
                    # Get creation time
                    created = datetime.fromtimestamp(backup_dir.stat().st_ctime)
                    
                    if created < cutoff_date:
                        if self.logger:
                            self.logger.info(f"Removing old backup: {backup_dir.name}")
                        shutil.rmtree(backup_dir)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cleaning up old backups: {e}")
    
    def schedule_backup(self) -> None:
        """Schedule backup based on configuration"""
        if not self.config.get('enabled', False):
            if self.logger:
                self.logger.info("Backup scheduling skipped (disabled in config)")
            return
        
        schedule_time = self.config.get('schedule_time', '23:00')
        
        # Schedule daily backup
        schedule.every().day.at(schedule_time).do(self.perform_backup)
        
        self.is_scheduled = True
        
        if self.logger:
            self.logger.info(f"Backup scheduled daily at {schedule_time}")
    
    def check_schedule(self) -> None:
        """Check if any scheduled backup should run"""
        if self.is_scheduled:
            schedule.run_pending()
    
    def get_backup_status(self) -> Dict[str, Any]:
        """
        Get backup status information
        
        Returns:
            Dictionary with backup status
        """
        return {
            'enabled': self.config.get('enabled', False),
            'scheduled': self.is_scheduled,
            'last_backup': self.last_backup_time.isoformat() if self.last_backup_time else None,
            'schedule_time': self.config.get('schedule_time'),
            'backup_type': self.config.get('type')
        }
