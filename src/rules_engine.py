"""
Rules Engine
Evaluates files against organization rules and determines actions
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class RulesEngine:
    """Evaluates files against organization rules"""
    
    def __init__(self, rules: List[Dict[str, Any]], logger=None):
        """
        Initialize rules engine
        
        Args:
            rules: List of organization rules from configuration
            logger: Logger instance
        """
        self.rules = rules
        self.logger = logger
        self._validate_rules()
    
    def _validate_rules(self) -> None:
        """Validate rules structure"""
        for rule in self.rules:
            if 'file_types' not in rule:
                if self.logger:
                    self.logger.warning(f"Rule '{rule.get('name', 'unnamed')}' missing file_types")
            
            if 'destination' not in rule:
                if self.logger:
                    self.logger.warning(f"Rule '{rule.get('name', 'unnamed')}' missing destination")
    
    def find_matching_rule(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Find the first rule that matches the given file
        
        Args:
            file_path: Path to the file to evaluate
            
        Returns:
            Matching rule dictionary or None if no match
        """
        if not os.path.exists(file_path):
            if self.logger:
                self.logger.warning(f"File does not exist: {file_path}")
            return None
        
        file_extension = Path(file_path).suffix.lower()
        file_name = Path(file_path).name.lower()
        
        for rule in self.rules:
            if not rule.get('enabled', True):
                continue
            
            # Check file type match
            file_types = rule.get('file_types', [])
            if file_extension in [ft.lower() for ft in file_types]:
                if self.logger:
                    self.logger.debug(
                        f"File '{file_name}' matched rule '{rule.get('name', 'unnamed')}'"
                    )
                return rule
            
            # Optional: Check name pattern match (if implemented in config)
            name_patterns = rule.get('name_patterns', [])
            for pattern in name_patterns:
                if pattern.lower() in file_name:
                    if self.logger:
                        self.logger.debug(
                            f"File '{file_name}' matched rule '{rule.get('name', 'unnamed')}' by pattern"
                        )
                    return rule
        
        if self.logger:
            self.logger.debug(f"No matching rule found for: {file_name}")
        
        return None
    
    def get_destination(self, file_path: str) -> Optional[str]:
        """
        Get destination directory for a file based on rules
        
        Args:
            file_path: Path to the file
            
        Returns:
            Destination directory path or None if no match
        """
        rule = self.find_matching_rule(file_path)
        
        if rule is None:
            return None
        
        destination = rule.get('destination')
        
        if destination:
            # Ensure destination directory exists
            Path(destination).mkdir(parents=True, exist_ok=True)
            return destination
        
        return None
    
    def should_process_file(self, file_path: str) -> bool:
        """
        Determine if a file should be processed
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be processed, False otherwise
        """
        # Skip if file doesn't exist
        if not os.path.exists(file_path):
            return False
        
        # Skip directories
        if os.path.isdir(file_path):
            return False
        
        # Skip hidden files (starting with .)
        if Path(file_path).name.startswith('.'):
            if self.logger:
                self.logger.debug(f"Skipping hidden file: {file_path}")
            return False
        
        # Skip system files
        system_files = ['desktop.ini', 'thumbs.db', '.ds_store']
        if Path(file_path).name.lower() in system_files:
            if self.logger:
                self.logger.debug(f"Skipping system file: {file_path}")
            return False
        
        # Skip temporary files
        if Path(file_path).name.endswith('.tmp') or Path(file_path).name.endswith('.temp'):
            if self.logger:
                self.logger.debug(f"Skipping temporary file: {file_path}")
            return False
        
        # Check if any rule matches
        return self.find_matching_rule(file_path) is not None
    
    def get_rule_stats(self) -> Dict[str, int]:
        """
        Get statistics about rules
        
        Returns:
            Dictionary with rule statistics
        """
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules if r.get('enabled', True)),
            'disabled_rules': sum(1 for r in self.rules if not r.get('enabled', True))
        }
