#!/usr/bin/env python3
"""
Master Verification Script for BeAScout System

Runs all verification tests to ensure code changes don't break existing functionality.
This script should be run before committing changes or deploying updates.

Usage:
    python3 tests/verify_all.py [--quick]
    
Options:
    --quick     Run only critical verification tests (faster)
    
Exit Codes:
    0 - All tests passed
    1 - Some tests failed
    2 - Setup/configuration error
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def run_verification_script(script_path, description, quick_mode=False):
    """Run a verification script and return success status"""
    print(f"🔧 Running {description}...")
    
    if not os.path.exists(script_path):
        print(f"❌ Verification script not found: {script_path}")
        return False
    
    try:
        # Add --quick flag if in quick mode and script supports it
        cmd = f'python3 {script_path}'
        if quick_mode and '--quick' in open(script_path).read():
            cmd += ' --quick'
            
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=600
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def check_prerequisites():
    """Check that all required files and dependencies are available"""
    print("🔍 Checking prerequisites...")
    
    required_files = [
        "tests/reference/units/unit_identifier_debug_scraped_reference_u.log",
        "tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log", 
        "tests/reference/key_three/HNE_key_three.json",
        "tests/reference/key_three/input/HNE_key_three.xlsx",
        "src/scripts/process_full_dataset_v2.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nRun the setup commands from verification_tools.md first")
        return False
    
    print("✅ All prerequisite files found")
    return True

def main():
    """Main verification workflow"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', 
                       help='Run only critical verification tests (faster)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("🛡️  BEASCOUT SYSTEM VERIFICATION")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.quick:
        print("Mode: QUICK (critical tests only)")
    else:
        print("Mode: FULL (all verification tests)")
    print()
    
    # Ensure we're in the project root
    if not os.path.exists("src/scripts/process_full_dataset_v2.py"):
        print("❌ Must run from project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(2)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(2)
    
    # Define verification tests
    tests = [
        {
            'script': 'tests/reference/units/scripts/verify_scraped_units.py',
            'description': 'Scraped HTML Unit Data Processing',
            'critical': True
        },
        {
            'script': 'tests/reference/key_three/scripts/verify_key_three.py', 
            'description': 'Key Three Data Processing',
            'critical': False
        }
    ]
    
    # Filter tests based on mode
    if args.quick:
        tests = [t for t in tests if t['critical']]
    
    # Run verification tests
    results = []
    for test in tests:
        success = run_verification_script(
            test['script'], 
            test['description'],
            args.quick
        )
        results.append({
            'name': test['description'],
            'success': success
        })
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for result in results:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"   {result['name']:<40} {status}")
    
    print()
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("   Your code changes are safe to commit/deploy")
        exit_code = 0
    else:
        print("🚨 SOME VERIFICATION TESTS FAILED!")
        print("   Review the failures above and fix issues before committing")
        exit_code = 1
    
    print("=" * 70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()