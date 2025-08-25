# BeAScout Unit Information System - Technical Architecture

**Version**: 2.0 | **Last Updated**: 2025-08-24 | **Strategy**: Production-Ready Dual-Source System

## Technology Stack
- **Dual-Source Scraping**: Playwright for browser automation (BeAScout + JoinExploring)
- **HTML Parsing**: BeautifulSoup for unit data extraction from dynamic content
- **Browser Automation**: Retry logic with exponential backoff and jitter
- **Data Processing**: JSON for structured unit data with quality scoring
- **Unit Types**: Packs, Troops, Crews, Ships, Posts, Clubs (all 6 types)
- **Reporting**: Personalized Key Three emails and Excel district reports
- **Territory Filtering**: HNE Council boundary validation with town prioritization
- **Language**: Python 3.13+ with Playwright dependency

## Project Structure
```
beascout/
├── # Core Production System ✅
├── src/
│   ├── scraping/                         # ✅ Dual-source browser automation
│   │   ├── browser_scraper.py           # Playwright automation with exponential backoff retry
│   │   │                                # - BeAScout + JoinExploring integration
│   │   │                                # - Common retry logic with jitter
│   │   │                                # - Fresh page contexts for retries
│   │   └── url_generator.py             # URL generation for both platforms
│   │                                    # - Proper array parameter encoding
│   │                                    # - Configurable radius and unit types
│   ├── analysis/
│   │   └── quality_scorer.py            # ✅ Enhanced quality scoring system
│   │                                    # - Specialized unit support (Posts/Clubs/Crews)
│   │                                    # - Personal email classification with 5-pass refinement
│   │                                    # - Human-readable recommendation identifiers
│   ├── scrapers/                        # 🔄 Legacy single-source scrapers (deprecated)
│   │   ├── base_scraper.py              # Original scraping infrastructure
│   │   └── beascout_scraper.py          # Pre-Playwright BeAScout scraper
│   ├── notifications/                   # Empty directory
│   └── storage/                         # Empty directory
├── 
├── scripts/                              # ✅ Production automation scripts
│   ├── generate_key_three_emails.py     # Personalized Key Three email generation
│   │                                    # - Actual HNE Key Three contact integration
│   │                                    # - Unit-specific improvement recommendations
│   │                                    # - Email cleanup system (removes old emails)
│   ├── generate_district_reports.py     # Excel district reports
│   │                                    # - Quinapoxet District operational
│   │                                    # - Unit quality metrics and recommendations
│   ├── email_analysis.py                # Email classification validation tool for manual reviews
│   └── convert_key_three_to_json.py     # Key Three data management utility
├── 
├── prototype/                            # ✅ Enhanced extraction and utilities
│   ├── extract_all_units.py            # ✅ Dual-source extraction with HNE filtering
│   │                                    # - BeAScout + JoinExploring processing
│   │                                    # - Enhanced HNE territory filtering
│   │                                    # - Unit_town prioritization over org matching
│   │                                    # - All 6 unit types (Packs/Troops/Crews/Ships/Posts/Clubs)
│   ├── extract_hne_towns.py            # Council territory analysis
│   ├── analyze_data.py                  # Legacy analysis script
│   ├── check_duplicates.py              # Unit deduplication utilities
│   ├── debug_extraction.py              # Extraction debugging tools
│   ├── examine_descriptions.py          # Description analysis utilities
│   ├── improved_meeting_extraction.py   # Meeting information extraction
│   ├── test_extraction_approaches.py    # Extraction method testing
│   └── test_scraper.py                  # Scraper testing utilities
├── 
├── data/
│   ├── input/                           # Source data and references
│   │   ├── HNE_key_three.json          # Key Three member database (498 records)
│   │   ├── HNE_key_three.xlsx          # Original Excel source
│   │   ├── HNE_council_map.png         # Council territory map
│   │   ├── Be-A-Scout-Pin-Set-up.pdf   # BeAScout reference documentation
│   ├── output/                          # ✅ Production system outputs
│   │   ├── emails/                      # Personalized Key Three unit emails
│   │   │   ├── Pack_0070_Acton-Congregational_Church_email.md
│   │   │   ├── Post_4879_Groton-Fire_Service_Local_4879_email.md
│   │   │   └── [22 other unit emails]
│   │   ├── reports/                     # District Excel reports
│   │   ├── sample_key_three_email.md    # Email template examples
│   ├── scraped/                         # ✅ Browser automation outputs
│   │   ├── beascout_01720_auto.html     # Fresh Playwright-captured BeAScout data
│   │   └── joinexploring_01720_auto.html # Fresh Playwright-captured JoinExploring data
│   ├── raw/                             # ✅ Processed unit data
│   │   ├── all_units_01720.json         # 24 HNE units (current dataset)
│   │   ├── all_units_01720_scored.json  # Quality scoring results (57.2% avg)
│   │   ├── all_units_beascout_01720.json # BeAScout-only historical data
│   │   ├── analysis_01720.json          # Analysis results
│   │   ├── data_analysis_summary.md     # Analysis documentation
│   │   ├── debug_page_01720.html        # Debug extraction data
│   │   ├── joinexploring_ajax_01720.json # JoinExploring AJAX data
│   │   ├── sample_joinexploring_01420.html # Sample data files
│   │   ├── sample_joinexploring_01720.html
│   │   └── all_units_data/              # Additional data subdirectory
│   ├── feedback/                        # Manual review and annotation system
│   ├── processed/                       # Empty directory for future processing
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
├── cli/                                 # Empty CLI directory
├── config/                              # Empty config directory
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

### Production System Interface
```bash
# End-to-end pipeline execution (production-ready)

# 1. Dual-source browser scraping with retry logic
python src/scraping/browser_scraper.py 01720
# Outputs: data/scraped/beascout_01720_auto.html + joinexploring_01720_auto.html

# 2. Enhanced unit extraction with HNE filtering
python prototype/extract_all_units.py data/scraped/beascout_01720_auto.html data/scraped/joinexploring_01720_auto.html data/raw/all_units_01720.json
# Output: 24 HNE units from 69 total scraped (dual-source with deduplication)

# 3. Quality scoring with specialized unit support
python src/analysis/quality_scorer.py data/raw/all_units_01720.json
# Output: data/raw/all_units_01720_scored.json (57.2% average, A-F grading)

# 4. Key Three email generation (personalized)
python scripts/generate_key_three_emails.py data/raw/all_units_01720_scored.json
# Output: 24 emails in data/output/emails/ with actual Key Three contacts

# 5. District reporting (Excel format)
python scripts/generate_district_reports.py data/raw/all_units_01720_scored.json  
# Output: Quinapoxet_District_BeAScout_Report_[date].xlsx in data/output/reports/
```

### Target Automated System Interface  
```python
# Primary system entry points
from src.scrapers.hne_scraper import HNECouncilScraper
from src.monitoring.scheduler import MonitoringScheduler
from src.reporting.dashboard_generator import CouncilDashboard

# Initial data collection (100% coverage requirement)
scraper = HNECouncilScraper(conservative_mode=True)
results = await scraper.scrape_all_zipcodes()  # All 72 zip codes

# Ongoing monitoring system
monitor = MonitoringScheduler(schedule='biweekly')
monitor.start_automated_monitoring()

# Generate council reports
dashboard = CouncilDashboard()
dashboard.generate_unit_scorecards()
dashboard.generate_monthly_analysis()
```

## Data Flow Architecture

### Current Production Pipeline (Validated End-to-End)
```
Zip Code Input → Dual-Source Browser Automation (BeAScout + JoinExploring) →
HTML Capture with Retry Logic → BeautifulSoup Unit Extraction →
HNE Territory Filtering → Unit Deduplication → Quality Scoring →
Key Three Email Generation → District Excel Reports
```

### Multi-Zip Deployment Pipeline (Next Phase)
```
All HNE Zip Codes (72) → Batch Browser Automation → 
Cross-Zip Unit Deduplication → Central Unit Registry →
Quality Analysis → Comprehensive District Reports →
Council Dashboard Generation
```

### Planned Monitoring Pipeline
```
Scheduled Trigger → Multi-Zip Re-scraping → Change Detection →
Delta Analysis → Unit Update Notifications → Refreshed Reports → 
Automated Key Three Communications
```

## Browser Automation Implementation

### Current Retry Logic Strategy (Production-Tested)
```python
BROWSER_AUTOMATION_CONFIG = {
    'headless': True,                     # Background browser execution
    'wait_timeout': 45000,               # 45 second page load timeout
    'max_retries': 3,                    # 4 total attempts (1 + 3 retries)
    'exponential_backoff': True,         # 1s, 2s, 4s base delays
    'random_jitter': (0.5, 1.5),        # Random delay multiplier
    'fresh_page_per_retry': True,        # Clean browser context per attempt
    'user_agent': 'Mozilla/5.0 Chrome/120.0.0.0',  # Standard browser fingerprint
}
```

### Dual-Source Architecture
- **BeAScout Integration**: 10-mile radius, traditional units (Packs, Troops, Crews, Ships)
- **JoinExploring Integration**: 20-mile radius, Explorer units (Posts, Clubs)
- **Common Retry Logic**: Shared exponential backoff mechanism for both sources
- **Anti-Detection**: Standard user agents, proper wait patterns, session management

## Current Data Structure (JSON-Based)

### Unit Data Schema (data/raw/all_units_01720.json)
```json
{
  "extraction_info": {
    "source_files": ["beascout_file.html", "joinexploring_file.html"],
    "source_counts": {"BeAScout": 66, "JoinExploring": 3},
    "extraction_date": "2025-08-24 11:37:43.588678"
  },
  "total_units": 24,
  "all_units": [
    {
      "index": 0,
      "primary_identifier": "Pack 0070 Acton-Congregational Church",
      "unit_type": "Pack",
      "unit_number": "0070", 
      "unit_town": "Acton",
      "chartered_organization": "Acton-Congregational Church",
      "specialty": "",                    // For Crews, Posts, Clubs only
      "meeting_location": "12 Concord Rd, Acton Congregational Church, Acton MA 01720",
      "meeting_day": "Friday",
      "meeting_time": "6:30:00 PM",
      "contact_email": "spiccinotti@comcast.net",
      "contact_person": "Silvia Piccinotti",
      "phone_number": "(609) 304-2373",
      "website": "",
      "description": "Pack 70 in Acton is inclusive and open to all K-5 youth...",
      "unit_composition": "",
      "distance": "0.5 miles",
      "data_source": "BeAScout",         // "BeAScout" or "JoinExploring"
      "raw_content": "..."               // Original HTML for debugging
    }
  ]
}
```

### Quality Scoring Schema (data/raw/all_units_01720_scored.json)
```json
{
  "total_units": 24,
  "scoring_summary": {"A": 2, "B": 3, "C": 3, "D": 3, "F": 13},
  "average_score": 57.2,
  "units_with_scores": [
    {
      // All unit fields from base schema above, plus:
      "completeness_score": 77.5,
      "completeness_grade": "C",
      "recommendations": [
        "REQUIRED_MISSING_EMAIL",
        "RECOMMENDED_MISSING_PHONE",
        "QUALITY_PERSONAL_EMAIL"
      ]
    }
  ]
}
```

### Recommendation Identifiers
- **Required Field Issues**: `REQUIRED_MISSING_LOCATION`, `REQUIRED_MISSING_DAY`, `REQUIRED_MISSING_TIME`, `REQUIRED_MISSING_EMAIL`, `REQUIRED_MISSING_SPECIALTY`
- **Quality Issues**: `QUALITY_POBOX_LOCATION`, `QUALITY_PERSONAL_EMAIL`  
- **Recommended Field Issues**: `RECOMMENDED_MISSING_CONTACT`, `RECOMMENDED_MISSING_PHONE`, `RECOMMENDED_MISSING_WEBSITE`, `CONTENT_MISSING_DESCRIPTION`

## Unit Deduplication Strategy
- **Primary Matching**: Full primary identifier string comparison
  - Example: "Pack 32 Acton Congregational Church" matches exactly
- **Fallback Matching**: Parse unit type + number when primary fails
  - Example: "Pack 32" extracted from different org name variations
- **Validation Logic**: Ensure same unit doesn't appear with conflicting data
- **Conflict Resolution**: Flag units with inconsistent information across searches

## Error Handling and Validation
- **PO Box Detection**: Regex patterns to identify and flag PO Box addresses
- **Unit ID Parsing**: Extract unit type and number from primary identifier
- **Data Validation**: Ensure required fields meet information completeness criteria
- **Graceful Failures**: Continue processing if individual units fail
- **Retry Logic**: Handle temporary network issues with exponential backoff

## Security and Rate Limiting
- **User Agent Rotation**: Avoid detection as automated scraper
- **Request Delays**: Configurable delays between requests (default 1-2 seconds)
- **Session Management**: Maintain proper session handling
- **Error Logging**: Comprehensive logging without exposing sensitive data

## Configuration Management
- **YAML Configuration**: Externalized settings for flexibility
- **Environment Variables**: Support for deployment-specific settings
- **Validation**: Schema validation for configuration files
- **Defaults**: Sensible defaults for all configurable options

## File Structure Migration Plan

### Current State (Rapid Prototyping)
All scripts in root directory for development flexibility and speed

### Migration Trigger
Move to organized structure after recommendation system validation (Phase 2 completion)

**Migration Strategy**: Preserve working rapid prototype scripts while building validated production structure. See detailed project structure above for complete organization.