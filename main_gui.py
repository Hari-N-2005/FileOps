"""
Personal Automation Engine - GUI Entry Point
Launch the engine with graphical user interface
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui_controller import GUIEngineController
from gui_dashboard import AutomationDashboard


def main():
    """Main entry point for GUI mode"""
    print("Starting Personal Automation Engine GUI...")
    
    # Check if config exists
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        print(f"\n✗ Configuration file not found: {config_path}")
        print("\nPlease run setup first:")
        print("  python setup.py")
        sys.exit(1)
    
    try:
        # Create engine controller
        engine = GUIEngineController(config_path)
        
        # Create dashboard
        dashboard = AutomationDashboard(engine)
        
        # Connect engine to dashboard for log updates
        engine.add_gui_callback(dashboard.add_log_entry)
        
        # Add initial log entry
        dashboard.add_log_entry("Dashboard initialized. Click 'Start Engine' to begin.", "info")
        
        # Run the GUI
        dashboard.run()
        
    except Exception as e:
        print(f"\n✗ Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
