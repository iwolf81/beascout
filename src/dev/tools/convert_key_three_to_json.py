#!/usr/bin/env python3
"""
Convert HNE Key Three Excel spreadsheet to JSON format for faster processing

Usage:
    python scripts/convert_key_three_to_json.py "data/input/Key 3 08-22-2025.xlsx"  # Use real data for production
    python scripts/convert_key_three_to_json.py tests/reference/key_three/anonymized_key_three.xlsx  # Use anonymized data for development
"""

import pandas as pd
import json
import sys
from pathlib import Path


def convert_key_three_to_json(excel_file: str, output_file: str = None) -> str:
    """Convert Key Three Excel file to JSON format"""
    
    if output_file is None:
        output_file = str(Path(excel_file).with_suffix('.json'))
    
    try:
        # Read Excel file (header in row 8)
        df = pd.read_excel(excel_file, header=8)
        print(f"Loaded {len(df)} Key Three member records from Excel")
        
        # Convert to list of dictionaries
        key_three_data = []
        
        for _, row in df.iterrows():
            member_data = {
                'district': str(row.get('districtname', '')).strip(),
                'unit_display': str(row.get('displayname', '')).strip(),
                'member_name': str(row.get('fullname', '')).strip(),
                'address': str(row.get('address', '')).strip(),
                'citystate': str(row.get('citystate', '')).strip(),
                'zip': str(row.get('zip', '')).strip(),
                'email': str(row.get('email', '')).strip(),
                'phone': str(row.get('phone', '')).strip(),
                'position': str(row.get('position', '')).strip(),
                'unit_org_name': str(row.get('unitcommorgname', '')).strip(),
                'ypt_status': str(row.get('yptstatus', '')).strip()
            }
            
            # Clean up missing data
            for key, value in member_data.items():
                if value in ['nan', 'None', '', 'NaT']:
                    member_data[key] = ''
            
            key_three_data.append(member_data)
        
        # Save to JSON
        output_data = {
            'metadata': {
                'source_file': excel_file,
                'conversion_date': pd.Timestamp.now().isoformat(),
                'total_records': len(key_three_data)
            },
            'key_three_members': key_three_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Converted to JSON: {output_file}")
        print(f"Total records: {len(key_three_data)}")
        
        return output_file
        
    except Exception as e:
        print(f"Error converting Excel to JSON: {e}", file=sys.stderr)
        return ""


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/convert_key_three_to_json.py <excel_file> [output_file]")
        print("Example (production): python scripts/convert_key_three_to_json.py data/input/HNE_key_three.xlsx")
        print("Example (development): python scripts/convert_key_three_to_json.py tests/reference/key_three/anonymized_key_three.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(excel_file).exists():
        print(f"File not found: {excel_file}", file=sys.stderr)
        sys.exit(1)
    
    convert_key_three_to_json(excel_file, output_file)


if __name__ == "__main__":
    main()