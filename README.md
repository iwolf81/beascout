# BeAScout Unit Data Quality Analysis System

Data quality analysis and reporting platform for Scouting America unit information from [beascout.org](https://beascout.scouting.org/) and [joinexploring.org](https://joinexploring.org/) for the Heart of New England Council (central Massachusetts). Generates data quality reports and personalized improvement recommendations for Council leadership and unit Key Three members (i.e., those authorized to update their unit's information).

Project development employed rapid-prototyping, specification programming, and vibe coding techniques with Anthropic's Claude Code 4 AI. [COLLABORATION_LOG.md](https://github.com/iwolf81/beascout/blob/main/COLLABORATION_LOG.md) documents AI-human collaboration evolution for best practices insight. [COLLABORATION_LESSONS.md](https://github.com/iwolf81/beascout/blob/main/COLLABORATION_LESSONS.md) summarizes technical insights and meta-insights about AI-human collaboration effectiveness from this log.

Each new Claude session initializes with markdown files from the [iwolf81/ai-context](https://github.com/iwolf81/ai-context) repository. [AI_INTERACTION_GUIDELINES.md](https://github.com/iwolf81/ai-context/blob/master/AI_INTERACTION_GUIDELINES.md) updates iteratively as new lessons emerge.  

## System Overview

The BeAScout system processes three primary data sources to generate comprehensive unit quality reports:
- **Key Three Database** (169 units) - Official council unit registry with leadership contacts
- **BeAScout/JoinExploring Web Data** (165 HNE units across 71 zip codes) - Public unit information with contact details
- **HNE Council Territory Map** (65 towns across 2 districts) - Authoritative geographic boundaries

The system features consolidated data layer with single source of truth for town mappings, position-first town extraction logic, comprehensive debug logging, and automated generation of district reports and personalized Key Three emails.

## Data Flow Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES (3)                           │
├───────────────────────────────────────────────────────────────────┤
│ BeAScout.org      │ JoinExploring.org  │ Key Three Spreadsheet    │
│ (10mi radius)     │ (20mi radius)      │ (169 units)              │
│                   │                    │                          │
│ Browser Automation│ Browser Automation │ Excel Parser             │
│ ↓                 │ ↓                  │ ↓                        │
│ HTML Files        │ HTML Files         │ Structured Data          │
└───────────────────────────────────────────────────────────────────┘
                                  │
                                  ↓
┌───────────────────────────────────────────────────────────────────┐
│                   DATA PROCESSING PIPELINE                        │
├───────────────────────────────────────────────────────────────────┤
│ 1. HTML → JSON Extraction (Legacy Parser)                         │
│ 2. Unit Town Extraction (4-source precedence with position-first) │
│ 3. Territory Filtering (65 HNE Towns using consolidated mapping)  │
│ 4. Quality Scoring (Required vs Recommended Fields)               │
│ 5. Deduplication (unit_key matching)                              │
│ 6. District Assignment (Quinapoxet vs Soaring Eagle)              │
└───────────────────────────────────────────────────────────────────┘
                                  │
                                  ↓
┌───────────────────────────────────────────────────────────────────┐
│                    OUTPUTS (2 types)                              │
├───────────────────────────────────────────────────────────────────┤
│ Excel District Reports          │ Personalized Key Three Emails   │
│ • Quinapoxet District Sheet     │ • Individual improvement plans  │
│ • Soaring Eagle District Sheet  │ • Contact information           │
│ • Quality scores & grades       │ • Specific recommendations      │
│ • Key Three member contacts     │ • Ready-to-send email format    │
└───────────────────────────────────────────────────────────────────┘
```

## Key Features

- **Automated Data Collection**: Browser automation for dual-source scraping (BeAScout + JoinExploring) with retry logic and rate limiting
- **Unit Presence Correlation System**: Comprehensive correlation between Key Three authoritative registry, BeAScout, and JoinExploring to identify missing web presence and potentially defunct units
- **Position-First Town Extraction**: Enhanced text parsing prioritizes first occurrence for hyphenated towns (fixes "Acton-Boxborough" → "Acton")
- **Quality Scoring System**: Professional grading (A-F) with weighted scoring for required vs recommended fields
- **Territory Validation**: Precise HNE boundary filtering across 65 towns in Quinapoxet and Soaring Eagle districts
- **Comprehensive Debug Logging**: Source-specific debug files distinguish Key Three vs scraped data parsing with full audit trails
- **Automated Report Generation**: Excel district reports with Key Three member integration and personalized email recommendations
- **Email Generation System**: Personalized unit improvement emails with actual contact information and specific recommendations
- **Complete Anonymization Support**: Safe development environment with full anonymized datasets for testing and development
- **Production-Ready Pipeline**: End-to-end processing from fresh scraping through final reports with error handling and monitoring

## Recent Achievements (September 2025)

**✅ Unit Presence Correlation System**
- 97.6% correlation success rate between Key Three authoritative registry (169 units) and web data (165 units), identifying missing web presence and potentially defunct units
- Perfect unit key normalization between 4-digit internal format and display format for reports  
- Comprehensive identification of units with incomplete Key Three data (10 units with <3 members)

**✅ Email Generation Complete**
- Production-ready personalized email system with actual Key Three contact information
- 100% compatibility with both real and anonymized data for safe development
- Individual improvement recommendations based on quality analysis and missing data identification

**✅ Development Infrastructure**
- Complete anonymization pipeline for safe development and testing
- GitHub issue management system established with 8 development priorities (#12-19)
- Reference testing framework prevents regressions and validates pipeline changes
- Documentation fully updated to reflect current system architecture and capabilities

## Quick Start

### System Requirements & Installation

```bash
# Clone the repository
git clone https://github.com/iwolf81/beascout.git
cd beascout

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers for web scraping
playwright install

# Verify installation
python src/core/unit_identifier.py  # Test unit identifier normalization
python scripts/test_key_three_debug.py  # Test Key Three parsing
```

## 📁 Project Structure

**For detailed directory structure and organization principles, see [ARCHITECTURE.md](ARCHITECTURE.md).**

**Quick Summary:**
- `src/pipeline/`: 11 core operational files (acquisition → processing → analysis → core)
- `src/dev/`: Development tools, alternatives, and archived code  
- `data/`: Organized by processing stage with dedicated logs
- Significant reduction in root directory clutter (clean, production-ready structure)

### **🗂️ Quick File Reference**

**Need to modify the scraper?** → `src/pipeline/acquisition/multi_zip_scraper.py`

**Data processing issues?** → `src/pipeline/processing/process_full_dataset.py`

**Report generation?** → `src/pipeline/analysis/generate_commissioner_report.py`

**Email generation?** → `src/pipeline/analysis/generate_unit_emails.py`

**District mappings?** → `src/pipeline/core/district_mapping.py`

**Data source configuration?** → `src/pipeline/config/data_sources.py`

**Development utilities** → `src/dev/tools/`

**Old/experimental code** → `src/dev/archive/`

## 🛡️ Data Safety & Privacy

**Development Mode (Default)**: System uses anonymized test data by default
- ✅ **Safe for commits** - no real personal information
- ✅ **Safe for sharing** - repository can be shared publicly  
- ✅ **Realistic testing** - maintains all data relationships
- 📁 **Test data location**: `tests/reference/key_three/anonymized_key_three.*`

**Production Mode**: Use only for generating actual reports
- ⚠️ **Contains real personal data** - DO NOT commit generated files
- 🔒 **Local use only** - never push outputs to repository
- 📁 **Real data location**: `data/input/HNE_key_three.*` (local only)

## Debug and Monitoring

### Debug Log Analysis
The system generates comprehensive debug logs for troubleshooting:

```bash
# View latest scraped data processing
cat data/debug/unit_identifier_debug_scraped_$(date +%Y%m%d)*.log | head -20

# Check Key Three parsing results  
cat data/debug/unit_identifier_debug_keythree_$(date +%Y%m%d)*.log | head -10

# Review excluded units
cat data/debug/discarded_unit_identifier_debug_*$(date +%Y%m%d)*.log

# Count unique units processed
sort -u data/debug/unit_identifier_debug_scraped_*.log | wc -l
```

### Reference Testing and Regression Validation
Compare current processing results against known good references:
```bash
# Set up verification aliases (add to ~/.zshrc)
alias udiff='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'
alias dudiff='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'

# Process scraped unit data
python src/pipeline/processing/process_full_dataset.py data/scraped/20250905_123456/

# Run regression testing after processing
udiff data/debug/unit_identifier_debug_scraped_20250905_164237.log
dudiff data/debug/discarded_unit_identifier_debug_scraped_20250905_164237.log

# Should show no differences if processing is consistent
# Any differences indicate potential regressions or improvements
```

### Required Input Files
Place these files in `data/input/` before running the pipeline:
- **Key Three Spreadsheet**: `Key 3 08-22-2025.xlsx` (or current month)
- **Council Territory Map**: HNE town boundaries (built-in to `src/pipeline/core/district_mapping.py`)
- **Optional**: Existing scraped HTML files in `data/scraped/YYYYMMDD_HHMMSS/`

### 🚀 **Operational Pipeline Execution**

#### **Complete Production Workflow:**
1. **acquisition/**: Scrape BeAScout.org and JoinExploring.org
2. **processing/**: Convert HTML → JSON with quality scoring  
3. **analysis/**: Generate Excel reports and unit emails
4. **core/**: Shared utilities for all pipeline components

#### Option 1: Full Pipeline from Fresh Scraping
```bash
# Step 1: Fresh Unit Data Scraping (60-75 minutes for all 71 zip codes)
python src/pipeline/acquisition/multi_zip_scraper.py full

# Step 2: Process Scraped Unit Data
python src/pipeline/processing/process_full_dataset.py data/scraped/YYYYMMDD_HHMMSS/

# Step 3: Convert Key Three Data from XLSX to JSON
#         This step only needs to be done when real Key Three data is updated
python src/dev/tools/convert_key_three_to_json.py "data/input/Key 3 08-22-2025.xlsx"

# Step 4: Correlate Scraped Unit Data with Key Three Authoritative Registry
python src/pipeline/analysis/three_way_validator.py --key-three "data/input/Key 3 08-22-2025.json"

# Step 5: Generate BeAScout Quality Report (Commissioner Report)
python src/pipeline/analysis/generate_commissioner_report.py

# Step 6: Generate Unit Improvement Emails
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx"
```

#### Option 2: Process Existing Scraped Data
```bash
# Use existing scraped HTML files
python src/pipeline/processing/process_full_dataset.py data/scraped/20250905_000339/
python src/pipeline/analysis/three_way_validator.py --key-three "data/input/Key 3 08-22-2025.json"
python src/pipeline/analysis/generate_commissioner_report.py
```

# Professional Reporting
```bash
python src/pipeline/reporting/generate_commissioner_report.py  # Excel reports with BeAScout Quality analysis
```

## Quality Scoring System

**Implemented A-F grading with recommendation identifiers for Key Three outreach**

### Required Fields (100% of score)
- **Meeting location** (25% standard units, 20% Crews): Street address required, half credit for PO boxes only, half credit for empty unit-address
- **Meeting day** (25%/20%): Full weekday names, supports abbreviation expansion  
- **Meeting time** (25%/20%): Precise times with enhanced parsing (3-4 digit formats)
- **Contact email** (25%/20%): Unit-specific preferred, personal emails flagged for continuity
- **Specialty** (20% Venturing Crews only): Program focus area

### Informational Fields (no scoring impact)
- **Contact person**: Unit leader or designated contact (tracked for recommendations)
- **Phone number**: Direct contact method (tracked for recommendations)
- **Website**: Unit-specific information page (tracked for recommendations)
- **Description**: Informative program details (tracked for recommendations)

### Current Production Status (All 71 HNE Zip Codes)
- **Total Units Processed**: 2,034 raw scraped → 165 unique HNE units (92% deduplication)
- **Unit Presence Correlation Results**: 97.6% correlation success (165/169), identifying missing web presence and potentially defunct units
- **District Distribution**: Quinapoxet and Soaring Eagle districts fully processed
- **Unit Key Normalization**: Fixed format consistency between 4-digit internal processing and display format
- **Territory Filtering**: Successfully excludes non-HNE units (Connecticut, non-council MA towns)
- **Email Generation**: 100% success rate with both real and anonymized data support
- **System Status**: Production-ready with complete unit presence correlation and personalized email generation


## Project Documentation

For the complete project documentation structure and reading order, see [Project Documentation Structure](CLAUDE.md#project-documentation-structure) in CLAUDE.md.

## Data Sources

- **beascout.scouting.org**: Cub Scout Packs, Scout Troops, Venturing Crews, Sea Scout Ships
- **joinexploring.org**: Exploring Posts and Clubs
- **Heart of New England Council**: Unit Key Three member contact lists

## Council Structure

The Heart of New England Council is comprised of two Districts:
- **QUINAPOXET District** (blue on council map): Northern and central Massachusetts towns
- **SOARING EAGLE District** (red on council map): Southern and western Massachusetts towns

Each District contains multiple towns, and each town may have zero or more Scout units. The BeAScout system processes units from both districts across all council territory.

## Lessons Learned and Best Practices

### Email Classification System
- **Challenge**: Distinguishing personal vs unit-specific emails (e.g., "sudburypack62@gmail.com" vs "john.smith@gmail.com")
- **Solution**: 5-tier precedence system with unit number detection and role pattern matching
- **Key Learning**: Unit numbers in email addresses (even with leading zeros) are strong indicators of unit-specific emails
- **Best Practice**: Always include organization name validation to handle duplicate unit numbers across different chartered organizations

### Organization Matching Logic
- **Challenge**: Multiple units sharing same numbers across different organizations (e.g., Troop 7012 in both Acton and Leominster)
- **Solution**: Two-stage matching with keyword extraction and flexible threshold requirements
- **Key Learning**: Stop words ("of", "the", "inc") must be filtered, but meaningful terms ("acton", "group", "citizens") provide reliable matching
- **Best Practice**: Extract organization keywords and require minimum match threshold rather than exact string matching

### Manual Review Framework
- **Challenge**: Validating 62 units worth of email classifications and scoring accuracy
- **Solution**: Systematic 5-pass review process with direct annotation in feedback files
- **Key Learning**: Commit-before-fix pattern enables easy change tracking and rollback
- **Best Practice**: Structure feedback as pass-by-pass annotations with specific index references for systematic improvement

### Data Quality and Edge Cases
- **Discovery**: Meeting times in formats like "330" (3:30 PM) and "1230" (12:30 PM) required enhanced parsing
- **Solution**: Regex patterns for 3-4 digit time formats with AM/PM inference
- **Key Learning**: Real-world data contains more format variations than initial assumptions
- **Best Practice**: Build parsing systems incrementally based on actual data patterns, not theoretical specifications

### Production Readiness Assessment
- **Metric**: 60.2% average unit completeness score across 165 HNE units
- **Validation**: 97.6% Key Three correlation accuracy (165/169 units matched between registry and web data)
- **Scalability**: System handles duplicate unit numbers, missing data, and format variations reliably
- **Recommendation**: Production-ready for all 165 HNE Council units with complete unit presence correlation

## Development

### Technology Stack
- **Python 3.8+** with Playwright for dynamic web scraping
- **BeautifulSoup** for HTML parsing and data extraction
- **pandas + openpyxl** for Excel file processing (Key Three roster)
- **JSON** for raw data storage and configuration
- **Regex** for sophisticated pattern matching and text extraction
- **pytest** for automated testing (future implementation)

### Architecture Principles
- **Modular Design**: Separate extraction, scoring, and email generation components
- **Data Pipeline**: Raw → Processed → Scored → Reports workflow
- **Manual Review Integration**: Direct feedback annotation system for continuous improvement
- **Production Safety**: Comprehensive error handling and fallback mechanisms

## Contributing

This project follows Acceptance-Test Driven Development (ATDD) principles and maintains comprehensive test coverage. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed development guidelines.

## License

[MIT License](LICENSE)

## Contact

For questions about this project or the Heart of New England Council, please contact the repository maintainer. 
