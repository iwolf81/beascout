#!/usr/bin/env python3
"""
Test Quality Debug Logging
Demonstrates the new quality debug logging functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.analysis.quality_scorer import UnitQualityScorer

def test_quality_debug():
    """Test quality debug logging with sample units"""
    
    # Sample units with different quality issues
    test_units = [
        {
            'unit_type': 'Pack',
            'unit_number': '0123', 
            'unit_town': 'Acton',
            'meeting_location': '123 Main St, Acton MA',
            'meeting_day': 'Tuesday',
            'meeting_time': '7:00 PM',
            'contact_email': 'pack123acton@gmail.com',
            'contact_person': 'John Smith',
            'phone_number': '508-555-1234',
            'quality_flags': ['QUALITY_ADDRESS_EMPTY']  # Address found in description
        },
        {
            'unit_type': 'Troop',
            'unit_number': '0456',
            'unit_town': 'Bedford', 
            'meeting_location': 'PO Box 123, Bedford MA',  # PO Box issue
            'meeting_day': 'Monday',
            'contact_email': 'john.smith@gmail.com'  # Personal email issue
            # Missing time, person, phone, website, description
        },
        {
            'unit_type': 'Crew',
            'unit_number': '0789',
            'unit_town': 'Concord',
            'contact_email': 'crew789@venturing.org'
            # Missing location, day, time, specialty, plus recommended fields
        },
        {
            'unit_type': 'Pack',
            'unit_number': '0999',
            'unit_town': 'Lexington',
            'meeting_location': 'Lexington Community Center, 123 Oak St, Lexington MA',
            'meeting_day': 'Thursday',
            'meeting_time': '6:30 PM',
            'contact_email': 'pack999lexington@gmail.com',
            'contact_person': 'Jane Doe',
            'phone_number': '781-555-9999',
            'website': 'pack999lexington.org',
            'description': 'Active Cub Scout Pack meeting Thursdays 6:30-8:00 PM'
            # This should be a high-scoring unit (A or B grade)
        }
    ]
    
    scorer = UnitQualityScorer()
    
    print("Testing quality debug logging...")
    print("=" * 50)
    
    for i, unit in enumerate(test_units, 1):
        score, recommendations = scorer.score_unit(unit)
        grade = scorer.get_letter_grade(score)
        
        print(f"Unit {i}: {unit.get('unit_type')} {unit.get('unit_number')} ({unit.get('unit_town')})")
        print(f"  Score: {score:.1f} (Grade: {grade})")
        print(f"  Issues: {len(recommendations)} recommendations")
        if recommendations:
            print(f"  Flags: {', '.join(recommendations[:3])}{'...' if len(recommendations) > 3 else ''}")
        print()
    
    print("Quality debug log created in data/debug/")
    print("Check the latest quality_debug_YYYYMMDD_HHMMSS.log file")
    print()
    print("Log format matches unit_identifier_debug but shows:")
    print("- unit_type, unit_number, unit_town (for identification)")  
    print("- score and grade (for quality assessment)")
    print("- quality_flags (all recommendations for manual review)")

if __name__ == "__main__":
    test_quality_debug()