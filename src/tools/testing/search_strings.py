#!/usr/bin/env python3
"""
Search Strings Tool
Searches a set of files for each string from an input list file
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Set, Dict, Any

def load_search_strings(strings_file: Path) -> List[str]:
    """Load search strings from file, one per line"""
    try:
        with open(strings_file, 'r', encoding='utf-8') as f:
            strings = [line.strip() for line in f if line.strip()]
        return strings
    except Exception as e:
        print(f"Error loading strings file {strings_file}: {e}")
        return []

def search_string_in_file(file_path: Path, search_string: str, case_insensitive: bool = True) -> List[Dict[str, Any]]:
    """Search for a string in a file and return matches with line numbers"""
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                search_line = line.lower() if case_insensitive else line
                search_term = search_string.lower() if case_insensitive else search_string
                
                if search_term in search_line:
                    matches.append({
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'file_path': str(file_path)
                    })
    except Exception as e:
        print(f"Error searching in {file_path}: {e}")
    
    return matches

def search_strings_in_files(strings_file: Path, target_files: List[Path], 
                          case_insensitive: bool = True, output_file: Path = None) -> None:
    """Main search function"""
    
    # Load search strings
    search_strings = load_search_strings(strings_file)
    if not search_strings:
        print("No search strings found")
        return
    
    print(f"Loaded {len(search_strings)} search strings")
    print(f"Searching in {len(target_files)} files...")
    
    # Prepare output
    results = []
    
    # Search each string in all files
    for search_string in search_strings:
        string_matches = []
        
        for file_path in target_files:
            if file_path.is_file():
                matches = search_string_in_file(file_path, search_string, case_insensitive)
                string_matches.extend(matches)
        
        if string_matches:
            results.append({
                'search_string': search_string,
                'total_matches': len(string_matches),
                'matches': string_matches
            })
    
    # Output results
    output_lines = []
    total_strings_found = 0
    total_matches = 0
    
    for result in results:
        total_strings_found += 1
        total_matches += result['total_matches']
        
        output_lines.append(f"\n=== '{result['search_string']}' ({result['total_matches']} matches) ===")
        
        # Group by file for cleaner output
        file_matches = {}
        for match in result['matches']:
            file_path = match['file_path']
            if file_path not in file_matches:
                file_matches[file_path] = []
            file_matches[file_path].append(match)
        
        for file_path, matches in file_matches.items():
            output_lines.append(f"  {file_path}:")
            for match in matches:
                output_lines.append(f"    Line {match['line_number']}: {match['line_content']}")
    
    # Summary
    summary = f"\n📊 SUMMARY:"
    summary += f"\n  Search strings found: {total_strings_found}/{len(search_strings)}"
    summary += f"\n  Total matches: {total_matches}"
    summary += f"\n  Files searched: {len(target_files)}"
    
    output_lines.insert(0, summary)
    output_text = "\n".join(output_lines)
    
    # Write to output file or print
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Results written to {output_file}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            print(output_text)
    else:
        print(output_text)

def main():
    parser = argparse.ArgumentParser(description='Search for strings from a file in a set of target files')
    parser.add_argument('strings_file', help='File containing search strings (one per line)')
    parser.add_argument('target_files', nargs='+', help='Files to search in (supports wildcards)')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='Case sensitive search')
    parser.add_argument('-o', '--output', help='Output file for results')
    
    args = parser.parse_args()
    
    # Validate strings file
    strings_file = Path(args.strings_file)
    if not strings_file.exists():
        print(f"Error: Strings file not found: {strings_file}")
        sys.exit(1)
    
    # Expand target files (handle wildcards)
    target_files = []
    for pattern in args.target_files:
        if '*' in pattern or '?' in pattern:
            # Handle wildcards
            pattern_path = Path(pattern)
            if pattern_path.is_absolute():
                matches = list(pattern_path.parent.glob(pattern_path.name))
            else:
                matches = list(Path('.').glob(pattern))
            target_files.extend(matches)
        else:
            target_files.append(Path(pattern))
    
    # Filter to existing files
    existing_files = [f for f in target_files if f.is_file()]
    if not existing_files:
        print("Error: No valid target files found")
        sys.exit(1)
    
    output_file = Path(args.output) if args.output else None
    case_insensitive = not args.case_sensitive
    
    search_strings_in_files(strings_file, existing_files, case_insensitive, output_file)

if __name__ == "__main__":
    main()