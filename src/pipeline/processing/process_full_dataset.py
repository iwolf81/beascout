#!/usr/bin/env python3
"""
Process Full Dataset - Current Version
Process scraped HTML files using current ScrapedDataParser pipeline to generate debug logs
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.pipeline.processing.scraped_data_parser import ScrapedDataParser

def extract_units_from_html(beascout_file: Path, joinexploring_file: Path, zip_code: str) -> str:
    """
    Extract units from HTML files using legacy parser, save to JSON
    Returns path to generated JSON file
    """
    print(f"  Processing BeAScout: {beascout_file}")
    print(f"  Processing JoinExploring: {joinexploring_file}")

    try:
        # Initialize debug session in subprocess by setting environment variable
        import os
        import datetime
        if 'UNIT_DEBUG_TIMESTAMP' not in os.environ:
            shared_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            os.environ['UNIT_DEBUG_TIMESTAMP'] = shared_timestamp
        
        # Use HTML parser to extract units to JSON with proper working directory
        # Ensure we're in the project root for proper imports
        import subprocess
        project_root = Path(__file__).parent.parent.parent.parent
        cmd = [
            'python3',
            'src/pipeline/processing/html_extractor.py',
            str(beascout_file),
            str(joinexploring_file)
        ]
        result = subprocess.run(cmd, cwd=project_root, capture_output=False)
        result = result.returncode

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
    Process raw JSON through current ScrapedDataParser pipeline
    This will generate debug logs via UnitIdentifierNormalizer.create_unit_record()
    """
    try:
        # Use ScrapedDataParser to create standardized records with debug logging
        parser = ScrapedDataParser()
        units = parser.parse_json_file(json_file)

        print(f"    Processed {len(units)} units through current pipeline")
        
        # Check if units have integrated quality data
        if units and len(units) > 0:
            first_unit = units[0]
            has_score = 'completeness_score' in first_unit
            has_grade = 'completeness_grade' in first_unit
            has_tags = 'quality_tags' in first_unit
            print(f"    Quality integration check: score={has_score}, grade={has_grade}, tags={has_tags}")

        # Ensure directory exists
        import os
        os.makedirs("data/raw", exist_ok=True)

        # Save processed units with wrapper structure for consistency with combine_datasets
        processed_json = f"data/raw/all_units_{zip_code}_processed.json"
        data_wrapper = {
            'units_with_scores': units,
            'total_units': len(units),
            'average_score': sum(u.get('completeness_score', 0) for u in units) / len(units) if units else 0.0,
            'extraction_timestamp': datetime.now().isoformat()
        }
        with open(processed_json, 'w') as f:
            json.dump(data_wrapper, f, indent=2)
            
        # Verify file was created
        if os.path.exists(processed_json):
            print(f"    ✅ File saved successfully: {processed_json}")
        else:
            print(f"    ❌ File was not created: {processed_json}")
            return None

        return processed_json

    except Exception as e:
        print(f"    ❌ Current pipeline processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_scraped_session(session_dir: str):
    """Process a complete scraping session directory using current pipeline"""
    # Reset debug session to ensure single debug file per execution
    from src.pipeline.core.unit_identifier import UnitIdentifierNormalizer
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

            # Step 2: Process through current pipeline (includes integrated quality scoring!)
            processed_json = process_with_current_pipeline(temp_json, zip_code)
            if not processed_json:
                print(f"❌ {zip_code} pipeline processing failed")
                continue

            # Quality scoring is now integrated into HTML parsing - no separate step needed
            successful_files.append(processed_json)
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
        combine_datasets(successful_files, session_dir)
    else:
        print("❌ No data to combine")

def combine_datasets(json_files: list, session_dir: str = None):
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

        # Load session metadata if session_dir is provided
        session_metadata = {}
        if session_dir:
            try:
                session_summary_path = Path(session_dir) / 'session_summary.json'
                if session_summary_path.exists():
                    with open(session_summary_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        session_metadata = {
                            'scraped_data_source': session_dir,
                            'session_summary': {
                                'session_timestamp': session_data.get('session_timestamp', ''),
                                'start_time': session_data.get('start_time', ''),
                                'end_time': session_data.get('end_time', ''),
                                'total_zip_codes': session_data.get('total_zip_codes', 0),
                                'successful_zips': session_data.get('successful_zips', 0),
                                'success_rate': session_data.get('success_rate', 0.0)
                            }
                        }
                        print(f"📅 Added source tracking for session: {session_data.get('session_timestamp', 'Unknown')}")
                else:
                    print(f"⚠️ No session_summary.json found in {session_dir}")
            except Exception as e:
                print(f"⚠️ Could not load session metadata: {e}")

        combined_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'total_units': len(combined_units),
            'average_completeness_score': round(avg_score, 1),
            'deduplication_summary': {
                'units_before_dedup': total_before,
                'units_after_dedup': len(combined_units),
                'duplicates_removed': total_before - len(combined_units)
            },
            **session_metadata,  # Include source tracking if available
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