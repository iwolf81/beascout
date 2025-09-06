# BeAScout Unit Data Quality Monitoring System - Technical Architecture

**Version**: 5.0 | **Last Updated**: 2025-08-30 | **Status**: Production-Ready with Consolidated Data Layer

## System Overview

The BeAScout system is a production-ready data quality monitoring platform that processes three primary data sources to generate comprehensive unit quality reports for the Heart of New England Council. The system features consolidated data mappings with single source of truth, position-first town extraction logic, comprehensive debug logging, and automated report generation.

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

## 🏗️ Project Structure & Directory Organization

```
src/
├── pipeline/              # 🚀 OPERATIONAL PIPELINE (11 core files)
│   ├── acquisition/       # Data collection (2 files)
│   │   ├── multi_zip_scraper.py    # Main scraper - dual-source automation
│   │   │                          # - BeAScout.org + JoinExploring.org processing
│   │   │                          # - Rate limiting & retry logic
│   │   │                          # - Timestamped session directories
│   │   └── browser_scraper.py      # Browser automation engine
│   │                              # - Playwright-based web scraping
│   │                              # - Exponential backoff retry logic
│   │                              # - Fresh page contexts for reliability
│   ├── processing/        # Data processing (3 files)
│   │   ├── process_full_dataset.py # HTML → JSON orchestrator
│   │   │                          # - Main pipeline coordination
│   │   │                          # - Source tracking & data lineage
│   │   │                          # - Quality scoring integration
│   │   ├── html_extractor.py       # HTML parsing engine
│   │   │                          # - BeautifulSoup unit extraction
│   │   │                          # - 6-pattern address parsing
│   │   │                          # - Territory validation
│   │   └── scraped_data_parser.py  # JSON processing & quality scoring
│   │                              # - Position-first town extraction
│   │                              # - 4-source precedence logic
│   │                              # - HNE territory filtering
│   ├── analysis/          # Reports & outputs (2 files)
│   │   ├── generate_commissioner_report.py  # Excel report generation
│   │   │                                   # - Professional formatting
│   │   │                                   # - District-specific analysis
│   │   │                                   # - Quality metrics & grading
│   │   └── generate_unit_emails.py         # Unit improvement emails
│   │                                       # - Personalized recommendations
│   │                                       # - Key Three contact matching
│   │                                       # - Unit-specific action items
│   └── core/              # Shared infrastructure (4 files)
│       ├── district_mapping.py    # Town/district mapping (SINGLE SOURCE OF TRUTH)
│       │                         # - 65 HNE towns across 2 districts
│       │                         # - TOWN_TO_DISTRICT authority
│       │                         # - Village definitions & aliases
│       ├── unit_identifier.py     # Unit normalization & debug logging
│       │                         # - Standardized unit_key format
│       │                         # - Source-specific debug files
│       │                         # - Discarded unit audit trails
│       ├── quality_scorer.py      # Quality assessment system
│       │                         # - A-F grading (70% required, 30% recommended)
│       │                         # - Specialized unit type scoring
│       │                         # - Recommendation identifiers
│       └── hne_towns.py          # HNE Council town utilities
│                                 # - Town validation functions
│                                 # - Geographic boundary support
└── dev/                   # 🛠️ DEVELOPMENT TOOLS
    ├── archive/           # All deprecated/legacy code (flattened)
    ├── tools/             # Analysis utilities & scripts  
    ├── parsing/           # Alternative parsers
    ├── reporting/         # Alternative report generators
    ├── validation/        # Development validation tools
    └── scraping/          # Alternative scraping utilities

data/                      # Data organization by processing stage
├── input/                 # Source data files
├── output/               # Generated reports & emails
│   ├── reports/          # Excel commissioner reports
│   └── emails/           # Unit improvement emails
├── raw/                  # Processed JSON data
├── scraped/              # HTML scraping results
├── logs/                 # Application logs (organized)
├── feedback/             # User feedback & planning
└── debug/                # Debug & regression data

tests/                    # Test framework & regression validation
├── reference/            # Reference files for regression testing
└── verify_all.py         # Comprehensive validation runner
```

### **🏗️ Directory Organization Principles**

#### **Separation of Concerns**
- **`src/pipeline/`**: Production-critical operational code only
- **`src/dev/`**: Development tools, alternatives, and archived code
- **Clear data flow**: acquisition → processing → analysis → core

#### **Pipeline Flow Architecture**
```
Scraping → Processing → Analysis
   ↓           ↓          ↓
HTML files → JSON data → Reports/Emails
```

#### **Development vs Operations**
- **Never modify `src/pipeline/`** without full testing
- **Use `src/dev/tools/`** for analysis and debugging
- **Archive old code** in `src/dev/archive/` with clear rationale

#### **Cloud Deployment Ready**
- All operational files in single `src/pipeline/` tree
- Clear separation enables containerization
- Environment-agnostic configuration in `src/pipeline/core/`

## Key Technical Features

### Consolidated Data Layer (Single Source of Truth)
All town and district mappings consolidated to `src/mapping/district_mapping.py`:
- **TOWN_TO_DISTRICT**: 65 HNE towns with district assignments
- **TOWN_ALIASES**: Handles common variations and abbreviations
- **Validation Functions**: Town lookup, alias resolution, coverage statistics
- **Village Support**: Fiskdale, Whitinsville, Jefferson as distinct towns

### Position-First Town Extraction
Enhanced text parsing logic in `fixed_scraped_data_parser.py`:
- **Position Priority**: First occurrence in text beats longer matches
- **Hyphenated Town Fix**: "Acton-Boxborough" → "Acton" (not "Boxborough")
- **4-Source Precedence**: unit_address → unit_name → unit_description → chartered_org
- **Length Tiebreaker**: When positions equal, longer town name wins

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
│ 2. Unit Normalization & Town Extraction                                  │
│    • Standardized unit_key creation: "Pack 3 Leominster"                │
│    • Position-first town extraction with 4-source precedence rule       │
│    • Uses centralized TOWN_TO_DISTRICT mapping for consistency          │
│    • Debug logging with source identification                             │
│                                                                            │
│ 3. Territory Filtering                                                    │
│    • HNE boundary validation using consolidated district mapping         │
│    • Village-aware processing (Fiskdale, Whitinsville, Jefferson)       │
│    • Non-HNE unit exclusion with comprehensive logging                   │
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

## 🚀 Pipeline Execution Commands

### **Complete Production Pipeline**
```bash
# Step 1: Fresh data collection (30-45 minutes for all 72 zip codes)
python src/pipeline/acquisition/multi_zip_scraper.py full

# Step 2: Complete processing pipeline
python src/pipeline/processing/process_full_dataset.py data/scraped/YYYYMMDD_HHMMSS/

# Step 3: Generate BeAScout Quality Report (primary)
python src/pipeline/analysis/generate_commissioner_report.py

# Step 4: Generate Unit Improvement Emails
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx"
```

### **Process Existing Data**
```bash
# Use existing scraped data
python src/pipeline/processing/process_full_dataset.py data/scraped/20250905_000339/
python src/pipeline/analysis/generate_commissioner_report.py
```

### **Development & Validation**
```bash
# Test single zip code for development
python src/pipeline/acquisition/multi_zip_scraper.py test

# Run regression testing after processing
python src/pipeline/processing/process_full_dataset.py data/scraped/YYYYMMDD_HHMMSS/
# Compare with reference logs using verification aliases

# View latest debug logs with organized structure
ls -la data/debug/unit_identifier_debug_*$(date +%Y%m%d)*.log
ls -la data/logs/scraper_full_run_$(date +%Y%m%d)*.log
```

## Production Metrics

### Current Data Processing
- **Total Units Processed**: 308 units from dual-source scraping
- **HNE Units After Filtering**: ~150 units (territory validation)
- **Quality Assessment**: A-F grading with professional Excel reports
- **Report Format**: BeAScout Quality Reports with district organization, Key Three integration

### District Distribution  
- **Quinapoxet District**: Northern and central Massachusetts towns
- **Soaring Eagle District**: Southern and western Massachusetts towns
- **Professional Formatting**: Excel reports with borders, frozen panes, numeric quality scores

### Processing Performance
- **Zip Codes Processed**: 71 of 72 HNE zip codes (98.6% coverage)
- **Village Extraction**: 100% accurate for Fiskdale, Whitinsville, Jefferson
- **Debug Logging**: Complete audit trail with source-specific identification
- **Report Generation**: BeAScout Quality Reports with professional formatting and multi-line cell support

The system is production-ready and successfully processes the complete HNE Council unit dataset with comprehensive quality assessment and reporting capabilities.