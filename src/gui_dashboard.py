"""
GUI Dashboard for Personal Automation Engine
Lightweight Tkinter-based interface with real-time updates
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
try:
    from PIL import Image
    import pystray
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class AutomationDashboard:
    """Main GUI Dashboard"""
    
    def __init__(self, engine_controller):
        """
        Initialize dashboard
        
        Args:
            engine_controller: Reference to the automation engine
        """
        self.engine = engine_controller
        
        # Set Windows taskbar icon (must be done before creating Tk window)
        self._set_windows_taskbar_icon()
        
        self.root = tk.Tk()
        self.root.title("Personal Automation Engine")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # Set icon if available
        self.icon_path = None
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
                self.icon_path = str(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Variables
        self.status_var = tk.StringVar(value="Stopped")
        self.files_processed_var = tk.StringVar(value="0")
        self.last_activity_var = tk.StringVar(value="None")
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
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
        
        # Attention Leak Insights button
        ttk.Button(
            button_frame,
            text="🧠 Attention Insights",
            command=self._show_attention_insights,
            width=20
        ).grid(row=0, column=4, padx=5)
    
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
            # Create custom dialog with three options
            response = messagebox.askyesnocancel(
                "Engine Running",
                "Engine is running. What would you like to do?\n\n"
                "• Yes: Stop engine and quit\n"
                "• No: Minimize to system tray (engine keeps running)\n"
                "• Cancel: Keep window open"
            )
            
            if response is True:  # Yes - Stop and quit
                self.engine.stop()
                self._cleanup_tray()
                self.root.destroy()
            elif response is False:  # No - Minimize to tray
                if TRAY_AVAILABLE:
                    self._minimize_to_tray()
                else:
                    messagebox.showwarning(
                        "System Tray Not Available",
                        "System tray support not installed.\n"
                        "Install: pip install pillow pystray\n\n"
                        "Stopping engine and quitting..."
                    )
                    self.engine.stop()
                    self.root.destroy()
            # else: Cancel - do nothing
        else:
            self._cleanup_tray()
            self.root.destroy()
    
    def _show_attention_insights(self):
        """Show attention leak insights in a new window"""
        insights_window = tk.Toplevel(self.root)
        insights_window.title("Attention Leak Insights")
        insights_window.geometry("1000x700")
        
        # Set icon for popup window
        if self.icon_path:
            try:
                insights_window.iconbitmap(self.icon_path)
            except:
                pass
        
        # Main frame
        main_frame = ttk.Frame(insights_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🧠 Attention Leak Detection",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Summary Tab
        summary_frame = ttk.Frame(notebook, padding="10")
        notebook.add(summary_frame, text="Summary")
        
        # Detailed Leaks Tab
        leaks_frame = ttk.Frame(notebook, padding="10")
        notebook.add(leaks_frame, text="Detailed Leaks")
        
        # Statistics Tab
        stats_frame = ttk.Frame(notebook, padding="10")
        notebook.add(stats_frame, text="Statistics")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Analyze button
        analyze_btn = ttk.Button(
            button_frame,
            text="🔍 Analyze Now",
            command=lambda: self._run_attention_analysis(
                summary_text, leaks_text, stats_text, analyze_btn
            )
        )
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # Export report button
        ttk.Button(
            button_frame,
            text="📄 Export Report",
            command=lambda: self._export_attention_report()
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(
            button_frame,
            text="Close",
            command=insights_window.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Create text widgets for each tab
        # Summary text
        summary_text = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=30
        )
        summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Leaks text
        leaks_text = scrolledtext.ScrolledText(
            leaks_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=30
        )
        leaks_text.pack(fill=tk.BOTH, expand=True)
        
        # Stats text
        stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=30
        )
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Load initial data
        self._load_attention_data(summary_text, leaks_text, stats_text)
    
    def _load_attention_data(self, summary_text, leaks_text, stats_text):
        """Load attention leak data into text widgets"""
        try:
            # Get attention stats
            stats = self.engine.get_attention_stats()
            
            # Display in summary
            summary_text.delete('1.0', tk.END)
            summary_text.insert(tk.END, "=== ATTENTION TRACKING STATISTICS ===\n\n", "header")
            summary_text.insert(tk.END, f"Files Tracked: {stats.get('total_files_tracked', 0)}\n")
            summary_text.insert(tk.END, f"Total Accesses: {stats.get('total_accesses', 0)}\n")
            summary_text.insert(tk.END, f"Folder Switches (24h): {stats.get('folder_switches_today', 0)}\n")
            summary_text.insert(tk.END, f"Last Analysis: {stats.get('last_analysis', 'Never')}\n\n")
            summary_text.insert(tk.END, "Click 'Analyze Now' to run a full attention leak analysis.\n", "info")
            
            # Display stats
            stats_text.delete('1.0', tk.END)
            stats_text.insert(tk.END, "=== TRACKING STATISTICS ===\n\n")
            for key, value in stats.items():
                stats_text.insert(tk.END, f"{key}: {value}\n")
            
        except Exception as e:
            summary_text.delete('1.0', tk.END)
            summary_text.insert(tk.END, f"Error loading attention data: {e}\n")
    
    def _run_attention_analysis(self, summary_text, leaks_text, stats_text, analyze_btn):
        """Run attention leak analysis"""
        try:
            analyze_btn.config(state=tk.DISABLED, text="Analyzing...")
            self.root.update()
            
            # Get attention leak summary
            summary = self.engine.get_attention_leaks()
            
            if not summary:
                summary_text.delete('1.0', tk.END)
                summary_text.insert(tk.END, "No attention leak data available yet.\n")
                summary_text.insert(tk.END, "The system needs to track files for a while before analysis.\n")
                return
            
            # Display summary
            summary_text.delete('1.0', tk.END)
            summary_text.insert(tk.END, "=== ATTENTION LEAK ANALYSIS SUMMARY ===\n\n", "header")
            summary_text.insert(tk.END, f"Generated: {summary.get('timestamp', 'Unknown')}\n\n")
            summary_text.insert(tk.END, f"Total Leaks Detected: {summary.get('total_leaks_detected', 0)}\n")
            summary_text.insert(tk.END, f"Estimated Time Loss: {summary.get('total_estimated_time_loss_minutes', 0):.1f} minutes\n")
            summary_text.insert(tk.END, f"Files Tracked: {summary.get('total_files_tracked', 0)}\n\n")
            
            # Severity breakdown
            severity = summary.get('leaks_by_severity', {})
            summary_text.insert(tk.END, "Severity Breakdown:\n")
            summary_text.insert(tk.END, f"  🔴 High:   {severity.get('high', 0)}\n")
            summary_text.insert(tk.END, f"  🟡 Medium: {severity.get('medium', 0)}\n")
            summary_text.insert(tk.END, f"  🟢 Low:    {severity.get('low', 0)}\n\n")
            
            # Overall status
            total_leaks = summary.get('total_leaks_detected', 0)
            if total_leaks == 0:
                summary_text.insert(tk.END, "✅ Status: Excellent - No attention leaks detected!\n\n")
            elif severity.get('high', 0) > 0:
                summary_text.insert(tk.END, "⚠️ Status: Action Required - High priority leaks detected\n\n")
            elif severity.get('medium', 0) > 0:
                summary_text.insert(tk.END, "🔔 Status: Room for Improvement\n\n")
            else:
                summary_text.insert(tk.END, "👍 Status: Good - Minor issues detected\n\n")
            
            # Display detailed leaks
            leaks_text.delete('1.0', tk.END)
            leaks_text.insert(tk.END, "=== DETAILED ATTENTION LEAKS ===\n\n")
            
            leaks = summary.get('leaks', [])
            if leaks:
                for i, leak in enumerate(leaks, 1):
                    severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(leak.get('severity'), '⚪')
                    
                    leaks_text.insert(tk.END, f"{i}. {leak.get('title', 'Unknown')}\n", "header")
                    leaks_text.insert(tk.END, f"   Severity: {severity_icon} {leak.get('severity', 'unknown').upper()}\n")
                    leaks_text.insert(tk.END, f"   Time Loss: {leak.get('estimated_time_loss_minutes', 0):.1f} minutes\n\n")
                    leaks_text.insert(tk.END, f"   Description:\n   {leak.get('description', 'No description')}\n\n")
                    
                    affected = leak.get('affected_items', [])
                    if affected:
                        leaks_text.insert(tk.END, f"   Affected Items ({len(affected)} shown):\n")
                        for item in affected[:10]:  # Show first 10
                            leaks_text.insert(tk.END, f"   - {item}\n")
                        leaks_text.insert(tk.END, "\n")
                    
                    leaks_text.insert(tk.END, f"   💡 Suggestion:\n   {leak.get('suggestion', 'No suggestion')}\n\n")
                    leaks_text.insert(tk.END, "-" * 80 + "\n\n")
            else:
                leaks_text.insert(tk.END, "No attention leaks detected! Your workspace is well-organized. ✓\n")
            
            # Update stats
            self._load_attention_data(summary_text, leaks_text, stats_text)
            
            messagebox.showinfo("Analysis Complete", 
                              f"Found {total_leaks} attention leaks.\n"
                              f"Estimated time loss: {summary.get('total_estimated_time_loss_minutes', 0):.1f} minutes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run analysis:\n{e}")
        finally:
            analyze_btn.config(state=tk.NORMAL, text="🔍 Analyze Now")
    
    def _export_attention_report(self):
        """Export attention leak report"""
        try:
            from attention_report_generator import AttentionReportGenerator
            
            # Get summary
            summary = self.engine.get_attention_leaks()
            
            if not summary or summary.get('total_leaks_detected', 0) == 0:
                messagebox.showinfo("Info", "No attention leaks to report. Run analysis first.")
                return
            
            # Generate report
            generator = AttentionReportGenerator()
            report_path = generator.generate_markdown_report(summary)
            
            messagebox.showinfo("Success", f"Report generated:\n{report_path}")
            
            # Open report
            if messagebox.askyesno("Open Report?", "Would you like to open the report now?"):
                os.startfile(report_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report:\n{e}")
    
    def _set_windows_taskbar_icon(self):
        """Set custom icon for Windows taskbar"""
        try:
            # Only works on Windows
            if sys.platform == 'win32':
                import ctypes
                
                # Get the absolute path to the icon
                icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
                
                if icon_path.exists():
                    # Set the AppUserModelID to make Windows treat this as a unique app
                    myappid = 'FileOps.AutomationEngine.GUI.1.0'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            # Silently fail if icon setting doesn't work
            pass
    
    def _minimize_to_tray(self):
        """Minimize the application to system tray"""
        if not TRAY_AVAILABLE:
            return
        
        try:
            # Hide the main window
            self.root.withdraw()
            self.is_minimized_to_tray = True
            
            # Load icon for system tray
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                icon_image = Image.open(str(icon_path))
            else:
                # Create a simple default icon if file not found
                icon_image = Image.new('RGB', (64, 64), color='blue')
            
            # Create system tray icon
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", self._restore_from_tray),
                pystray.MenuItem("Stop Engine & Quit", self._quit_from_tray)
            )
            
            self.tray_icon = pystray.Icon(
                "FileOps",
                icon_image,
                "FileOps Automation Engine\n(Running in background)",
                menu
            )
            
            # Run tray icon in separate thread
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
        except Exception as e:
            print(f"Error minimizing to tray: {e}")
            self.root.deiconify()
    
    def _restore_from_tray(self, icon=None, item=None):
        """Restore window from system tray"""
        self.is_minimized_to_tray = False
        
        # Stop the tray icon
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        
        # Show the window
        self.root.after(0, self.root.deiconify)
    
    def _quit_from_tray(self, icon=None, item=None):
        """Quit application from system tray"""
        # Stop the engine
        if self.engine.is_running():
            self.engine.stop()
        
        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        
        # Destroy the window
        self.root.after(0, self.root.destroy)
    
    def _cleanup_tray(self):
        """Clean up system tray icon if present"""
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self.tray_icon = None


