"""
Quick validation script to check if all modules can be imported
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Validating Attention Leak Detector Implementation...")
print("=" * 60)

try:
    print("\n1. Testing attention_leak_detector.py import...")
    from attention_leak_detector import AttentionLeakDetector, FileActivity, AttentionLeak
    print("   ✓ attention_leak_detector imports successfully")
    
    print("\n2. Testing attention_report_generator.py import...")
    from attention_report_generator import AttentionReportGenerator
    print("   ✓ attention_report_generator imports successfully")
    
    print("\n3. Testing attention_scheduler.py import...")
    from attention_scheduler import AttentionLeakScheduler
    print("   ✓ attention_scheduler imports successfully")
    
    print("\n4. Testing gui_controller.py import...")
    from gui_controller import GUIEngineController
    print("   ✓ gui_controller imports successfully")
    
    print("\n5. Testing gui_dashboard.py import...")
    from gui_dashboard import AutomationDashboard
    print("   ✓ gui_dashboard imports successfully")
    
    print("\n6. Creating test instances...")
    detector = AttentionLeakDetector(data_file="logs/test_tracker.json")
    print("   ✓ AttentionLeakDetector instantiated")
    
    generator = AttentionReportGenerator(output_dir="logs/test_reports")
    print("   ✓ AttentionReportGenerator instantiated")
    
    print("\n7. Testing basic functionality...")
    stats = detector.get_stats()
    print(f"   ✓ Detector stats: {stats}")
    
    print("\n" + "=" * 60)
    print("✅ ALL VALIDATION CHECKS PASSED!")
    print("=" * 60)
    print("\nThe Attention Leak Detector is ready to use.")
    print("\nTo start using:")
    print("  1. Run: python main_gui.py")
    print("  2. Click 'Start Engine'")
    print("  3. Click '🧠 Attention Insights'")
    print("\nOr run the demo: python demo_attention_detector.py")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
