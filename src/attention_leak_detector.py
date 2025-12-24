"""
Attention Leak Detector Module
Analyzes filesystem activity to identify hidden productivity losses
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict


@dataclass
class FileActivity:
    """Tracks activity for a single file"""
    path: str
    size: int
    created_at: float
    last_accessed: Optional[float] = None
    access_count: int = 0
    parent_folder: str = ""
    file_hash: Optional[str] = None
    is_deleted: bool = False


@dataclass
class AttentionLeak:
    """Represents a detected attention leak"""
    leak_type: str
    severity: str  # 'low', 'medium', 'high'
    title: str
    description: str
    estimated_time_loss_minutes: float
    affected_items: List[str]
    suggestion: str


class AttentionLeakDetector:
    """
    Detects hidden productivity losses from digital clutter and inefficient file usage
    """
    
    def __init__(self, data_file: str = "logs/attention_tracker.json", logger=None):
        """
        Initialize attention leak detector
        
        Args:
            data_file: Path to store tracking data
            logger: Logger instance
        """
        self.data_file = data_file
        self.logger = logger
        self.file_activities: Dict[str, FileActivity] = {}
        self.folder_switches: List[Tuple[str, float]] = []  # (folder, timestamp)
        self.last_analysis_time: Optional[float] = None
        
        # Configuration thresholds
        self.cold_file_days = 7  # Files not accessed in X days
        self.micro_clutter_threshold = 50  # Number of small files to trigger alert
        self.small_file_size_kb = 50  # Files smaller than this are "small"
        self.context_switch_threshold = 10  # Folder switches per hour to flag
        self.duplicate_download_window_hours = 24  # Time window to detect re-downloads
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load tracking data from disk"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Restore file activities
                    for path, activity_data in data.get('file_activities', {}).items():
                        self.file_activities[path] = FileActivity(**activity_data)
                    
                    # Restore folder switches
                    self.folder_switches = [
                        (folder, timestamp) 
                        for folder, timestamp in data.get('folder_switches', [])
                    ]
                    
                    self.last_analysis_time = data.get('last_analysis_time')
                    
                    if self.logger:
                        self.logger.debug(f"Loaded {len(self.file_activities)} tracked files")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not load attention tracker data: {e}")
    
    def _save_data(self) -> None:
        """Save tracking data to disk"""
        try:
            # Create directory if needed
            Path(self.data_file).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'file_activities': {
                    path: asdict(activity) 
                    for path, activity in self.file_activities.items()
                },
                'folder_switches': self.folder_switches[-1000:],  # Keep last 1000
                'last_analysis_time': self.last_analysis_time
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save attention tracker data: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate MD5 hash of file for duplicate detection"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Only hash files smaller than 100MB to avoid performance issues
            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                return None
            
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Read in chunks
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Could not hash file {file_path}: {e}")
            return None
    
    def track_file_created(self, file_path: str) -> None:
        """
        Track a newly created file
        
        Args:
            file_path: Path to the created file
        """
        try:
            if not os.path.exists(file_path):
                return
            
            file_size = os.path.getsize(file_path)
            parent_folder = str(Path(file_path).parent)
            file_hash = self._calculate_file_hash(file_path)
            
            self.file_activities[file_path] = FileActivity(
                path=file_path,
                size=file_size,
                created_at=time.time(),
                parent_folder=parent_folder,
                file_hash=file_hash
            )
            
            # Track folder context switch
            self._track_folder_switch(parent_folder)
            
            # Auto-save periodically
            if len(self.file_activities) % 10 == 0:
                self._save_data()
                
            if self.logger:
                self.logger.debug(f"Tracking new file: {file_path}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error tracking file creation: {e}")
    
    def track_file_accessed(self, file_path: str) -> None:
        """
        Track file access (open, read, etc.)
        
        Args:
            file_path: Path to the accessed file
        """
        try:
            if file_path in self.file_activities:
                activity = self.file_activities[file_path]
                activity.last_accessed = time.time()
                activity.access_count += 1
            else:
                # File was created before tracking started
                if os.path.exists(file_path):
                    self.track_file_created(file_path)
                    self.file_activities[file_path].last_accessed = time.time()
                    self.file_activities[file_path].access_count = 1
            
            # Track folder context switch
            parent_folder = str(Path(file_path).parent)
            self._track_folder_switch(parent_folder)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error tracking file access: {e}")
    
    def track_file_deleted(self, file_path: str) -> None:
        """
        Track file deletion
        
        Args:
            file_path: Path to the deleted file
        """
        if file_path in self.file_activities:
            self.file_activities[file_path].is_deleted = True
    
    def _track_folder_switch(self, folder: str) -> None:
        """Track folder context switches"""
        current_time = time.time()
        
        # Only count as switch if different from last folder
        if self.folder_switches:
            last_folder, last_time = self.folder_switches[-1]
            # Must be different folder and at least 10 seconds apart
            if folder != last_folder and (current_time - last_time) >= 10:
                self.folder_switches.append((folder, current_time))
        else:
            self.folder_switches.append((folder, current_time))
    
    def _detect_cold_files(self) -> List[AttentionLeak]:
        """Detect files that were created but never opened"""
        leaks = []
        current_time = time.time()
        cold_days_seconds = self.cold_file_days * 24 * 3600
        
        cold_files = []
        total_size_mb = 0
        
        for path, activity in self.file_activities.items():
            # Skip deleted files
            if activity.is_deleted:
                continue
            
            # File created but never accessed
            age = current_time - activity.created_at
            if activity.access_count == 0 and age >= cold_days_seconds:
                if os.path.exists(path):  # Verify file still exists
                    cold_files.append(path)
                    total_size_mb += activity.size / (1024 * 1024)
        
        if cold_files:
            # Estimate time loss: 5 seconds per file to scan/decide
            estimated_loss = len(cold_files) * 5 / 60
            
            severity = 'low'
            if len(cold_files) > 50:
                severity = 'high'
            elif len(cold_files) > 20:
                severity = 'medium'
            
            leaks.append(AttentionLeak(
                leak_type='cold_files',
                severity=severity,
                title=f'{len(cold_files)} Cold Files Detected',
                description=f'Found {len(cold_files)} files created {self.cold_file_days}+ days ago '
                           f'that were never opened, wasting {total_size_mb:.1f}MB of storage. '
                           f'These files clutter your workspace and create visual noise.',
                estimated_time_loss_minutes=estimated_loss,
                affected_items=cold_files[:10],  # Show first 10
                suggestion='Review and delete unused files. Consider automated cleanup rules '
                          'for file types you frequently download but never use.'
            ))
        
        return leaks
    
    def _detect_duplicate_downloads(self) -> List[AttentionLeak]:
        """Detect files that were re-downloaded multiple times"""
        leaks = []
        current_time = time.time()
        window_seconds = self.duplicate_download_window_hours * 3600
        
        # Group files by hash
        hash_groups: Dict[str, List[FileActivity]] = defaultdict(list)
        
        for activity in self.file_activities.values():
            if activity.file_hash and not activity.is_deleted:
                # Only consider recent files
                if current_time - activity.created_at <= window_seconds:
                    hash_groups[activity.file_hash].append(activity)
        
        # Find duplicates
        duplicate_groups = []
        total_duplicates = 0
        
        for file_hash, activities in hash_groups.items():
            if len(activities) >= 2:
                # Multiple files with same hash = re-downloads
                duplicate_groups.append(activities)
                total_duplicates += len(activities) - 1  # Count extras
        
        if duplicate_groups:
            # Estimate time loss: 30 seconds per duplicate to handle
            estimated_loss = total_duplicates * 30 / 60
            
            severity = 'low'
            if total_duplicates > 10:
                severity = 'high'
            elif total_duplicates > 5:
                severity = 'medium'
            
            affected_files = []
            for group in duplicate_groups[:5]:  # Show first 5 groups
                for activity in group:
                    affected_files.append(f"{Path(activity.path).name} ({activity.parent_folder})")
            
            leaks.append(AttentionLeak(
                leak_type='duplicate_downloads',
                severity=severity,
                title=f'{total_duplicates} Duplicate Files Downloaded',
                description=f'Detected {total_duplicates} duplicate files downloaded within '
                           f'{self.duplicate_download_window_hours} hours. Re-downloading files '
                           f'indicates poor file organization or inability to locate existing files.',
                estimated_time_loss_minutes=estimated_loss,
                affected_items=affected_files,
                suggestion='Implement better file naming conventions and use a dedicated downloads '
                          'organizer. Consider bookmarking frequently accessed files.'
            ))
        
        return leaks
    
    def _detect_micro_clutter(self) -> List[AttentionLeak]:
        """Detect excessive small files scattered across folders"""
        leaks = []
        small_file_bytes = self.small_file_size_kb * 1024
        
        # Group small files by folder
        folder_small_files: Dict[str, List[str]] = defaultdict(list)
        
        for path, activity in self.file_activities.items():
            if activity.size < small_file_bytes and not activity.is_deleted:
                if os.path.exists(path):
                    folder_small_files[activity.parent_folder].append(path)
        
        # Find folders with excessive small files
        cluttered_folders = []
        total_small_files = 0
        
        for folder, files in folder_small_files.items():
            if len(files) >= self.micro_clutter_threshold:
                cluttered_folders.append((folder, len(files)))
                total_small_files += len(files)
        
        if cluttered_folders:
            # Estimate time loss: 2 seconds per small file to scan
            estimated_loss = total_small_files * 2 / 60
            
            severity = 'low'
            if total_small_files > 200:
                severity = 'high'
            elif total_small_files > 100:
                severity = 'medium'
            
            affected_items = [
                f"{folder}: {count} small files"
                for folder, count in sorted(cluttered_folders, key=lambda x: x[1], reverse=True)[:5]
            ]
            
            leaks.append(AttentionLeak(
                leak_type='micro_clutter',
                severity=severity,
                title=f'Micro-Clutter in {len(cluttered_folders)} Folders',
                description=f'Found {total_small_files} small files (<{self.small_file_size_kb}KB) '
                           f'scattered across {len(cluttered_folders)} folders. Small files create '
                           f'visual clutter and slow down folder navigation.',
                estimated_time_loss_minutes=estimated_loss,
                affected_items=affected_items,
                suggestion='Archive or consolidate small files into dedicated folders. Use compression '
                          'for collections of related small files. Delete temporary/cache files.'
            ))
        
        return leaks
    
    def _detect_context_switching(self) -> List[AttentionLeak]:
        """Detect excessive context switching between folders"""
        leaks = []
        current_time = time.time()
        hour_seconds = 3600
        
        # Count folder switches in the last hour
        recent_switches = [
            folder for folder, timestamp in self.folder_switches
            if current_time - timestamp <= hour_seconds
        ]
        
        if len(recent_switches) >= self.context_switch_threshold:
            # Count unique folders
            unique_folders = len(set(recent_switches))
            
            # Estimate time loss: 15 seconds per switch (mental overhead)
            estimated_loss = len(recent_switches) * 15 / 60
            
            severity = 'low'
            if len(recent_switches) > 30:
                severity = 'high'
            elif len(recent_switches) > 20:
                severity = 'medium'
            
            # Show most frequently accessed folders
            folder_counts = Counter(recent_switches)
            top_folders = [
                f"{Path(folder).name}: {count} visits"
                for folder, count in folder_counts.most_common(5)
            ]
            
            leaks.append(AttentionLeak(
                leak_type='context_switching',
                severity=severity,
                title=f'High Context Switching: {len(recent_switches)} Folder Changes',
                description=f'Detected {len(recent_switches)} folder switches in the last hour '
                           f'across {unique_folders} different folders. Frequent switching '
                           f'between unrelated folders fragments attention and reduces productivity.',
                estimated_time_loss_minutes=estimated_loss,
                affected_items=top_folders,
                suggestion='Group related work in fewer folders. Use project-based organization. '
                          'Consider keeping a "working" folder for active tasks. Enable file tags '
                          'or shortcuts to reduce navigation.'
            ))
        
        return leaks
    
    def _detect_orphaned_folders(self) -> List[AttentionLeak]:
        """Detect folders with files but no recent activity"""
        leaks = []
        current_time = time.time()
        inactive_days = 30
        inactive_seconds = inactive_days * 24 * 3600
        
        # Group files by folder and find last activity
        folder_activity: Dict[str, Tuple[float, int]] = {}  # folder -> (last_access, file_count)
        
        for activity in self.file_activities.values():
            if activity.is_deleted:
                continue
            
            folder = activity.parent_folder
            last_time = activity.last_accessed or activity.created_at
            
            if folder in folder_activity:
                old_time, count = folder_activity[folder]
                folder_activity[folder] = (max(old_time, last_time), count + 1)
            else:
                folder_activity[folder] = (last_time, 1)
        
        # Find orphaned folders
        orphaned = []
        total_files = 0
        
        for folder, (last_time, file_count) in folder_activity.items():
            age = current_time - last_time
            if age >= inactive_seconds and file_count >= 5:
                orphaned.append((folder, file_count, age / (24 * 3600)))
                total_files += file_count
        
        if orphaned:
            estimated_loss = len(orphaned) * 1  # 1 minute per orphaned folder
            
            severity = 'low'
            if len(orphaned) > 10:
                severity = 'high'
            elif len(orphaned) > 5:
                severity = 'medium'
            
            affected_items = [
                f"{Path(folder).name}: {count} files ({days:.0f} days inactive)"
                for folder, count, days in sorted(orphaned, key=lambda x: x[2], reverse=True)[:5]
            ]
            
            leaks.append(AttentionLeak(
                leak_type='orphaned_folders',
                severity=severity,
                title=f'{len(orphaned)} Orphaned Folders Detected',
                description=f'Found {len(orphaned)} folders with {total_files} files that '
                           f'haven\'t been accessed in {inactive_days}+ days. These folders '
                           f'create mental overhead during navigation and file searches.',
                estimated_time_loss_minutes=estimated_loss,
                affected_items=affected_items,
                suggestion='Archive old project folders to a "Completed" or "Archive" directory. '
                          'Delete folders that are no longer needed. Use date-based folder naming '
                          'to quickly identify old content.'
            ))
        
        return leaks
    
    def analyze_attention_leaks(self) -> List[AttentionLeak]:
        """
        Analyze all tracked data and detect attention leaks
        
        Returns:
            List of detected attention leaks
        """
        try:
            if self.logger:
                self.logger.info("Running attention leak analysis...")
            
            leaks = []
            
            # Run all detection heuristics
            leaks.extend(self._detect_cold_files())
            leaks.extend(self._detect_duplicate_downloads())
            leaks.extend(self._detect_micro_clutter())
            leaks.extend(self._detect_context_switching())
            leaks.extend(self._detect_orphaned_folders())
            
            # Sort by severity and estimated time loss
            severity_order = {'high': 3, 'medium': 2, 'low': 1}
            leaks.sort(
                key=lambda x: (severity_order[x.severity], x.estimated_time_loss_minutes),
                reverse=True
            )
            
            self.last_analysis_time = time.time()
            self._save_data()
            
            if self.logger:
                self.logger.info(f"Analysis complete: {len(leaks)} attention leaks detected")
            
            return leaks
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during attention leak analysis: {e}", exc_info=True)
            return []
    
    def generate_summary(self) -> Dict:
        """
        Generate a comprehensive summary of attention leaks
        
        Returns:
            Dictionary with summary statistics and leaks
        """
        leaks = self.analyze_attention_leaks()
        
        total_time_loss = sum(leak.estimated_time_loss_minutes for leak in leaks)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_leaks_detected': len(leaks),
            'total_estimated_time_loss_minutes': round(total_time_loss, 1),
            'total_files_tracked': len([a for a in self.file_activities.values() if not a.is_deleted]),
            'leaks_by_severity': {
                'high': len([l for l in leaks if l.severity == 'high']),
                'medium': len([l for l in leaks if l.severity == 'medium']),
                'low': len([l for l in leaks if l.severity == 'low'])
            },
            'leaks': [asdict(leak) for leak in leaks],
            'analysis_period_days': self.cold_file_days
        }
        
        return summary
    
    def cleanup_old_data(self, days: int = 90) -> None:
        """
        Clean up tracking data older than specified days
        
        Args:
            days: Number of days to retain data
        """
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            # Remove old file activities
            old_paths = [
                path for path, activity in self.file_activities.items()
                if activity.created_at < cutoff_time
            ]
            
            for path in old_paths:
                del self.file_activities[path]
            
            # Remove old folder switches
            self.folder_switches = [
                (folder, timestamp) for folder, timestamp in self.folder_switches
                if timestamp >= cutoff_time
            ]
            
            self._save_data()
            
            if self.logger:
                self.logger.info(f"Cleaned up {len(old_paths)} old file records")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_stats(self) -> Dict:
        """Get basic statistics about tracked data"""
        active_files = [a for a in self.file_activities.values() if not a.is_deleted]
        
        return {
            'total_files_tracked': len(active_files),
            'total_accesses': sum(a.access_count for a in active_files),
            'folder_switches_today': len([
                f for f, t in self.folder_switches
                if time.time() - t <= 24 * 3600
            ]),
            'last_analysis': datetime.fromtimestamp(self.last_analysis_time).strftime('%Y-%m-%d %H:%M:%S')
            if self.last_analysis_time else 'Never'
        }
