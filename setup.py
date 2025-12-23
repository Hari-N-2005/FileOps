"""
Setup and Installation Script
Helps set up the automation engine on Windows
"""

import os
import sys
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling dependencies...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print(f"✗ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error installing dependencies: {e}")
        return False


def create_config():
    """Create configuration file from example"""
    config_dir = Path("config")
    example_config = config_dir / "config.example.yaml"
    target_config = config_dir / "config.yaml"
    user_settings = config_dir / "user_settings.txt"
    
    if target_config.exists():
        response = input("\nConfiguration file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing configuration")
            # Still create user_settings.txt if it doesn't exist
            if not user_settings.exists():
                _create_user_settings()
            return True
    
    try:
        shutil.copy(example_config, target_config)
        print(f"✓ Created configuration file: {target_config}")
        
        # Create user_settings.txt
        if not user_settings.exists():
            _create_user_settings()
        
        # Prompt for username
        print("\n" + "="*50)
        username = input("Enter your Windows username (leave empty to set later): ").strip()
        
        if username:
            # Update user_settings.txt with the username
            try:
                with open(user_settings, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = content.replace("USERNAME=YourUsername", f"USERNAME={username}")
                
                with open(user_settings, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Username set to: {username}")
                print(f"✓ Configuration will use: C:/Users/{username}/...")
            except Exception as e:
                print(f"⚠ Could not update username: {e}")
        else:
            print("\n⚠ IMPORTANT: Edit config/user_settings.txt and set your USERNAME")
            print("  This will automatically update all paths in the configuration")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}")
        return False


def _create_user_settings():
    """Create user_settings.txt file from example"""
    user_settings_path = Path("config/user_settings.txt")
    example_settings_path = Path("config/user_settings.example.txt")
    
    if user_settings_path.exists():
        return
    
    # Try to copy from example first
    if example_settings_path.exists():
        try:
            shutil.copy(example_settings_path, user_settings_path)
            print(f"✓ Created user settings file: {user_settings_path}")
            return
        except Exception as e:
            print(f"⚠ Could not copy example file: {e}")
    
    # Fallback: create from scratch if example doesn't exist
    content = """# User Settings
# Edit this file with your Windows username and other personal settings
# These values will automatically replace placeholders in config.yaml

# Your Windows username (e.g., John, Sarah, Admin)
USERNAME=YourUsername

# Optional: Custom base paths (leave as-is to use defaults)
# DOWNLOADS_PATH=C:/Users/{USERNAME}/Downloads
# DOCUMENTS_PATH=C:/Users/{USERNAME}/Documents
# DESKTOP_PATH=C:/Users/{USERNAME}/Desktop
# PICTURES_PATH=C:/Users/{USERNAME}/Pictures
# VIDEOS_PATH=C:/Users/{USERNAME}/Videos
"""
    
    try:
        with open(user_settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created user settings file: {user_settings_path}")
    except Exception as e:
        print(f"⚠ Could not create user settings file: {e}")


def create_shortcut():
    """Create desktop shortcut (Windows)"""
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "Personal Automation Engine.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        # Get absolute path to main.py
        script_path = Path(__file__).parent.absolute() / "main.py"
        python_path = sys.executable
        
        shortcut.Targetpath = python_path
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = str(Path(__file__).parent.absolute())
        shortcut.IconLocation = python_path
        shortcut.save()
        
        print(f"✓ Desktop shortcut created: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠ Could not create shortcut (pywin32 not available)")
        print("  Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"⚠ Could not create desktop shortcut: {e}")
        return False


def create_startup_script():
    """Create a batch file to run on Windows startup"""
    try:
        startup_folder = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        batch_file = startup_folder / "PersonalAutomationEngine.bat"
        
        script_path = Path(__file__).parent.absolute() / "main.py"
        python_path = sys.executable
        
        batch_content = f"""@echo off
cd /d "{Path(__file__).parent.absolute()}"
start "" "{python_path}" "{script_path}"
"""
        
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        print(f"✓ Startup script created: {batch_file}")
        print("  Engine will start automatically on Windows login")
        return True
        
    except Exception as e:
        print(f"⚠ Could not create startup script: {e}")
        return False


def main():
    """Main setup routine"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║   Personal Automation Engine Setup        ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    # Create configuration
    if not create_config():
        print("\n✗ Setup failed: Could not create configuration")
        sys.exit(1)
    
    # Optional features
    print("\n" + "="*50)
    print("Optional Setup Steps:")
    print("="*50)
    
    # Create desktop shortcut
    response = input("\nCreate desktop shortcut? (Y/n): ")
    if response.lower() != 'n':
        create_shortcut()
    
    # Create startup script
    response = input("\nRun engine on Windows startup? (y/N): ")
    if response.lower() == 'y':
        create_startup_script()
    
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("  1. Edit config/config.yaml with your directories")
    print("  2. Run: python main.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
