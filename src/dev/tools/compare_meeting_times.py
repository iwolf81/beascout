#!/usr/bin/env python3
"""
Compare meeting times between two Excel reports to show changes
"""

import pandas as pd
import sys
from pathlib import Path

def extract_meeting_times(excel_file):
    """Extract unit identifiers and meeting times from Excel report"""
    try:
        times_dict = {}
        
        # Read district sheets (Quinapoxet and Soaring Eagle)
        xl_file = pd.ExcelFile(excel_file)
        
        for sheet_name in xl_file.sheet_names:
            if sheet_name in ['Quinapoxet', 'Soaring Eagle']:
                # Read with proper header row (row 8 is the header)
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=8)
                
                # Find the columns - first column should be Unit Identifier
                # Meeting Time should be one of the columns
                unit_col = df.columns[0]  # First column is Unit Identifier
                time_col = None
                
                # Look for Meeting Time column
                for col in df.columns:
                    if 'meeting time' in str(col).lower() or 'time' in str(col).lower():
                        time_col = col
                        break
                
                # If no explicit time column, check common column positions
                if not time_col and len(df.columns) > 2:
                    # Try column index 2 (Meeting Time is often 3rd column)
                    time_col = df.columns[2] if len(df.columns) > 2 else None
                
                if time_col:
                    # Extract unit -> time mapping
                    for _, row in df.iterrows():
                        unit = str(row[unit_col]).strip() if pd.notna(row[unit_col]) else ""
                        time = str(row[time_col]).strip() if pd.notna(row[time_col]) else ""
                        if unit and unit != "nan" and not unit.startswith("Unit"):
                            times_dict[unit] = time if time != "nan" else ""
                else:
                    print(f"Could not find meeting time column in {sheet_name}")
                    print(f"Available columns: {list(df.columns)}")
        
        return times_dict
        
    except Exception as e:
        print(f"Error reading {excel_file}: {e}")
        return {}

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_meeting_times.py <old_report.xlsx> <new_report.xlsx>")
        print("\nExample:")
        print("  python scripts/compare_meeting_times.py \\")
        print("    BeAScout_Quality_Report_20250901_224619.xlsx \\")
        print("    BeAScout_Quality_Report_20250902_075344.xlsx")
        sys.exit(1)
    
    # Get file paths from command line arguments
    old_report = sys.argv[1]
    new_report = sys.argv[2]
    
    # Convert to full paths if they're just filenames
    if not old_report.startswith('/'):
        old_report = f"/Users/iwolf/Repos/beascout/data/output/reports/{old_report}"
    if not new_report.startswith('/'):
        new_report = f"/Users/iwolf/Repos/beascout/data/output/reports/{new_report}"
    
    print("📊 Comparing Meeting Times Between Reports")
    print("=" * 60)
    print(f"OLD: {Path(old_report).name}")
    print(f"NEW: {Path(new_report).name}")
    print()
    
    # Extract times from both reports
    old_times = extract_meeting_times(old_report)
    new_times = extract_meeting_times(new_report)
    
    if not old_times or not new_times:
        print("❌ Could not extract data from one or both files")
        return
    
    print(f"📋 OLD report: {len(old_times)} units")
    print(f"📋 NEW report: {len(new_times)} units")
    print()
    
    # Find changes
    changes = []
    unchanged_count = 0
    
    # Get all units from both reports
    all_units = set(old_times.keys()) | set(new_times.keys())
    
    for unit in sorted(all_units):
        old_time = old_times.get(unit, "[NOT IN OLD]")
        new_time = new_times.get(unit, "[NOT IN NEW]")
        
        if old_time != new_time:
            changes.append((unit, old_time, new_time))
        else:
            unchanged_count += 1
    
    # Report results
    print(f"🔄 CHANGES DETECTED: {len(changes)}")
    print(f"✅ UNCHANGED: {unchanged_count}")
    print()
    
    if changes:
        print("📝 MEETING TIME CHANGES:")
        print("=" * 80)
        print(f"{'UNIT IDENTIFIER':<40} {'OLD TIME':<20} {'NEW TIME':<20}")
        print("=" * 80)
        
        for unit, old_time, new_time in changes:
            # Format empty times as "(none)" for clarity
            old_display = old_time if old_time and old_time.strip() else "(none)"
            new_display = new_time if new_time and new_time.strip() else "(none)"
            
            print(f"{unit:<40} {old_display:<20} {new_display:<20}")
            
        print("=" * 80)
        print(f"\n📊 SUMMARY:")
        print(f"  • Total units processed: {len(all_units)}")
        print(f"  • Units with time changes: {len(changes)}")
        print(f"  • Units unchanged: {unchanged_count}")
        
        # Count specific types of changes
        removed_times = sum(1 for _, old, new in changes if old and old.strip() and not (new and new.strip()))
        added_times = sum(1 for _, old, new in changes if not (old and old.strip()) and new and new.strip())
        modified_times = sum(1 for _, old, new in changes if (old and old.strip()) and (new and new.strip()))
        
        print(f"  • Times removed: {removed_times}")
        print(f"  • Times added: {added_times}")
        print(f"  • Times modified: {modified_times}")
        
    else:
        print("✅ No meeting time changes detected between reports")

if __name__ == "__main__":
    main()