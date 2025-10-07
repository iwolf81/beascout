#!/usr/bin/env python3
"""
Generate All Unit Improvement Emails

Main script to generate improvement emails for all HNE units
using the new email generation system.
"""

import sys
import os
from pathlib import Path
import argparse
import json

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import using absolute path fallback
try:
    from src.dev.reporting.generate_unit_emails_v2 import UnitEmailGenerator
except ImportError:
    # Fallback - direct file import
    import importlib.util
    email_gen_path = project_root / "src" / "dev" / "reporting" / "generate_unit_emails_v2.py"
    spec = importlib.util.spec_from_file_location("generate_unit_emails_v2", email_gen_path)
    email_gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(email_gen_module)
    UnitEmailGenerator = email_gen_module.UnitEmailGenerator

def main():
    parser = argparse.ArgumentParser(
        description='Generate improvement emails for all HNE units',
        epilog="""
Examples:
  # Use validation results (recommended - already has correct Key Three join):
  python src/pipeline/analysis/generate_unit_emails.py data/output/enhanced_three_way_validation_results.json

  # Legacy mode (re-does join - not recommended):
  python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json data/input/Key_3_09-29-2025.xlsx
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'validation_file',
        help='Path to validation results JSON with units and Key Three data already joined'
    )

    parser.add_argument(
        '--output-dir',
        default='data/output/unit_emails_v2',
        help='Output directory for email files (default: data/output/unit_emails_v2)'
    )

    parser.add_argument(
        '--max-units',
        type=int,
        help='Maximum number of emails to generate (for testing)'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize email generator
    generator = UnitEmailGenerator()

    # Load validation results with pre-joined data
    print(f"🔄 Loading validation results from {args.validation_file}")
    with open(args.validation_file, 'r') as f:
        validation_data = json.load(f)

    # Extract units with their Key Three members from validation results
    units_with_key_three = []
    for result in validation_data['validation_results']:
        if result.get('status') in ['both_sources', 'scraped_only']:
            # Has scraped data - can generate email
            unit = result.get('scraped_data', {})
            key_three_members = []

            if 'key_three_data' in result:
                # Extract the 3 Key Three members
                kt_data = result['key_three_data']
                key_three_members = kt_data.get('key_three_members', [])[:3]  # Limit to 3

            units_with_key_three.append({
                'unit': unit,
                'key_three_members': key_three_members
            })

    print("=" * 60)

    generated_count = 0
    skipped_count = 0
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

    for item in units_with_key_three:
        unit = item['unit']
        key_three_members = item['key_three_members']

        unit_key = unit.get('unit_key', 'Unknown_Unit')
        completeness_grade = unit.get('completeness_grade', 'F')
        grade_counts[completeness_grade] += 1

        print(f"Processing {unit_key} (Grade: {completeness_grade})...")

        if not key_three_members:
            print(f"  ⚠️  Warning: No Key Three members found for {unit_key}")
            skipped_count += 1
            continue

        # Convert Key Three member format for email generator
        formatted_members = []
        for member in key_three_members:
            formatted_members.append({
                'member_name': member.get('fullname', ''),
                'email': member.get('email', ''),
                'phone': member.get('phone', ''),
                'position': member.get('position', '')
            })

        # Generate email content
        email_content = generator.generate_email_content(unit, formatted_members)

        # Save email to file with display format (no leading zeros in unit number)
        # Convert "Troop 0001 Acton" -> "Troop_1_Acton"
        parts = unit_key.split()
        if len(parts) >= 3:
            unit_type = parts[0]
            unit_number_4digit = parts[1]
            unit_town = ' '.join(parts[2:])
            # Strip leading zeros for display format
            display_number = unit_number_4digit.lstrip('0') or '0'
            display_filename = f"{unit_type}_{display_number}_{unit_town}".replace(' ', '_').replace('/', '_')
        else:
            display_filename = unit_key.replace(' ', '_').replace('/', '_')

        email_file = output_dir / f"{display_filename}_improvement_email.md"

        with open(email_file, 'w') as f:
            f.write(email_content)

        print(f"  ✅ Generated: {email_file.name}")
        generated_count += 1

    # TODO: Handle key_three_only units (missing from BeAScout) - generate setup emails

    print("\n" + "=" * 60)
    print(f"📊 EMAIL GENERATION SUMMARY:")
    print(f"  Total units processed: {len(units_with_key_three)}")
    print(f"  Emails generated: {generated_count}")
    print(f"  Units skipped (no Key Three): {skipped_count}")
    print(f"  Output directory: {output_dir}")
    print()
    print(f"📈 UNIT GRADE DISTRIBUTION:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        print(f"  Grade {grade}: {grade_counts[grade]} units")


if __name__ == "__main__":
    main()