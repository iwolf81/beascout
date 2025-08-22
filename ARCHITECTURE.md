# BeaScout Unit Information Analyzer - Architecture

## Technology Stack
- **Web Scraping**: Playwright (handles dynamic JavaScript content)
- **CLI Framework**: Python Click/Argparse for subcommand structure
- **Data Storage**: SQLite database for structured queries and deduplication
- **Testing**: pytest with automated unit tests
- **Language**: Python 3.8+

## Project Structure
```
beascout/
├── cli/
│   ├── main.py              # Entry point and argument parsing
│   ├── commands/
│   │   ├── collect_zipcodes.py
│   │   ├── scrape.py
│   │   ├── deduplicate.py
│   │   ├── analyze.py
│   │   └── report.py
│   └── config.py
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py     # Abstract base scraper
│   │   ├── beascout_scraper.py # 10-mile radius scraper
│   │   └── exploring_scraper.py # 20-mile radius scraper
│   ├── storage/
│   │   ├── database.py         # SQLite operations
│   │   ├── models.py           # Data models/schemas
│   │   └── deduplication.py    # Unit ID matching logic
│   ├── analysis/
│   │   ├── completeness_checker.py # Validates against criteria
│   │   └── report_generator.py     # Creates analysis reports
│   └── notifications/
│       └── email_generator.py      # Key Three email creation
├── data/
│   ├── input/                  # Key Three CSV from council
│   ├── zipcodes/              # Heart of New England zip codes
│   ├── raw/                   # Scraped data before deduplication
│   ├── processed/             # Clean, deduplicated unit data
│   └── reports/               # Analysis and email outputs
├── config/
│   ├── completeness_criteria.yaml
│   └── scraping_config.yaml
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

## CLI Command Structure
```bash
# Collect zip codes for Heart of New England Council
beascout collect-zipcodes --council "Heart of New England" --output data/zipcodes/

# Scrape units from both websites
beascout scrape --zipcodes data/zipcodes/hne_zipcodes.json --output data/raw/

# Remove duplicates using unit ID matching
beascout deduplicate --input data/raw/ --output data/processed/ --strategy unit-id

# Analyze completeness against criteria
beascout analyze --input data/processed/units.json --criteria config/completeness_criteria.yaml

# Generate reports and emails
beascout report --units data/processed/units.json --keythree data/input/key_three.csv --output data/reports/
```

## Data Flow Pipeline
```
Zip Codes → Playwright Scrapers → Raw JSON → Deduplication → SQLite → Analysis → Reports → Emails
```

## Scraping Strategy
- **beascout.scouting.org**: 10-mile radius searches per zip code
- **joinexploring.org**: 20-mile radius searches per zip code  
- **Unit Identification**: Primary identifier format `<unit type> <unit number> <chartered organization name>`
- **Deduplication**: Multi-level matching strategy (see Unit Deduplication section)
- **Dynamic Content**: Playwright waits for JavaScript-loaded results
- **Rate Limiting**: Configurable delays between requests

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