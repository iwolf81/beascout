#!/usr/bin/env python3
"""
Create Complete Dataset with Missing Units
Combines scraped data with Key Three units (missing units get 0 scores)
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import district assignment function
from src.config.district_mapping import get_district_for_town

def create_complete_dataset():
    """Create complete dataset by adding missing Key Three units with 0 scores"""
    
    # Load scraped data
    scraped_file = "data/raw/all_units_comprehensive_scored.json"
    try:
        with open(scraped_file, 'r') as f:
            scraped_data = json.load(f)
        scraped_units = scraped_data.get('units_with_scores', [])
        print(f"Loaded {len(scraped_units)} scraped units")
    except FileNotFoundError:
        print(f"Error: Could not find scraped data file at {scraped_file}")
        return
    
    # Load Key Three comparison data
    comparison_file = "data/raw/key_three_comparison.json"
    try:
        with open(comparison_file, 'r') as f:
            comparison_data = json.load(f)
        missing_unit_records = comparison_data.get('missing_unit_records', [])
        print(f"Found {len(missing_unit_records)} missing units from Key Three")
    except FileNotFoundError:
        print(f"Error: Could not find comparison data file at {comparison_file}")
        return
    
    # Create complete dataset by combining scraped + missing units
    complete_units = scraped_units.copy()
    
    # Add missing units with proper structure
    for missing_unit in missing_unit_records:
        # Create unit record matching scraped data structure
        unit_record = {
            'index': len(complete_units),
            'primary_identifier': missing_unit['primary_identifier'],
            'unit_type': missing_unit['unit_type'],
            'unit_number': missing_unit['unit_number'],
            'unit_town': missing_unit['unit_town'],
            'chartered_organization': f"{missing_unit['unit_town']}-{missing_unit['chartered_org']}",
            'specialty': '',
            'meeting_location': '',
            'meeting_day': '',
            'meeting_time': '',
            'contact_email': '',
            'contact_person': '',
            'phone_number': '',
            'website': '',
            'description': '',
            'unit_composition': '',
            'distance': '',
            'raw_content': '',
            'district': get_district_for_town(missing_unit['unit_town']),
            'data_source': 'Key Three Only',
            'completeness_score': 0,
            'completeness_grade': 'F',
            'recommendations': ['MISSING_FROM_WEB']
        }
        complete_units.append(unit_record)
    
    print(f"Created complete dataset with {len(complete_units)} total units")
    print(f"  - {len(scraped_units)} scraped from web")
    print(f"  - {len(missing_unit_records)} missing units from Key Three")
    
    # Recalculate summary statistics
    grade_summary = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    total_score = 0
    district_summary = {}
    
    for unit in complete_units:
        grade = unit.get('completeness_grade', 'F')
        if grade in grade_summary:
            grade_summary[grade] += 1
        total_score += unit.get('completeness_score', 0)
        
        # Track by district
        district = unit.get('district', 'Unknown')
        if district not in district_summary:
            district_summary[district] = 0
        district_summary[district] += 1
    
    # Calculate average score
    average_score = round(total_score / len(complete_units), 1) if complete_units else 0
    
    # Create complete dataset
    complete_data = {
        'total_units': len(complete_units),
        'scraped_units': len(scraped_units),
        'key_three_only_units': len(missing_unit_records),
        'scoring_summary': grade_summary,
        'district_summary': district_summary,
        'average_score': average_score,
        'units_with_scores': complete_units
    }
    
    # Save complete dataset
    complete_file = 'data/raw/all_units_complete_scored.json'
    with open(complete_file, 'w') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Complete dataset saved to: {complete_file}")
    print(f"   Total units: {len(complete_units)} (should match 169 Key Three units)")
    print(f"   Average score: {average_score}%")
    print(f"   Grade distribution: {grade_summary}")
    print(f"   District distribution: {district_summary}")
    
    return complete_data

if __name__ == '__main__':
    print("Creating complete dataset with missing units...")
    complete_data = create_complete_dataset()
    
    if complete_data:
        print("\n📊 Dataset Summary:")
        print(f"   Key Three Total: 169 units")
        print(f"   Complete Dataset: {complete_data['total_units']} units")
        
        if complete_data['total_units'] == 169:
            print("✅ Unit count matches Key Three database exactly!")
        else:
            print(f"❌ Unit count mismatch - difference: {169 - complete_data['total_units']}")
    else:
        print("❌ Failed to create complete dataset")