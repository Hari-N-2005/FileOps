"""
GUI-Enhanced Automation Engine Controller
Wraps the main engine with GUI-friendly interfaces
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import get_config
from logger import init_logger_from_config
from file_watcher import FileWatcher
from rules_engine import RulesEngine
from file_organizer import FileOrganizer
from backup_manager import BackupManager


class GUIEngineController:
    """Engine controller with GUI-friendly interfaces"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize engine controller"""
        self.config_path = config_path
        self.running = False
        self.config = None
        self.logger = None
        self.file_watcher = None
        self.rules_engine = None
        self.file_organizer = None
        self.backup_manager = None
        
        # Statistics tracking
        self.files_processed = 0
        self.last_activity = None
        self.gui_callbacks = []
        
        self.initialize()
    
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Load configuration
            self.config = get_config(self.config_path)
            
            # Initialize logger
            logging_config = self.config.get_logging_config()
            self.logger = init_logger_from_config(logging_config)
            self.logger.log_engine_status("STARTED", "GUI Engine initializing")
            
            # Initialize file organizer
            self.file_organizer = FileOrganizer(logger=self.logger)
            
            # Initialize rules engine
            rules = self.config.get_organization_rules()
            self.rules_engine = RulesEngine(rules, logger=self.logger)
            
            # Initialize file watcher
            watched_dirs = self.config.get_watched_directories()
            if watched_dirs:
                stable_time = self.config.get_file_stable_time()
                self.file_watcher = FileWatcher(
                    watched_dirs,
                    self._process_file,
                    stable_time,
                    logger=self.logger
                )
            
            # Initialize backup manager
            backup_config = self.config.get_backup_config()
            self.backup_manager = BackupManager(backup_config, logger=self.logger)
            
            if self.config.is_backup_enabled():
                self.backup_manager.schedule_backup()
            
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            if self.logger:
                self.logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def add_gui_callback(self, callback):
        """Add callback for GUI updates"""
        self.gui_callbacks.append(callback)
    
    def _notify_gui(self, message: str, level: str = "info"):
        """Notify GUI of events"""
        for callback in self.gui_callbacks:
            try:
                callback(message, level)
            except:
                pass
    
    def _process_file(self, file_path: str) -> None:
        """Process a detected file"""
        try:
            if not self.rules_engine.should_process_file(file_path):
                return
            
            destination = self.rules_engine.get_destination(file_path)
            
            if destination:
                filename = Path(file_path).name
                success = self.file_organizer.move_file(file_path, destination)
                
                if success:
                    self.files_processed += 1
                    self.last_activity = datetime.now().strftime("%H:%M:%S")
                    self._notify_gui(f"Moved: {filename} → {destination}", "success")
                else:
                    self._notify_gui(f"Failed to move: {filename}", "error")
                    
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            self._notify_gui(f"Error: {str(e)}", "error")
    
    def start(self) -> None:
        """Start the automation engine"""
        if self.running:
            return
        
        self.running = True
        
        if self.file_watcher:
            self.file_watcher.start()
        
        self.logger.log_engine_status("RUNNING", "Engine started via GUI")
        self._notify_gui("Engine started successfully", "success")
        
        # Main processing loop (non-blocking for GUI)
        import time
        while self.running:
            try:
                if self.file_watcher:
                    self.file_watcher.check_pending_files()
                
                if self.backup_manager:
                    self.backup_manager.check_schedule()
                
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Engine loop error: {e}", exc_info=True)
                break
    
    def stop(self) -> None:
        """Stop the automation engine"""
        if not self.running:
            return
        
        self.running = False
        
        if self.file_watcher:
            self.file_watcher.stop()
        
        if self.logger:
            self.logger.log_engine_status("STOPPED", "Engine stopped via GUI")
        
        self._notify_gui("Engine stopped", "info")
    
    def is_running(self) -> bool:
        """Check if engine is running"""
        return self.running
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        stats = {
            'files_processed': self.files_processed,
            'last_activity': self.last_activity or 'None',
            'watched_dirs': len(self.config.get_watched_directories()) if self.config else 0,
            'active_rules': 0,
            'backup_enabled': False,
            'backup_schedule': None
        }
        
        if self.rules_engine:
            rule_stats = self.rules_engine.get_rule_stats()
            stats['active_rules'] = rule_stats['enabled_rules']
        
        if self.backup_manager:
            backup_status = self.backup_manager.get_backup_status()
            stats['backup_enabled'] = backup_status['enabled']
            stats['backup_schedule'] = backup_status.get('schedule_time')
        
        return stats
    
    def reload_config(self) -> None:
        """Reload configuration"""
        self.config.reload()
        
        # Reinitialize components
        rules = self.config.get_organization_rules()
        self.rules_engine = RulesEngine(rules, logger=self.logger)
        
        self.logger.info("Configuration reloaded")
