#!/usr/bin/env python3
"""
Test Key Three Parser Debug Logging
Generates debug logs for Key Three spreadsheet parsing
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.parsing.key_three_parser import KeyThreeParser

def test_key_three_parsing():
    """Test Key Three parsing with debug logging"""
    
    # Look for Key Three Excel files
    key_three_files = [
        "data/input/Key 3 08-22-2025.xlsx",
        "data/input/Key_3_08-22-2025_original.xlsx",
        "data/input/Key_3_08-22-2025.csv"  # If CSV format
    ]
    
    key_three_file = None
    for file_path in key_three_files:
        if Path(file_path).exists():
            key_three_file = file_path
            break
    
    if not key_three_file:
        print("❌ No Key Three input file found. Looking for:")
        for file_path in key_three_files:
            print(f"   {file_path}")
        return
    
    print(f"📊 Testing Key Three parser with: {key_three_file}")
    
    try:
        # Parse Key Three data
        parser = KeyThreeParser(key_three_file)
        units = parser.parse_all_units()
        
        print(f"✅ Successfully parsed {len(units)} units from Key Three")
        print(f"📋 Debug logs generated in data/debug/ directory")
        
        # Show sample of parsed units
        print(f"\n📋 Sample units:")
        for i, unit in enumerate(units[:5]):
            print(f"   {i+1}. {unit.get('unit_key', 'N/A')} - {unit.get('district', 'N/A')}")
        
        if len(units) > 5:
            print(f"   ... and {len(units) - 5} more units")
            
    except Exception as e:
        print(f"❌ Error testing Key Three parser: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_key_three_parsing()