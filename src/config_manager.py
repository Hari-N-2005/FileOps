"""
Configuration Manager
Loads and validates automation rules and settings from config.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any


class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.user_settings = self._load_user_settings()
        self._load_config()
    
    def _load_user_settings(self) -> Dict[str, str]:
        """Load user settings from user_settings.txt"""
        settings_path = "config/user_settings.txt"
        settings = {}
        
        if not os.path.exists(settings_path):
            return settings
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip()
            
            # Set default paths based on username if provided
            if 'USERNAME' in settings:
                username = settings['USERNAME']
                if username and username != 'YourUsername':
                    settings.setdefault('DOWNLOADS_PATH', f"C:/Users/{username}/Downloads")
                    settings.setdefault('DOCUMENTS_PATH', f"C:/Users/{username}/Documents")
                    settings.setdefault('DESKTOP_PATH', f"C:/Users/{username}/Desktop")
                    settings.setdefault('PICTURES_PATH', f"C:/Users/{username}/Pictures")
                    settings.setdefault('VIDEOS_PATH', f"C:/Users/{username}/Videos")
        
        except Exception as e:
            print(f"Warning: Could not load user settings: {e}")
        
        return settings
    
    def _substitute_variables(self, text: str) -> str:
        """Substitute variables in text with user settings"""
        if not isinstance(text, str):
            return text
        
        result = text
        for key, value in self.user_settings.items():
            result = result.replace(f"{{{key}}}", value)
            # Also replace YourUsername directly if USERNAME is set
            if key == 'USERNAME' and value and value != 'YourUsername':
                result = result.replace("YourUsername", value)
        
        return result
    
    def _substitute_in_dict(self, data: Any) -> Any:
        """Recursively substitute variables in dictionaries and lists"""
        if isinstance(data, dict):
            return {key: self._substitute_in_dict(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_in_dict(item) for item in data]
        elif isinstance(data, str):
            return self._substitute_variables(data)
        else:
            return data
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config/config.example.yaml to config/config.yaml and customize it."
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
            
            # Substitute user variables
            self.config = self._substitute_in_dict(raw_config)
            
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration structure and required fields"""
        required_sections = ['watched_directories', 'organization_rules', 'backup', 'logging', 'general']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate watched directories
        if not isinstance(self.config['watched_directories'], list):
            raise ValueError("'watched_directories' must be a list")
        
        # Validate organization rules
        if not isinstance(self.config['organization_rules'], list):
            raise ValueError("'organization_rules' must be a list")
        
        # Create destination directories if they don't exist (safely)
        for rule in self.config['organization_rules']:
            if rule.get('enabled', True):
                dest = rule.get('destination')
                if dest:
                    try:
                        # Check if parent drive/path exists before creating
                        parent = Path(dest).parent
                        if parent.exists() or str(parent) in ['', '.']:
                            Path(dest).mkdir(parents=True, exist_ok=True)
                    except (OSError, PermissionError) as e:
                        # Don't fail on directory creation, just warn
                        print(f"Warning: Could not create directory {dest}: {e}")
        
        # Create backup destination if enabled (safely)
        if self.config['backup'].get('enabled', False):
            backup_dest = self.config['backup'].get('destination')
            if backup_dest:
                try:
                    # Check if the drive exists first
                    dest_path = Path(backup_dest)
                    
                    # Extract drive letter for Windows paths
                    drive = dest_path.drive
                    if drive:
                        # Check if drive exists
                        if not Path(drive + '/').exists():
                            raise ValueError(
                                f"Backup destination drive does not exist: {drive}\n"
                                f"Please update 'backup.destination' in config.yaml to use an existing drive.\n"
                                f"Example: C:/Backups or {Path.home()}/Backups"
                            )
                    
                    dest_path.mkdir(parents=True, exist_ok=True)
                    
                except ValueError:
                    # Re-raise validation errors
                    raise
                except (OSError, PermissionError) as e:
                    raise ValueError(
                        f"Cannot create backup destination: {backup_dest}\n"
                        f"Error: {e}\n"
                        f"Please check the path and permissions, or disable backups by setting 'backup.enabled: false'"
                    )
    
    def get_watched_directories(self) -> List[str]:
        """Get list of enabled watched directories"""
        return [
            d['path'] for d in self.config['watched_directories']
            if d.get('enabled', True) and os.path.exists(d['path'])
        ]
    
    def get_organization_rules(self) -> List[Dict[str, Any]]:
        """Get list of enabled organization rules"""
        return [
            rule for rule in self.config['organization_rules']
            if rule.get('enabled', True)
        ]
    
    def get_backup_config(self) -> Dict[str, Any]:
        """Get backup configuration"""
        return self.config['backup']
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config['logging']
    
    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration"""
        return self.config['general']
    
    def is_backup_enabled(self) -> bool:
        """Check if backup is enabled"""
        return self.config['backup'].get('enabled', False)
    
    def get_file_stable_time(self) -> int:
        """Get time to wait before processing new files"""
        return self.config['general'].get('file_stable_time', 2)
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()


# Singleton instance
_config_instance = None


def get_config(config_path: str = "config/config.yaml") -> ConfigManager:
    """
    Get singleton configuration manager instance
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    return _config_instance
