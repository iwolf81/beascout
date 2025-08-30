#!/usr/bin/env python3
"""
Verification script for Key Three data processing

Compares current Key Three parsing results against reference data.
Run this script after making changes to Key Three parsing logic.

Usage:
    python3 tests/reference/key_three/scripts/verify_key_three.py

The script will:
1. Parse the reference Key Three Excel file
2. Compare results against reference JSON output
3. Report any discrepancies found
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    from src.parsing.key_three_parser import KeyThreeParser
except ImportError:
    print("❌ Could not import KeyThreeParser")
    sys.exit(1)

def parse_reference_excel():
    """Parse the reference Key Three Excel file"""
    print("🔧 Parsing reference Key Three Excel file...")
    
    excel_path = Path("tests/reference/key_three/input/HNE_key_three.xlsx")
    if not excel_path.exists():
        print(f"❌ Reference Excel file not found: {excel_path}")
        return None
    
    try:
        parser = KeyThreeParser()
        result = parser.parse_excel_file(str(excel_path))
        print(f"✅ Successfully parsed {len(result.get('units', []))} units from Excel")
        return result
    except Exception as e:
        print(f"❌ Failed to parse Excel file: {e}")
        return None

def load_reference_json():
    """Load the reference JSON output"""
    print("📄 Loading reference JSON output...")
    
    json_path = Path("tests/reference/key_three/HNE_key_three.json")
    if not json_path.exists():
        print(f"❌ Reference JSON file not found: {json_path}")
        return None
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"✅ Successfully loaded reference JSON with {len(data.get('units', []))} units")
        return data
    except Exception as e:
        print(f"❌ Failed to load reference JSON: {e}")
        return None

def compare_unit_data(current_data, reference_data):
    """Compare current parsing results with reference data"""
    print("🔍 Comparing parsed data against reference...")
    
    current_units = current_data.get('units', [])
    reference_units = reference_data.get('units', [])
    
    success = True
    
    # Check unit counts
    if len(current_units) != len(reference_units):
        print(f"❌ Unit count mismatch: current={len(current_units)}, reference={len(reference_units)}")
        success = False
    else:
        print(f"✅ Unit count matches: {len(current_units)} units")
    
    # Create lookup dictionaries for comparison
    current_lookup = {}
    reference_lookup = {}
    
    for unit in current_units:
        key = f"{unit.get('unit_type', '')} {unit.get('unit_number', '')}"
        current_lookup[key] = unit
    
    for unit in reference_units:
        key = f"{unit.get('unit_type', '')} {unit.get('unit_number', '')}"
        reference_lookup[key] = unit
    
    # Check for missing units
    missing_units = set(reference_lookup.keys()) - set(current_lookup.keys())
    extra_units = set(current_lookup.keys()) - set(reference_lookup.keys())
    
    if missing_units:
        print(f"❌ Missing units in current data: {sorted(missing_units)}")
        success = False
    
    if extra_units:
        print(f"❌ Extra units in current data: {sorted(extra_units)}")
        success = False
    
    if not missing_units and not extra_units:
        print("✅ All expected units present")
    
    # Compare unit details for common units
    common_units = set(current_lookup.keys()) & set(reference_lookup.keys())
    field_mismatches = 0
    
    critical_fields = [
        'unit_type', 'unit_number', 'unit_town', 'chartered_organization',
        'contact_email', 'meeting_day', 'meeting_time'
    ]
    
    for unit_key in sorted(common_units)[:5]:  # Check first 5 units in detail
        current_unit = current_lookup[unit_key]
        reference_unit = reference_lookup[unit_key]
        
        for field in critical_fields:
            current_value = current_unit.get(field, '')
            reference_value = reference_unit.get(field, '')
            
            if current_value != reference_value:
                print(f"❌ {unit_key} field '{field}': current='{current_value}', reference='{reference_value}'")
                field_mismatches += 1
                success = False
    
    if field_mismatches == 0:
        print("✅ Unit field values match reference data")
    
    return success

def verify_critical_parsing():
    """Verify that critical parsing logic works correctly"""
    print("🎯 Verifying critical Key Three parsing logic...")
    
    # Parse fresh data
    current_data = parse_reference_excel()
    if not current_data:
        return False
    
    success = True
    units = current_data.get('units', [])
    
    # Test cases for critical parsing logic
    critical_tests = [
        {
            'description': 'Should parse unit types correctly',
            'test': lambda: len([u for u in units if u.get('unit_type') in ['Pack', 'Troop', 'Crew', 'Ship', 'Post', 'Club']]) > 0
        },
        {
            'description': 'Should normalize unit numbers (remove leading zeros)',
            'test': lambda: not any(u.get('unit_number', '').startswith('0') and len(u.get('unit_number', '')) > 1 for u in units)
        },
        {
            'description': 'Should extract contact emails',
            'test': lambda: len([u for u in units if '@' in u.get('contact_email', '')]) > 10
        },
        {
            'description': 'Should parse meeting days', 
            'test': lambda: len([u for u in units if u.get('meeting_day')]) > 5
        }
    ]
    
    for test in critical_tests:
        try:
            if test['test']():
                print(f"  ✅ {test['description']}")
            else:
                print(f"  ❌ {test['description']}")
                success = False
        except Exception as e:
            print(f"  ❌ {test['description']} (error: {e})")
            success = False
    
    return success

def main():
    """Main verification workflow"""
    print("=" * 60)
    print("🗝️  KEY THREE DATA VERIFICATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ensure we're in the project root
    if not os.path.exists("tests/reference/key_three/input/HNE_key_three.xlsx"):
        print("❌ Reference Key Three files not found")
        print("   Make sure to run this from project root directory")
        sys.exit(1)
    
    success = True
    
    # Step 1: Parse current data
    current_data = parse_reference_excel()
    if not current_data:
        success = False
    else:
        # Step 2: Load reference data
        reference_data = load_reference_json()
        if not reference_data:
            success = False
        else:
            # Step 3: Compare data
            if not compare_unit_data(current_data, reference_data):
                success = False
    
        # Step 4: Verify critical parsing
        if not verify_critical_parsing():
            success = False
    
    # Final result
    print()
    print("=" * 60)
    if success:
        print("✅ ALL KEY THREE VERIFICATION TESTS PASSED")
        print("   Key Three parsing is working correctly")
    else:
        print("❌ KEY THREE VERIFICATION FAILED")
        print("   Key Three parsing may have regressions")
        print("   Review the differences above and fix issues")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()