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
  python src/scripts/generate_all_unit_emails.py data/raw/all_units_comprehensive_scored.json tests/reference/key_three/anonymized_key_three.json
  python src/scripts/generate_all_unit_emails.py data/raw/all_units_comprehensive_scored.json tests/reference/key_three/anonymized_key_three.xlsx --output-dir emails_test
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'units_file',
        help='Path to processed units JSON file with quality scores'
    )
    
    parser.add_argument(
        'key_three_file', 
        help='Path to Key Three contacts file (Excel .xlsx or JSON .json)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/output/emails',
        help='Output directory for email files (default: data/output/emails)'
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
    
    # Load data
    print(f"🔄 Loading unit data from {args.units_file}")
    units = generator.load_unit_data(args.units_file)
    
    print(f"🔄 Loading Key Three data from {args.key_three_file}")
    key_three_index = generator.load_key_three_data(args.key_three_file)
    
    # Check for units in Key Three data that don't have online presence
    all_key_three_units = set()
    for unit_display, members in key_three_index.items():
        all_key_three_units.add(unit_display)
    
    scraped_units = set()
    for unit in units:
        # Use the same format as Key Three index: "Unit Type Number Town"
        unit_key = unit.get('unit_key', '')
        if unit_key:
            scraped_units.add(unit_key)
    
    missing_online_units = all_key_three_units - scraped_units
    if missing_online_units:
        print(f"⚠️  WARNING: Found {len(missing_online_units)} units in Key Three data with NO online presence:")
        for missing_unit in sorted(missing_online_units)[:10]:  # Show first 10
            if missing_unit.strip():  # Skip empty entries
                print(f"  🚨 {missing_unit} - NOT FOUND on BeAScout.org/JoinExploring.org")
        if len(missing_online_units) > 10:
            print(f"  ... and {len(missing_online_units) - 10} more units missing online")
        print(f"  📧 These units ESPECIALLY need emails encouraging them to set up online presence!\n")
    
    print(f"📧 Generating emails for {len(units)} units...")
    print("=" * 60)
    
    generated_count = 0
    skipped_count = 0
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    
    for unit in units:
        unit_key = unit.get('unit_key', 'Unknown_Unit')
        completeness_grade = unit.get('completeness_grade', 'F')
        grade_counts[completeness_grade] += 1
        
        print(f"Processing {unit_key} (Grade: {completeness_grade})...")
        
        # Find Key Three members for this unit
        key_three_members = generator.find_key_three_for_unit(unit, key_three_index)
        
        if not key_three_members:
            print(f"  ⚠️  Warning: No Key Three members found for {unit_key}")
            skipped_count += 1
            continue
        
        # Generate email content
        email_content = generator.generate_email_content(unit, key_three_members)
        
        # Save email to file
        safe_filename = unit_key.replace(' ', '_').replace('/', '_')
        email_file = output_dir / f"{safe_filename}_improvement_email.md"
        
        with open(email_file, 'w') as f:
            f.write(email_content)
        
        print(f"  ✅ Generated: {email_file.name}")
        generated_count += 1
    
    # Generate emails for units with NO online presence
    missing_emails_count = 0
    if missing_online_units:
        print(f"\n🚨 Generating URGENT setup emails for {len(missing_online_units)} units with NO online presence...")
        print("=" * 60)
        
        for unit_display in sorted(missing_online_units):
            if not unit_display.strip():  # Skip empty entries
                continue
                
            # Find Key Three members for this missing unit
            if unit_display in key_three_index:
                key_three_members = key_three_index[unit_display]
                
                print(f"Processing MISSING unit: {unit_display}...")
                
                # Parse unit info to get proper identifiers including town name
                from src.dev.parsing.key_three_parser import KeyThreeParser
                
                # Use existing parser to get unit info from the first Key Three member
                if key_three_members:
                    unit_org_name = key_three_members[0].get('unit_org_name', '')
                    if unit_org_name:
                        parser = KeyThreeParser("")  # Don't need to load data, just use parsing logic
                        unit_info = parser.extract_unit_info_from_unitcommorgname(unit_org_name)
                        
                        if unit_info and unit_info.get('unit_town'):
                            # Create proper filename with town name
                            unit_type = unit_info['unit_type']
                            unit_number = unit_info['unit_number'].lstrip('0') or '0'
                            unit_town = unit_info['unit_town']
                            safe_filename = f"{unit_type}_{unit_number}_{unit_town}".replace(' ', '_').replace('/', '_')
                        else:
                            # Fallback to original unit_display if parsing fails
                            safe_filename = unit_display.replace(' ', '_').replace('/', '_')
                    else:
                        # No unit org name available
                        safe_filename = unit_display.replace(' ', '_').replace('/', '_')
                else:
                    # No key three members available
                    safe_filename = unit_display.replace(' ', '_').replace('/', '_')
                
                # Generate urgent setup email - pass unit_display as string to trigger missing unit logic
                email_content = generator.generate_email_content(unit_display, key_three_members)
                
                email_file = output_dir / f"{safe_filename}_setup_email.md"
                
                with open(email_file, 'w') as f:
                    f.write(email_content)
                
                print(f"  🚨 Generated URGENT: {email_file.name}")
                missing_emails_count += 1
            else:
                print(f"  ⚠️ No Key Three members found for missing unit: {unit_display}")
    
    print("\n" + "=" * 60)
    print(f"📊 EMAIL GENERATION SUMMARY:")
    print(f"  Total units processed: {len(units)}")
    print(f"  Emails generated: {generated_count}")
    print(f"  Units skipped (no Key Three): {skipped_count}")
    print(f"  URGENT emails for missing units: {missing_emails_count}")
    print(f"  Output directory: {output_dir}")
    print()
    print(f"📈 UNIT GRADE DISTRIBUTION:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = grade_counts[grade]
        percentage = (count / len(units)) * 100 if units else 0
        print(f"  Grade {grade}: {count:3d} units ({percentage:4.1f}%)")
    
    # Generate summary report
    summary_file = output_dir / "email_generation_summary.json"
    summary = {
        "generation_date": generator.analysis_date,
        "total_units": len(units),
        "emails_generated": generated_count,
        "units_skipped": skipped_count,
        "urgent_emails_missing_units": missing_emails_count,
        "grade_distribution": grade_counts,
        "output_directory": str(output_dir)
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Summary saved to: {summary_file}")
    
    if generated_count > 0:
        print(f"\n✨ Successfully generated {generated_count} personalized improvement emails!")
        print("   Each email includes:")
        print("   - Unit-specific quality analysis")
        print("   - Key Three member contact information") 
        print("   - Prioritized recommendations")
        print("   - Professional formatting matching council standards")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())