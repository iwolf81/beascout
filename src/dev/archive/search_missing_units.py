#!/usr/bin/env python3
"""
Search for missing units in newly processed scraped data
Check if units from missing_beascout.txt are now found with correct towns
"""

import json

def search_missing_units():
    """Search for units from missing_beascout.txt in fixed scraped data"""
    
    # Load the missing units list
    missing_units = []
    with open('data/feedback/missing_beascout.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                missing_units.append(line)
    
    # Load newly processed scraped data
    with open('data/raw/scraped_units_comprehensive.json', 'r') as f:
        scraped_data = json.load(f)
    
    scraped_units = scraped_data.get('scraped_units', [])
    
    print(f"🔍 Searching for {len(missing_units)} missing units in FIXED scraped data")
    print("=" * 80)
    
    found_count = 0
    
    for missing_unit in missing_units:
        parts = missing_unit.split(' ', 2)
        if len(parts) < 3:
            continue
            
        unit_type = parts[0]
        unit_number = parts[1] 
        expected_town = parts[2]
        
        print(f"\n📋 Searching for: {missing_unit}")
        
        # Search for exact unit_key match first
        exact_matches = [u for u in scraped_units if u.get('unit_key') == missing_unit]
        if exact_matches:
            found_count += 1
            print(f"   ✅ EXACT MATCH FOUND:")
            for match in exact_matches:
                print(f"      • {match['unit_key']} → District: {match.get('district')}")
                print(f"        Meeting: {match.get('meeting_location', 'N/A')[:60]}...")
            continue
        
        # Search for same unit type and number with different towns
        unit_num_int = int(unit_number)
        type_number_matches = []
        
        for unit in scraped_units:
            unit_key = unit.get('unit_key', '')
            if unit_key.startswith(f"{unit_type} {unit_num_int} "):
                type_number_matches.append(unit)
        
        if type_number_matches:
            found_count += 1
            print(f"   ⚠️  FOUND WITH DIFFERENT TOWN:")
            for match in type_number_matches:
                scraped_town = match['unit_key'].split(' ', 2)[2] if len(match['unit_key'].split(' ')) > 2 else 'Unknown'
                print(f"      • {match['unit_key']} (expected: {expected_town})")
                print(f"        Meeting: {match.get('meeting_location', 'N/A')[:60]}...")
        else:
            print(f"   ❌ NOT FOUND in scraped data")
    
    print(f"\n📊 Summary:")
    print(f"   Missing units searched: {len(missing_units)}")
    print(f"   Found in scraped data: {found_count}")
    print(f"   Still missing: {len(missing_units) - found_count}")
    
    # Show some stats
    total_units_by_type = {}
    for unit in scraped_units:
        unit_type = unit.get('unit_key', '').split(' ')[0] if unit.get('unit_key') else 'Unknown'
        total_units_by_type[unit_type] = total_units_by_type.get(unit_type, 0) + 1
    
    print(f"\n📈 Scraped Data Overview:")
    for unit_type, count in sorted(total_units_by_type.items()):
        print(f"   {unit_type}: {count} units")

if __name__ == "__main__":
    search_missing_units()