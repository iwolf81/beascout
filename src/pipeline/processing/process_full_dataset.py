#!/usr/bin/env python3
"""
Process Full Dataset - Current Version
Process scraped HTML files using current ScrapedDataParser pipeline to generate debug logs
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.pipeline.processing.scraped_data_parser import ScrapedDataParser
from src.pipeline.core.session_utils import SessionManager, session_logging

def extract_units_from_html(beascout_file: Path, joinexploring_file: Path, zip_code: str, session_manager: SessionManager = None) -> str:
    """
    Extract units from HTML files using legacy parser, save to JSON
    Returns path to generated JSON file
    """
    # These detailed messages go to log file only in terminal_terse mode
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
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        # Print subprocess output (will go to log file in terminal_terse mode)
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='')

        result_code = result.returncode

        if result_code == 0:
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

def process_with_current_pipeline(json_file: str, zip_code: str, session_manager: SessionManager = None) -> str:
    """
    Process raw JSON through current ScrapedDataParser pipeline
    This will generate debug logs via UnitIdentifierNormalizer.create_unit_record()
    """
    try:
        # Use ScrapedDataParser to create standardized records with debug logging
        parser = ScrapedDataParser()
        units = parser.parse_json_file(json_file)

        # These detailed messages go to log file only in terminal_terse mode
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


def process_scraped_session_with_terse_output(session_dir: str, session_manager: SessionManager, verbose: bool):
    """Process a scraped session with terse terminal output and full logging"""

    # In terse mode, show only zip code progress and final summary to terminal
    # All detailed output goes to log file

    session_path = Path(session_dir)
    if not session_path.exists():
        session_manager.terse_print(f"❌ Session directory not found: {session_dir}")
        return

    # Find all HTML files and determine zip codes to process
    beascout_files = list(session_path.glob("beascout_*.html"))
    joinexploring_files = list(session_path.glob("joinexploring_*.html"))

    # Get unique zip codes from filenames
    zip_codes = set()
    for file in beascout_files:
        zip_code = file.stem.replace('beascout_', '')
        zip_codes.add(zip_code)

    # Show initial progress
    session_manager.terse_print(f"Processing {len(zip_codes)} unique zip codes...")

    # Process each zip code with minimal terminal feedback
    successful_files = []
    for zip_code in sorted(zip_codes):
        beascout_file = session_path / f"beascout_{zip_code}.html"
        joinexploring_file = session_path / f"joinexploring_{zip_code}.html"

        if beascout_file.exists() and joinexploring_file.exists():
            # Show zip code being processed (terse terminal output)
            session_manager.terse_print(f"Processing ZIP {zip_code}...")

            # Do the actual processing (detailed output goes to log)
            temp_json = extract_units_from_html(beascout_file, joinexploring_file, zip_code, session_manager)
            if temp_json:
                processed_json = process_with_current_pipeline(temp_json, zip_code, session_manager)
                if processed_json:
                    successful_files.append(processed_json)
                    # Clean up temp file
                    try:
                        os.remove(temp_json)
                    except:
                        pass

    # Combine datasets (detailed output goes to log)
    if successful_files:
        combine_datasets(successful_files, session_dir)

    # Show final summary on terminal (matches the expected format from Pass 3 feedback)
    session_manager.terse_print(f"📊 Successfully processed {len(successful_files)} zip codes")
    session_manager.terse_print("Combining all scored datasets with deduplication...")

    # Try to extract final summary information for terminal display
    try:
        with open("data/raw/all_units_comprehensive_scored.json", 'r') as f:
            data = json.load(f)
            total_units = data.get('total_units', 0)
            avg_score = data.get('average_completeness_score', 0)
            session_timestamp = data.get('session_summary', {}).get('session_timestamp', 'Unknown')

            session_manager.terse_print(f"📅 Added source tracking for scraped unit data from session: {session_timestamp}")
            dedup_info = data.get('deduplication_summary', {})
            if dedup_info:
                before = dedup_info.get('units_before_dedup', 0)
                after = dedup_info.get('units_after_dedup', 0)
                session_manager.terse_print(f"   Deduplicated from {before} to {after} unique units")

            session_manager.terse_print("✅ Combined datasets into comprehensive file")
            session_manager.terse_print(f"   Total units: {total_units}")
            session_manager.terse_print(f"   Average score: {avg_score}%")
            session_manager.terse_print("   Saved to: data/raw/all_units_comprehensive_scored.json")
    except Exception:
        # If we can't read the final file, just show basic completion
        session_manager.terse_print("✅ Processing completed")


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
    # These detailed messages go to log file only in terminal_terse mode
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
                        print(f"📅 Added source tracking for scraped unit data from session: {session_data.get('session_timestamp', 'Unknown')}")
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
    """Main function with session management and logging support"""
    parser = argparse.ArgumentParser(
        description="Process scraped HTML files using current ScrapedDataParser pipeline"
    )
    parser.add_argument('session_directory', help='Directory containing scraped HTML files')

    # Add session management arguments
    session_manager = SessionManager()
    session_manager.add_session_args(parser)

    args = parser.parse_args()

    # Create session manager from arguments
    if args.session_id:
        session_manager = SessionManager.from_args(args)

    # Use terminal_terse mode for regression testing - always terse terminal, full logs
    with session_logging(session_manager, "process_full_dataset",
                        log_enabled=args.log, verbose=args.verbose, terminal_terse=True):

        # Process the scraped session with terse terminal output
        process_scraped_session_with_terse_output(args.session_directory, session_manager, args.verbose)

if __name__ == "__main__":
    main()