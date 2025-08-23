#!/usr/bin/env python3
"""
Email Analysis Script for BeAScout Unit Data

Analyzes contact_email fields from all_units_<zip>.json files and generates
a table showing index, contact_email, and quality classification.

Usage:
    python scripts/email_analysis.py data/raw/all_units_01720.json
    python scripts/email_analysis.py data/raw/all_units_*.json
"""

import json
import sys
import glob
from pathlib import Path
from typing import List, Tuple
import re


def is_personal_email(email: str, unit_data: dict = None) -> bool:
    """Check if email appears to be personal rather than unit-specific"""
    if not email:
        return False
    
    # Extract the local part (before @) for analysis
    local_part = email.split('@')[0].lower()
    
    # Extract unit number for comparison if available
    unit_number = None
    if unit_data:
        unit_num_str = unit_data.get('unit_number', '')
        if unit_num_str:
            # Remove leading zeros and convert to int for matching
            try:
                unit_number = int(unit_num_str.lstrip('0') or '0')
            except ValueError:
                unit_number = None
    
    # FIRST: Check for unit-specific patterns that should override personal detection
    unit_role_patterns = [
        r'^scoutmaster',
        r'^cubmaster', 
        r'^committee',
        r'^beascout',  # Platform-specific email
        r'^secretary',
        r'^info',
        r'^admin',
    ]
    
    is_unit_role = any(re.search(pattern, local_part) 
                      for pattern in unit_role_patterns)
    
    if is_unit_role:
        return False  # Unit role emails are not personal
    
    # SECOND: Check for personal identifier patterns FIRST (they override unit patterns)
    personal_patterns = [
        r'[a-z]+\.[a-z]+',             # first.last format anywhere (overrides unit context)
        r'[a-z]+\.[a-z]+\.[a-z]+',     # first.middle.last anywhere
        r'^[a-z]{3}$',                 # 3-letter initials (like DRD)
    ]
    
    has_personal_identifier = any(re.search(pattern, local_part) 
                                for pattern in personal_patterns)
    
    # If has clear personal identifiers, it's personal regardless of unit context
    if has_personal_identifier:
        return True
    
    # THIRD: Check for unit-only identifiers (no personal names mixed in)
    # These are clearly unit emails with numbers or other patterns
    unit_only_patterns = [
        r'^[a-z]*pack\d+[a-z]*$',           # pack62, westfordpack100, etc.
        r'^[a-z]*troop\d+[a-z]*$',          # troop100, etc.
        r'^[a-z]*crew\d+[a-z]*$',           # crew100, etc.
        r'^[a-z]*ship\d+[a-z]*$',           # ship100, etc.
        r'^[a-z]*scouts?[a-z]*$',           # scouts, ayerscouts, etc.
        r'^cubscout[a-z]*pack\d+[a-z]*$',   # cubscoutchelmsfordpack81, etc.
        r'^[a-z]*scoutmaster\d*[a-z]*$',    # scoutmaster1gstow, etc.
    ]
    
    has_unit_only_identifier = any(re.search(pattern, local_part) 
                                 for pattern in unit_only_patterns)
    
    if has_unit_only_identifier:
        return False  # Clear unit-only identifier - not personal
        
    # FOURTH: Check remaining personal patterns (for ambiguous cases)
    # First check for unit numbers in the email to avoid false positives
    if unit_number:
        # Look for unit number anywhere in email (with or without leading zeros)
        unit_patterns = [
            rf'\b0*{unit_number}\b',  # unit number with optional leading zeros
            rf'^{unit_number}[a-z]',  # unit number at start followed by letters (130scoutmaster)
            rf'[a-z]{unit_number}[a-z]', # unit number embedded in letters (troop195scoutmaster)
        ]
        
        has_unit_number = any(re.search(pattern, local_part) for pattern in unit_patterns)
        if has_unit_number:
            return False  # Contains unit number - not personal
    
    ambiguous_personal_patterns = [
        r'^[a-z]{2,3}[a-z]{4,8}$',     # initials + name (2-3 chars + 4-8 chars)
        r'[a-z]+[0-9]{2,4}$',          # ends with name + year/numbers (but check unit number first)
        r'[a-z]+[0-9]{1,3}$',          # ends with name + small numbers (but check unit number first)
    ]
    
    has_ambiguous_personal = any(re.search(pattern, local_part) 
                               for pattern in ambiguous_personal_patterns)
    
    # If has ambiguous personal patterns, it's personal
    if has_ambiguous_personal:
        return True
    
    # FOURTH: For emails without unit or personal identifiers, check personal domains
    personal_domains = [
        r'@gmail\.com$',
        r'@yahoo\.com$', 
        r'@hotmail\.com$',
        r'@aol\.com$',
        r'@comcast\.net$'
    ]
    
    is_personal_domain = any(re.search(pattern, email, re.IGNORECASE) 
                            for pattern in personal_domains)
    
    # If on personal domain with no unit identifiers, it's personal
    return is_personal_domain


def analyze_file(file_path: str) -> List[Tuple[int, str, str, str]]:
    """Analyze a single JSON file and return list of (index, email, quality_tag, primary_identifier)"""
    results = []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle both raw extraction files and scored files
        units = data.get('all_units', data.get('units_with_scores', []))
        
        for unit in units:
            index = unit.get('index', 0)
            email = unit.get('contact_email', '')
            primary_id = unit.get('primary_identifier', 'Unknown Unit')
            
            if not email:
                quality_tag = 'NONE'
            elif is_personal_email(email, unit):
                quality_tag = 'QUALITY_PERSONAL_EMAIL'
            else:
                quality_tag = 'GOOD'
            
            results.append((index, email, quality_tag, primary_id))
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
    
    return results


def print_table(results: List[Tuple[int, str, str, str]], file_path: str = ""):
    """Print results in a formatted table"""
    if not results:
        return
    
    if file_path:
        print(f"\n=== {Path(file_path).name} ===")
    
    # Calculate column widths with minimum 3 spaces between columns
    max_index_len = max(len(str(index)) for index, _, _, _ in results) if results else 5
    max_index_len = max(max_index_len, len('Index'))
    
    max_email_len = max(len(email if email else '(empty)') for _, email, _, _ in results) if results else 13
    max_email_len = max(max_email_len, len('Contact Email'))
    
    max_quality_len = max(len(quality_tag) for _, _, quality_tag, _ in results) if results else 13
    max_quality_len = max(max_quality_len, len('Email Quality'))
    
    # Header
    print(f"{'Index':<{max_index_len}}   {'Contact Email':<{max_email_len}}   {'Email Quality':<{max_quality_len}}   {'Unit'}")
    print(f"{'='*max_index_len}   {'='*max_email_len}   {'='*max_quality_len}   {'='*50}")
    
    # Rows
    for index, email, quality_tag, primary_id in results:
        email_display = email if email else '(empty)'
        unit_display = primary_id[:50] + '...' if len(primary_id) > 50 else primary_id
        print(f"{index:<{max_index_len}}   {email_display:<{max_email_len}}   {quality_tag:<{max_quality_len}}   {unit_display}")


def print_summary(results: List[Tuple[int, str, str, str]]):
    """Print summary statistics"""
    if not results:
        return
    
    total = len(results)
    personal_count = sum(1 for _, _, tag, _ in results if tag == 'QUALITY_PERSONAL_EMAIL')
    good_count = sum(1 for _, _, tag, _ in results if tag == 'GOOD')
    none_count = sum(1 for _, _, tag, _ in results if tag == 'NONE')
    
    print(f"\nSummary:")
    print(f"  Total units: {total}")
    print(f"  Good unit emails: {good_count} ({good_count/total*100:.1f}%)")
    print(f"  Personal emails: {personal_count} ({personal_count/total*100:.1f}%)")
    print(f"  Missing emails: {none_count} ({none_count/total*100:.1f}%)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/email_analysis.py <json_file_pattern>", file=sys.stderr)
        print("Examples:")
        print("  python scripts/email_analysis.py data/raw/all_units_01720.json")
        print("  python scripts/email_analysis.py data/raw/all_units_*.json")
        sys.exit(1)
    
    # Handle glob patterns
    file_patterns = sys.argv[1:]
    all_files = []
    for pattern in file_patterns:
        if '*' in pattern or '?' in pattern:
            all_files.extend(glob.glob(pattern))
        else:
            all_files.append(pattern)
    
    if not all_files:
        print("No matching files found", file=sys.stderr)
        sys.exit(1)
    
    # Sort files for consistent output
    all_files.sort()
    
    all_results = []
    
    for file_path in all_files:
        if not Path(file_path).exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            continue
        
        results = analyze_file(file_path)
        
        if len(all_files) > 1:
            print_table(results, file_path)
        else:
            print_table(results)
        
        all_results.extend(results)
    
    # Print combined summary if multiple files
    if len(all_files) > 1:
        print(f"\n{'='*80}")
        print("COMBINED SUMMARY")
        print_summary(all_results)
    else:
        print_summary(all_results)


if __name__ == "__main__":
    main()