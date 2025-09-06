# Development Workflow
python src/pipeline/acquisition/multi_zip_scraper.py test    # Test with 3 zip codes
python src/pipeline/acquisition/multi_zip_scraper.py full    # Process all zip codes from file

## To view and capture output (note the -u flag)
python -u src/pipeline/acquisition/multi_zip_scraper.py full 2>&1 | tee scraper_full_run_$(date +%Y%m%d_%H%M%S).log

## Parse scraped HTML unit data
python -u src/pipeline/processing/process_full_dataset.py data/scraped/20250905_000339/ 2>&1 | tee process_full_run_$(date +%Y%m%d_%H%M%S).log

## Test for regressions in parsing of scraped HTML unit data
(venv) iwolf@Iras-MacBook-Pro debug % pwd
/Users/iwolf/Repos/beascout/data/debug
(venv) iwolf@Iras-MacBook-Pro debug % alias udiff2
udiff2='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'
(venv) iwolf@Iras-MacBook-Pro debug % alias dudiff2
dudiff2='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'

**No diff output means no regressions with HNE-units**
(venv) iwolf@Iras-MacBook-Pro debug % udiff2 unit_identifier_debug_scraped_20250905_085924.log
(venv) iwolf@Iras-MacBook-Pro debug % 

**Open defects for correctly identifying towns in discarded debug logging prevent successful regression analysis of discarded units.**

# Generate MS Excel report
python src/pipeline/analysis/generate_commissioner_report.py
**A tool for automatically comparing Commissioners Reports is needed. It will help identify regressions and improvements**

# Generate unit emails
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx"