#!/usr/bin/env python3
"""
Process Full 72-Zip Dataset
Extract units from all scraped HTML files and generate council report
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def process_scraped_session(session_dir: str):
    """Process a complete scraping session directory"""
    session_path = Path(session_dir)
    
    if not session_path.exists():
        print(f"Session directory not found: {session_dir}")
        return
    
    # Find all HTML files
    beascout_files = list(session_path.glob("beascout_*.html"))
    joinexploring_files = list(session_path.glob("joinexploring_*.html"))
    
    print(f"Found {len(beascout_files)} BeAScout files")
    print(f"Found {len(joinexploring_files)} JoinExploring files")
    
    # Extract units from each zip code
    all_json_files = []
    
    # Get unique zip codes from filenames
    zip_codes = set()
    for file in beascout_files:
        zip_code = file.stem.replace('beascout_', '')
        zip_codes.add(zip_code)
    
    print(f"Processing {len(zip_codes)} unique zip codes...")
    
    for zip_code in sorted(zip_codes):
        beascout_file = session_path / f"beascout_{zip_code}.html"
        joinexploring_file = session_path / f"joinexploring_{zip_code}.html"
        
        if beascout_file.exists() and joinexploring_file.exists():
            print(f"Processing ZIP {zip_code}...")
            
            # Run extraction
            cmd = f'python3 prototype/extract_all_units.py "{beascout_file}" "{joinexploring_file}"'
            result = os.system(cmd)
            
            if result == 0:
                # Run quality scoring
                json_file = f"data/raw/all_units_{zip_code}.json"
                if os.path.exists(json_file):
                    cmd = f'python3 src/analysis/quality_scorer.py "{json_file}"'
                    result = os.system(cmd)
                    
                    if result == 0:
                        scored_file = f"data/raw/all_units_{zip_code}_scored.json"
                        if os.path.exists(scored_file):
                            all_json_files.append(scored_file)
                            print(f"✅ {zip_code} completed")
                        else:
                            print(f"❌ {zip_code} scoring failed - no output file")
                    else:
                        print(f"❌ {zip_code} scoring failed - command error")
                else:
                    print(f"❌ {zip_code} extraction failed - no output file")
            else:
                print(f"❌ {zip_code} extraction failed - command error")
        else:
            print(f"⚠️  {zip_code} missing HTML files")
    
    print(f"\n📊 Successfully processed {len(all_json_files)} zip codes")
    
    # Combine all scored JSON files into comprehensive dataset with deduplication
    if all_json_files:
        print("Combining all scored datasets with deduplication...")
        unique_units = {}  # Use primary_identifier as key to deduplicate
        
        for json_file in all_json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    for unit in data.get('units_with_scores', []):
                        identifier = unit.get('primary_identifier', f"unknown_{len(unique_units)}")
                        if identifier not in unique_units:
                            unique_units[identifier] = unit
                        # If duplicate found, keep the one with higher completeness score
                        elif unit.get('completeness_score', 0) > unique_units[identifier].get('completeness_score', 0):
                            unique_units[identifier] = unit
                            
            except Exception as e:
                print(f"Warning: Could not process {json_file}: {e}")
        
        # Convert back to list and recalculate summary statistics
        combined_units = list(unique_units.values())
        
        # Recalculate grade summary based on deduplicated units
        grade_summary = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        total_score = 0
        for unit in combined_units:
            grade = unit.get('completeness_grade', 'F')
            if grade in grade_summary:
                grade_summary[grade] += 1
            total_score += unit.get('completeness_score', 0)
        
        # Calculate combined average score
        average_score = round(total_score / len(combined_units), 1) if combined_units else 0
        
        print(f"   Deduplicated from {sum(len(json.load(open(f, 'r')).get('units_with_scores', [])) for f in all_json_files)} to {len(combined_units)} unique units")
        
        # Create comprehensive dataset
        comprehensive_data = {
            'total_units': len(combined_units),
            'scoring_summary': grade_summary,
            'average_score': average_score,
            'units_with_scores': combined_units
        }
        
        # Save comprehensive dataset
        comprehensive_file = 'data/raw/all_units_comprehensive_scored.json'
        with open(comprehensive_file, 'w') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Combined {len(all_json_files)} datasets into comprehensive file")
        print(f"   Total units: {len(combined_units)}")
        print(f"   Average score: {average_score}%")
        print(f"   Saved to: {comprehensive_file}")
        
        # Generate council report from comprehensive dataset
        print("Generating comprehensive council report...")
        cmd = f'python3 scripts/generate_district_reports.py "{comprehensive_file}"'
        result = os.system(cmd)
        
        if result == 0:
            print("✅ Comprehensive council report generated successfully")
        else:
            print("❌ Council report generation failed")
    else:
        print("❌ No data to generate report")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/process_full_dataset.py <session_directory>")
        print("Example: python scripts/process_full_dataset.py data/scraped/20250824_220843")
        sys.exit(1)
    
    session_dir = sys.argv[1]
    process_scraped_session(session_dir)