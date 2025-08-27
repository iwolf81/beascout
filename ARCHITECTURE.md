# BeAScout Unit Data Quality Monitoring System - Technical Architecture

**Version**: 4.0 | **Last Updated**: 2025-08-27 | **Status**: Production-Ready with Village-Aware Processing

## System Overview

The BeAScout system is a production-ready data quality monitoring platform that processes three primary data sources to generate comprehensive unit quality reports for the Heart of New England Council. The system features village-aware processing, comprehensive debug logging, and automated report generation.

## Core Components

### Data Sources
- **Key Three Database** (169 units): Official council unit registry from Excel exports
- **BeAScout.org** (10-mile radius search): Primary unit information platform  
- **JoinExploring.org** (20-mile radius search): Exploring/Venturing unit information
- **HNE Territory Map** (65 towns, 2 districts): Authoritative geographic boundaries

### Processing Pipeline
```
Raw Data → HTML/Excel → JSON → Normalized → Scored → Reports
   ↓           ↓          ↓        ↓         ↓        ↓
Scraping   Parsing   Extraction  Quality   Final   Output
```

## Project Structure

```
src/                                 # All production code (organized by function)
├── core/                           # ✅ Core system components
│   └── unit_identifier.py         # Unit normalization with debug logging
│                                   # - Creates standardized unit_key format
│                                   # - Handles village extraction (Fiskdale, Whitinsville, Jefferson)
│                                   # - Source-specific debug file generation
│                                   # - Discarded unit logging with audit trails
├── mapping/                        # ✅ Geographic data management  
│   └── district_mapping.py        # HNE territory definitions
│                                   # - 65 towns across Quinapoxet/Soaring Eagle districts
│                                   # - Centralized TOWN_TO_DISTRICT dictionary
│                                   # - Village definitions as separate towns
├── parsing/                        # ✅ Data parsing engines
│   ├── fixed_scraped_data_parser.py # Scraped HTML processor
│   │                               # - Village-priority extraction logic
│   │                               # - 6-pattern address parsing
│   │                               # - HNE territory filtering
│   │                               # - Comprehensive error handling
│   └── key_three_parser.py        # Excel spreadsheet processor  
│                                   # - 169 unit processing with edge case handling
│                                   # - Sophisticated town extraction (9 patterns)
│                                   # - Debug logging integration
├── scraping/                       # ✅ Data collection (when needed)
│   ├── browser_scraper.py         # Playwright automation
│   └── url_generator.py           # Search URL creation
├── analysis/                       # ✅ Data quality assessment
│   └── quality_scorer.py          # Unit completeness scoring
│                                   # - Required vs recommended field weighting
│                                   # - A-F grading system
│                                   # - Specialized scoring for unit types
├── scripts/                        # ✅ Production pipeline scripts
│   ├── process_full_dataset_v2.py      # Main pipeline orchestration
│   ├── generate_district_reports.py    # Excel report generation
│   ├── generate_key_three_emails.py    # Personalized email creation
│   ├── create_authoritative_dataset.py # Dataset consolidation
│   └── generate_commissioner_report.py # Executive summary reports
└── legacy/                         # ✅ Legacy tools (still used)
    └── extract_all_units.py       # HTML → JSON conversion

scripts/                            # Utility & testing scripts
├── search_strings.py              # Multi-file search tool
└── test_key_three_debug.py        # Key Three parser validation

data/                              # All data files (organized by stage)
├── input/                         # Source data files
│   └── Key 3 08-22-2025.xlsx     # Monthly Key Three export
├── scraped/                       # Raw HTML from websites  
│   └── YYYYMMDD_HHMMSS/          # Timestamped scraping sessions
├── raw/                          # Processed JSON data
│   └── all_units_comprehensive_scored.json # Final consolidated dataset
├── debug/                        # Debug & audit logs
│   ├── unit_identifier_debug_scraped_*.log      # Scraped data processing
│   ├── unit_identifier_debug_keythree_*.log     # Key Three processing  
│   └── discarded_unit_identifier_debug_*.log    # Excluded units
├── output/                       # Final reports
│   ├── reports/                  # Excel district reports
│   └── emails/                   # Generated Key Three emails
└── feedback/                     # Analysis & documentation

archive/                          # Deprecated code (historical reference)
```

## Key Technical Features

### Village-Aware Processing
The system correctly identifies and processes village units that were causing cross-validation failures:
- **Fiskdale** (within Sturbridge) - 2-3 units
- **Whitinsville** (within Northbridge) - 2 units  
- **Jefferson** (within Holden) - 1 unit

### Debug Logging System
Comprehensive audit trails distinguish between data sources:
- `unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log`
- `unit_identifier_debug_keythree_YYYYMMDD_HHMMSS.log`  
- `discarded_unit_identifier_debug_SOURCE_YYYYMMDD_HHMMSS.log`

### Quality Scoring Algorithm
- **Required Fields** (70% weight): Location, meeting day/time, contact email, unit composition
- **Recommended Fields** (30% weight): Contact person, phone, website, description
- **Grading Scale**: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- **Penalties**: Half credit for PO Box locations, personal email addresses

### Territory Management
- **65 HNE Towns**: Definitive list with district assignments
- **2 Districts**: Quinapoxet (29 towns), Soaring Eagle (36 towns)
- **Boundary Filtering**: Excludes non-HNE units (e.g., Uxbridge MA, Connecticut towns)

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INPUT STAGE (3 Sources)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Web Scraping (BeAScout + JoinExploring)                                │
│    • 71 zip codes × 2 websites = 142 HTML files                           │
│    • Rate-limited browser automation                                      │
│    • Exponential backoff retry logic                                      │
│                                                                            │
│ 2. Key Three Excel Processing                                             │
│    • Monthly export with 169 active units                                │
│    • Sophisticated town extraction (9 patterns)                          │
│    • Contact information integration                                      │
│                                                                            │
│ 3. Territory Mapping                                                      │
│    • 65 towns across 2 districts                                         │
│    • Village definitions as separate entities                             │
│    • Geographic boundary validation                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROCESSING STAGE (6 Steps)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. HTML → JSON Extraction                                                 │
│    • Legacy parser processes HTML to structured JSON                      │
│    • Unit container identification and data extraction                    │
│                                                                            │
│ 2. Unit Normalization & Village Processing                               │
│    • Standardized unit_key creation: "Pack 3 Leominster"                │
│    • Village-priority extraction (Fiskdale, Whitinsville, Jefferson)     │
│    • Debug logging with source identification                             │
│                                                                            │
│ 3. Territory Filtering                                                    │
│    • HNE boundary validation using TOWN_TO_DISTRICT mapping              │
│    • Non-HNE unit exclusion with logging                                 │
│                                                                            │
│ 4. Quality Scoring                                                        │
│    • Weighted field analysis (70% required, 30% recommended)             │
│    • A-F grade assignment                                                 │
│    • Improvement recommendations generation                                │
│                                                                            │
│ 5. Deduplication                                                          │
│    • Cross-zip unit_key matching                                         │
│    • Best-score unit retention                                           │
│                                                                            │
│ 6. District Assignment & Key Three Integration                           │
│    • Town → District mapping                                             │
│    • Key Three member contact matching                                    │
│    • Final dataset consolidation                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT STAGE (2 Types)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Excel District Reports                                                │
│    • HNE_Council_BeAScout_Report_YYYYMMDD_HHMMSS.xlsx                   │
│    • Separate sheets for Quinapoxet and Soaring Eagle districts          │
│    • Quality scores, grades, and specific recommendations                 │
│    • Key Three member contact information (up to 3 per unit)             │
│    • Professional formatting for commissioner distribution                 │
│                                                                            │
│ 2. Personalized Key Three Emails                                         │
│    • Individual improvement plans for unit leaders                        │
│    • Specific, actionable recommendations                                 │
│    • Contact information and next steps                                   │
│    • Ready-to-send email format                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Execution Commands

### Complete Pipeline (Fresh Scraping)
```bash
# Step 1: Fresh data collection (30-45 minutes)
python src/scraping/browser_scraper.py --all-zipcodes --output data/scraped/$(date +%Y%m%d_%H%M%S)/

# Step 2: Complete processing pipeline
python src/scripts/process_full_dataset_v2.py data/scraped/YYYYMMDD_HHMMSS/

# Step 3: Generate district reports  
python src/scripts/generate_district_reports.py data/raw/all_units_comprehensive_scored.json --output-dir data/output/reports/

# Step 4: Generate personalized emails (optional)
python src/scripts/generate_key_three_emails.py data/raw/all_units_comprehensive_scored.json
```

### Process Existing Data
```bash
# Use existing scraped data
python src/scripts/process_full_dataset_v2.py data/scraped/20250824_220843/
python src/scripts/generate_district_reports.py data/raw/all_units_comprehensive_scored.json --output-dir data/output/reports/
```

### Debug & Validation  
```bash
# Test Key Three parsing
python scripts/test_key_three_debug.py

# Search across multiple files
python scripts/search_strings.py search_terms.txt data/debug/*.log

# View latest debug logs
ls -la data/debug/unit_identifier_debug_*$(date +%Y%m%d)*.log
```

## Production Metrics

### Current Data Processing
- **Total Units Processed**: 308 units from dual-source scraping
- **HNE Units After Filtering**: 156 units (territory validation)
- **Average Quality Score**: 62.8%
- **Grade Distribution**: A(57), B(48), C(32), D(25), F(146)

### District Distribution  
- **Quinapoxet District**: 96 units across 29 towns
- **Soaring Eagle District**: 55 units across 36 towns (includes 5 units from unknown district classification)

### Processing Performance
- **Zip Codes Processed**: 71 of 72 HNE zip codes (98.6% coverage)
- **Village Extraction**: 100% accurate for Fiskdale, Whitinsville, Jefferson
- **Debug Logging**: Complete audit trail with source-specific identification
- **Report Generation**: Professional Excel reports with Key Three integration

The system is production-ready and successfully processes the complete HNE Council unit dataset with comprehensive quality assessment and reporting capabilities.