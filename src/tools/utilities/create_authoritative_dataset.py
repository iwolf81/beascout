#!/usr/bin/env python3
"""
Create Authoritative 169-Unit Dataset
Use Key Three database as definitive source of HNE units
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import district assignment function
from src.mapping.district_mapping import get_district_for_town

def normalize_identifier(identifier):
    """Normalize identifier for consistent comparison"""
    import re
    
    # Extract components
    match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)\s+(.+)', identifier)
    if match:
        unit_type = match.group(1)
        unit_number = match.group(2).lstrip('0') or '0'  # Remove leading zeros for standard format
        rest = match.group(3)
        
        # Normalize spaces around hyphens
        rest = re.sub(r'\s*-\s*', '-', rest)
        
        return f"{unit_type} {unit_number} {rest}"
    
    return identifier

def create_flexible_lookup(units):
    """Create lookup that can match both with and without leading zeros"""
    lookup = {}
    for unit in units:
        if unit.get('primary_identifier'):
            # Store with both formats
            normalized = normalize_identifier(unit['primary_identifier'])
            lookup[normalized] = unit
            
            # Also store with zero-padded version for flexibility
            import re
            match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)\s+(.+)', normalized)
            if match:
                unit_type = match.group(1)
                unit_number = match.group(2).zfill(4)  # Add leading zeros
                rest = match.group(3)
                padded_key = f"{unit_type} {unit_number} {rest}"
                lookup[padded_key] = unit
    return lookup

def create_authoritative_dataset():
    """Create dataset with exactly 169 units based on Key Three database"""
    
    # Load Key Three parsed units (definitive source)
    key_three_file = "data/raw/key_three_parsed_units.json"
    try:
        with open(key_three_file, 'r') as f:
            key_three_data = json.load(f)
        key_three_units = key_three_data.get('parsed_units', [])
        print(f"Loaded {len(key_three_units)} Key Three units (definitive)")
    except FileNotFoundError:
        print(f"Error: Could not find Key Three data at {key_three_file}")
        return
    
    # Load scraped data
    scraped_file = "data/raw/all_units_comprehensive_scored.json"
    try:
        with open(scraped_file, 'r') as f:
            scraped_data = json.load(f)
        scraped_units = scraped_data.get('units_with_scores', [])
        print(f"Loaded {len(scraped_units)} scraped units")
    except FileNotFoundError:
        print(f"Error: Could not find scraped data at {scraped_file}")
        return
    
    # Create flexible lookup for scraped units that handles both formats
    scraped_lookup = create_flexible_lookup(scraped_units)
    
    # Build authoritative dataset
    authoritative_units = []
    matched_count = 0
    missing_count = 0
    
    for i, key_three_unit in enumerate(key_three_units):
        primary_id = key_three_unit.get('primary_identifier', '')
        normalized_id = normalize_identifier(primary_id)
        
        if normalized_id in scraped_lookup:
            # Use scraped data (has quality scores)
            scraped_unit = scraped_lookup[normalized_id].copy()
            scraped_unit['index'] = i
            scraped_unit['data_source'] = 'Web Scraped'
            authoritative_units.append(scraped_unit)
            matched_count += 1
        else:
            # Create missing unit with 0 score - use standard format (no leading zeros)
            normalized_primary_id = normalize_identifier(primary_id)
            missing_unit = {
                'index': i,
                'primary_identifier': normalized_primary_id,
                'unit_type': key_three_unit['unit_type'],
                'unit_number': key_three_unit['unit_number'].lstrip('0') or '0',  # Standard format without leading zeros
                'unit_town': key_three_unit['town'],
                'chartered_organization': f"{key_three_unit['town']}-{key_three_unit['chartered_org']}",
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
                'district': get_district_for_town(key_three_unit['town']),
                'data_source': 'Key Three Only',
                'completeness_score': 0,
                'completeness_grade': 'F',
                'recommendations': ['MISSING_FROM_WEB']
            }
            authoritative_units.append(missing_unit)
            missing_count += 1
    
    print(f"\n📊 Authoritative Dataset Construction:")
    print(f"   Key Three units: {len(key_three_units)}")
    print(f"   Matched with web data: {matched_count}")
    print(f"   Missing from web: {missing_count}")
    print(f"   Total authoritative units: {len(authoritative_units)}")
    
    # Calculate final statistics
    grade_summary = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    total_score = 0
    district_summary = {}
    
    for unit in authoritative_units:
        # Grade summary
        grade = unit.get('completeness_grade', 'F')
        if grade in grade_summary:
            grade_summary[grade] += 1
        total_score += unit.get('completeness_score', 0)
        
        # District summary
        district = unit.get('district', 'Unknown')
        if district not in district_summary:
            district_summary[district] = 0
        district_summary[district] += 1
    
    # Calculate average score
    average_score = round(total_score / len(authoritative_units), 1) if authoritative_units else 0
    
    # Create final authoritative dataset
    authoritative_data = {
        'total_units': len(authoritative_units),
        'scraped_units': matched_count,
        'key_three_only_units': missing_count,
        'scoring_summary': grade_summary,
        'district_summary': district_summary,
        'average_score': average_score,
        'units_with_scores': authoritative_units
    }
    
    # Save authoritative dataset
    authoritative_file = 'data/raw/all_units_authoritative_final.json'
    with open(authoritative_file, 'w') as f:
        json.dump(authoritative_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Authoritative dataset saved to: {authoritative_file}")
    print(f"   Total units: {len(authoritative_units)} (matches Key Three exactly)")
    print(f"   Web scraped: {matched_count} units")
    print(f"   Missing from web: {missing_count} units")
    print(f"   Average score: {average_score}%")
    print(f"   Grade distribution: {grade_summary}")
    print(f"   District distribution: {district_summary}")
    
    return authoritative_data

if __name__ == '__main__':
    print("Creating authoritative 169-unit dataset based on Key Three...")
    auth_data = create_authoritative_dataset()
    
    if auth_data:
        print("\n🎯 Final Authoritative Dataset:")
        print(f"   Expected (Key Three): 169 units")
        print(f"   Authoritative dataset: {auth_data['total_units']} units")
        
        if auth_data['total_units'] == 169:
            print("✅ Perfect match - dataset contains exactly 169 units from Key Three!")
        else:
            print(f"❌ Unexpected count - difference: {169 - auth_data['total_units']} units")
    else:
        print("❌ Failed to create authoritative dataset")