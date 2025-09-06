#!/usr/bin/env python3
"""
Verify Key Three Contact Information in Reports
Check if missing units have proper contact information
"""

import json
import pandas as pd

def verify_key_three_contacts():
    """Verify Key Three contact information for missing units"""
    
    # Load the authoritative dataset
    with open('data/raw/all_units_authoritative_final.json', 'r') as f:
        data = json.load(f)
    
    units = data.get('units_with_scores', [])
    
    # Check for missing units (Key Three Only)
    missing_units = [unit for unit in units if unit.get('data_source') == 'Key Three Only']
    
    print(f"Found {len(missing_units)} units missing from web")
    print("Checking Key Three contact matching...")
    
    # Load Key Three data manually to verify matching
    df = pd.read_excel('data/input/Key 3 08-22-2025.xlsx', header=None, skiprows=3)
    df.columns = ['district', 'unit_id', 'fullname', 'address', 'citystate', 'zipcode', 
                 'email', 'phone', 'position', 'unitcommorgname', 'status']
    df = df[df['status'] == 'ACTIVE']
    
    print(f"Key Three database has {len(df)} active records")
    
    # Check a few examples
    sample_missing = missing_units[:5]
    for unit in sample_missing:
        identifier = unit.get('primary_identifier', '')
        print(f"\nChecking: {identifier}")
        
        # Find matching Key Three records
        matches = []
        for _, row in df.iterrows():
            org_name = str(row['unitcommorgname']).strip()
            # Simple check - just see if there are matches
            if identifier.replace(' ', '').lower() in org_name.replace(' ', '').lower() or \
               org_name.replace(' ', '').lower() in identifier.replace(' ', '').lower():
                matches.append({
                    'name': row['fullname'],
                    'position': row['position'],
                    'email': row['email'],
                    'unitcommorgname': org_name
                })
        
        if matches:
            print(f"  Found {len(matches)} Key Three contacts:")
            for match in matches[:3]:
                print(f"    - {match['name']} ({match['position']}) - {match['email']}")
        else:
            print(f"  ❌ No Key Three contacts found")
            
    return len(missing_units), len(df)

if __name__ == '__main__':
    missing_count, key_three_count = verify_key_three_contacts()
    print(f"\n📊 Summary:")
    print(f"   Missing from web: {missing_count} units")
    print(f"   Key Three records: {key_three_count} members")
    print(f"   Report should include Key Three contacts for missing units")