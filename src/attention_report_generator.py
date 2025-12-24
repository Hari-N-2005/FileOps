"""
Attention Leak Report Generator
Creates user-friendly reports from attention leak analysis
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class AttentionReportGenerator:
    """Generates reports for attention leak analysis"""
    
    def __init__(self, output_dir: str = "logs/attention_reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level"""
        return {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity, '⚪')
    
    def _get_leak_type_icon(self, leak_type: str) -> str:
        """Get icon for leak type"""
        return {
            'cold_files': '❄️',
            'duplicate_downloads': '📥',
            'micro_clutter': '🗂️',
            'context_switching': '🔄',
            'orphaned_folders': '📁'
        }.get(leak_type, '⚠️')
    
    def generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """
        Generate a markdown report from attention leak summary
        
        Args:
            summary: Summary dictionary from AttentionLeakDetector.generate_summary()
            
        Returns:
            Path to the generated report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.output_dir, f'attention_leak_report_{timestamp}.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# 🧠 Attention Leak Detection Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            f.write(f"- **Total Leaks Detected:** {summary['total_leaks_detected']}\n")
            f.write(f"- **Estimated Time Loss:** {summary['total_estimated_time_loss_minutes']:.1f} minutes\n")
            f.write(f"- **Files Tracked:** {summary['total_files_tracked']}\n")
            f.write(f"- **Analysis Period:** {summary['analysis_period_days']} days\n\n")
            
            # Severity Breakdown
            severity_counts = summary['leaks_by_severity']
            f.write("### Severity Breakdown\n\n")
            f.write(f"- 🔴 **High Priority:** {severity_counts['high']} leaks\n")
            f.write(f"- 🟡 **Medium Priority:** {severity_counts['medium']} leaks\n")
            f.write(f"- 🟢 **Low Priority:** {severity_counts['low']} leaks\n\n")
            
            # Overall Status
            if summary['total_leaks_detected'] == 0:
                f.write("### ✅ Status: Excellent\n\n")
                f.write("No significant attention leaks detected! Your digital workspace is well-organized.\n\n")
            elif severity_counts['high'] > 0:
                f.write("### ⚠️ Status: Action Required\n\n")
                f.write("High-priority attention leaks detected. Review the recommendations below to improve productivity.\n\n")
            elif severity_counts['medium'] > 0:
                f.write("### 🔔 Status: Room for Improvement\n\n")
                f.write("Some attention leaks detected. Consider implementing the suggestions to optimize your workflow.\n\n")
            else:
                f.write("### 👍 Status: Good\n\n")
                f.write("Minor attention leaks detected. Your workspace is generally well-maintained.\n\n")
            
            # Detailed Leaks
            if summary['leaks']:
                f.write("---\n\n")
                f.write("## 🔍 Detailed Findings\n\n")
                
                for i, leak in enumerate(summary['leaks'], 1):
                    severity_emoji = self._get_severity_emoji(leak['severity'])
                    icon = self._get_leak_type_icon(leak['leak_type'])
                    
                    f.write(f"### {i}. {icon} {leak['title']}\n\n")
                    f.write(f"**Severity:** {severity_emoji} {leak['severity'].upper()}\n\n")
                    f.write(f"**Estimated Time Loss:** {leak['estimated_time_loss_minutes']:.1f} minutes\n\n")
                    
                    f.write(f"**Description:**\n\n{leak['description']}\n\n")
                    
                    if leak['affected_items']:
                        f.write(f"**Affected Items ({len(leak['affected_items'])} shown):**\n\n")
                        for item in leak['affected_items']:
                            f.write(f"- `{item}`\n")
                        f.write("\n")
                    
                    f.write(f"**💡 Suggestion:**\n\n{leak['suggestion']}\n\n")
                    f.write("---\n\n")
            
            # Action Plan
            if summary['leaks']:
                f.write("## 📝 Recommended Action Plan\n\n")
                f.write("Based on the detected attention leaks, here's a prioritized action plan:\n\n")
                
                # Group by severity
                high_priority = [l for l in summary['leaks'] if l['severity'] == 'high']
                medium_priority = [l for l in summary['leaks'] if l['severity'] == 'medium']
                low_priority = [l for l in summary['leaks'] if l['severity'] == 'low']
                
                if high_priority:
                    f.write("### 🔴 High Priority (Do First)\n\n")
                    for leak in high_priority:
                        f.write(f"1. **{leak['title']}**\n")
                        f.write(f"   - {leak['suggestion']}\n\n")
                
                if medium_priority:
                    f.write("### 🟡 Medium Priority (Do This Week)\n\n")
                    for leak in medium_priority:
                        f.write(f"1. **{leak['title']}**\n")
                        f.write(f"   - {leak['suggestion']}\n\n")
                
                if low_priority:
                    f.write("### 🟢 Low Priority (Do When Time Permits)\n\n")
                    for leak in low_priority:
                        f.write(f"1. **{leak['title']}**\n")
                        f.write(f"   - {leak['suggestion']}\n\n")
            
            # Footer
            f.write("---\n\n")
            f.write("## 🎯 Tips for Maintaining a Healthy Digital Workspace\n\n")
            f.write("1. **Regular Cleanup:** Set aside 15 minutes weekly to review and organize files\n")
            f.write("2. **Consistent Naming:** Use clear, consistent file naming conventions\n")
            f.write("3. **Project Organization:** Keep related files together in dedicated folders\n")
            f.write("4. **Delete Aggressively:** If you haven't used it in 30 days, consider deleting it\n")
            f.write("5. **Automation:** Use file organization rules to automatically sort new files\n")
            f.write("6. **Regular Reviews:** Run this analysis weekly to catch issues early\n\n")
            
            f.write("---\n\n")
            f.write("*Report generated by FileOps Attention Leak Detector*\n")
        
        return report_path
    
    def generate_text_summary(self, summary: Dict[str, Any]) -> str:
        """
        Generate a brief text summary for display
        
        Args:
            summary: Summary dictionary from AttentionLeakDetector.generate_summary()
            
        Returns:
            Text summary string
        """
        lines = []
        lines.append("=== ATTENTION LEAK SUMMARY ===")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append(f"Total Leaks: {summary['total_leaks_detected']}")
        lines.append(f"Estimated Time Loss: {summary['total_estimated_time_loss_minutes']:.1f} minutes")
        lines.append("")
        
        severity_counts = summary['leaks_by_severity']
        lines.append("Severity Breakdown:")
        lines.append(f"  High:   {severity_counts['high']}")
        lines.append(f"  Medium: {severity_counts['medium']}")
        lines.append(f"  Low:    {severity_counts['low']}")
        lines.append("")
        
        if summary['leaks']:
            lines.append("Top Issues:")
            for i, leak in enumerate(summary['leaks'][:3], 1):
                lines.append(f"  {i}. {leak['title']} ({leak['severity']})")
                lines.append(f"     {leak['estimated_time_loss_minutes']:.1f} min loss")
        else:
            lines.append("No attention leaks detected! Great job! ✓")
        
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def generate_json_report(self, summary: Dict[str, Any]) -> str:
        """
        Save summary as JSON for programmatic access
        
        Args:
            summary: Summary dictionary from AttentionLeakDetector.generate_summary()
            
        Returns:
            Path to the generated JSON file
        """
        import json
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.output_dir, f'attention_leak_report_{timestamp}.json')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return report_path
    
    def get_latest_report(self) -> str:
        """Get path to the most recent report"""
        try:
            reports = list(Path(self.output_dir).glob('attention_leak_report_*.md'))
            if reports:
                return str(max(reports, key=os.path.getctime))
            return None
        except Exception:
            return None
