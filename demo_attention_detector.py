"""
Attention Leak Detector - Demo Script
Demonstrates the core functionality of the attention leak detector
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from attention_leak_detector import AttentionLeakDetector
from attention_report_generator import AttentionReportGenerator


def demo_attention_leak_detector():
    """
    Demonstrate the Attention Leak Detector functionality
    """
    print("=" * 70)
    print("🧠 ATTENTION LEAK DETECTOR - DEMO")
    print("=" * 70)
    print()
    
    # Create detector instance
    print("1️⃣ Initializing Attention Leak Detector...")
    detector = AttentionLeakDetector(data_file="logs/demo_attention_tracker.json")
    print("✓ Detector initialized")
    print()
    
    # Simulate file tracking
    print("2️⃣ Simulating file activity tracking...")
    
    # Create some test scenarios
    test_files = [
        # Cold files (never accessed)
        ("C:/Users/Demo/Downloads/never_opened_1.pdf", False),
        ("C:/Users/Demo/Downloads/never_opened_2.pdf", False),
        ("C:/Users/Demo/Downloads/never_opened_3.pdf", False),
        
        # Accessed files (normal behavior)
        ("C:/Users/Demo/Downloads/opened_document.pdf", True),
        ("C:/Users/Demo/Documents/active_project.docx", True),
        
        # Small files (micro-clutter)
        *[(f"C:/Users/Demo/Desktop/note_{i}.txt", False) for i in range(55)],
    ]
    
    # Track file creation
    for file_path, should_access in test_files:
        detector.track_file_created(file_path)
        if should_access:
            detector.track_file_accessed(file_path)
    
    print(f"✓ Tracked {len(test_files)} files")
    print()
    
    # Simulate folder switching
    print("3️⃣ Simulating folder navigation...")
    folders = [
        "C:/Users/Demo/Downloads",
        "C:/Users/Demo/Documents",
        "C:/Users/Demo/Desktop",
        "C:/Users/Demo/Pictures",
        "C:/Users/Demo/Downloads",
        "C:/Users/Demo/Music",
        "C:/Users/Demo/Videos",
        "C:/Users/Demo/Desktop",
        "C:/Users/Demo/Downloads",
        "C:/Users/Demo/Documents",
        "C:/Users/Demo/Desktop",
        "C:/Users/Demo/Downloads",
    ]
    
    for folder in folders:
        detector._track_folder_switch(folder)
        time.sleep(0.1)  # Simulate time between switches
    
    print(f"✓ Simulated {len(folders)} folder switches")
    print()
    
    # Run analysis
    print("4️⃣ Running attention leak analysis...")
    summary = detector.generate_summary()
    print("✓ Analysis complete")
    print()
    
    # Display results
    print("=" * 70)
    print("📊 ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    print(f"Total Leaks Detected: {summary['total_leaks_detected']}")
    print(f"Estimated Time Loss: {summary['total_estimated_time_loss_minutes']:.1f} minutes")
    print(f"Files Tracked: {summary['total_files_tracked']}")
    print()
    
    # Severity breakdown
    severity = summary['leaks_by_severity']
    print("Severity Breakdown:")
    print(f"  🔴 High:   {severity['high']}")
    print(f"  🟡 Medium: {severity['medium']}")
    print(f"  🟢 Low:    {severity['low']}")
    print()
    
    # Show detected leaks
    if summary['leaks']:
        print("=" * 70)
        print("🔍 DETECTED ATTENTION LEAKS")
        print("=" * 70)
        print()
        
        for i, leak in enumerate(summary['leaks'], 1):
            severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(leak['severity'], '⚪')
            type_icon = {
                'cold_files': '❄️',
                'duplicate_downloads': '📥',
                'micro_clutter': '🗂️',
                'context_switching': '🔄',
                'orphaned_folders': '📁'
            }.get(leak['leak_type'], '⚠️')
            
            print(f"{i}. {type_icon} {leak['title']}")
            print(f"   Severity: {severity_icon} {leak['severity'].upper()}")
            print(f"   Time Loss: {leak['estimated_time_loss_minutes']:.1f} minutes")
            print()
            print(f"   {leak['description']}")
            print()
            print(f"   💡 Suggestion: {leak['suggestion']}")
            print()
            print("-" * 70)
            print()
    
    # Generate report
    print("5️⃣ Generating report...")
    generator = AttentionReportGenerator(output_dir="logs/demo_reports")
    report_path = generator.generate_markdown_report(summary)
    print(f"✓ Report saved to: {report_path}")
    print()
    
    # Show text summary
    print("=" * 70)
    print("📄 TEXT SUMMARY")
    print("=" * 70)
    print()
    text_summary = generator.generate_text_summary(summary)
    print(text_summary)
    print()
    
    # Cleanup demo data
    print("6️⃣ Cleaning up demo data...")
    try:
        if os.path.exists("logs/demo_attention_tracker.json"):
            os.remove("logs/demo_attention_tracker.json")
        print("✓ Demo data cleaned up")
    except Exception as e:
        print(f"⚠ Could not clean up: {e}")
    
    print()
    print("=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print()
    print("This demo showed how the Attention Leak Detector:")
    print("  • Tracks file creation and access events")
    print("  • Detects patterns like cold files and micro-clutter")
    print("  • Monitors folder navigation for context switching")
    print("  • Calculates time loss estimates")
    print("  • Generates actionable insights and reports")
    print()
    print("To use with real data:")
    print("  1. Start the automation engine")
    print("  2. Let it run for a few days to gather data")
    print("  3. Click '🧠 Attention Insights' in the GUI")
    print("  4. Review and act on the recommendations")
    print()


if __name__ == "__main__":
    try:
        demo_attention_leak_detector()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
