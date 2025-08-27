#!/usr/bin/env python3
"""
Analyze identifier matching between Key Three and scraped data
Debug why we have 312 units instead of 169
"""

import json
import re

def normalize_identifier(identifier):
    """Normalize identifier for better matching"""
    # Remove extra spaces and standardize separators
    normalized = re.sub(r'\s+', ' ', identifier.strip())
    normalized = re.sub(r'\s*-\s*', '-', normalized)
    return normalized

def find_partial_matches():
    """Find partial matches between Key Three and scraped data"""
    
    # Load scraped data
    with open('data/raw/all_units_comprehensive_scored.json', 'r') as f:
        scraped_data = json.load(f)
    scraped_identifiers = set(unit['primary_identifier'] for unit in scraped_data['units_with_scores'])
    
    # Load Key Three data
    with open('data/raw/key_three_parsed_units.json', 'r') as f:
        key_three_data = json.load(f)
    key_three_identifiers = set(unit['primary_identifier'] for unit in key_three_data['parsed_units'])
    
    # Load comparison data
    with open('data/raw/key_three_comparison.json', 'r') as f:
        comparison_data = json.load(f)
    missing_identifiers = set(comparison_data['missing_units'])
    extra_identifiers = set(comparison_data['extra_units'])
    
    print(f"Scraped identifiers: {len(scraped_identifiers)}")
    print(f"Key Three identifiers: {len(key_three_identifiers)}")
    print(f"Missing identifiers: {len(missing_identifiers)}")
    print(f"Extra identifiers: {len(extra_identifiers)}")
    
    # Check for exact matches in missing units
    print("\nChecking for exact matches in 'missing' units...")
    false_missing = []
    for missing_id in list(missing_identifiers)[:10]:  # Check first 10
        if missing_id in scraped_identifiers:
            false_missing.append(missing_id)
            print(f"❌ FALSE MISSING: {missing_id}")
    
    # Look for near matches by comparing unit type + number + town
    print("\nLooking for near matches...")
    def extract_components(identifier):
        match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)\s+(.+)', identifier)
        if match:
            return (match.group(1), match.group(2), match.group(3).split('-')[0])
        return None
    
    scraped_components = {}
    for identifier in scraped_identifiers:
        components = extract_components(identifier)
        if components:
            key = f"{components[0]} {components[1]} {components[2]}"
            scraped_components[key] = identifier
    
    near_matches = []
    for missing_id in list(missing_identifiers)[:20]:  # Check first 20
        components = extract_components(missing_id)
        if components:
            key = f"{components[0]} {components[1]} {components[2]}"
            if key in scraped_components:
                near_matches.append((missing_id, scraped_components[key]))
                print(f"🔍 NEAR MATCH:")
                print(f"    Key Three: {missing_id}")
                print(f"    Scraped:   {scraped_components[key]}")
    
    print(f"\nFound {len(near_matches)} near matches")
    
    # Analyze why we have so many extra units
    print(f"\nAnalyzing extra units (first 10):")
    for extra_id in list(extra_identifiers)[:10]:
        print(f"  Extra: {extra_id}")
    
    return {
        'false_missing': false_missing,
        'near_matches': near_matches,
        'scraped_count': len(scraped_identifiers),
        'key_three_count': len(key_three_identifiers),
        'missing_count': len(missing_identifiers),
        'extra_count': len(extra_identifiers)
    }

if __name__ == '__main__':
    results = find_partial_matches()
    
    print(f"\n📊 Summary:")
    print(f"Expected (Key Three): 169 units")
    print(f"Scraped from web: {results['scraped_count']} units")
    print(f"Missing units: {results['missing_count']} units")
    print(f"Extra units: {results['extra_count']} units")
    print(f"Total if combined: {results['scraped_count'] + results['missing_count']} units")
    
    if results['near_matches']:
        print(f"\n⚠️  Found {len(results['near_matches'])} potential identifier format mismatches")
        print("These may be causing false missing/extra classifications.")