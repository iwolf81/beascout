## 🚀 **Operational Pipeline Workflow**

### **Weekly Reports Pipeline (Recommended):**
For comprehensive weekly quality reports with automated email drafts:
```bash
# Complete weekly pipeline (scraping → processing → reporting → analytics → email)
python src/pipeline/operation/generate_weekly_report.py

# See WEEKLY_REPORT_WORKFLOW.md for complete documentation
```

### **Complete Production Pipeline (Manual):**
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
(venv) iwolf@Iras-MacBook-Pro logs % alias udiff
udiff='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'
(venv) iwolf@Iras-MacBook-Pro debug % alias dudiff
dudiff='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'

# No diff output means no regressions with HNE-units
# Regression test for discarded units awaits fix for unit town names - issue [#5](https://github.com/iwolf81/beascout/issues/5)
(venv) iwolf@Iras-MacBook-Pro debug % udiff unit_identifier_debug_scraped_20250905_085924.log
(venv) iwolf@Iras-MacBook-Pro debug % 
```

## **Processing:**

### Anonymize **real** Key Three personal data for testing and publishing (e.g., public github).
- The Key Three leaders for a unit are authorized to update their unit's information in BeAScout.
- Their information is provided by the Council Office in a generated xlsx spreadsheet.
- This information must be anonymized for reports uploaded to github.

#### Two-Step Anonymization Process:

**Step 1: Anonymize Excel File**
#### Input:
- "data/input/Key 3 08-22-2025.xlsx"
#### Output:
- tests/reference/key_three/anonymized_key_three.xlsx
```bash
# Anonymize personal data while preserving organizational structure
# NOTE: Each run generates new random fake data (names, emails, phones, addresses)
python src/dev/tools/anonymize_key_three.py "data/input/Key 3 08-22-2025.xlsx" --verify
```

**Step 2: Convert to JSON for Pipeline Use**
#### Input:
- tests/reference/key_three/anonymized_key_three.xlsx
#### Output:
- tests/reference/key_three/anonymized_key_three.json
```bash
# Convert anonymized Excel to clean JSON format expected by pipeline
python src/dev/tools/convert_key_three_to_json.py tests/reference/key_three/anonymized_key_three.xlsx
```

**🔄 Important Notes:**
- Only regenerate when real Key Three data is updated
- Each anonymization run produces different (but valid) fake personal data - new random data is generated each time
- For regression testing, use current `tests/reference/key_three/anonymized_key_three.xlsx` and `anonymized_key_three.json` as baseline (generated with cleaned-up code)

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

## **Town/District Data Management:**

### **Complete HNE Territory Definition Workflow**

The HNE Council territory data flows through a defined pipeline from visual source to scraper input:

```
HNE_council_map.png (visual source)
    ↓ (iterative AI-human analysis)
src/pipeline/core/district_mapping.py (authoritative towns/districts)
    ↓ (automated zip code assignment)
src/pipeline/core/hne_towns.py (adds zip codes)
    ↓ (generates JSON output)
data/zipcodes/hne_council_zipcodes.json (scraper input)
```

#### **Step 1: Authoritative Source**
- **Input**: `data/input/HNE_council_map.png` (visual district boundaries)
- **Process**: Iterative AI-human analysis to extract towns and district assignments
- **Output**: `src/pipeline/core/district_mapping.py` (65 towns/villages with districts)
- **Status**: **Complete and stable** - contains all HNE towns plus villages (Jefferson, Fiskdale, Whitinsville)

#### **Step 2: Zip Code Assignment**
- **Input**: `src/pipeline/core/district_mapping.py` (authoritative towns)
- **Process**: Automated zip code lookup and assignment
- **Script**: `python src/pipeline/core/hne_towns.py`
- **Output**: `data/zipcodes/hne_council_zipcodes.json` (65 towns, 75 zip codes)

#### **Step 3: Scraper Integration**
- **Input**: `data/zipcodes/hne_council_zipcodes.json`
- **Usage**: `src/pipeline/acquisition/multi_zip_scraper.py` reads all_zipcodes array
- **Coverage**: Complete HNE territory (both districts, all villages)

#### **Regeneration Commands**
```bash
# Regenerate zip codes from authoritative town/district source
python src/pipeline/core/hne_towns.py

# Update regression test reference data
cp data/zipcodes/hne_council_zipcodes.json tests/reference/towns/hne_council_zipcodes.json
```

#### **Key Design Principles**
- **Single Source of Truth**: `district_mapping.py` is the definitive HNE territory authority
- **Automated Propagation**: Zip code generation prevents manual synchronization errors
- **Village Support**: Jefferson, Fiskdale, Whitinsville treated as separate towns for unit identification
- **Future USPS Integration**: Current manual zip codes can be replaced with USPS lookup API

---

### **🗂️ Quick File Reference**

**Need to modify the scraper?** → `src/pipeline/acquisition/multi_zip_scraper.py`
**Data processing issues?** → `src/pipeline/processing/process_full_dataset.py`
**Report generation?** → `src/pipeline/analysis/generate_commissioner_report.py`
**Email generation?** → `src/pipeline/analysis/generate_unit_emails.py`
**District mappings?** → `src/pipeline/core/district_mapping.py`
**Territory zip codes?** → `src/pipeline/core/hne_towns.py`

**Development utilities** → `src/dev/tools/`
**Old/experimental code** → `src/dev/archive/`