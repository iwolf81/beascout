#!/usr/bin/env python3
"""
Analyze Missing Units from Commissioner Feedback
Compare Key Three units vs scraped data to understand matching failures
"""

import json
import sys
from pathlib import Path

def load_data():
    """Load Key Three and scraped data"""
    with open('data/raw/key_three_foundation_units.json', 'r') as f:
        key_three_data = json.load(f)
    
    with open('data/raw/scraped_units_comprehensive.json', 'r') as f:
        scraped_data = json.load(f)
    
    return key_three_data['units'], scraped_data['scraped_units']

def analyze_commissioner_feedback_units():
    """Analyze the specific units mentioned in commissioner feedback"""
    
    # Units that commissioner says should be matched
    commissioner_units = [
        'Crew 204 West Boylston',
        'Pack 106 Grafton', 
        'Pack 148 East Brookfield',
        'Pack 150 Whitinsville',
        'Pack 151 West Boylston',
        'Pack 158 Shrewsbury',
        'Pack 46 Jefferson',
        'Troop 118 West Brookfield',
        'Troop 151 West Boylston',
        'Troop 155 Whitinsville',
        'Troop 161 Sturbridge',
        'Troop 238 East Brookfield',
        'Troop 7163 Sturbridge',
        'Troop 9 Worcester'
    ]
    
    key_three_units, scraped_units = load_data()
    
    # Create lookups by unit type and number
    key_three_lookup = {}
    for unit in key_three_units:
        parts = unit['unit_key'].split(' ', 2)
        if len(parts) >= 2:
            type_number = f"{parts[0]} {parts[1]}"
            if type_number not in key_three_lookup:
                key_three_lookup[type_number] = []
            key_three_lookup[type_number].append(unit)
    
    scraped_lookup = {}
    for unit in scraped_units:
        parts = unit['unit_key'].split(' ', 2)
        if len(parts) >= 2:
            type_number = f"{parts[0]} {parts[1]}"
            if type_number not in scraped_lookup:
                scraped_lookup[type_number] = []
            scraped_lookup[type_number].append(unit)
    
    print("🔍 Analysis of Commissioner Feedback Units")
    print("=" * 60)
    
    for commissioner_unit in commissioner_units:
        print(f"\n📋 {commissioner_unit}")
        
        parts = commissioner_unit.split(' ', 2)
        if len(parts) >= 2:
            type_number = f"{parts[0]} {parts[1]}"
            expected_town = parts[2] if len(parts) >= 3 else "Unknown"
            
            # Check Key Three
            kt_matches = key_three_lookup.get(type_number, [])
            print(f"   Key Three matches for {type_number}:")
            if kt_matches:
                for match in kt_matches:
                    print(f"     • {match['unit_key']} (District: {match.get('district', 'Unknown')})")
            else:
                print(f"     • No matches found")
            
            # Check scraped data
            scraped_matches = scraped_lookup.get(type_number, [])
            print(f"   Scraped matches for {type_number}:")
            if scraped_matches:
                for match in scraped_matches:
                    meeting_loc = match.get('meeting_location', '')[:60] + '...' if len(match.get('meeting_location', '')) > 60 else match.get('meeting_location', '')
                    print(f"     • {match['unit_key']} → Meeting: {meeting_loc}")
            else:
                print(f"     • No matches found")
            
            # Analysis
            if kt_matches and scraped_matches:
                print(f"   💡 Analysis: Unit exists in both sources but towns don't match")
            elif kt_matches and not scraped_matches:
                print(f"   ⚠️  Analysis: Unit in Key Three but not found in scraped data")
            elif not kt_matches and scraped_matches:
                print(f"   ❓ Analysis: Unit in scraped data but not in Key Three")
            else:
                print(f"   ❌ Analysis: Unit not found in either source")

def main():
    analyze_commissioner_feedback_units()

if __name__ == "__main__":
    main()