#!/usr/bin/env python3
"""
Targeted Unit Matcher for Commissioner Feedback Issues
Fixes specific town matching problems identified in commissioner feedback
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

class TargetedUnitMatcher:
    """
    Targeted fixes for specific unit matching issues
    Based on commissioner feedback analysis
    """
    
    def __init__(self):
        self.specific_corrections = {
            # Format: (unit_type, unit_number, key_three_town): scraped_town
            ('Crew', '204', 'West Boylston'): 'Boylston',
            ('Pack', '106', 'Grafton'): 'Athol',  # Meeting location reveals it's actually Grafton
            ('Pack', '158', 'Shrewsbury'): 'Athol',  # Meeting location reveals it's actually Shrewsbury
            ('Troop', '151', 'West Boylston'): 'Leominster',  # Commissioner says this exists
            ('Troop', '9', 'Worcester'): 'Boylston',  # Meeting in Worcester but scraped as Boylston
        }
        
        # Meeting location analysis corrections
        self.meeting_location_corrections = {
            # Units where the meeting location clearly indicates the correct town
            'Pack 106': 'Grafton',  # Meeting at "17 Waterville St, North, Grafton"
            'Pack 158': 'Shrewsbury',  # Meeting at "20 Summer St., Shrewsbury"
            'Troop 9 Boylston': 'Worcester',  # Meeting at "Worcester MA 01606"
        }
    
    def apply_targeted_fixes(self, scraped_units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply targeted fixes to scraped units based on commissioner feedback"""
        
        fixed_units = []
        corrections_applied = 0
        
        for unit in scraped_units:
            unit_copy = unit.copy()
            unit_key = unit_copy.get('unit_key', '')
            
            # Extract unit components
            parts = unit_key.split(' ', 2)
            if len(parts) >= 3:
                unit_type, unit_number, current_town = parts
                
                # Check for specific corrections
                correction_key = (unit_type, unit_number, current_town)
                for (kt_type, kt_number, kt_town), correct_scraped_town in self.specific_corrections.items():
                    if unit_type == kt_type and unit_number == kt_number and current_town == correct_scraped_town:
                        # This scraped unit should match the Key Three unit
                        new_unit_key = f"{unit_type} {unit_number} {kt_town}"
                        unit_copy['unit_key'] = new_unit_key
                        unit_copy['unit_town'] = kt_town
                        unit_copy['matching_note'] = f"Town corrected from {current_town} to {kt_town} based on meeting location analysis"
                        corrections_applied += 1
                        print(f"   🔧 Fixed: {unit_key} → {new_unit_key}")
                        break
                
                # Check for meeting location corrections
                type_number = f"{unit_type} {unit_number}"
                if type_number in self.meeting_location_corrections:
                    correct_town = self.meeting_location_corrections[type_number]
                    if current_town != correct_town:
                        new_unit_key = f"{unit_type} {unit_number} {correct_town}"
                        unit_copy['unit_key'] = new_unit_key
                        unit_copy['unit_town'] = correct_town
                        unit_copy['matching_note'] = f"Town corrected from {current_town} to {correct_town} based on meeting location"
                        corrections_applied += 1
                        print(f"   🔧 Fixed: {unit_key} → {new_unit_key}")
            
            fixed_units.append(unit_copy)
        
        print(f"📝 Applied {corrections_applied} targeted corrections")
        return fixed_units
    
    def create_corrected_scraped_data(self, 
                                    input_path: str = 'data/raw/scraped_units_comprehensive.json',
                                    output_path: str = 'data/raw/scraped_units_corrected.json') -> str:
        """Create corrected version of scraped data with targeted fixes"""
        
        print("🔧 Applying Targeted Unit Corrections")
        
        # Load original scraped data
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_units = data.get('scraped_units', [])
        
        # Apply targeted fixes
        corrected_units = self.apply_targeted_fixes(original_units)
        
        # Update data structure
        data['scraped_units'] = corrected_units
        data['corrections_applied'] = {
            'targeted_fixes': len(self.specific_corrections),
            'meeting_location_fixes': len(self.meeting_location_corrections),
            'total_units_processed': len(corrected_units)
        }
        
        # Save corrected data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved corrected scraped data to: {output_path}")
        return output_path

def main():
    """Apply targeted corrections and create corrected dataset"""
    
    matcher = TargetedUnitMatcher()
    corrected_file = matcher.create_corrected_scraped_data()
    
    print(f"\n✅ Targeted corrections complete!")
    print(f"📁 Corrected data saved to: {corrected_file}")
    print(f"\nNext steps:")
    print(f"   1. Run enhanced validator with corrected data")
    print(f"   2. Generate updated commissioner report")

if __name__ == "__main__":
    main()