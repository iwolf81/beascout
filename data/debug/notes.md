# Devlopment Notes

## Process Scraped beascout/joinexploring data

  python3 scripts/process_full_dataset.py data/scraped/20250824_220843/

  Or if you want to extract units from the HTML files:

  python3 src/legacy/extract_all_units.py data/scraped/20250824_220843/

  These scripts will parse the HTML files in that directory and extract unit information, which
  will then trigger the unit identifier debug logging system.

## Based on the codebase structure, here are the exact commands to execute the full pipeline:

  # 1. Process scraped HTML data to extract units
  python3 src/tools/utilities/process_full_dataset_v2.py data/scraped/20250824_220843/

  # 2. Generate BeAScout Quality Report (primary)
  python3 src/pipeline/reporting/generate_commissioner_report.py

  # 3. Generate district reports (legacy format - optional)
  python3 src/pipeline/reporting/generate_district_reports.py

  # 4. Generate Key Three personalized emails (optional)
  python3 src/pipeline/reporting/generate_key_three_emails.py

  These commands process the data through the complete pipeline from raw scraped HTML → parsed
  units → cross-validation → quality scoring → final reports and emails.

## Call Hierarchy for Creating Unit Record from Scraped BeAScout Data:

  1. src/tools/utilities/process_full_dataset_v2.py
     └── src/parsing/fixed_scraped_data_parser.py
         └── FixedScrapedDataParser.parse_json_file()
             └── FixedScrapedDataParser._create_standardized_record()
                 └── UnitIdentifierNormalizer.create_unit_record()
                     ├── UnitIdentifierNormalizer.normalize_unit_identifier()
                     │   ├── UnitIdentifierNormalizer._normalize_unit_type()
                     │   ├── UnitIdentifierNormalizer._normalize_unit_number()
                     │   └── UnitIdentifierNormalizer._normalize_town_name()
                     ├── get_district_for_town() [from district_mapping.py]
                     └── Debug logging → data/debug/unit_identifier_debug_<timestamp>.log

  Detailed Flow:

  1. Entry Point: src/tools/utilities/process_full_dataset_v2.py processes scraped HTML files
  2. Parser: FixedScrapedDataParser.parse_json_file() reads scraped JSON data
  3. Record Creation: _create_standardized_record() calls UnitIdentifierNormalizer.create_unit_record()
  4. Normalization:
    - normalize_unit_identifier() creates the unit_key
    - _normalize_town_name() handles village mappings (Fiskdale, Jefferson, Whitinsville)
    - get_district_for_town() assigns district from TOWN_TO_DISTRICT
  5. Debug Logging: Every call writes debug info to timestamped log file
  6. Output: Standardized unit record with unit_key, district, and all scraped fields

  The key is that UnitIdentifierNormalizer.create_unit_record() in
  /Users/iwolf/Repos/beascout/src/core/unit_identifier.py:78 is the central point where all unit
  records are standardized and debug logging occurs.

  ## When you rerun the pipeline, ask me to:

  1. Compare Before/After Debug Logs

  "Compare the new quality debug logs with the previous ones to verify these fixes:
  - Post 4879 Groton: should show QUALITY_POBOX_LOCATION instead of REQUIRED_MISSING_LOCATION
  - Troop 1 Berlin: should show RECOMMENDED_MISSING_DESCRIPTION only once (no duplicates)
  - Troop 281 Ware: should NOT show REQUIRED_MISSING_DAY or REQUIRED_MISSING_TIME flags"

  2. Spot-Check Specific Units

  "Check the scored JSON data for these specific units to verify correct field extraction:
  - Post 4879 Groton: meeting_location should contain 'PO Box 314, Groton MA 01450'
  - Troop 281 Ware: meeting_day should be 'Tuesday', meeting_time should be '6 PM'
  - Any other units with similar patterns"

  3. Pattern-Based Verification

  "Search the debug logs for patterns to verify systemic fixes:
  - All PO Box addresses should show QUALITY_POBOX_LOCATION (not REQUIRED_MISSING_LOCATION)
  - No duplicate quality flags should appear in any unit
  - Units with meeting info in descriptions should extract day/time properly"

  4. Quality Metrics Comparison

  "Compare overall quality metrics before/after to ensure improvements:
  - Average completeness scores should improve
  - Units with F grades should decrease (due to proper meeting info extraction)
  - Distribution of quality flags should be more accurate"