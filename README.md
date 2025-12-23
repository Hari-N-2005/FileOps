# Personal Automation Engine

A powerful, local background automation system that intelligently organizes your files, performs scheduled backups, and maintains detailed activity logs—all running silently in the background to keep your computer tidy and data safe.

## 🚀 Features

- **🗂️ Automatic File Organization**: Monitor directories (Downloads, Desktop, etc.) and automatically sort files by type into designated folders
- **💾 Scheduled Backups**: Perform full or incremental backups of important directories at scheduled times
- **📝 Activity Logging**: Comprehensive logging with timestamps for all operations
- **⚙️ Simple Configuration**: Single YAML file to define all rules and settings
- **🔄 Real-time Monitoring**: Watches directories continuously for new files
- **🛡️ Duplicate Handling**: Intelligently handles filename conflicts
- **⏰ Smart Scheduling**: Built-in scheduler for automated backup tasks
- **📊 Detailed Logs**: Rotating log files with configurable retention

## 📋 Prerequisites

- **Python 3.7+** (Python 3.9+ recommended)
- **Windows OS** (primary support)
- Administrator privileges (for some features)

## 🔧 Installation

### Option 1: Automated Setup (Recommended)

1. **Clone or download this repository**:
   ```bash
   git clone https://github.com/Hari-N-2005/idk-pro.git
   cd idk-pro
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```
   
   The setup will:
   - Check Python version
   - Install all dependencies
   - Create configuration file
   - Optionally create desktop shortcut
   - Optionally set up auto-start on Windows login

3. **Edit the configuration**:
   ```bash
   notepad config\config.yaml
   ```
   Update paths to match your system (replace `YourUsername` with your actual username)

### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create configuration**:
   ```bash
   copy config\config.example.yaml config\config.yaml
   ```

3. **Edit configuration** with your preferred text editor

## ⚙️ Configuration

The `config/config.yaml` file controls all automation behavior. Key sections:

### Watched Directories
Define which folders to monitor:
```yaml
watched_directories:
  - path: "C:/Users/YourUsername/Downloads"
    enabled: true
  - path: "C:/Users/YourUsername/Desktop"
    enabled: true
```

### Organization Rules
Define how files should be organized:
```yaml
organization_rules:
  - name: "Organize Documents"
    file_types: [".pdf", ".docx", ".doc", ".txt"]
    destination: "C:/Users/YourUsername/Documents/Organized"
    enabled: true
```

### Backup Configuration
Set up automated backups:
```yaml
backup:
  enabled: true
  source_directories:
    - "C:/Users/YourUsername/Documents"
  destination: "D:/Backups"
  schedule_time: "23:00"  # Daily at 11 PM
  type: "incremental"     # or "full"
  retention_days: 30      # Keep backups for 30 days
```

### Logging Settings
Configure logging behavior:
```yaml
logging:
  log_file: "logs/automation.log"
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  max_size_mb: 10
  backup_count: 5
```

## 🎯 Usage

### Starting the Engine

**Option 1: Double-click the batch file**
```
run.bat
```

**Option 2: Run directly with Python**
```bash
python main.py
```

**Option 3: Use the desktop shortcut** (if created during setup)

### Stopping the Engine

Press `Ctrl+C` in the terminal window, or close the window for graceful shutdown.

### Running as Background Service

For Windows startup, use the setup script's auto-start option, or manually place a shortcut to `run.bat` in your Startup folder:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   Configuration File                     │
│              (config/config.yaml)                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Automation Engine Starts                    │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌─────────────┐      ┌─────────────────┐
│File Watcher │      │Backup Scheduler │
│ (Real-time) │      │   (Scheduled)   │
└──────┬──────┘      └────────┬────────┘
       │                      │
       ▼                      ▼
┌──────────────┐      ┌─────────────┐
│ Rules Engine │      │   Backup    │
│  (Evaluate)  │      │  Manager    │
└──────┬───────┘      └──────┬──────┘
       │                     │
       ▼                     │
┌─────────────┐              │
│   File      │              │
│ Organizer   │◄─────────────┘
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Activity Log   │
│ (All Actions)   │
└─────────────────┘
```

### Workflow:

1. **Configuration Loading**: Engine reads `config.yaml` on startup
2. **File Monitoring**: Watchdog monitors specified directories in real-time
3. **File Detection**: New files trigger the rules engine
4. **Rule Evaluation**: File extension/name matches against defined rules
5. **File Organization**: Matched files moved to appropriate destinations
6. **Backup Execution**: Scheduled backups run at configured time
7. **Logging**: All operations recorded with timestamps

## 📁 Project Structure

```
idk-pro/
├── main.py                 # Main entry point
├── setup.py                # Setup and installation script
├── run.bat                 # Quick start batch file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # License information
├── .gitignore            # Git ignore rules
├── config/
│   ├── config.example.yaml  # Example configuration
│   └── config.yaml          # Your configuration (create this)
├── src/
│   ├── __init__.py
│   ├── config_manager.py    # Configuration loader
│   ├── logger.py            # Logging system
│   ├── file_watcher.py      # Directory monitoring
│   ├── rules_engine.py      # Rule evaluation
│   ├── file_organizer.py    # File operations
│   └── backup_manager.py    # Backup functionality
└── logs/
    └── automation.log       # Activity logs (created on first run)
```

## 🔍 Examples

### Example 1: Organize Downloads

**Scenario**: Automatically sort downloaded files into folders

**Configuration**:
```yaml
watched_directories:
  - path: "C:/Users/John/Downloads"
    enabled: true

organization_rules:
  - name: "PDFs to Documents"
    file_types: [".pdf"]
    destination: "C:/Users/John/Documents/PDFs"
    enabled: true
```

**Result**: Any PDF downloaded goes straight to Documents/PDFs

### Example 2: Daily Photo Backup

**Scenario**: Backup photos every night at midnight

**Configuration**:
```yaml
backup:
  enabled: true
  source_directories:
    - "C:/Users/John/Pictures"
  destination: "E:/PhotoBackups"
  schedule_time: "00:00"
  type: "incremental"
  retention_days: 90
```

**Result**: Incremental backups of Pictures folder, keeping 90 days of history

### Example 3: Multi-directory Organization

**Scenario**: Monitor both Downloads and Desktop, sort multiple file types

**Configuration**:
```yaml
watched_directories:
  - path: "C:/Users/John/Downloads"
    enabled: true
  - path: "C:/Users/John/Desktop"
    enabled: true

organization_rules:
  - name: "Images"
    file_types: [".jpg", ".png", ".gif"]
    destination: "C:/Users/John/Pictures/Auto"
    enabled: true
  
  - name: "Videos"
    file_types: [".mp4", ".avi", ".mkv"]
    destination: "C:/Users/John/Videos/Auto"
    enabled: true
  
  - name: "Archives"
    file_types: [".zip", ".rar", ".7z"]
    destination: "C:/Users/John/Documents/Archives"
    enabled: true
```

## 📝 Logs

Activity logs are stored in `logs/automation.log` with the following format:

```
2025-12-23 14:30:45 - AutomationEngine - INFO - [ENGINE-STARTED] Personal Automation Engine initializing
2025-12-23 14:30:46 - AutomationEngine - INFO - [MOVE] SUCCESS | C:/Users/John/Downloads/report.pdf -> C:/Users/John/Documents/Organized/report.pdf
2025-12-23 23:00:00 - AutomationEngine - INFO - [BACKUP-INCREMENTAL] SUCCESS | Sources: C:/Users/John/Documents | Destination: D:/Backups/backup_20251223_230000 | Files: 145
```

## ❓ FAQ

**Q: Does this work on Mac/Linux?**  
A: The core functionality is cross-platform, but setup scripts are optimized for Windows. You can manually configure it on other systems.

**Q: Will it move files that are still downloading?**  
A: No, the engine waits for files to be stable (default 2 seconds) before processing.

**Q: Can I undo file moves?**  
A: Check the logs to see where files were moved. Manual restoration is required.

**Q: How much disk space do backups use?**  
A: Incremental backups only copy changed files. Full backups copy everything. Set `retention_days` to limit storage.

**Q: Can I run multiple instances?**  
A: Not recommended. Use one instance with multiple watched directories instead.

## 🛠️ Troubleshooting

### Engine won't start
- Verify Python 3.7+ is installed: `python --version`
- Check `config/config.yaml` exists
- Review logs in `logs/automation.log`

### Files not being organized
- Verify directories exist and are accessible
- Check file extensions match rules
- Ensure rules are `enabled: true`
- Check logs for errors

### Backup not running
- Verify `backup.enabled: true` in config
- Check schedule_time format (24-hour: "HH:MM")
- Ensure source and destination directories exist
- Review logs around scheduled time

### Permission errors
- Run as administrator if accessing system folders
- Check folder permissions
- Verify antivirus isn't blocking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## 📄 License

This project is licensed under the terms in the LICENSE file.

## 🙏 Acknowledgments

- **watchdog**: File system monitoring
- **PyYAML**: Configuration parsing
- **schedule**: Task scheduling
- **pywin32**: Windows integration

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for automated productivity**