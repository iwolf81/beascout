#!/usr/bin/env python3
"""
Filter HNE Units from Complete Dataset
Remove units that are clearly not in HNE Council territory
Note: Webster is a town in HNE, but Daniel Webster Council is a different scout council
"""

import json

def is_hne_unit(unit):
    """Determine if a unit belongs to HNE Council"""
    
    # Get unit identifiers
    primary_id = unit.get('primary_identifier', '')
    chartered_org = unit.get('chartered_organization', '')
    
    # Exclude units explicitly from other councils
    # Note: Webster is a town in HNE, but Daniel Webster Council is a different scout council
    other_councils = [
        'Daniel Webster Council',
        'Mohegan Council', 
        'Connecticut Council',
        'Pioneer Valley Council',
        'Yankee Council',
        'Knox Trail Council'
    ]
    
    for other_council in other_councils:
        if other_council in primary_id or other_council in chartered_org:
            return False
    
    # Include units explicitly marked as HNE
    if 'Heart of New England Council' in primary_id or 'Heart of New England Council' in chartered_org:
        return True
    
    # Include units that are in Key Three (data_source = Key Three Only)
    if unit.get('data_source') == 'Key Three Only':
        return True
    
    # For all other units, include them (conservative approach)
    # The Key Three database is our definitive source of what should be included
    return True

def filter_hne_units():
    """Filter complete dataset to include only HNE units"""
    
    # Load complete dataset
    complete_file = "data/raw/all_units_complete_scored.json"
    try:
        with open(complete_file, 'r') as f:
            complete_data = json.load(f)
        
        all_units = complete_data.get('units_with_scores', [])
        print(f"Loaded {len(all_units)} total units")
    except FileNotFoundError:
        print(f"Error: Could not find complete dataset at {complete_file}")
        return
    
    # Filter to HNE units only
    hne_units = []
    excluded_units = []
    
    for unit in all_units:
        if is_hne_unit(unit):
            hne_units.append(unit)
        else:
            excluded_units.append(unit)
    
    print(f"Filtered to {len(hne_units)} HNE units")
    print(f"Excluded {len(excluded_units)} non-HNE units")
    
    # Show excluded units for verification
    if excluded_units:
        print("\nExcluded units:")
        for unit in excluded_units:
            print(f"  - {unit.get('primary_identifier', 'Unknown')}")
    
    # Recalculate statistics for HNE-only dataset
    grade_summary = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    total_score = 0
    district_summary = {}
    scraped_count = 0
    key_three_only_count = 0
    
    for i, unit in enumerate(hne_units):
        # Update index
        unit['index'] = i
        
        # Count by source
        if unit.get('data_source') == 'Key Three Only':
            key_three_only_count += 1
        else:
            scraped_count += 1
        
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
    average_score = round(total_score / len(hne_units), 1) if hne_units else 0
    
    # Create final HNE dataset
    hne_data = {
        'total_units': len(hne_units),
        'scraped_units': scraped_count,
        'key_three_only_units': key_three_only_count,
        'scoring_summary': grade_summary,
        'district_summary': district_summary,
        'average_score': average_score,
        'units_with_scores': hne_units
    }
    
    # Save HNE-filtered dataset
    hne_file = 'data/raw/all_units_hne_final.json'
    with open(hne_file, 'w') as f:
        json.dump(hne_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ HNE-filtered dataset saved to: {hne_file}")
    print(f"   Total HNE units: {len(hne_units)}")
    print(f"   Scraped from web: {scraped_count}")
    print(f"   Key Three only: {key_three_only_count}")
    print(f"   Average score: {average_score}%")
    print(f"   District distribution: {district_summary}")
    
    return hne_data

if __name__ == '__main__':
    print("Filtering dataset to HNE units only...")
    hne_data = filter_hne_units()
    
    if hne_data:
        print("\n📊 Final Dataset Summary:")
        print(f"   Expected (Key Three): 169 units")
        print(f"   HNE-filtered dataset: {hne_data['total_units']} units")
        
        if hne_data['total_units'] == 169:
            print("✅ Unit count matches Key Three database exactly!")
        elif abs(hne_data['total_units'] - 169) <= 5:
            print(f"⚠️  Close match - difference: {169 - hne_data['total_units']} units")
        else:
            print(f"❌ Significant mismatch - difference: {169 - hne_data['total_units']} units")
    else:
        print("❌ Failed to filter HNE dataset")