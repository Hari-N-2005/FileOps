"""
Attention Leak Scheduler
Runs periodic attention leak analysis and generates reports
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path


class AttentionLeakScheduler:
    """Schedules periodic attention leak analysis"""
    
    def __init__(self, detector, report_generator, 
                 interval_hours: int = 24, auto_report: bool = True, logger=None):
        """
        Initialize scheduler
        
        Args:
            detector: AttentionLeakDetector instance
            report_generator: AttentionReportGenerator instance
            interval_hours: Hours between analyses
            auto_report: Whether to automatically generate reports
            logger: Logger instance
        """
        self.detector = detector
        self.report_generator = report_generator
        self.interval_hours = interval_hours
        self.auto_report = auto_report
        self.logger = logger
        
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_analysis_time: Optional[datetime] = None
    
    def start(self) -> None:
        """Start the scheduler"""
        if self.running:
            if self.logger:
                self.logger.warning("Attention leak scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        if self.logger:
            self.logger.info(f"Attention leak scheduler started (interval: {self.interval_hours}h)")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        if self.logger:
            self.logger.info("Attention leak scheduler stopped")
    
    def _run_loop(self) -> None:
        """Main scheduler loop"""
        while self.running:
            try:
                # Check if it's time to run analysis
                if self._should_run_analysis():
                    self._run_analysis()
                    self.last_analysis_time = datetime.now()
                
                # Sleep for a while before checking again
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in attention leak scheduler: {e}", exc_info=True)
                time.sleep(60)  # Wait a minute before retrying
    
    def _should_run_analysis(self) -> bool:
        """Check if it's time to run analysis"""
        if not self.last_analysis_time:
            # Never run before, run now
            return True
        
        # Check if enough time has passed
        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last >= timedelta(hours=self.interval_hours)
    
    def _run_analysis(self) -> None:
        """Run the attention leak analysis"""
        try:
            if self.logger:
                self.logger.info("Running scheduled attention leak analysis...")
            
            # Run analysis
            leaks = self.detector.analyze_attention_leaks()
            
            if self.logger:
                self.logger.info(f"Analysis complete: {len(leaks)} leaks detected")
            
            # Generate report if enabled
            if self.auto_report:
                summary = self.detector.generate_summary()
                report_path = self.report_generator.generate_markdown_report(summary)
                
                if self.logger:
                    self.logger.info(f"Attention leak report generated: {report_path}")
                
                # Also generate text summary for log
                text_summary = self.report_generator.generate_text_summary(summary)
                if self.logger:
                    self.logger.info(f"\n{text_summary}")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to run scheduled analysis: {e}", exc_info=True)
    
    def force_analysis(self) -> None:
        """Force an immediate analysis"""
        if self.logger:
            self.logger.info("Forcing immediate attention leak analysis...")
        self._run_analysis()
        self.last_analysis_time = datetime.now()
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'interval_hours': self.interval_hours,
            'auto_report': self.auto_report,
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'next_analysis': (self.last_analysis_time + timedelta(hours=self.interval_hours)).isoformat()
                            if self.last_analysis_time else 'Pending'
        }
