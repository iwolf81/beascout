# BeAScout Unit Information Analyzer

Automated analysis and improvement of Scouting America unit information published on [beascout.scouting.org](https://beascout.scouting.org/) and [joinexploring.org](https://joinexploring.org/) for the Heart of New England Council (Massachusetts). This tool helps prospective Scouts and their families easily find complete, accurate contact information for local units.

## Overview

The BeAScout analyzer collects unit information from official Scouting websites, validates completeness against established criteria, and generates improvement recommendations for unit leaders. The system operates on a configurable periodic schedule for report generation to ensure information stays current and helpful for families seeking Scouting opportunities.

## Key Features

- **Comprehensive Data Collection**: Scrapes unit information from both beascout.scouting.org (10-mile radius) and joinexploring.org (20-mile radius)
- **Intelligent Deduplication**: Uses sophisticated unit identification to eliminate duplicates across multiple search results
- **Production Quality Scoring**: A-F grading system with 10 human-readable recommendation identifiers
- **Advanced Email Classification**: 5-tier precedence system distinguishing personal vs unit emails with sophisticated edge case handling
- **Automated Key Three Email Generation**: Cross-references unit data with HNE Key Three roster to generate personalized improvement emails
- **Organization Matching Logic**: Handles duplicate unit numbers across different chartered organizations (e.g., multiple Troop 7012s)
- **Manual Review Framework**: Systematic 5-pass review process with direct annotation feedback system

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/iwolf81/beascout.git
cd beascout

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Basic Usage
```bash
# Production-ready workflow (tested with 62 units from 01720 zip code)
python prototype/extract_all_units.py data/raw/debug_page_01720.html  # Extract unit data from scraped HTML
python src/analysis/quality_scorer.py data/raw/all_units_01720.json  # Generate A-F quality scores with recommendations
python scripts/email_analysis.py data/raw/all_units_01720_scored.json  # Manual review of email classifications
python scripts/generate_key_three_emails.py data/raw/all_units_01720_scored.json  # Generate personalized Key Three emails

# Full production pipeline (ready for all 72 HNE zip codes, ~200 units)
python prototype/extract_all_units.py data/raw/debug_page_{zipcode}.html  # For each zip code
python src/analysis/quality_scorer.py data/raw/all_units_{zipcode}.json  # Score each zip code
python scripts/generate_key_three_emails.py data/raw/all_units_*_scored.json --output-dir data/output/emails/
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

### Production Results (62 units, ZIP 01720)
- **Average score**: 61.0% indicating significant improvement opportunities
- **Grade distribution**: 9.7% A, 16.1% B, 12.9% C, 6.5% D, 54.8% F
- **Email classification**: 27.4% unit emails, 56.5% personal emails, 16.1% missing
- **Key Three coverage**: 98%+ (only 1 HNE unit missing Key Three data)
- **Automated emails generated**: 62 personalized improvement emails with actual Key Three contact information
- **Key insight**: System ready for production deployment across all ~200 HNE Council units

## File Hierarchy

```
beascout/
├── data/
│   ├── input/
│   │   └── HNE_key_three.xlsx                 # Key Three member roster (498 records)
│   ├── raw/
│   │   ├── debug_page_01720.html              # Scraped BeAScout HTML for zip 01720
│   │   ├── all_units_01720.json               # Extracted unit data (62 units)
│   │   └── all_units_01720_scored.json        # Scored unit data with recommendations
│   ├── output/
│   │   ├── emails/                            # Generated Key Three emails (62 files)
│   │   ├── sample_key_three_email.md          # Template email for good units
│   │   └── sample_key_three_email_worst_case.md # Template for critical cases
│   ├── feedback/                              # Manual review and feedback files
│   └── zipcodes/
│       └── hne_council_zipcodes.json          # All 72 HNE Council zip codes
├── src/
│   └── analysis/
│       └── quality_scorer.py                 # Production A-F scoring system
├── scripts/
│   ├── generate_key_three_emails.py          # Automated personalized email generation
│   └── email_analysis.py                     # Manual review tool for email classifications
├── prototype/
│   ├── extract_all_units.py                  # Enhanced data extraction with parsing
│   └── extract_hne_towns.py                  # HNE Council territory definitions
├── venv/                                      # Python virtual environment
├── requirements.txt                           # Python dependencies
├── CLAUDE.md                                  # AI development context
├── SYSTEM_DESIGN.md                           # Business requirements
└── README.md                                  # This file
```

## Project Documentation

Review and process the following markdown files in the listed order:
1. **[CLAUDE.md](CLAUDE.md)**: AI development context and project specifications
2. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: Complete business requirements, operational workflows, and success metrics
3. **Current Status**: Production-ready system tested with 62 units, ready for ~200 unit deployment

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
