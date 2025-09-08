#!/usr/bin/env python3
"""
Enhanced Key Three Anonymization Tool
Replaces personal information with fake data while preserving ALL organizational structure.
Maintains exact unit counts and relationships for proper pipeline testing.
"""

import json
import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

# Import from same directory
from name_generators import generate_contact_batch


def load_key_three_data(file_path: str) -> Dict[str, Any]:
    """Load Key Three data from JSON or Excel file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    print(f"📂 Loading Key Three data from: {file_path}")
    
    if file_path.suffix.lower() == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        # Convert Excel to JSON structure (header in row 8)
        df = pd.read_excel(file_path, header=8)
        
        # Create structure matching the JSON format
        key_three_data = {
            "metadata": {
                "source_file": str(file_path),
                "conversion_date": datetime.now().isoformat(),
                "total_records": len(df)
            },
            "key_three_members": []
        }
        
        # Convert DataFrame to list of dictionaries
        for _, row in df.iterrows():
            member = {}
            for col in df.columns:
                # Handle NaN values
                value = row[col]
                if pd.isna(value):
                    member[col.lower().replace(' ', '_')] = ""
                else:
                    member[col.lower().replace(' ', '_')] = str(value)
            
            key_three_data["key_three_members"].append(member)
        
        return key_three_data
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def anonymize_key_three_data(data: Dict[str, Any], preserve_count: bool = True) -> Dict[str, Any]:
    """
    Anonymize personal information while preserving ALL organizational data.
    
    Args:
        data: Key Three data dictionary
        preserve_count: If True, maintains exact member count (recommended)
    
    Returns:
        Anonymized data with same structure and relationships
    """
    members = data["key_three_members"]
    total_members = len(members)
    
    print(f"🔄 Anonymizing {total_members} member records...")
    print(f"   Preserving organizational data: unit_display, unit_org_name, district, position, etc.")
    print(f"   Anonymizing personal data: member_name, email, phone, address")
    
    # Generate unique anonymous contacts for all members
    anonymous_contacts = generate_contact_batch(total_members)
    
    # Create anonymized data with preserved metadata
    anonymized_data = {
        "metadata": {
            **data["metadata"],
            "anonymized": True,
            "anonymization_date": datetime.now().isoformat(),
            "original_source": data["metadata"].get("source_file", "unknown"),
            "original_record_count": total_members,
            "anonymized_record_count": total_members,
            "preservation_note": "ALL organizational data preserved - only personal info anonymized"
        },
        "key_three_members": []
    }
    
    # Track anonymization statistics
    fields_anonymized = set()
    fields_preserved = set()
    
    # Map each member to a unique anonymous contact (1:1 relationship)
    for i, member in enumerate(members):
        anonymous_contact = anonymous_contacts[i]
        
        # Create anonymized member record - preserve ALL non-personal fields
        anonymized_member = {}
        
        for key, value in member.items():
            if key in ['member_name', 'name', 'fullname']:
                anonymized_member[key] = anonymous_contact['name']
                fields_anonymized.add(key)
            elif key in ['email', 'email_address']:
                anonymized_member[key] = anonymous_contact['email']
                fields_anonymized.add(key)
            elif key in ['phone', 'phone_number', 'telephone']:
                anonymized_member[key] = anonymous_contact['phone']
                fields_anonymized.add(key)
            elif key in ['address', 'street_address']:
                # Generate fake street address but keep same city/state from citystate field
                anonymized_member[key] = anonymous_contact.get('address', f"{anonymous_contact['phone'].split(') ')[1].replace('-', '')} Main St")
                fields_anonymized.add(key)
            else:
                # Preserve ALL other fields exactly as-is (organizational data)
                anonymized_member[key] = value
                fields_preserved.add(key)
        
        anonymized_data["key_three_members"].append(anonymized_member)
    
    # Add anonymization summary to metadata
    anonymized_data["metadata"]["anonymization_summary"] = {
        "fields_anonymized": sorted(list(fields_anonymized)),
        "fields_preserved": sorted(list(fields_preserved)),
        "total_fields_processed": len(fields_anonymized) + len(fields_preserved)
    }
    
    print(f"   ✅ Anonymized fields: {', '.join(sorted(fields_anonymized))}")
    print(f"   ✅ Preserved fields: {len(fields_preserved)} organizational fields")
    
    return anonymized_data


def save_anonymized_data(data: Dict[str, Any], output_path: str, format: str = 'both'):
    """Save anonymized data with enhanced metadata."""
    output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    if format in ['json', 'both']:
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Anonymized JSON saved: {json_path}")
        saved_files.append(str(json_path))
    
    if format in ['excel', 'both']:
        excel_path = output_path.with_suffix('.xlsx')
        
        # Convert to DataFrame for Excel export
        df = pd.DataFrame(data["key_three_members"])
        
        # Create Excel file matching the real Key Three Excel format exactly
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Create main sheet with header rows 0-7, column names on row 8, data starting row 9
            ws = writer.book.create_sheet("Sheet1")
            writer.sheets["Sheet1"] = ws
            
            # Add header rows (0-7) to match real Excel format
            metadata = data["metadata"]
            ws['A1'] = 'Report: Key 3 Contact Report (Anonymized)'
            ws['A2'] = 'Council: Heart of New England Council 230 '
            ws['A3'] = 'Organization Name: Heart of New England Council 230'
            ws['A4'] = 'Report Generated By: Anonymized Data'
            ws['A5'] = f"Date Report Generated: {metadata['anonymization_date'][:10]}"  # Just date part
            ws['A6'] = '..'
            ws['A7'] = 'This information is ANONYMIZED and safe for testing/development purposes.'
            ws['A8'] = '..'
            
            # Add column names on row 9 (index 8)
            columns = df.columns.tolist()
            for col_idx, col_name in enumerate(columns, 1):
                ws.cell(row=9, column=col_idx, value=col_name)
            
            # Add data starting from row 10 (index 9)
            for row_idx, (_, row_data) in enumerate(df.iterrows(), 10):
                for col_idx, value in enumerate(row_data, 1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
            
            # Enhanced metadata sheet
            metadata_rows = [
                ["Property", "Value"],
                ["Anonymized", "True"],
                ["Original Source", metadata.get("original_source", "unknown")],
                ["Anonymization Date", metadata["anonymization_date"]],
                ["Original Record Count", metadata.get("original_record_count", "unknown")],
                ["Anonymized Record Count", metadata.get("anonymized_record_count", "unknown")],
                ["Fields Anonymized", ", ".join(metadata.get("anonymization_summary", {}).get("fields_anonymized", []))],
                ["Fields Preserved", f"{len(metadata.get('anonymization_summary', {}).get('fields_preserved', []))} organizational fields"],
                ["Preservation Note", metadata.get("preservation_note", "")],
                ["Safe for Git", "Yes - contains no real personal information"],
                ["Pipeline Compatible", "Yes - maintains all unit relationships"]
            ]
            
            metadata_df = pd.DataFrame(metadata_rows[1:], columns=metadata_rows[0])
            metadata_df.to_excel(writer, sheet_name='Anonymization_Info', index=False)
        
        print(f"✅ Anonymized Excel saved: {excel_path}")
        saved_files.append(str(excel_path))
    
    return saved_files


def verify_anonymization(original_data: Dict[str, Any], anonymized_data: Dict[str, Any]) -> bool:
    """Verify anonymization preserved organizational structure."""
    print(f"🔍 Verifying anonymization integrity...")
    
    original_members = original_data["key_three_members"]
    anonymized_members = anonymized_data["key_three_members"]
    
    # Check member count preservation
    if len(original_members) != len(anonymized_members):
        print(f"❌ Member count mismatch: {len(original_members)} → {len(anonymized_members)}")
        return False
    
    # Check organizational field preservation
    organizational_fields = {'unit_display', 'unit_org_name', 'district', 'position', 'ypt_status', 'citystate'}
    
    for i, (original, anonymized) in enumerate(zip(original_members, anonymized_members)):
        for field in organizational_fields:
            if field in original:
                if original[field] != anonymized.get(field):
                    print(f"❌ Organizational field changed at record {i}: {field}")
                    print(f"   Original: {original[field]}")
                    print(f"   Anonymized: {anonymized.get(field)}")
                    return False
    
    print(f"✅ Verification passed: {len(anonymized_members)} members, organizational data intact")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Anonymize Key Three data for safe testing and development',
        epilog='''
Examples:
  # Anonymize with defaults
  python anonymize_key_three_v2.py data/input/HNE_key_three.xlsx
  
  # Specify output location and format
  python anonymize_key_three_v2.py data/input/HNE_key_three.json -o tests/reference/key_three/test_data -f json
  
  # Process Excel and save both formats
  python anonymize_key_three_v2.py data/input/HNE_key_three.xlsx -o anonymized_data -f both

This script generates:
  • anonymized_key_three.json (used by: generate_commissioner_report.py --key-three)
  • anonymized_key_three.xlsx (Excel format for manual review)
  
Pipeline Integration:
  Use output with: generate_commissioner_report.py --key-three [OUTPUT_PATH].json
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_file', 
                       help='Input Key Three file (JSON or Excel format)')
    parser.add_argument('-o', '--output', 
                       default='tests/reference/key_three/anonymized_key_three',
                       help='Output file path [default: tests/reference/key_three/anonymized_key_three]')
    parser.add_argument('-f', '--format', 
                       choices=['json', 'excel', 'both'], 
                       default='both', 
                       help='Output format [default: both]')
    parser.add_argument('--verify', 
                       action='store_true',
                       help='Run verification checks after anonymization')
    
    args = parser.parse_args()
    
    try:
        print("🔐 Key Three Anonymization Tool")
        print("=" * 50)
        
        # Load original data
        original_data = load_key_three_data(args.input_file)
        original_count = len(original_data["key_three_members"])
        print(f"📊 Original data: {original_count} member records")
        
        # Perform anonymization
        anonymized_data = anonymize_key_three_data(original_data)
        
        # Verify if requested
        if args.verify:
            if not verify_anonymization(original_data, anonymized_data):
                print("❌ Verification failed!")
                sys.exit(1)
        
        # Save anonymized data
        print(f"💾 Saving anonymized data...")
        saved_files = save_anonymized_data(anonymized_data, args.output, args.format)
        
        # Success summary
        print(f"\n✅ Anonymization Complete!")
        print(f"   Original: {original_count} records")
        print(f"   Anonymized: {len(anonymized_data['key_three_members'])} records")
        print(f"   Files created: {len(saved_files)}")
        for file_path in saved_files:
            print(f"   • {file_path}")
        
        print(f"\n🔒 Privacy Protection:")
        print(f"   • All personal information (names, emails, phones) replaced with fake data")
        print(f"   • All organizational data (units, districts, positions) preserved exactly")
        print(f"   • Safe to commit to Git and share with developers")
        
        print(f"\n🔄 Usage:")
        json_file = next((f for f in saved_files if f.endswith('.json')), saved_files[0])
        print(f"   python generate_commissioner_report.py --key-three {json_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()