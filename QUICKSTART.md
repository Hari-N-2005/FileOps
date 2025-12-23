# Quick Start Guide

Get your Personal Automation Engine running in 5 minutes!

## Step 1: Verify Python Installation

Open Command Prompt and run:
```bash
python --version
```

You should see Python 3.7 or higher. If not, download from [python.org](https://www.python.org/downloads/).

## Step 2: Run Setup

Navigate to the project directory and run:
```bash
python setup.py
```

Follow the prompts to:
- Install dependencies
- Create configuration file
- (Optional) Create desktop shortcut
- (Optional) Set up auto-start

## Step 3: Configure Your Automation

Edit `config/config.yaml` with Notepad or your favorite editor:

```bash
notepad config\config.yaml
```

**Important**: Replace all instances of `YourUsername` with your actual Windows username!

### Quick Configuration Example

```yaml
watched_directories:
  - path: "C:/Users/YOUR_USERNAME/Downloads"  # ← Change this
    enabled: true

organization_rules:
  - name: "Organize PDFs"
    file_types: [".pdf"]
    destination: "C:/Users/YOUR_USERNAME/Documents/PDFs"  # ← Change this
    enabled: true

backup:
  enabled: false  # Set to true if you want backups
```

## Step 4: Start the Engine

Double-click `run.bat` or run:
```bash
python main.py
```

You should see:
```
╔═══════════════════════════════════════════╗
║   Personal Automation Engine v1.0.0       ║
║   Automate Your Everyday Tasks            ║
╚═══════════════════════════════════════════╝

Initializing Personal Automation Engine...
✓ Configuration loaded
✓ All components initialized successfully
```

## Step 5: Test It!

1. Download a PDF file
2. Watch as it automatically moves to your configured destination
3. Check `logs/automation.log` to see the activity

## Common First-Time Issues

### "Configuration file not found"
**Solution**: Make sure you ran `python setup.py` or manually copied `config.example.yaml` to `config.yaml`

### "Directory does not exist"
**Solution**: Update all paths in `config.yaml` to match your actual folder structure

### "Permission denied"
**Solution**: Run Command Prompt as Administrator or check folder permissions

## What's Next?

- Read the full [README.md](README.md) for advanced features
- Customize more organization rules
- Set up scheduled backups
- Configure logging levels

## Need Help?

Check the logs at `logs/automation.log` for detailed error messages, or open an issue on GitHub.

---

**That's it! Your automation engine is now running and organizing your files automatically.**
