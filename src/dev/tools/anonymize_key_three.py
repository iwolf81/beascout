#!/usr/bin/env python3
"""
Anonymize Key Three data by replacing personal information with fake data.
Preserves all unit and organizational information while protecting privacy.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
import argparse

# Import from same directory
from name_generators import generate_contact_batch


def load_key_three_data(file_path: str) -> Dict[str, Any]:
    """Load Key Three data from JSON or Excel file."""
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.json':
        with open(file_path, 'r') as f:
            return json.load(f)
    
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        # Convert Excel to JSON structure
        df = pd.read_excel(file_path)
        
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


def anonymize_key_three_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Anonymize personal information in Key Three data."""
    members = data["key_three_members"]
    
    # Generate enough anonymous contacts for all members
    anonymous_contacts = generate_contact_batch(len(members))
    
    # Create anonymized data
    anonymized_data = {
        "metadata": {
            **data["metadata"],
            "anonymized": True,
            "anonymization_date": datetime.now().isoformat(),
            "original_source": data["metadata"].get("source_file", "unknown"),
            "note": "Personal information (names, emails, phones) replaced with fake data for testing"
        },
        "key_three_members": []
    }
    
    # Map each member to an anonymous contact
    for i, member in enumerate(members):
        anonymous_contact = anonymous_contacts[i]
        
        # Create anonymized member record
        anonymized_member = {}
        
        # Copy all fields, but replace personal information
        for key, value in member.items():
            if key in ['member_name', 'name']:
                anonymized_member[key] = anonymous_contact['name']
            elif key == 'email':
                anonymized_member[key] = anonymous_contact['email']
            elif key == 'phone':
                anonymized_member[key] = anonymous_contact['phone']
            else:
                # Keep all other fields unchanged (unit info, positions, etc.)
                anonymized_member[key] = value
        
        anonymized_data["key_three_members"].append(anonymized_member)
    
    return anonymized_data


def save_anonymized_data(data: Dict[str, Any], output_path: str, format: str = 'both'):
    """Save anonymized data in JSON and/or Excel format."""
    output_path = Path(output_path)
    
    if format in ['json', 'both']:
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Anonymized JSON saved: {json_path}")
    
    if format in ['excel', 'both']:
        excel_path = output_path.with_suffix('.xlsx')
        
        # Convert to DataFrame for Excel export
        df = pd.DataFrame(data["key_three_members"])
        
        # Create Excel file with metadata sheet
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Key_Three_Data', index=False)
            
            # Add metadata sheet
            metadata_df = pd.DataFrame([
                ["Anonymized", "True"],
                ["Original Source", data["metadata"].get("original_source", "unknown")],
                ["Anonymization Date", data["metadata"]["anonymization_date"]],
                ["Total Records", data["metadata"]["total_records"]],
                ["Note", data["metadata"]["note"]]
            ], columns=["Property", "Value"])
            
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        print(f"✅ Anonymized Excel saved: {excel_path}")


def main():
    parser = argparse.ArgumentParser(description='Anonymize Key Three data for safe testing')
    parser.add_argument('input_file', help='Input Key Three file (JSON or Excel)')
    parser.add_argument('-o', '--output', help='Output file path (default: anonymized_key_three)')
    parser.add_argument('-f', '--format', choices=['json', 'excel', 'both'], 
                       default='both', help='Output format (default: both)')
    
    args = parser.parse_args()
    
    # Default output path
    if not args.output:
        args.output = "tests/reference/key_three/anonymized_key_three"
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"📖 Loading Key Three data from: {args.input_file}")
        data = load_key_three_data(args.input_file)
        
        print(f"🔄 Anonymizing {len(data['key_three_members'])} member records...")
        anonymized_data = anonymize_key_three_data(data)
        
        print(f"💾 Saving anonymized data...")
        save_anonymized_data(anonymized_data, args.output, args.format)
        
        print(f"\n✅ Anonymization complete!")
        print(f"   Original records: {len(data['key_three_members'])}")
        print(f"   Anonymized records: {len(anonymized_data['key_three_members'])}")
        print(f"   All personal information (names, emails, phones) replaced with fake data")
        print(f"   Unit and organizational information preserved")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()