## 🚀 **Operational Pipeline Workflow**

### **Complete Production Pipeline:**
1. **acquisition/**: Scrape BeAScout.org and JoinExploring.org
2. **processing/**: Convert HTML → JSON with quality scoring  
3. **analysis/**: Generate Excel reports and unit emails
4. **core/**: Shared utilities for all pipeline components

**IMPORTANT:** It is critical to consistently follow the **real** data workflow or the **test** data workflow.

## **Acquisition:**

### Scrape and prepare unit data from beascout.org and joinexploring.org for processing.
#### Input:
- beascout.org and joinexploring.org for zip codes of towns in Heart of New England Council
- data/zipcodes/hne_council_zipcodes.json
#### Output:
- data/scraped/YYYYMMDD_HHMMSS/beascout_<zip-code>.html
- data/scraped/YYYYMMDD_HHMMSS/joinexploring_<zip-code>.html
- data/raw/all_units_comprehensive_scored.json

```bash
# The scraped HTML files, <source>_<zip-code>.html, are written to - data/scraped/YYYYMMDD_HHMMSS/

# Development: Scrape **real** unit data for 3 zip codes for testing script
python src/pipeline/acquisition/multi_zip_scraper.py test

# Production: Scrape **real** unit data for all 71 zip codes from data/zipcodes/hne_council_zipcodes.json
# @claude - Identify dev script that creates hne_council_zipcodes.json
# @claude - Create enhancement request to specify alternate zip code file (for a different council)
python src/pipeline/acquisition/multi_zip_scraper.py full

# Optionally capture output with logging (note the -u flag; needed for tee with 1+ hour scape)
python -u src/pipeline/acquisition/multi_zip_scraper.py full 2>&1 | tee data/logs/multi_zip_scraper_$(date +%Y%m%d_%H%M%S).log

# Parse **real** scraped HTML unit data to identify quality issues
# Input: data/scraped/YYYYMMDD_HHMMSS/*.html
# Output: data/raw/all_units_comprehensive_scored.json
python -u src/pipeline/processing/process_full_dataset.py data/scraped/20250905_000339/ 2>&1 | tee data/logs/process_full_dataset_$(date +%Y%m%d_%H%M%S).log

# OR

# Parse **test** scraped HTML unit data to identify quality issues
# - No need to execute multi_zip_scraper.py
# Input: tests/reference/units/scraped/*.html
# Output: data/raw/all_units_comprehensive_scored.json
python -u src/pipeline/processing/process_full_dataset.py tests/reference/units/scraped/ 2>&1 | tee data/logs/process_full_dataset_$(date +%Y%m%d_%H%M%S).log

```

### Test for regressions in parsing of scraped HTML unit data by comparing generated debug logs, uniquely sorted, to reference debug logs.
Note: Regression test for discarded units awaits fix for unit town names - beascout issue [#5](https://github.com/iwolf81/beascout/issues/5)

#### Reference Files:
- tests/reference/units/unit_identifier_debug_scraped_reference_u.log
- tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log
#### Comparison Files:
- data/debug/unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log
- data/debug/discarded_unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log

```bash
(venv) iwolf@Iras-MacBook-Pro debug % pwd
/Users/iwolf/Repos/beascout/data/debug
(venv) iwolf@Iras-MacBook-Pro debug % alias udiff2
udiff2='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'
(venv) iwolf@Iras-MacBook-Pro debug % alias dudiff2
dudiff2='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'

# No diff output means no regressions with HNE-units
# Regression test for discarded units awaits fix for unit town names - issue [#5](https://github.com/iwolf81/beascout/issues/5)
(venv) iwolf@Iras-MacBook-Pro debug % udiff2 unit_identifier_debug_scraped_20250905_085924.log
(venv) iwolf@Iras-MacBook-Pro debug % 
```

## **Processing:**

### Anonymize **real** Key Three personal data for testing and publishing (e.g., public github).
- The Key Three leaders for a unit are authorized to update their unit's information in BeAScout.
- Their information is provided by the Council Office in a generated xlsx spreadsheet.
- This information must be anonymized for reports uploaded to github.
#### Input:
- "data/input/Key 3 08-22-2025.xlsx"
#### Output:
- tests/reference/key_three/anonymized_key_three.xlsx
- tests/reference/key_three/anonymized_key_three.json
```bash
# This step saves anonymized data in xlsx and json formats
# It only needs to be done when real Key Three data is updated
python src/dev/tools/anonymize_key_three_v2.py "data/input/Key 3 08-22-2025.xlsx" --verify
```

### Convert **real** Key Three xlsx file to json.
- Subsequent processing and analysis required the Key Three data in JSON format.
#### Input:
- "data/input/Key 3 08-22-2025.xlsx"
#### Output:
- "data/input/Key 3 08-22-2025.json"
```bash
# This step only needs to be done when **real** Key Three data is updated
# Output: "data/input/Key 3 08-22-2025.json"
python src/dev/tools/convert_key_three_to_json.py "data/input/Key 3 08-22-2025.xlsx"
```

### Correlate processed beascout.org/joinexploring.org unit data with **real** or **test** (anonymized) Key Three data.
#### Input:
- Processed Unit data: data/raw/all_units_comprehensive_scored.json
- Real Key Three data: "data/input/Key 3 08-22-2025.json" **OR**
- Test Key Three data: tests/reference/key_three/anonymized_key_three.json
#### Output:
- data/output/three_way_validation_results.json
- data/debug/cross_reference_validation_debug_YYYMMDD_HHMMSS.log
```bash
# Correlate scraped unit data with **real** Key Three data
python src/pipeline/analysis/three_way_validator.py --key-three "data/input/Key 3 08-22-2025.json"

# OR

# Correlate scraped unit data with **test** Key Three data
python src/pipeline/analysis/three_way_validator.py --key-three tests/reference/key_three/anonymized_key_three.json
```

## **Analysis:**

### **Generate Commissioner Report**
#### Input:
- Prepared unit data:   data/raw/all_units_comprehensive_scored.json
- Correlated unit data: data/output/three_way_validation_results.json
- Real Key Three data:  "data/input/Key 3 08-22-2025.json" **OR**
- Test Key Three data:  tests/reference/key_three/anonymized_key_three.json
#### Output:
- data/output/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xslx
```bash
# Notes:
# 1. process_full_dataset.py could have previously generated data/raw/all_units_comprehensive_scored.json with either **real** scraped HTML unit data or **test** scraped HTML unit data.
# 2. three_way_validator.py could have previously generated data/output/three_way_validation_results.json with either **real** Key Three data or **test** Key Three data AND with either **real** scraped HTML unit data or **test** scraped HTML unit data.
# 3. It is critical to follow the **real** or **test** workflow consistently.

# Generate MS Excel report with **real** Key Three data
python src/pipeline/analysis/generate_commissioner_report.py 2>&1 | tee data/logs/generate_commissioner_report_$(date +%Y%m%d_%H%M%S).log

# OR

# Generate MS Excel report with **test** Key Three data
python src/pipeline/analysis/generate_commissioner_report.py --key-three tests/reference/key_three/anonymized_key_three.json 2>&1 | tee data/logs/generate_commissioner_report_$(date +%Y%m%d_%H%M%S).log
```

### **Generate Unit Emails**
#### Input:
- Prepared unit data:   data/raw/all_units_comprehensive_scored.json
- Real Key Three data:  "data/input/Key 3 08-22-2025.xlsx" **OR**
- Test Key Three data:  tests/reference/key_three/anonymized_key_three.xlsx
#### Output:
- data/output/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xslx
```bash
# Generate unit improvement emails with **real** Key Three data
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx"

# Generate unit improvement emails with **test** Key Three data
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json tests/reference/key_three/anonymized_key_three.xlsx 2>&1 | tee data/logs/generate_unit_emails_$(date +%Y%m%d_%H%M%S).log
```

### **🗂️ Quick File Reference**

**Need to modify the scraper?** → `src/pipeline/acquisition/multi_zip_scraper.py`
**Data processing issues?** → `src/pipeline/processing/process_full_dataset.py`  
**Report generation?** → `src/pipeline/analysis/generate_commissioner_report.py`
**Email generation?** → `src/pipeline/analysis/generate_unit_emails.py`
**District mappings?** → `src/pipeline/core/district_mapping.py`

**Development utilities** → `src/dev/tools/`
**Old/experimental code** → `src/dev/archive/`