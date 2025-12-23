"""
GUI Dashboard for Personal Automation Engine
Lightweight Tkinter-based interface with real-time updates
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class AutomationDashboard:
    """Main GUI Dashboard"""
    
    def __init__(self, engine_controller):
        """
        Initialize dashboard
        
        Args:
            engine_controller: Reference to the automation engine
        """
        self.engine = engine_controller
        self.root = tk.Tk()
        self.root.title("Personal Automation Engine")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # Set icon if available
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Variables
        self.status_var = tk.StringVar(value="Stopped")
        self.files_processed_var = tk.StringVar(value="0")
        self.last_activity_var = tk.StringVar(value="None")
        
        # Setup UI
        self._setup_ui()
        
        # Start update loop
        self._update_status()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🤖 Personal Automation Engine",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status Section
        self._create_status_section(main_frame)
        
        # Statistics Section
        self._create_stats_section(main_frame)
        
        # Activity Log Section
        self._create_activity_section(main_frame)
        
        # Control Buttons
        self._create_control_buttons(main_frame)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def _create_status_section(self, parent):
        """Create status display section"""
        status_frame = ttk.LabelFrame(parent, text="Engine Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status indicator
        status_label = ttk.Label(status_frame, text="Status:")
        status_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.status_display = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            foreground="red"
        )
        self.status_display.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Watched directories count
        ttk.Label(status_frame, text="Watched Directories:").grid(row=0, column=2, sticky=tk.W, padx=20)
        self.watched_dirs_label = ttk.Label(status_frame, text="0")
        self.watched_dirs_label.grid(row=0, column=3, sticky=tk.W)
        
        # Active rules count
        ttk.Label(status_frame, text="Active Rules:").grid(row=0, column=4, sticky=tk.W, padx=20)
        self.active_rules_label = ttk.Label(status_frame, text="0")
        self.active_rules_label.grid(row=0, column=5, sticky=tk.W)
    
    def _create_stats_section(self, parent):
        """Create statistics section"""
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Files processed
        ttk.Label(stats_frame, text="Files Processed:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, textvariable=self.files_processed_var, font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )
        
        # Last activity
        ttk.Label(stats_frame, text="Last Activity:").grid(row=0, column=2, sticky=tk.W, padx=20)
        ttk.Label(stats_frame, textvariable=self.last_activity_var).grid(
            row=0, column=3, sticky=tk.W, padx=5
        )
        
        # Backup status
        ttk.Label(stats_frame, text="Backup:").grid(row=0, column=4, sticky=tk.W, padx=20)
        self.backup_status_label = ttk.Label(stats_frame, text="Disabled")
        self.backup_status_label.grid(row=0, column=5, sticky=tk.W, padx=5)
    
    def _create_activity_section(self, parent):
        """Create activity log section"""
        activity_frame = ttk.LabelFrame(parent, text="Recent Activity", padding="10")
        activity_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        activity_frame.rowconfigure(0, weight=1)
        activity_frame.columnconfigure(0, weight=1)
        
        # Activity log text widget
        self.activity_log = scrolledtext.ScrolledText(
            activity_frame,
            wrap=tk.WORD,
            height=15,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.activity_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure tags for colored output
        self.activity_log.tag_config("success", foreground="#008000")
        self.activity_log.tag_config("error", foreground="#FF0000")
        self.activity_log.tag_config("info", foreground="#0000FF")
        self.activity_log.tag_config("timestamp", foreground="#666666")
    
    def _create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Start/Stop button
        self.start_stop_btn = ttk.Button(
            button_frame,
            text="▶ Start Engine",
            command=self._toggle_engine,
            width=20
        )
        self.start_stop_btn.grid(row=0, column=0, padx=5)
        
        # Open config button
        ttk.Button(
            button_frame,
            text="⚙ Open Config",
            command=self._open_config,
            width=20
        ).grid(row=0, column=1, padx=5)
        
        # View full log button
        ttk.Button(
            button_frame,
            text="📄 View Full Log",
            command=self._open_log,
            width=20
        ).grid(row=0, column=2, padx=5)
        
        # Reload config button
        ttk.Button(
            button_frame,
            text="🔄 Reload Config",
            command=self._reload_config,
            width=20
        ).grid(row=0, column=3, padx=5)
    
    def _toggle_engine(self):
        """Toggle engine start/stop"""
        if self.engine.is_running():
            self.engine.stop()
            self.start_stop_btn.config(text="▶ Start Engine")
            self.add_log_entry("Engine stopped", "info")
        else:
            threading.Thread(target=self.engine.start, daemon=True).start()
            self.start_stop_btn.config(text="⏹ Stop Engine")
            self.add_log_entry("Engine started", "success")
    
    def _open_config(self):
        """Open configuration file"""
        # Use absolute path to avoid path resolution issues
        config_path = os.path.abspath("config/config.yaml")
        try:
            if os.path.exists(config_path):
                os.startfile(config_path)
            else:
                messagebox.showerror("Error", f"Configuration file not found:\n{config_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open config file:\n{e}\n\nPath: {config_path}")
    
    def _open_log(self):
        """Open log file"""
        # Use absolute path to avoid path resolution issues
        log_path = os.path.abspath("logs/automation.log")
        try:
            if os.path.exists(log_path):
                os.startfile(log_path)
            else:
                messagebox.showinfo("Info", f"Log file doesn't exist yet. Start the engine to create it.\n\nExpected path:\n{log_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open log file:\n{e}\n\nPath: {log_path}")
    
    def _reload_config(self):
        """Reload configuration"""
        try:
            self.engine.reload_config()
            self.add_log_entry("Configuration reloaded successfully", "success")
            messagebox.showinfo("Success", "Configuration reloaded! Restart engine for changes to take effect.")
        except Exception as e:
            self.add_log_entry(f"Failed to reload config: {e}", "error")
            messagebox.showerror("Error", f"Failed to reload configuration:\n{e}")
    
    def _update_status(self):
        """Update status display"""
        try:
            if self.engine.is_running():
                self.status_var.set("Running ✓")
                self.status_display.config(foreground="green")
            else:
                self.status_var.set("Stopped")
                self.status_display.config(foreground="red")
            
            # Update stats
            stats = self.engine.get_stats()
            self.watched_dirs_label.config(text=str(stats.get('watched_dirs', 0)))
            self.active_rules_label.config(text=str(stats.get('active_rules', 0)))
            self.files_processed_var.set(str(stats.get('files_processed', 0)))
            
            if stats.get('last_activity'):
                self.last_activity_var.set(stats['last_activity'])
            
            # Update backup status
            if stats.get('backup_enabled'):
                self.backup_status_label.config(
                    text=f"Enabled ({stats.get('backup_schedule', 'N/A')})",
                    foreground="green"
                )
            else:
                self.backup_status_label.config(text="Disabled", foreground="gray")
        
        except Exception as e:
            print(f"Error updating status: {e}")
        
        # Schedule next update
        self.root.after(1000, self._update_status)
    
    def add_log_entry(self, message: str, level: str = "info"):
        """
        Add entry to activity log
        
        Args:
            message: Log message
            level: Log level (info, success, error)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.activity_log.config(state=tk.NORMAL)
        self.activity_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.activity_log.insert(tk.END, f"{message}\n", level)
        self.activity_log.see(tk.END)
        self.activity_log.config(state=tk.DISABLED)
        
        # Limit log size
        lines = int(self.activity_log.index('end-1c').split('.')[0])
        if lines > 500:
            self.activity_log.config(state=tk.NORMAL)
            self.activity_log.delete('1.0', '100.0')
            self.activity_log.config(state=tk.DISABLED)
    
    def run(self):
        """Run the GUI main loop"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window close"""
        if self.engine.is_running():
            if messagebox.askokcancel("Quit", "Engine is running. Stop and quit?"):
                self.engine.stop()
                self.root.destroy()
        else:
            self.root.destroy()
