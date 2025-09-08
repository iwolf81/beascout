# BeAScout Unit Data Quality Monitoring System

Production-ready data quality monitoring and reporting platform for Scouting America unit information across [beascout.scouting.org](https://beascout.scouting.org/) and [joinexploring.org](https://joinexploring.org/) for the Heart of New England Council (Massachusetts). The system provides comprehensive data quality auditing, automated reporting, and personalized improvement recommendations for council leadership and unit Key Three members.

## System Overview

The BeAScout system processes three primary data sources to generate comprehensive unit quality reports:
- **Key Three Database** (169 units) - Official council unit registry with leadership contacts
- **BeAScout/JoinExploring Web Data** (308+ units across 71 zip codes) - Public unit information with contact details
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
- **Position-First Town Extraction**: Enhanced text parsing prioritizes first occurrence for hyphenated towns (fixes "Acton-Boxborough" → "Acton")
- **Quality Scoring System**: Professional grading (A-F) with weighted scoring for required vs recommended fields
- **Territory Validation**: Precise HNE boundary filtering across 65 towns in Quinapoxet and Soaring Eagle districts
- **Comprehensive Debug Logging**: Source-specific debug files distinguish Key Three vs scraped data parsing with full audit trails
- **Automated Report Generation**: Excel district reports with Key Three member integration and personalized email recommendations
- **Production-Ready Pipeline**: End-to-end processing from fresh scraping through final reports with error handling and monitoring

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

**Switch modes**:
```bash
# Development mode (default - anonymized data)
export BEASCOUT_DEV_MODE=true

# Production mode (real data - use with caution)
export BEASCOUT_DEV_MODE=false

# Check current configuration
python src/pipeline/config/data_sources.py
```

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

# Search for specific issues
python scripts/search_strings.py search_terms.txt data/debug/*.log
```

### Reference Testing and Regression Validation
Compare current processing results against known good references:
```bash
# Set up verification aliases (add to ~/.zshrc)
alias verify_units='f() { code --diff ~/Repos/beascout/tests/reference/units/unit_identifier_debug_scraped_reference_u.log "$1"; }; f'
alias verify_units_discards='f() { code --diff ~/Repos/beascout/tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log "$1"; }; f'

# Run regression testing after processing
python src/pipeline/processing/process_full_dataset.py data/scraped/20250905_123456/
verify_units data/debug/unit_identifier_debug_scraped_20250905_164237_u.log

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
# Step 1: Fresh Data Scraping (30-45 minutes for all 72 zip codes)
python src/pipeline/acquisition/multi_zip_scraper.py full

# Step 2: Process Scraped Data Through Complete Pipeline
python src/pipeline/processing/process_full_dataset.py data/scraped/YYYYMMDD_HHMMSS/

# Step 3: Generate BeAScout Quality Report (Commissioner Report)
python src/pipeline/analysis/generate_commissioner_report.py

# Step 4: Generate Unit Improvement Emails
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx"
```

#### Option 2: Process Existing Scraped Data
```bash
# Use existing scraped HTML files
python src/pipeline/processing/process_full_dataset.py data/scraped/20250905_000339/
python src/pipeline/analysis/generate_commissioner_report.py
```

#### Option 3: Test Key Three Parsing Only
```bash
# Generate debug logs for Key Three parsing verification
python scripts/test_key_three_debug.py
```

# Professional Reporting
python src/pipeline/reporting/generate_commissioner_report.py  # Excel reports with BeAScout Quality analysis
```

## Quality Scoring System

**Implemented A-F grading with recommendation identifiers for Key Three outreach**

### Required Fields (70% weight)
- **Meeting location** (17.5% non-Crews, 14% Crews): Street address required, half credit for PO boxes
- **Meeting day** (17.5%/14%): Full weekday names, supports abbreviation expansion  
- **Meeting time** (17.5%/14%): Precise times with enhanced parsing (3-4 digit formats)
- **Contact email** (17.5%/14%): Unit-specific preferred, personal emails flagged for continuity
- **Specialty** (14% Venturing Crews only): Program focus area

### Recommended Fields (30% weight)  
- **Contact person** (7.5%): Unit leader or designated contact
- **Phone number** (7.5%): Direct contact method
- **Website** (7.5%): Unit-specific information page
- **Description** (7.5%): Informative program details

### Current Production Status (All 72 HNE Zip Codes)
- **Total Units Processed**: 2,034 raw scraped → 152 unique units (92% deduplication)
- **Three-Way Validation Results**: 84.0% web presence (142/169), 0% false positives
- **District Distribution**: Quinapoxet 78 units, Soaring Eagle 76 units
- **Town Extraction Success**: 74.9% address parsing, 17.4% chartered org fallback, 0.5% failed
- **Territory Filtering**: Successfully excludes non-HNE units (Connecticut, non-council MA towns)
- **Parsing Accuracy**: 100% success rate with enhanced edge case handling
- **System Status**: Production-ready with comprehensive end-to-end validation



## Project Documentation

Review and process the following markdown files **in their entirety** in the listed order:
1. **[CLAUDE.md](CLAUDE.md)**: AI development context and technical constraints
1. **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)**: Current session state and context preservation
1. **[COLLABORATION_LOG.md](COLLABORATION_LOG.md)**: AI-human collaboration insights and lessons learned
1. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: Business requirements, success metrics, operational workflows
1. **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical system design and component architecture
1. **[PRODUCTION_STATUS.md](PRODUCTION_STATUS.md)**: Current deployment status and achievements

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
- **Metric**: 61.0% average unit completeness score across 62 units
- **Validation**: 98%+ Key Three cross-referencing accuracy (1 miss out of 62 units)
- **Scalability**: System handles duplicate unit numbers, missing data, and format variations reliably
- **Recommendation**: Ready for deployment across all ~200 HNE Council units

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
