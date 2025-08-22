# BeaScout Unit Information Analyzer

Automated analysis and improvement of Scouting America unit information published on [beascout.scouting.org](https://beascout.scouting.org/) and [joinexploring.org](https://joinexploring.org/) for the Heart of New England Council (Massachusetts). This tool helps prospective Scouts and their families easily find complete, accurate contact information for local units.

## Overview

The BeaScout analyzer collects unit information from official Scouting websites, validates completeness against established criteria, and generates improvement recommendations for unit leaders. The system operates on a biannual schedule (January and June) to ensure information stays current and helpful for families seeking Scouting opportunities.

## Key Features

- **Comprehensive Data Collection**: Scrapes unit information from both beascout.scouting.org (10-mile radius) and joinexploring.org (20-mile radius)
- **Intelligent Deduplication**: Uses sophisticated unit identification to eliminate duplicates across multiple search results
- **Completeness Analysis**: Validates unit information against required and recommended criteria
- **Automated Reporting**: Generates detailed reports and improvement recommendations
- **Email Integration**: Creates targeted emails for unit Key Three members with specific improvement suggestions

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
# Full analysis pipeline
beascout collect-zipcodes --council "Heart of New England" --output data/zipcodes/
beascout scrape --zipcodes data/zipcodes/hne_zipcodes.json --output data/raw/
beascout deduplicate --input data/raw/ --output data/processed/ --strategy unit-id
beascout analyze --input data/processed/units.json --criteria config/completeness_criteria.yaml
beascout report --units data/processed/units.json --keythree data/input/key_three.csv --output data/reports/
```

## Information Completeness Criteria

### Required Fields
- Unit meeting location (PO boxes not accepted)
- Unit meeting day and time
- Contact email (unit-specific preferred over personal)
- Unit composition (Boys, Girls, or Boys and Girls)
- Specialty (Venturing Crews only)

### Recommended Fields
- Contact person name
- Phone number
- Unit website
- Informative and inviting description

## Project Documentation

- **[CLAUDE.md](CLAUDE.md)**: Complete project specification, requirements, and usage guidelines
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical design, database schema, and implementation details

## Data Sources

- **beascout.scouting.org**: Cub Scout Packs, Scout Troops, Venturing Crews, Sea Scout Ships
- **joinexploring.org**: Exploring Posts and Clubs
- **Heart of New England Council**: Unit Key Three member contact lists

## Development

### Technology Stack
- **Python 3.8+** with Playwright for web scraping
- **SQLite** for data storage and deduplication
- **CLI framework** with subcommand structure
- **pytest** for automated testing

### Project Structure
```
beascout/
├── cli/                    # Command-line interface
├── src/                    # Core application logic
│   ├── scrapers/          # Web scraping modules
│   ├── storage/           # Database and data models
│   ├── analysis/          # Completeness checking
│   └── notifications/     # Email generation
├── data/                  # Data storage directories
├── config/                # Configuration files
└── tests/                 # Test suites
```

## Contributing

This project follows Acceptance-Test Driven Development (ATDD) principles and maintains comprehensive test coverage. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed development guidelines.

## License

[MIT License](LICENSE)

## Contact

For questions about this project or the Heart of New England Council, please contact the repository maintainer. 
