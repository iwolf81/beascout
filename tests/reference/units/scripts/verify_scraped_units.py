#!/usr/bin/env python3
"""
Verification script for scraped HTML unit data processing

Compares current pipeline results against reference data to identify regressions.
Run this script after making code changes to ensure unit extraction hasn't broken.

Usage:
    python3 tests/reference/units/scripts/verify_scraped_units.py

The script will:
1. Run the pipeline on reference input data
2. Compare results against reference output files
3. Report any discrepancies found
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def run_pipeline_on_reference_data():
    """Run the full pipeline on reference input data"""
    print("🔧 Running pipeline on reference data...")
    
    # Use reference input data
    reference_input = "tests/reference/units/input"
    
    try:
        # Run the processing pipeline
        cmd = f'python3 src/scripts/process_full_dataset_v2.py {reference_input}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ Pipeline execution failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
        print("✅ Pipeline completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Pipeline execution timed out")
        return False
    except Exception as e:
        print(f"❌ Pipeline execution error: {e}")
        return False

def find_latest_debug_files():
    """Find the most recent debug files generated"""
    debug_dir = Path("data/debug")
    
    # Find latest unit identifier debug file
    unit_files = list(debug_dir.glob("unit_identifier_debug_scraped_*.log"))
    unit_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest_unit_file = unit_files[0] if unit_files else None
    
    # Find latest discarded debug file  
    discarded_files = list(debug_dir.glob("discarded_unit_identifier_debug_scraped_*.log"))
    discarded_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest_discarded_file = discarded_files[0] if discarded_files else None
    
    return latest_unit_file, latest_discarded_file

def compare_debug_files():
    """Compare generated debug files against reference files"""
    print("🔍 Comparing debug files against reference...")
    
    # Get latest generated files
    latest_unit_file, latest_discarded_file = find_latest_debug_files()
    
    if not latest_unit_file or not latest_discarded_file:
        print("❌ Could not find generated debug files")
        return False
    
    # Reference files
    ref_unit_file = Path("tests/reference/units/unit_identifier_debug_scraped_reference_u.log")
    ref_discarded_file = Path("tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log")
    
    success = True
    
    # Compare unit identifier debug files
    print(f"Comparing unit identifiers: {latest_unit_file.name} vs reference")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_file:
        # Sort current file for comparison
        subprocess.run(f'sort -u {latest_unit_file} > {temp_file.name}', shell=True)
        
        # Compare files
        diff_result = subprocess.run(
            f'diff {ref_unit_file} {temp_file.name}', 
            shell=True, capture_output=True, text=True
        )
        
        if diff_result.returncode == 0:
            print("  ✅ Unit identifier debug files match reference")
        else:
            print("  ❌ Unit identifier debug files differ from reference:")
            print(diff_result.stdout[:1000] + "..." if len(diff_result.stdout) > 1000 else diff_result.stdout)
            success = False
        
        os.unlink(temp_file.name)
    
    # Compare discarded debug files
    print(f"Comparing discarded units: {latest_discarded_file.name} vs reference")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_file:
        # Sort current file for comparison
        subprocess.run(f'sort -u {latest_discarded_file} > {temp_file.name}', shell=True)
        
        # Compare files
        diff_result = subprocess.run(
            f'diff {ref_discarded_file} {temp_file.name}', 
            shell=True, capture_output=True, text=True
        )
        
        if diff_result.returncode == 0:
            print("  ✅ Discarded units debug files match reference")
        else:
            print("  ❌ Discarded units debug files differ from reference:")
            print(diff_result.stdout[:1000] + "..." if len(diff_result.stdout) > 1000 else diff_result.stdout)
            success = False
        
        os.unlink(temp_file.name)
    
    return success

def verify_critical_units():
    """Verify that critical units are correctly processed"""
    print("🎯 Verifying critical units...")
    
    latest_unit_file, _ = find_latest_debug_files()
    if not latest_unit_file:
        return False
    
    critical_tests = [
        {
            'description': 'Troop 7012 should be in Acton (not Boxborough)',
            'pattern': "unit_type: 'Troop',   unit_number: '7012',   unit_town: 'Acton'",
            'should_exist': True
        },
        {
            'description': 'Troop 7012 should NOT be in Boxborough', 
            'pattern': "unit_type: 'Troop',   unit_number: '7012',   unit_town: 'Boxborough'",
            'should_exist': False
        },
        {
            'description': 'Post 1872 should be filtered out (Franklin Fire Dept is non-HNE)',
            'pattern': "unit_type: 'Post',   unit_number: '1872'",
            'should_exist': False
        }
    ]
    
    success = True
    with open(latest_unit_file, 'r') as f:
        content = f.read()
    
    for test in critical_tests:
        found = test['pattern'] in content
        if test['should_exist'] and not found:
            print(f"  ❌ {test['description']}")
            print(f"     Expected to find: {test['pattern']}")
            success = False
        elif not test['should_exist'] and found:
            print(f"  ❌ {test['description']}")
            print(f"     Should NOT have found: {test['pattern']}")
            success = False
        else:
            print(f"  ✅ {test['description']}")
    
    return success

def main():
    """Main verification workflow"""
    print("=" * 60)
    print("🛡️  SCRAPED UNITS VERIFICATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ensure we're in the project root
    if not os.path.exists("src/scripts/process_full_dataset_v2.py"):
        print("❌ Must run from project root directory")
        sys.exit(1)
    
    success = True
    
    # Step 1: Run pipeline
    if not run_pipeline_on_reference_data():
        success = False
    else:
        # Step 2: Compare debug files
        if not compare_debug_files():
            success = False
        
        # Step 3: Verify critical units
        if not verify_critical_units():
            success = False
    
    # Final result
    print()
    print("=" * 60)
    if success:
        print("✅ ALL VERIFICATION TESTS PASSED")
        print("   Code changes have not broken scraped unit processing")
    else:
        print("❌ VERIFICATION FAILED")  
        print("   Code changes may have introduced regressions")
        print("   Review the differences above and fix issues")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()