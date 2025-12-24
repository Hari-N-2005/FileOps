# FileOps - Personal Automation Engine

Automated file organization, scheduled backups, and productivity insights running silently in the background.

## 🚀 Features

- **🗂️ Auto File Organization**: Monitors folders (Downloads, Desktop) and sorts files by type
- **🧠 Attention Leak Detector**: Identifies productivity losses from clutter, duplicates, and context switching
- **💾 Scheduled Backups**: Full or incremental backups at scheduled times
- **📝 Activity Logging**: Comprehensive logs of all operations
- **🎨 GUI Dashboard**: User-friendly interface with real-time insights

## 📋 Quick Start

See **[EASY_SETUP.md](EASY_SETUP.md)** for detailed installation instructions.

```bash
git clone https://github.com/Hari-N-2005/FileOps.git
cd FileOps
python setup.py
```

Edit `config/config.yaml` to set your paths, then run:
```bash
python main_gui.py
```

## 🔧 Core Features

### 1. Automatic File Organization

**How it works:** Watches specified directories and moves files based on extension rules.

**Example config:**
```yaml
watched_directories:
  - path: "C:/Users/YourName/Downloads"
    enabled: true

organization_rules:
  - name: "Documents"
    file_types: [".pdf", ".docx", ".txt"]
    destination: "C:/Users/YourName/Documents/Organized"
    enabled: true
```

**Result:** New PDFs/documents in Downloads → automatically moved to Documents/Organized

### 2. Scheduled Backups

**How it works:** Performs backups at specified times. Supports full and incremental modes.

**Example config:**
```yaml
backup:
  enabled: true
  source_directories:
    - "C:/Users/YourName/Documents"
  destination: "D:/Backups"
  schedule_time: "23:00"
  type: "incremental"
  retention_days: 30
```

**Result:** Daily backups at 11 PM, keeping 30 days of history

### 3. Attention Leak Detector

**How it works:** Tracks file activity and identifies productivity losses:
- ❄️ **Cold Files**: Created but never opened
- 📥 **Duplicates**: Same file downloaded multiple times  
- 🗂️ **Micro-Clutter**: Too many small files in folders
- 🔄 **Context Switching**: Frequent folder jumping
- 📁 **Orphaned Folders**: Inactive folders creating noise

**Usage:**
1. Click "🧠 Attention Insights" in GUI
2. Run analysis to see detected leaks
3. Export reports with actionable suggestions

**Example config:**
```yaml
attention_detector:
  enabled: true
  analysis_interval_hours: 24
  cold_file_days: 7
  auto_report: true
```

**Result:** Daily reports showing time wasted and specific improvements

## ⚙️ Configuration

All settings in `config/config.yaml`:

```yaml
# Watch folders for new files
watched_directories:
  - path: "C:/Users/YourName/Downloads"
    enabled: true

# Define organization rules
organization_rules:
  - name: "Images"
    file_types: [".jpg", ".png", ".gif"]
    destination: "C:/Users/YourName/Pictures/Auto"
    enabled: true

# Configure backups
backup:
  enabled: true
  source_directories: ["C:/Users/YourName/Documents"]
  destination: "D:/Backups"
  schedule_time: "23:00"
  type: "incremental"
  retention_days: 30

# Attention detector settings
attention_detector:
  enabled: true
  analysis_interval_hours: 24
  cold_file_days: 7
  micro_clutter_threshold: 50
  context_switch_threshold: 10
  auto_report: true
```

## 🎯 Usage

**GUI Mode (Recommended):**
```bash
python main_gui.py
```
- Click "▶ Start Engine"
- Monitor activity in real-time
- Access attention insights
- View logs and stats

**CLI Mode:**
```bash
python main.py
```

**Background Service:**
Place shortcut in Startup folder:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## 📊 How It Works

1. **Configuration** → Engine reads `config.yaml`
2. **Monitoring** → Watches directories for new files
3. **Detection** → New files trigger rule evaluation
4. **Organization** → Files moved to destinations
5. **Tracking** → Activity logged + attention patterns recorded
6. **Scheduling** → Backups run at specified times
7. **Analysis** → Periodic attention leak reports

## 🛠️ Troubleshooting

**Engine won't start:**
- Verify Python 3.7+: `python --version`
- Ensure `config/config.yaml` exists
- Check logs in `logs/automation.log`

**Files not organizing:**
- Verify paths exist and are accessible
- Check file extensions match rules
- Ensure rules are `enabled: true`

**Backups not running:**
- Verify `backup.enabled: true`
- Check time format: "HH:MM" (24-hour)
- Ensure source and destination exist

## 📚 Documentation

- **[EASY_SETUP.md](EASY_SETUP.md)** - Installation guide
- **[GUI_GUIDE.md](GUI_GUIDE.md)** - GUI usage instructions
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

Built with: watchdog, PyYAML, schedule, pywin32

---

**Made with ❤️ for automated productivity**
