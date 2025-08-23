# BeAScout Unit Information System - Technical Architecture

**Version**: 1.2 | **Last Updated**: 2025-08-22 | **Strategy**: Recommendation-First Development

## Technology Stack
- **Web Scraping**: Playwright (handles dynamic JavaScript content with conservative rate limiting)
- **HTML Parsing**: BeautifulSoup for data extraction and field parsing
- **Data Storage**: Hybrid approach - JSON for raw data, SQLite for processed analysis
- **Concurrency**: Asyncio for controlled parallel processing with semaphores
- **Monitoring**: Automated scheduling and change detection system
- **Testing**: pytest with automated unit and integration tests
- **Language**: Python 3.8+

## Project Structure
```
beascout/
├── prototype/                   # Current working prototypes
│   ├── extract_all_units.py   # Refined unit extraction (62 units)
│   ├── extract_hne_towns.py   # Council territory analysis  
│   ├── analyze_data.py         # Original analysis script (legacy)
│   └── [5 other prototype files]
├── 
├── # Next Development Phase (recommendation system)
├── src/analysis/quality_scorer.py           # Quality scoring (next priority)
├── src/notifications/report_generator.py   # Key Three recommendations (next priority)
├── 
├── # Target Production Structure
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py         # Abstract scraper with rate limiting
│   │   ├── hne_scraper.py          # Conservative multi-zip scraper
│   │   └── monitoring_scraper.py   # Periodic re-scraping system
│   ├── extraction/
│   │   ├── html_parser.py          # BeautifulSoup extraction logic
│   │   ├── meeting_extractor.py    # Regex + LLM meeting info extraction
│   │   └── field_validator.py      # Data quality validation
│   ├── storage/
│   │   ├── raw_storage.py          # JSON file management
│   │   ├── database.py             # SQLite operations and schema
│   │   └── deduplication.py        # Cross-zip duplicate detection
│   ├── analysis/
│   │   ├── completeness_scorer.py  # Quality scoring and grading
│   │   ├── change_detector.py      # Monitoring and delta analysis
│   │   └── trend_analyzer.py       # Temporal pattern analysis
│   ├── reporting/
│   │   ├── dashboard_generator.py  # Council office reports
│   │   ├── unit_scorecards.py      # Individual unit analysis
│   │   └── key_three_notifier.py   # Outreach communications
│   └── monitoring/
│       ├── scheduler.py            # Periodic processing automation
│       ├── alert_system.py         # Error and change notifications
│       └── health_checker.py       # System status monitoring
├── data/
│   ├── zipcodes/                   # HNE Council zip codes (72 total)
│   ├── raw/                        # HTML files per zip code
│   ├── processed/                  # Extracted and deduplicated units
│   ├── reports/                    # Generated dashboards and scorecards
│   └── monitoring/                 # Change tracking and alerts
├── config/
│   ├── scraping_config.json        # Rate limits, delays, session settings
│   ├── extraction_config.json      # Field definitions and scoring weights
│   └── monitoring_config.json      # Alert thresholds and reporting schedules
└── tests/
    ├── unit/                       # Component testing
    ├── integration/                # End-to-end workflow testing
    └── fixtures/                   # Sample data for testing
```

## System Interface Design

### Current Development Interface
```bash
# Generate refined unit extraction (62 units from ZIP 01720)
python prototype/extract_all_units.py

# Generate HNE Council territory analysis (72 zip codes, 62 towns)
python prototype/extract_hne_towns.py

# Next: Build recommendation system
python src/analysis/quality_scorer.py          # A-F grading for current units
python src/notifications/report_generator.py   # Key Three improvement reports
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

### Initial Collection Pipeline
```
HNE Zip Codes (72) → Conservative Scraper → Raw HTML Files → 
BeautifulSoup Parser → Unit Extraction → JSON Storage →
Cross-Zip Deduplication → SQLite Database → Quality Analysis → 
Baseline Reports
```

### Ongoing Monitoring Pipeline  
```
Scheduled Trigger → Re-scrape All Zips → Change Detection →
Delta Analysis → Alert Generation → Updated Reports → 
Key Three Notifications → Council Dashboard
```

## Conservative Scraping Implementation

### Rate Limiting Strategy (Implements SYSTEM_DESIGN.md requirements)
```python
SCRAPING_CONFIG = {
    'delay_between_requests': (8, 12),    # Random 8-12 seconds
    'max_requests_per_session': 8,        # Browser restart after 8 requests  
    'session_cooldown': 14400,            # 4 hours between sessions
    'daily_zip_limit': 12,                # Maximum 12 zip codes per day
    'max_concurrent_pages': 1,            # Sequential processing only
    'request_timeout': 30000,             # 30 second page timeout
    'business_hours_only': True,          # 9 AM - 5 PM EST only
}
```

### Detection Avoidance Patterns
- **Human-like navigation**: Homepage → Search → Results flow
- **Browser fingerprint randomization**: User agents, viewport sizes
- **Session management**: Cookie handling, realistic session duration
- **Error response monitoring**: Automatic pause on 403/429 responses

## Database Schema
```sql
CREATE TABLE units (
    id INTEGER PRIMARY KEY,
    unit_number TEXT,
    unit_type TEXT,
    chartered_organization TEXT,
    primary_identifier TEXT UNIQUE, -- "Pack 32 Acton Congregational Church"
    unit_id TEXT,                   -- Parsed "Pack 32" for fallback matching
    meeting_location TEXT,
    meeting_day TEXT,
    meeting_time TEXT,
    contact_email TEXT,
    contact_person TEXT,
    phone_number TEXT,
    website TEXT,
    description TEXT,
    unit_composition TEXT,
    specialty TEXT,                 -- Venturing Crews only
    source_website TEXT,
    last_updated DATETIME
);

CREATE TABLE completeness_scores (
    primary_identifier TEXT REFERENCES units(primary_identifier),
    required_fields_complete INTEGER,
    recommended_fields_complete INTEGER,
    total_score REAL,
    issues TEXT,                    -- JSON array of problems
    last_analyzed DATETIME
);
```

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