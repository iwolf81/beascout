#!/usr/bin/env python3
"""
Find Units Without Address Script
Searches scraped HTML files for units that lack a unit-address clause
"""

import sys
import argparse
import glob
from pathlib import Path
from bs4 import BeautifulSoup

def check_unit_for_address(unit_wrapper):
    """Check if a unit has a address section"""
    # Look for unit-address div within this unit
    address_div = unit_wrapper.find('div', class_='unit-address')
    
    if not address_div:
        return False, "No unit-address div found"
    
    # Check if address has content
    address_text = address_div.get_text(strip=True)
    if not address_text:
        return False, "unit-address div is empty"
    
    # Check if it's just whitespace or minimal content
    if len(address_text) < 10:  # Arbitrary threshold for "meaningful" address
        return False, f"Address too short ({len(address_text)} chars): '{address_text}'"
    
    return True, address_text[:100] + "..." if len(address_text) > 100 else address_text

def extract_unit_identifier(unit_wrapper):
    """Extract unit identifier from the unit wrapper"""
    # Look for unit-name div
    unit_name_div = unit_wrapper.find('div', class_='unit-name')
    if unit_name_div:
        h5_tag = unit_name_div.find('h5')
        if h5_tag:
            # Get text and clean it up
            unit_text = h5_tag.get_text(separator=' ', strip=True)
            # Remove line breaks and extra spaces
            unit_text = ' '.join(unit_text.split())
            return unit_text
    
    return "Unknown Unit"

def normalize_unit_identifier(unit_identifier):
    """Normalize unit identifier for deduplication (similar to primary_identifier logic)"""
    if not unit_identifier or unit_identifier == "Unknown Unit":
        return unit_identifier
    
    # Split by line breaks and take first line (remove specialty info)
    lines = unit_identifier.split('\n')
    main_line = lines[0].strip()
    
    # Remove "Specialty:" and everything after it
    if 'Specialty:' in main_line:
        main_line = main_line.split('Specialty:')[0].strip()
    
    return main_line

def process_html_file(html_file_path):
    """Process a single HTML file and find units without addresses"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [], f"Error reading file: {e}"
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all unit containers (card-body divs that contain units)
    unit_wrappers = soup.find_all('div', class_='card-body')
    
    units_without_address = []
    total_units = len(unit_wrappers)
    
    for i, wrapper in enumerate(unit_wrappers):
        unit_identifier = extract_unit_identifier(wrapper)
        has_address, address_info = check_unit_for_address(wrapper)
        
        if not has_address:
            units_without_address.append({
                'unit_identifier': unit_identifier,
                'reason': address_info,
                'unit_index': i
            })
    
    return units_without_address, f"Processed {total_units} units"

def main():
    parser = argparse.ArgumentParser(
        description='Find unique units without address clauses in scraped HTML files',
        epilog="""
Examples:
  python scripts/find_units_without_address.py data/scraped/*/beascout_*.html
  python scripts/find_units_without_address.py data/scraped/20250824_220843/beascout_01740.html
  python scripts/find_units_without_address.py "data/scraped/*/beascout_01*.html" --unique-only
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'html_files', 
        nargs='+',
        help='HTML file paths or glob patterns (use quotes for patterns with *)'
    )
    
    parser.add_argument(
        '-s', '--summary-only', 
        action='store_true',
        help='Show only summary counts, not detailed unit lists'
    )
    
    parser.add_argument(
        '-u', '--unique-only',
        action='store_true',
        help='Show only unique units (deduplicated across all files)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true', 
        help='Show verbose output including file processing details'
    )
    
    args = parser.parse_args()
    
    # Expand glob patterns
    html_files = []
    for pattern in args.html_files:
        if '*' in pattern or '?' in pattern:
            # Handle glob patterns
            matches = glob.glob(pattern)
            html_files.extend(matches)
        else:
            html_files.append(pattern)
    
    # Filter to existing files
    existing_files = [f for f in html_files if Path(f).is_file()]
    
    if not existing_files:
        print("❌ No valid HTML files found")
        print(f"Searched patterns: {args.html_files}")
        sys.exit(1)
    
    print(f"🔍 Searching {len(existing_files)} HTML files for units without addresses")
    print("=" * 80)
    
    total_units_without_address = 0
    total_units_processed = 0
    files_with_issues = []
    unique_units = {}  # For deduplication: normalized_id -> unit_info
    
    for html_file in sorted(existing_files):
        if args.verbose:
            print(f"\n📁 Processing: {Path(html_file).name}")
        
        units_without_desc, process_info = process_html_file(html_file)
        
        # Extract total units count from process_info
        import re
        units_count_match = re.search(r'Processed (\d+) units', process_info)
        file_unit_count = int(units_count_match.group(1)) if units_count_match else 0
        total_units_processed += file_unit_count
        
        if units_without_desc:
            total_units_without_address += len(units_without_desc)
            files_with_issues.append((html_file, units_without_desc))
            
            # Track unique units
            for unit_info in units_without_desc:
                normalized_id = normalize_unit_identifier(unit_info['unit_identifier'])
                if normalized_id not in unique_units:
                    unique_units[normalized_id] = {
                        'unit_identifier': unit_info['unit_identifier'],
                        'normalized_id': normalized_id,
                        'reason': unit_info['reason'],
                        'files': [Path(html_file).name],
                        'count': 1
                    }
                else:
                    # Unit already seen - track additional files
                    unique_units[normalized_id]['files'].append(Path(html_file).name)
                    unique_units[normalized_id]['count'] += 1
            
            if not args.summary_only and not args.unique_only:
                print(f"\n📄 {Path(html_file).name} - {len(units_without_desc)} units without address:")
                for unit_info in units_without_desc:
                    print(f"  • {unit_info['unit_identifier']}")
                    print(f"    Reason: {unit_info['reason']}")
        elif args.verbose:
            print(f"  ✅ All {file_unit_count} units have addresses")
    
    # Handle unique-only output
    if args.unique_only and unique_units:
        print(f"\n📋 UNIQUE UNITS WITHOUT ADDRESSS ({len(unique_units)} unique units):")
        print("=" * 80)
        for normalized_id, unit_info in sorted(unique_units.items()):
            print(f"• {unit_info['unit_identifier']}")
            print(f"  Reason: {unit_info['reason']}")
            if unit_info['count'] > 1:
                print(f"  Found in {unit_info['count']} files: {', '.join(unit_info['files'][:3])}" + 
                      (f" and {unit_info['count']-3} more" if unit_info['count'] > 3 else ""))
            else:
                print(f"  File: {unit_info['files'][0]}")
            print()
    
    # Summary
    print(f"📊 SUMMARY:")
    print(f"  Files processed: {len(existing_files)}")
    print(f"  Total units processed: {total_units_processed}")
    print(f"  Units without addresses: {total_units_without_address}")
    print(f"  Unique units without addresses: {len(unique_units)}")
    print(f"  Files with issues: {len(files_with_issues)}")
    
    if total_units_without_address > 0:
        print(f"  Percentage missing addresses: {(total_units_without_address/total_units_processed)*100:.1f}%")
        
        if not args.summary_only and not args.unique_only:
            print(f"\n📋 FILES WITH MISSING ADDRESSS:")
            for file_path, units in files_with_issues:
                print(f"  {Path(file_path).name}: {len(units)} units")

if __name__ == "__main__":
    main()