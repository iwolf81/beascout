#!/usr/bin/env python3
"""
Process Full Dataset - Current Version
Process scraped HTML files using current FixedScrapedDataParser pipeline to generate debug logs
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.parsing.fixed_scraped_data_parser import FixedScrapedDataParser
from src.analysis.quality_scorer import UnitQualityScorer

def extract_units_from_html(beascout_file: Path, joinexploring_file: Path, zip_code: str) -> str:
    """
    Extract units from HTML files using legacy parser, save to JSON
    Returns path to generated JSON file
    """
    print(f"  Processing BeAScout: {beascout_file}")
    print(f"  Processing JoinExploring: {joinexploring_file}")

    try:
        # Use HTML parser to extract units to JSON
        cmd = f'python3 src/parsing/html_extractor.py "{beascout_file}" "{joinexploring_file}"'
        result = os.system(cmd)

        if result == 0:
            json_file = f"data/raw/all_units_{zip_code}.json"
            if os.path.exists(json_file):
                print(f"    ✅ HTML extraction completed")
                return json_file
            else:
                print(f"    ❌ HTML extraction failed - no output file")
                return None
        else:
            print(f"    ❌ HTML extraction failed - command error")
            return None

    except Exception as e:
        print(f"    ❌ HTML parsing failed: {e}")
        return None

def process_with_current_pipeline(json_file: str, zip_code: str) -> str:
    """
    Process raw JSON through current FixedScrapedDataParser pipeline
    This will generate debug logs via UnitIdentifierNormalizer.create_unit_record()
    """
    try:
        # Use FixedScrapedDataParser to create standardized records with debug logging
        parser = FixedScrapedDataParser()
        units = parser.parse_json_file(json_file)

        print(f"    Processed {len(units)} units through current pipeline")

        # Save processed units
        processed_json = f"data/raw/all_units_{zip_code}.json"
        with open(processed_json, 'w') as f:
            json.dump(units, f, indent=2)

        return processed_json

    except Exception as e:
        print(f"    ❌ Current pipeline processing failed: {e}")
        return None

def score_units(json_file: str, zip_code: str) -> str:
    """Score units using UnitQualityScorer"""
    try:
        # Load units data
        with open(json_file, 'r') as f:
            units_data = json.load(f)

        scorer = UnitQualityScorer()
        scored_data = scorer.score_all_units({'all_units': units_data})

        scored_file = f"data/raw/all_units_{zip_code}_scored.json"
        with open(scored_file, 'w') as f:
            json.dump(scored_data, f, indent=2)

        print(f"    Quality scored {len(scored_data.get('units_with_scores', []))} units")
        return scored_file

    except Exception as e:
        print(f"    ❌ Quality scoring failed: {e}")
        return None

def process_scraped_session(session_dir: str):
    """Process a complete scraping session directory using current pipeline"""
    # Reset debug session to ensure single debug file per execution
    from src.core.unit_identifier import UnitIdentifierNormalizer
    UnitIdentifierNormalizer.reset_debug_session('scraped')

    session_path = Path(session_dir)

    if not session_path.exists():
        print(f"Session directory not found: {session_dir}")
        return

    # Find all HTML files
    beascout_files = list(session_path.glob("beascout_*.html"))
    joinexploring_files = list(session_path.glob("joinexploring_*.html"))

    print(f"Found {len(beascout_files)} BeAScout files")
    print(f"Found {len(joinexploring_files)} JoinExploring files")

    # Get unique zip codes from filenames
    zip_codes = set()
    for file in beascout_files:
        zip_code = file.stem.replace('beascout_', '')
        zip_codes.add(zip_code)

    print(f"Processing {len(zip_codes)} unique zip codes...")

    successful_files = []

    for zip_code in sorted(zip_codes):
        beascout_file = session_path / f"beascout_{zip_code}.html"
        joinexploring_file = session_path / f"joinexploring_{zip_code}.html"

        if beascout_file.exists() and joinexploring_file.exists():
            print(f"Processing ZIP {zip_code}...")

            # Step 1: Extract units from HTML
            temp_json = extract_units_from_html(beascout_file, joinexploring_file, zip_code)
            if not temp_json:
                print(f"❌ {zip_code} HTML extraction failed")
                continue

            # Step 2: Process through current pipeline (generates debug logs!)
            processed_json = process_with_current_pipeline(temp_json, zip_code)
            if not processed_json:
                print(f"❌ {zip_code} pipeline processing failed")
                continue

            # Step 3: Quality scoring
            scored_json = score_units(processed_json, zip_code)
            if not scored_json:
                print(f"❌ {zip_code} quality scoring failed")
                continue

            successful_files.append(scored_json)
            print(f"✅ {zip_code} completed successfully")

            # Clean up temp file
            try:
                os.remove(temp_json)
            except:
                pass

        else:
            print(f"⚠️  {zip_code} missing HTML files")

    print(f"\n📊 Successfully processed {len(successful_files)} zip codes")

    # Combine all scored files
    if successful_files:
        combine_datasets(successful_files)
    else:
        print("❌ No data to combine")

def combine_datasets(json_files: list):
    """Combine all scored datasets with deduplication"""
    print("Combining all scored datasets with deduplication...")

    unique_units = {}
    total_before = 0

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                units = data.get('units_with_scores', [])
                total_before += len(units)

                for unit in units:
                    unit_key = unit.get('unit_key', f"unknown_{len(unique_units)}")
                    if unit_key not in unique_units:
                        unique_units[unit_key] = unit
                    elif unit.get('completeness_score', 0) > unique_units[unit_key].get('completeness_score', 0):
                        unique_units[unit_key] = unit

        except Exception as e:
            print(f"Warning: Could not process {json_file}: {e}")

    combined_units = list(unique_units.values())

    # Calculate summary statistics
    if combined_units:
        total_score = sum(unit.get('completeness_score', 0) for unit in combined_units)
        avg_score = total_score / len(combined_units)

        combined_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'total_units': len(combined_units),
            'average_completeness_score': round(avg_score, 1),
            'deduplication_summary': {
                'units_before_dedup': total_before,
                'units_after_dedup': len(combined_units),
                'duplicates_removed': total_before - len(combined_units)
            },
            'units_with_scores': combined_units
        }

        # Save comprehensive dataset
        output_file = "data/raw/all_units_comprehensive_scored.json"
        with open(output_file, 'w') as f:
            json.dump(combined_data, f, indent=2)

        print(f"   Deduplicated from {total_before} to {len(combined_units)} unique units")
        print(f"✅ Combined {len(json_files)} datasets into comprehensive file")
        print(f"   Total units: {len(combined_units)}")
        print(f"   Average score: {avg_score:.1f}%")
        print(f"   Saved to: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/scripts/process_full_dataset_v2.py <session_directory>")
        print("Example: python3 src/scripts/process_full_dataset_v2.py data/scraped/20250824_220843/")
        sys.exit(1)

    session_dir = sys.argv[1]
    process_scraped_session(session_dir)

if __name__ == "__main__":
    main()