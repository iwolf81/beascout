#!/usr/bin/env python3
"""
Email Analysis Script for BeAScout Unit Data

Extracts contact_email fields and quality assessments from scored all_units_<zip>_scored.json files 
and displays them in a table for manual review. This script performs NO analysis or transformation - 
it only extracts existing data from already-scored JSON files.

Usage:
    python scripts/email_analysis.py data/raw/all_units_01720_scored.json
    python scripts/email_analysis.py data/raw/all_units_*_scored.json
"""

import json
import sys
import glob
from pathlib import Path
from typing import List, Tuple


def extract_from_file(file_path: str) -> List[Tuple[int, str, str, str]]:
    """Extract data from a single scored JSON file and return list of (index, email, quality_tag, primary_identifier)"""
    results = []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract from scored files (units_with_scores)
        units = data.get('units_with_scores', [])
        
        if not units:
            print(f"Warning: No 'units_with_scores' found in {file_path}. This script requires scored JSON files.", file=sys.stderr)
            return results
        
        for unit in units:
            index = unit.get('index', 0)
            email = unit.get('contact_email', '')
            primary_id = unit.get('primary_identifier', 'Unknown Unit')
            
            # Extract existing quality assessment from recommendations
            recommendations = unit.get('recommendations', [])
            
            if not email:
                quality_tag = 'NONE'
            elif 'QUALITY_PERSONAL_EMAIL' in recommendations:
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
        
        results = extract_from_file(file_path)
        
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