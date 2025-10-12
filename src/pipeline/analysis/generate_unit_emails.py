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

# Import from pipeline location
from src.pipeline.analysis.unit_email_generator import UnitEmailGenerator

def load_excluded_units():
    """Load list of units to exclude from all reports and emails"""
    excluded_file = project_root / "data/config/excluded_units.json"
    if not excluded_file.exists():
        return set()

    try:
        with open(excluded_file, 'r') as f:
            data = json.load(f)
        excluded = {unit['unit_key'] for unit in data.get('excluded_units', [])}
        if excluded:
            print(f"🚫 Loaded {len(excluded)} excluded units from config")
        return excluded
    except Exception as e:
        print(f"⚠️  Warning: Could not load excluded units: {e}")
        return set()

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
        default='data/output/unit_emails',
        help='Output directory for email files (default: data/output/unit_emails)'
    )

    parser.add_argument(
        '--max-units',
        type=int,
        help='Maximum number of emails to generate (for testing)'
    )

    parser.add_argument(
        '--analysis-timestamp',
        help='Analysis timestamp for session tracking (format: YYYYMMDD_HHMMSS)'
    )

    parser.add_argument(
        '--scraped-timestamp',
        help='BeAScout data scraping timestamp (format: YYYYMMDD_HHMMSS)'
    )

    parser.add_argument(
        '--key-three-timestamp',
        help='Key Three report date (format: YYYYMMDD - date only, no time)'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize email generator with timestamps
    generator = UnitEmailGenerator(
        analysis_timestamp=args.analysis_timestamp,
        scraped_timestamp=args.scraped_timestamp,
        key_three_timestamp=args.key_three_timestamp
    )

    # Load validation results with pre-joined data
    print(f"🔄 Loading validation results from {args.validation_file}")
    with open(args.validation_file, 'r') as f:
        validation_data = json.load(f)

    # Load excluded units
    excluded_units = load_excluded_units()

    # Extract units with their Key Three members from validation results
    units_with_key_three = []
    excluded_count = 0
    for result in validation_data['validation_results']:
        if result.get('status') in ['both_sources', 'scraped_only']:
            # Has scraped data - can generate email
            unit = result.get('scraped_data', {})
            unit_key = unit.get('unit_key', '')

            # Skip excluded units
            if unit_key in excluded_units:
                excluded_count += 1
                continue

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

        email_file = output_dir / f"{display_filename}_beascout_improvements.md"

        with open(email_file, 'w') as f:
            f.write(email_content)

        print(f"  ✅ Generated: {email_file.name}")
        generated_count += 1

    # Handle key_three_only units (missing from BeAScout) - generate setup emails
    missing_units = []
    for result in validation_data['validation_results']:
        if result.get('status') == 'key_three_only':
            # Unit exists in Key Three but not in scraped data
            kt_data = result.get('key_three_data', {})
            unit_key = kt_data.get('unit_key', 'Unknown_Unit')

            # Skip excluded units
            if unit_key in excluded_units:
                excluded_count += 1
                continue

            key_three_members = kt_data.get('key_three_members', [])[:3]

            missing_units.append({
                'unit_key': unit_key,
                'key_three_members': key_three_members
            })

    for item in missing_units:
        unit_key = item['unit_key']
        key_three_members = item['key_three_members']

        print(f"Processing {unit_key} (Missing from BeAScout)...")

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
                'position': member.get('position', ''),
                'unit_org_name': member.get('unitcommorgname', '')  # Needed for unit parsing
            })

        # Generate setup email - pass unit_key as string to trigger missing unit logic
        email_content = generator.generate_email_content(unit_key, formatted_members)

        # Save email to file with display format (no leading zeros in unit number)
        parts = unit_key.split()
        if len(parts) >= 3:
            unit_type = parts[0]
            unit_number_4digit = parts[1]
            unit_town = ' '.join(parts[2:])
            display_number = unit_number_4digit.lstrip('0') or '0'
            display_filename = f"{unit_type}_{display_number}_{unit_town}".replace(' ', '_').replace('/', '_')
        else:
            display_filename = unit_key.replace(' ', '_').replace('/', '_')

        email_file = output_dir / f"{display_filename}_beascout_setup.md"

        with open(email_file, 'w') as f:
            f.write(email_content)

        print(f"  ✅ Generated: {email_file.name}")
        generated_count += 1

    print("\n" + "=" * 60)
    print(f"📊 EMAIL GENERATION SUMMARY:")
    print(f"  Units with BeAScout presence: {len(units_with_key_three)}")
    print(f"  Units missing from BeAScout: {len(missing_units)}")
    print(f"  Total emails generated: {generated_count}")
    print(f"  Units skipped (no Key Three): {skipped_count}")
    if excluded_count > 0:
        print(f"  Units excluded (config): {excluded_count}")
    print(f"  Output directory: {output_dir}")
    print()
    print(f"📈 UNIT GRADE DISTRIBUTION:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        print(f"  Grade {grade}: {grade_counts[grade]} units")


if __name__ == "__main__":
    main()