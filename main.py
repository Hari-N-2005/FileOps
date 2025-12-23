"""
Personal Automation Engine - Main Entry Point
Orchestrates all automation components
"""

import os
import sys
import time
import signal
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import get_config
from logger import init_logger_from_config
from file_watcher import FileWatcher
from rules_engine import RulesEngine
from file_organizer import FileOrganizer
from backup_manager import BackupManager


class AutomationEngine:
    """Main automation engine controller"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize automation engine
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.running = False
        self.config = None
        self.logger = None
        self.file_watcher = None
        self.rules_engine = None
        self.file_organizer = None
        self.backup_manager = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nReceived shutdown signal. Stopping engine...")
        self.stop()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """
        Initialize all components
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("Initializing Personal Automation Engine...")
            
            # Load configuration
            self.config = get_config(self.config_path)
            print(f"✓ Configuration loaded from {self.config_path}")
            
            # Initialize logger
            logging_config = self.config.get_logging_config()
            self.logger = init_logger_from_config(logging_config)
            self.logger.log_engine_status("STARTED", "Personal Automation Engine initializing")
            
            # Initialize file organizer
            self.file_organizer = FileOrganizer(logger=self.logger)
            self.logger.info("File organizer initialized")
            
            # Initialize rules engine
            rules = self.config.get_organization_rules()
            self.rules_engine = RulesEngine(rules, logger=self.logger)
            stats = self.rules_engine.get_rule_stats()
            self.logger.info(
                f"Rules engine initialized with {stats['enabled_rules']} active rules"
            )
            
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
                self.logger.info(f"Watching {len(watched_dirs)} directories")
            else:
                self.logger.warning("No directories configured for watching")
            
            # Initialize backup manager
            backup_config = self.config.get_backup_config()
            self.backup_manager = BackupManager(backup_config, logger=self.logger)
            
            if self.config.is_backup_enabled():
                self.backup_manager.schedule_backup()
            
            print("✓ All components initialized successfully")
            return True
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            if self.logger:
                self.logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def _process_file(self, file_path: str) -> None:
        """
        Process a detected file
        
        Args:
            file_path: Path to file to process
        """
        try:
            # Check if file should be processed
            if not self.rules_engine.should_process_file(file_path):
                self.logger.debug(f"File not matched by any rule: {file_path}")
                return
            
            # Get destination for file
            destination = self.rules_engine.get_destination(file_path)
            
            if destination:
                # Move file to destination
                success = self.file_organizer.move_file(file_path, destination)
                
                if not success:
                    self.logger.error(f"Failed to move file: {file_path}")
            else:
                self.logger.debug(f"No destination found for file: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
    
    def start(self) -> None:
        """Start the automation engine"""
        if self.running:
            print("Engine is already running")
            return
        
        print("\n" + "="*50)
        print("Personal Automation Engine Started")
        print("="*50)
        
        self.running = True
        
        # Start file watcher
        if self.file_watcher:
            self.file_watcher.start()
        
        self.logger.log_engine_status("RUNNING", "Engine started successfully")
        
        # Display status
        self._display_status()
        
        print("\nEngine is now running. Press Ctrl+C to stop.")
        
        # Main loop
        try:
            check_interval = self.config.get_general_config().get('check_interval', 60)
            
            while self.running:
                # Check for pending files
                if self.file_watcher:
                    self.file_watcher.check_pending_files()
                
                # Check backup schedule
                if self.backup_manager:
                    self.backup_manager.check_schedule()
                
                # Sleep for a short time
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nShutdown requested...")
            self.stop()
    
    def stop(self) -> None:
        """Stop the automation engine"""
        if not self.running:
            return
        
        print("\nStopping Personal Automation Engine...")
        self.running = False
        
        # Stop file watcher
        if self.file_watcher:
            self.file_watcher.stop()
        
        if self.logger:
            self.logger.log_engine_status("STOPPED", "Engine stopped gracefully")
        
        print("✓ Engine stopped successfully")
    
    def _display_status(self) -> None:
        """Display current engine status"""
        print("\nStatus:")
        print(f"  • Watched directories: {len(self.config.get_watched_directories())}")
        print(f"  • Active rules: {self.rules_engine.get_rule_stats()['enabled_rules']}")
        
        if self.config.is_backup_enabled():
            backup_status = self.backup_manager.get_backup_status()
            print(f"  • Backup: Enabled (scheduled at {backup_status['schedule_time']})")
        else:
            print(f"  • Backup: Disabled")
        
        print(f"  • Logs: {self.config.get_logging_config()['log_file']}")


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║   Personal Automation Engine v1.0.0       ║
    ║   Automate Your Everyday Tasks            ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Determine config path
    config_path = "config/config.yaml"
    
    if not os.path.exists(config_path):
        print(f"\n✗ Configuration file not found: {config_path}")
        print("\nPlease create a configuration file:")
        print("  1. Copy config/config.example.yaml to config/config.yaml")
        print("  2. Edit config/config.yaml with your settings")
        print("  3. Run the engine again")
        sys.exit(1)
    
    # Create and initialize engine
    engine = AutomationEngine(config_path)
    
    if not engine.initialize():
        print("\n✗ Failed to initialize engine. Check logs for details.")
        sys.exit(1)
    
    # Start engine
    try:
        engine.start()
    except Exception as e:
        print(f"\n✗ Engine error: {e}")
        if engine.logger:
            engine.logger.critical(f"Engine error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
