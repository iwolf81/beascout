# BeAScout Unit Information System - Technical Architecture

**Version**: 3.0 | **Last Updated**: 2025-08-26 | **Strategy**: Production-Ready Three-Way Validation System

## Technology Stack
- **Three-Way Validation**: Key Three database (169 units) + dual-source web scraping (152 unique units)
- **Enhanced Address Parsing**: 6-pattern town extraction with MA/CT support and territory validation
- **Consistent Normalization**: unit_key format enables reliable cross-source matching and deduplication
- **Visual District Mapping**: HNE council map analysis eliminates "Special 04" database inconsistencies
- **Production-Scale Processing**: All 72 HNE zip codes (2,034 raw → 152 unique, 92% deduplication)
- **Territory Filtering**: Enhanced HNE filtering excludes non-council units (Uxbridge MA, Putnam CT)
- **Professional Reporting**: Excel commissioner reports with BOTH/KEY_THREE_ONLY/WEB_ONLY classification
- **Language**: Python 3.13+ with comprehensive parsing libraries

## Project Structure
```
beascout/
├── # Core Production System ✅
├── src/
│   ├── core/                            # ✅ Consistent normalization system
│   │   └── unit_identifier.py          # Standardized unit_key format for cross-source matching
│   │                                    # - Eliminates identifier inconsistencies
│   │                                    # - Handles town name variations (E Brookfield → East Brookfield)
│   │                                    # - Creates reliable join keys for validation
│   ├── mapping/                         # ✅ Visual district mapping system  
│   │   └── district_mapping.py         # HNE council map → town assignments
│   │                                    # - Eliminates "Special 04" database issues
│   │                                    # - 62 towns mapped to Quinapoxet/Soaring Eagle districts
│   │                                    # - Visual source of truth overrides database inconsistencies
│   ├── parsing/                         # ✅ Production-ready parsing engines
│   │   ├── key_three_parser.py         # Key Three database processing (169 active units)
│   │   │                                # - Handles all edge cases from manual analysis
│   │   │                                # - Extracts town from complex org names
│   │   │                                # - Normalizes directional abbreviations  
│   │   └── fixed_scraped_data_parser.py # Enhanced 6-pattern address parsing
│   │                                    # - Handles comma-separated directional towns
│   │                                    # - MA/CT address support with territory validation
│   │                                    # - Excludes non-HNE units (Uxbridge, Putnam CT)
│   ├── processing/                      # ✅ Massive-scale data processing
│   │   └── comprehensive_scraped_parser.py # All 72 zip codes with intelligent deduplication
│   │                                    # - Processes 2,034 raw units → 152 unique (92% efficiency)
│   │                                    # - Cross-zip deduplication using unit_key matching
│   │                                    # - Territory filtering and statistics tracking
│   ├── validation/                      # ✅ Three-way cross-validation engine
│   │   ├── three_way_validator.py       # BOTH/KEY_THREE_ONLY/WEB_ONLY classification
│   │   │                                # - Cross-references 169 Key Three vs 152 scraped units
│   │   │                                # - Identifies missing web presence and data gaps
│   │   ├── enhanced_validator.py        # Advanced validation with confidence scoring
│   │   └── targeted_unit_matcher.py     # Targeted matching for specific unit analysis
│   └── analysis/
│       └── quality_scorer.py            # Enhanced A-F quality scoring system
│                                        # - Specialized unit support (Posts/Clubs/Crews)
│                                        # - Personal email classification with 5-pass refinement
│                                        # - Human-readable recommendation identifiers
├── 
├── scripts/                              # ✅ Professional reporting and analysis scripts
│   ├── generate_commissioner_report.py  # Professional Excel reports for commissioners
│   │                                    # - 5-sheet Excel format with executive summary
│   │                                    # - BOTH/KEY_THREE_ONLY/WEB_ONLY unit classification
│   │                                    # - Action flags for commissioner follow-up
│   ├── process_full_dataset.py          # End-to-end pipeline orchestration
│   │                                    # - Coordinates all processing stages
│   │                                    # - Handles edge cases and error recovery
│   ├── analyze_identifier_matching.py   # Unit identifier analysis and debugging
│   ├── analyze_missing_units.py         # Missing unit investigation tools
│   ├── create_complete_dataset.py       # Dataset consolidation utilities
│   ├── filter_hne_units.py              # HNE territory filtering utilities
│   └── search_missing_units.py          # Targeted missing unit search tools
├── 
├── prototype/                            # ✅ Enhanced extraction and utilities
│   ├── conservative_multi_zip_scraper.py # Browser automation for all HNE zip codes
│   │                                    # - Playwright automation with exponential backoff
│   │                                    # - Dual-source BeAScout + JoinExploring
│   │                                    # - All 72 zip codes with rate limiting
│   ├── extract_all_units.py            # ✅ Dual-source extraction with HNE filtering
│   │                                    # - BeAScout + JoinExploring processing
│   │                                    # - Enhanced HNE territory filtering
│   │                                    # - Unit_town prioritization over org matching
│   │                                    # - All 6 unit types (Packs/Troops/Crews/Ships/Posts/Clubs)
│   └── multi_town_deduplication.py     # Advanced deduplication utilities
├── 
├── data/
│   ├── raw/                             # ✅ Production-scale processed data
│   │   ├── all_units_{zipcode}.json     # Raw scraped data for all 72 HNE zip codes
│   │   ├── scraped_units_comprehensive.json # 152 unique units (92% deduplication from 2,034 raw)
│   │   │                                # - Cross-zip deduplication complete
│   │   │                                # - District distribution: Quinapoxet 78, Soaring Eagle 76
│   │   │                                # - Territory filtering excludes non-HNE units
│   │   ├── key_three_comparison.json    # 169 Key Three units with web cross-reference
│   │   │                                # - BOTH_SOURCES: 142 units (84.0% web presence)
│   │   │                                # - KEY_THREE_ONLY: 27 units (missing web presence)
│   │   │                                # - WEB_ONLY: 10 units (not in Key Three)
│   │   └── key_three_parsed_units.json  # Processed Key Three database with edge cases
│   ├── output/                          # ✅ Professional reporting outputs
│   │   ├── reports/                     # Excel commissioner reports with action flags
│   │   │   └── HNE_Commissioner_Data_Quality_Report_[date].xlsx # 5-sheet professional format
│   │   ├── emails/                      # Personalized Key Three improvement emails
│   │   └── enhanced_three_way_validation_results.json # Detailed validation analysis
│   ├── feedback/                        # ✅ Edge case analysis and user feedback
│   │   ├── Rethinking_Processing.md     # Architectural guidance document
│   │   ├── missing_beascout.txt         # Units missing from web scraping
│   │   ├── unit_identifier_debug_*.md   # Parsing debugging with user annotations  
│   │   └── HNE_Commissioner_Data_Quality_Report_*_comments.xlsx # User feedback on reports
│   ├── debug/                           # ✅ System debugging and validation logs
│   │   └── unit_identifier_debug_*.log  # Detailed parsing logs for validation
│   └── zipcodes/
│       └── hne_council_zipcodes.json    # All 72 HNE Council zip codes
├── 
├── # Testing Infrastructure
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/                        # Test data fixtures
│   ├── integration/                     # Integration test directory
│   └── unit/
│       └── test_sample.py               # Sample unit test
├── 
├── # Configuration and Dependencies
├── requirements.txt                     # Python dependencies including Playwright
├── pytest.ini                          # pytest configuration
├── 
├── # Development Utilities
├── venv/                                # Python virtual environment
├── 
├── # Documentation Structure
├── README.md                            # System overview and usage examples
├── ARCHITECTURE.md                      # Technical architecture (this file)
├── SYSTEM_DESIGN.md                     # Business requirements and success metrics
├── PRODUCTION_STATUS.md                 # Current deployment status and achievements
├── COLLABORATION_LOG.md                 # AI-human development insights and lessons learned
├── SESSION_HANDOFF.md                   # Session context preservation
├── CLAUDE.md                           # AI development context and implementation status
└── LICENSE                             # Project license file
```

## System Interface Design

### Production Three-Way Validation Pipeline
```bash
# Complete production pipeline (all 72 HNE zip codes)

# Stage A: Visual District Mapping (eliminates database inconsistencies)
python src/mapping/district_mapping.py
# Output: Town → District assignments from HNE council map analysis

# Stage B: Key Three Database Processing (169 active units)
python src/parsing/key_three_parser.py
# Output: data/raw/key_three_parsed_units.json (handles all edge cases)

# Stage C: Consistent Unit Identifier Normalization
python src/core/unit_identifier.py
# Output: Standardized unit_key format for reliable cross-source matching

# Stage D: Enhanced Scraped Data Processing (all zip codes)
python src/processing/comprehensive_scraped_parser.py
# Output: data/raw/scraped_units_comprehensive.json (152 unique from 2,034 raw)

# Stage E: Three-Way Cross-Validation
python src/validation/three_way_validator.py
# Output: BOTH/KEY_THREE_ONLY/WEB_ONLY classification analysis

# Stage F: Professional Commissioner Reporting
python scripts/generate_commissioner_report.py
# Output: 5-sheet Excel report with executive summary and action flags
```

### Target Automated System Interface  
```python
# Primary system entry points
from src.processing.comprehensive_scraped_parser import ComprehensiveScrapedParser
from src.validation.three_way_validator import ThreeWayValidator
from src.reporting.commissioner_reports import CommissionerReportGenerator

# Complete data processing (all 72 zip codes)
parser = ComprehensiveScrapedParser()
scraped_results = parser.process_all_scraped_files()  # 152 unique units from 2,034 raw

# Three-way validation analysis
validator = ThreeWayValidator()
validation_results = validator.perform_comprehensive_validation()  # BOTH/KEY_THREE_ONLY/WEB_ONLY

# Professional commissioner reporting
reporter = CommissionerReportGenerator()
reporter.generate_executive_summary()  # Excel format with action flags
```

## Data Flow Architecture

### Current Three-Way Validation Pipeline (Production-Ready)
```
Key Three Database (169 units) + All HNE Zip Codes (72) → 
Enhanced Address Parsing (6 patterns) → Territory Validation → 
Consistent Normalization (unit_key format) → Cross-Source Deduplication (92% efficiency) → 
Three-Way Validation (BOTH/KEY_THREE_ONLY/WEB_ONLY) → 
Professional Commissioner Reports → Action Flag Classification
```

### Automated Monitoring Pipeline (Next Phase)
```
Scheduled Re-scraping (Biweekly) → Change Detection → 
Data Quality Trend Analysis → Unit Status Updates → 
Automated Commissioner Notifications → Dashboard Updates →
Key Three Integration for Missing Units
```

## Enhanced Address Parsing Implementation

### Six-Pattern Address Parsing Strategy
```python
ADDRESS_PARSING_PATTERNS = {
    'simple_town_state': r'^([A-Za-z\s]+)\s+(MA|CT)\s*\d*$',
    'street_city_state_zip': r',\s*([A-Za-z\s]+),\s*(MA|CT)\s+\d{5}',
    'street_city_state_no_comma': r',\s*([A-Za-z\s,]+?)\s+(MA|CT)\s+\d{5}',
    'directional_comma_town': r',\s*([A-Za-z]+),\s*([A-Za-z]+)\s+(MA|CT)',
    'concatenated_street_town': r'([A-Za-z\s]+St|Ave|Rd|Dr|Ln|Way|Blvd)([A-Za-z\s]+)\s+(MA|CT)\s+\d{5}',
    'facility_building_town': r'([A-Za-z\s]*Hall|Church|Center)([A-Za-z\s]+)\s+(MA|CT)\s+\d{5}'
}

TERRITORY_VALIDATION = {
    'exclude_non_hne': ['uxbridge', 'putnam', 'danielson', 'thompson'],
    'ma_ct_support': True,
    'directional_town_handling': True
}
```

### Current Data Structure (Enhanced JSON)

### Unit Data Schema (data/raw/scraped_units_comprehensive.json)
```json
{
  "total_unique_units": 152,
  "scraped_units": [
    {
      "unit_key": "Pack 70 Acton",
      "unit_type": "Pack",
      "unit_number": "70",
      "unit_town": "Acton",
      "chartered_organization": "Acton-Congregational Church",
      "district": "Quinapoxet",
      "data_source": "scraped",
      "meeting_location": "12 Concord Rd, Acton Congregational Church, Acton MA 01720",
      "meeting_day": "Friday",
      "meeting_time": "6:30:00 PM",
      "contact_email": "pack70acton@gmail.com",
      "contact_person": "Unit Contact",
      "phone_number": "(978) 555-0123",
      "website": "",
      "description": "Pack 70 in Acton is inclusive and open to all K-5 youth...",
      "specialty": "",
      "original_scraped_data": { /* Complete scraped unit data */ }
    }
  ],
  "parsing_stats": {
    "files_processed": 72,
    "total_raw_units": 2034,
    "unique_units": 152,
    "duplicates_removed": 1882,
    "district_distribution": {
      "Quinapoxet": 78,
      "Soaring Eagle": 76
    },
    "town_extraction_methods": {
      "unit_address": 1506,
      "unit_description": 160,
      "chartered_org": 351,
      "failed": 10
    }
  }
}
```

### Three-Way Validation Results Schema
```json
{
  "total_key_three_units": 169,
  "total_scraped_units": 152,
  "validation_results": {
    "BOTH_SOURCES": {
      "count": 142,
      "percentage": 84.0,
      "units": [/* Units found in both Key Three and web */]
    },
    "KEY_THREE_ONLY": {
      "count": 27,
      "percentage": 16.0,
      "units": [/* Units only in Key Three (missing web presence) */],
      "action_required": "Web presence creation needed"
    },
    "WEB_ONLY": {
      "count": 10,
      "percentage": 5.9,
      "units": [/* Units only on web (not in Key Three) */],
      "action_required": "Key Three registration verification needed"
    }
  }
}
```

## Unit Normalization Strategy
- **Consistent unit_key Format**: `"{unit_type} {unit_number} {unit_town}"`
- **Town Name Standardization**: Handles "E Brookfield" → "East Brookfield"
- **Number Format**: Removes leading zeros ("0070" → "70")
- **Cross-Source Matching**: Enables reliable joins between Key Three and scraped data
- **Edge Case Handling**: Processes complex organizational names and address formats

## Error Handling and Validation
- **Territory Validation**: Excludes non-HNE units (Uxbridge MA, Putnam CT)
- **Address Parsing Fallbacks**: 6 progressive patterns with graceful degradation
- **Edge Case Documentation**: Complete user feedback loop with manual annotation
- **Debug Logging**: Comprehensive parsing logs for validation and troubleshooting
- **Data Quality Assurance**: 100% parsing success with detailed statistics

## Professional Reporting Architecture
- **Executive Summary**: High-level metrics for commissioner briefings
- **Action Flag Classification**: Clear follow-up requirements for each unit
- **Multi-Sheet Excel Format**: Separate sheets for different unit categories
- **Cross-Reference Validation**: Links between Key Three and web data sources
- **Visual Data Presentation**: Charts and summaries for stakeholder communication

## Security and Data Privacy
- **Personal Information Exclusion**: No personal contact data in public repository
- **Local Data Retention**: Sensitive files kept only in local development environment
- **Anonymized Reporting**: Unit information without personal identifiers
- **Secure Processing**: All personal data processing occurs locally
- **Documentation Privacy**: Public documentation contains only system architecture

## Configuration Management
- **Environment-Based Processing**: Separate handling for development vs production data
- **Flexible Territory Definitions**: Easy updates to HNE Council boundary definitions
- **Configurable Parsing Parameters**: Adjustable address parsing patterns and thresholds
- **Modular Architecture**: Independent components for easy maintenance and updates
- **Version Control Integration**: Complete system state tracking with git workflow

## Performance and Scalability
- **Massive-Scale Processing**: 2,034 raw units processed efficiently
- **Intelligent Deduplication**: 92% efficiency in cross-zip duplicate removal
- **Memory-Efficient Processing**: Streaming JSON processing for large datasets
- **Parallel Processing Ready**: Architecture supports concurrent zip code processing
- **Incremental Updates**: System supports delta processing for ongoing monitoring