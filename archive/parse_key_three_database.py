#!/usr/bin/env python3
"""
Parse Key Three Database for Definitive Unit List
Based on analysis in data/feedback/key_three_unit_analysis.md
"""

import pandas as pd
import json
import re
from pathlib import Path

def extract_unit_info_from_unitcommorgname(unitcommorgname):
    """
    Extract unit type, number, and town from unitcommorgname column
    Based on patterns identified in key_three_unit_analysis.md
    """
    
    # Handle various patterns in unitcommorgname
    unit_info = {
        'unit_type': None,
        'unit_number': None,
        'town': None,
        'chartered_org': None,
        'original_string': unitcommorgname
    }
    
    # Extract unit type and number from beginning, handling gender designations
    unit_pattern = r'^(Pack|Troop|Crew|Ship|Post|Club)\s*(\d+)(?:\s*\([BFG]\))?'
    unit_match = re.match(unit_pattern, unitcommorgname, re.IGNORECASE)
    
    if unit_match:
        unit_info['unit_type'] = unit_match.group(1).title()
        unit_info['unit_number'] = unit_match.group(2).zfill(4)  # Pad to 4 digits
        
        # Remove unit type, number, and gender designation to analyze the rest
        remainder = unitcommorgname[len(unit_match.group(0)):].strip()
        
        # Remove leading separators like " - "
        if remainder.startswith(' - '):
            remainder = remainder[3:]
        elif remainder.startswith('-'):
            remainder = remainder[1:]
        elif remainder.startswith(' '):
            remainder = remainder[1:]
        
        # Various town extraction patterns based on examples from analysis
        town_found = False
        
        # Pattern 1: "Worcester - Heart of New England Council"
        match = re.match(r'^([A-Za-z\s]+)\s*-\s*Heart of New England Council', remainder)
        if match:
            unit_info['town'] = match.group(1).strip()
            unit_info['chartered_org'] = "Heart of New England Council"
            town_found = True
        
        # Pattern 2: "Clinton Heart of New England Council" (no separator)
        elif re.match(r'^([A-Za-z\s]+)\s+Heart of New England Council', remainder):
            match = re.match(r'^([A-Za-z\s]+)\s+Heart of New England Council', remainder)
            unit_info['town'] = match.group(1).strip()
            unit_info['chartered_org'] = "Heart of New England Council"
            town_found = True
        
        # Pattern 3: Handle abbreviated directions like "E Brookfield - Howe Lumber Co Inc"
        elif re.match(r'^([NSEW])\s+([A-Za-z\s]+)\s*-', remainder):
            match = re.match(r'^([NSEW])\s+([A-Za-z\s]+)\s*-\s*(.+)', remainder)
            direction = match.group(1)
            base_town = match.group(2).strip()
            unit_info['town'] = f"{direction} {base_town}".replace("E ", "East ").replace("W ", "West ").replace("N ", "North ").replace("S ", "South ")
            unit_info['chartered_org'] = match.group(3).strip()
            town_found = True
        
        # Pattern 4: Town-Organization format
        elif '-' in remainder:
            parts = remainder.split('-', 1)
            potential_town = parts[0].strip()
            # Check for special cases like "Fiskdale" which should be mapped to "Sturbridge"
            if potential_town == "Fiskdale":
                unit_info['town'] = "Sturbridge"  # As noted in analysis
            else:
                unit_info['town'] = potential_town
            unit_info['chartered_org'] = parts[1].strip() if len(parts) > 1 else ''
            town_found = True
        
        # Pattern 5: Town followed by organization (no separator)
        elif not town_found:
            # Split on first word as potential town
            words = remainder.split()
            if words:
                unit_info['town'] = words[0]
                unit_info['chartered_org'] = ' '.join(words[1:])
        
        # Clean up town name (remove any remaining quotes or extra spaces)
        if unit_info['town']:
            unit_info['town'] = unit_info['town'].strip().strip('"')
        if unit_info['chartered_org']:
            unit_info['chartered_org'] = unit_info['chartered_org'].strip().strip('"')
    
    return unit_info

def parse_key_three_database():
    """Parse Key Three Excel file to extract definitive unit list"""
    
    # Read the original Key Three Excel file
    excel_path = "data/input/Key 3 08-22-2025.xlsx"
    
    try:
        # Read Excel file, skip header rows to get to actual data
        df = pd.read_excel(excel_path, header=None, skiprows=3)
        print(f"Loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        
        # Column 9 (10th column) contains the unitcommorgname
        unitcommorgname_col = 9
        if len(df.columns) <= unitcommorgname_col:
            print(f"Error: Column {unitcommorgname_col} not found in file")
            return None
            
        # Get unique unitcommorgname values, filter out NaN and empty strings
        unit_column = df.iloc[:, unitcommorgname_col].dropna()
        unit_column = unit_column[unit_column != '']  # Remove empty strings
        unique_units = unit_column.unique()
        print(f"Found {len(unique_units)} unique unitcommorgname values")
        
        # Parse each unit
        parsed_units = []
        for unit_string in unique_units:
            unit_info = extract_unit_info_from_unitcommorgname(unit_string)
            
            # Create primary identifier to match scraped data format
            if unit_info['unit_type'] and unit_info['unit_number'] and unit_info['town']:
                # Format: "Pack 0001 Acton-The Church of The Good Shepherd" (with leading zeros to match scraped data)
                unit_number = unit_info['unit_number'].zfill(4)  # Ensure 4-digit format to match scraped units
                primary_identifier = f"{unit_info['unit_type']} {unit_number} {unit_info['town']}-{unit_info['chartered_org']}"
                unit_info['primary_identifier'] = primary_identifier
                parsed_units.append(unit_info)
            else:
                print(f"Warning: Could not parse unit info from: {unit_string}")
        
        print(f"Successfully parsed {len(parsed_units)} units")
        
        # Save parsed units
        output_file = "data/raw/key_three_parsed_units.json"
        with open(output_file, 'w') as f:
            json.dump({
                'total_units': len(parsed_units),
                'source_file': excel_path,
                'parsed_units': parsed_units
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Saved parsed units to: {output_file}")
        
        # Show sample of parsed units
        print("\nSample parsed units:")
        for i, unit in enumerate(parsed_units[:5]):
            print(f"  {i+1}. {unit['primary_identifier']}")
            print(f"      Original: {unit['original_string']}")
        
        return parsed_units
        
    except FileNotFoundError:
        print(f"Error: Could not find Excel file at {excel_path}")
        return None
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def normalize_identifier(identifier):
    """Normalize identifier for consistent comparison"""
    import re
    
    # Extract components
    match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)\s+(.+)', identifier)
    if match:
        unit_type = match.group(1)
        unit_number = match.group(2).lstrip('0') or '0'  # Remove leading zeros
        rest = match.group(3)
        
        # Normalize spaces around hyphens
        rest = re.sub(r'\s*-\s*', '-', rest)
        
        return f"{unit_type} {unit_number} {rest}"
    
    return identifier

def compare_with_scraped_data(key_three_units):
    """Compare Key Three units with scraped data to find missing units"""
    
    # Load comprehensive scraped data
    scraped_file = "data/raw/all_units_comprehensive_scored.json"
    
    try:
        with open(scraped_file, 'r') as f:
            scraped_data = json.load(f)
        
        scraped_units = scraped_data.get('units_with_scores', [])
        print(f"Loaded {len(scraped_units)} scraped units")
        
        # Create normalized identifier sets for comparison
        key_three_normalized = {}
        for unit in key_three_units:
            if unit.get('primary_identifier'):
                original = unit['primary_identifier']
                normalized = normalize_identifier(original)
                key_three_normalized[normalized] = original
        
        scraped_normalized = {}
        for unit in scraped_units:
            if unit.get('primary_identifier'):
                original = unit['primary_identifier']
                normalized = normalize_identifier(original)
                scraped_normalized[normalized] = original
        
        print(f"Key Three units: {len(key_three_normalized)}")
        print(f"Scraped units: {len(scraped_normalized)}")
        
        # Find missing units (in Key Three but not scraped)
        missing_normalized = set(key_three_normalized.keys()) - set(scraped_normalized.keys())
        missing_units = [key_three_normalized[norm] for norm in missing_normalized]
        
        # Find extra units (scraped but not in Key Three)
        extra_normalized = set(scraped_normalized.keys()) - set(key_three_normalized.keys())
        extra_units = [scraped_normalized[norm] for norm in extra_normalized]
        
        print(f"\nMissing units (in Key Three but not scraped): {len(missing_units)}")
        for unit_id in sorted(missing_units):
            print(f"  - {unit_id}")
        
        print(f"\nExtra units (scraped but not in Key Three): {len(extra_units)}")
        for unit_id in sorted(list(extra_units)[:10]):  # Show first 10
            print(f"  - {unit_id}")
        if len(extra_units) > 10:
            print(f"  ... and {len(extra_units) - 10} more")
        
        # Create missing units with 0 scores
        missing_unit_records = []
        for unit_id in missing_units:
            # Find the original Key Three record
            key_three_unit = next((u for u in key_three_units if u['primary_identifier'] == unit_id), None)
            if key_three_unit:
                missing_record = {
                    'primary_identifier': unit_id,
                    'unit_type': key_three_unit['unit_type'],
                    'unit_number': key_three_unit['unit_number'],
                    'unit_town': key_three_unit['town'],
                    'chartered_org': key_three_unit['chartered_org'],
                    'completeness_score': 0,
                    'completeness_grade': 'F',
                    'data_source': 'Key Three Only',
                    'missing_from_web': True,
                    'recommendations': ['MISSING_FROM_WEB']
                }
                missing_unit_records.append(missing_record)
        
        return {
            'missing_units': list(missing_units),
            'extra_units': list(extra_units),
            'missing_unit_records': missing_unit_records
        }
        
    except FileNotFoundError:
        print(f"Error: Could not find scraped data file at {scraped_file}")
        return None
    except Exception as e:
        print(f"Error comparing data: {e}")
        return None

if __name__ == '__main__':
    print("Parsing Key Three database...")
    
    # Parse Key Three database
    key_three_units = parse_key_three_database()
    
    if key_three_units:
        print(f"\n✅ Successfully parsed {len(key_three_units)} units from Key Three database")
        
        # Compare with scraped data
        comparison = compare_with_scraped_data(key_three_units)
        
        if comparison:
            # Save comparison results
            output_file = "data/raw/key_three_comparison.json"
            with open(output_file, 'w') as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Comparison results saved to: {output_file}")
        else:
            print("\n❌ Failed to compare with scraped data")
    else:
        print("\n❌ Failed to parse Key Three database")