#!/usr/bin/env python3
"""
Debug Key Three Contact Matching Issues
Analyze why many units are missing Key Three contact information
"""

import pandas as pd
import json
import re

def normalize_unit_identifier(identifier: str) -> str:
    """Normalize unit identifier for matching - same logic as report generator"""
    if not identifier:
        return ""
    
    # Remove extra spaces and standardize
    normalized = re.sub(r'\s+', ' ', identifier.strip())
    
    # Remove gender indicators like "(F)", "(B)", "(G)" and associated dashes/spaces
    normalized = re.sub(r'\s*\([FBG]\)\s*-?\s*', ' ', normalized)
    
    # Remove Crew specialty information (everything after "Specialty:")
    if 'Specialty:' in normalized:
        normalized = normalized.split('Specialty:')[0].strip()
    
    # Clean up multiple spaces that may result from the above
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def debug_key_three_matching():
    """Debug Key Three matching issues"""
    
    # Load authoritative dataset
    with open('data/raw/all_units_authoritative_final.json', 'r') as f:
        auth_data = json.load(f)
    units = auth_data['units_with_scores']
    
    # Load Key Three data
    key_three_df = pd.read_excel('data/input/Key 3 08-22-2025.xlsx', header=None, skiprows=3)
    key_three_df.columns = ['district', 'unit_id', 'fullname', 'address', 'citystate', 'zipcode', 
                           'email', 'phone', 'position', 'unitcommorgname', 'status']
    key_three_df = key_three_df[key_three_df['status'] == 'ACTIVE']
    
    print(f"Units in authoritative dataset: {len(units)}")
    print(f"Active Key Three records: {len(key_three_df)}")
    
    # Check matching for first 10 units
    print("\n🔍 Debugging Key Three Matching:")
    
    matches_found = 0
    no_matches = 0
    
    for i, unit in enumerate(units[:15]):
        primary_id = unit.get('primary_identifier', '')
        normalized_unit = normalize_unit_identifier(primary_id)
        
        print(f"\n{i+1}. {primary_id}")
        print(f"   Normalized: {normalized_unit}")
        
        # Find matches
        unit_matches = []
        for _, row in key_three_df.iterrows():
            org_name = str(row['unitcommorgname']).strip()
            normalized_org = normalize_unit_identifier(org_name)
            
            if normalized_org == normalized_unit:
                unit_matches.append({
                    'name': row['fullname'],
                    'email': row['email'],
                    'original': org_name
                })
        
        if unit_matches:
            print(f"   ✅ Found {len(unit_matches)} Key Three contacts:")
            for match in unit_matches[:2]:
                print(f"      - {match['name']} ({match['email']})")
                print(f"        From: {match['original']}")
            matches_found += 1
        else:
            print(f"   ❌ No Key Three contacts found")
            
            # Try to find potential matches by looking for similar entries
            unit_type = unit.get('unit_type', '')
            unit_number = unit.get('unit_number', '').lstrip('0')
            unit_town = unit.get('unit_town', '')
            
            potential_matches = []
            for _, row in key_three_df.iterrows():
                org_name = str(row['unitcommorgname']).strip()
                if (unit_type.lower() in org_name.lower() and 
                    unit_number in org_name and
                    unit_town.lower() in org_name.lower()):
                    potential_matches.append(org_name)
            
            if potential_matches:
                print(f"   🔍 Potential matches found:")
                for pot in potential_matches[:2]:
                    print(f"      - {pot}")
                    print(f"        Normalized: {normalize_unit_identifier(pot)}")
            
            no_matches += 1
    
    print(f"\n📊 Summary of first 15 units:")
    print(f"   Matches found: {matches_found}")
    print(f"   No matches: {no_matches}")
    print(f"   Match rate: {matches_found/15*100:.1f}%")
    
    # Check if there are common patterns in non-matching identifiers
    print(f"\n🔍 Analyzing Key Three database entries:")
    sample_entries = key_three_df['unitcommorgname'].unique()[:10]
    for entry in sample_entries:
        print(f"   Original: {entry}")
        print(f"   Normalized: {normalize_unit_identifier(entry)}")
        print()

if __name__ == '__main__':
    debug_key_three_matching()