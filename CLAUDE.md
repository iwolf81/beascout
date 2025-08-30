# CLAUDE.md - AI Development Context

## Context Initialization
Process the markdown files in https://github.com/iwolf81/ai-context at the start of each new session.

## Project Mission
Improve Scouting America unit information quality for the Heart of New England Council by building an automated system that monitors, analyzes, and reports on unit data completeness across beascout.scouting.org and joinexploring.org.

## Development Guidelines
- **Business value first**: Build recommendation system with current data before scaling
- **Conservative approach**: Respectful scraping with rate limiting to avoid blocking
- **100% coverage**: All 72 HNE Council zip codes must be processed successfully  
- **Board authority**: Developer is HNE Council Board member using data for legitimate council benefit
- **Production ready**: System operational with dual-source scraping and automated reporting

## Key Technical Constraints
- **Scale considerations**: ~200 units across 72 zip codes requires efficient processing
- **Detection avoidance**: 8-12 second delays, session limits, human-like patterns
- **Tiered extraction**: Regex primary, LLM fallback for complex cases
- **Ongoing monitoring**: System must support periodic re-scraping and change detection

## Core Business Rules
**See SYSTEM_DESIGN.md for complete requirements and success metrics**

**Primary Unit Identifier Format:** `<unit type> <unit number> <chartered organization name>`
- Example: "Pack 0070 Acton-Congregational Church" 
- Used for deduplication across zip codes and platforms

**Quality Scoring:**
- Required fields: 70% weight (meeting location/day/time, contact email, unit composition)
- Recommended fields: 30% weight (contact person, phone, website, description)
- Grade scale: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)

**Search Parameters:**
- beascout.scouting.org: 10-mile radius
- joinexploring.org: 20-mile radius  
- All unit types: Packs, Troops, Crews, Ships, Posts, Clubs
 
## Development Context
**See data/zipcodes/hne_council_zipcodes.json for complete zip code list**

**Current Implementation Status:**
- ✅ **Dual-source browser automation**: Playwright-based scraping for BeAScout and JoinExploring with retry logic
- ✅ **Explorer unit integration**: Posts and Clubs fully supported alongside traditional units (Packs, Troops, Crews, Ships)
- ✅ **Robust HNE filtering**: Enhanced territory classification with unit_town prioritization over chartered org matching
- ✅ **Production-ready data pipeline**: End-to-end processing from fresh scraping through final reports
- ✅ **Quality scoring system**: Specialized unit scoring with 24 HNE units at 57.2% average completeness
- ✅ **Key Three email generation**: 24 personalized emails with actual contact information and improvement recommendations
- ✅ **District reporting**: Excel reports for Quinapoxet District with unit-specific quality metrics
- ✅ **Exponential backoff retry**: Common retry logic for both websites with jitter and fresh page contexts
- 🎯 **Ready for multi-zip deployment**: System validated end-to-end with fresh data
- ⏳ **Feedback integration phase**: Review emails/reports with unit leaders and council commissioner
- ⏳ **Code cleanup phase**: Remove deprecated processing and optimize efficiency
- ⏳ **Infrastructure scaling**: All 72 HNE zip codes with deduplication across multiple zip queries

**Key Technical Patterns:**
- **Dual-source scraping**: `src/scraping/browser_scraper.py` with common retry logic for both BeAScout and JoinExploring
- **URL generation**: `src/scraping/url_generator.py` handles proper parameter encoding for both platforms
- **HNE filtering**: Enhanced `prototype/extract_all_units.py` with unit_town prioritization over org name matching
- **Quality scoring**: `src/analysis/quality_scorer.py` with specialized unit support (Crews, Posts, Clubs at 14% vs 17.5%)
- **Data flow**: Browser automation → HTML → JSON → Quality scoring → Personalized emails → District reports

**Quality Scoring Implementation:**
- **Required Fields (70% weight)**: Non-Crews: 17.5% each (location, day, time, email); Crews: 14% each (+ specialty)
- **Recommended Fields (30% weight)**: 7.5% each (contact person, phone, website, description)
- **Quality Penalties**: Half credit for PO Box locations, personal emails
- **Grade Scale**: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- **Current Results**: 24 HNE units, 57.2% average, 54.2% F grades (13 units) with dual-source integration complete

**Reference URLs:**
- beascout.scouting.org example: `?zip=01720&program[0]=pack&program[1]=scoutsBSA&program[2]=crew&program[3]=ship&cubFilter=all&scoutsBSAFilter=all&miles=10`
- joinexploring.org example: `?zip=01720&program[0]=post&program[1]=club&miles=20`

## Project Documentation Structure
Review and process the following markdown files **in their entirety** in the listed order:
1. **[CLAUDE.md](CLAUDE.md)**: AI development context and technical constraints
1. **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)**: Current session state and context preservation
1. **[README.md](README.md)**: Usage examples, getting started, system overview
1. **[COLLABORATION_LOG.md](COLLABORATION_LOG.md)**: AI-human collaboration insights and lessons learned
1. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: Business requirements, success metrics, operational workflows
1. **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical system design and component architecture
1. **[PRODUCTION_STATUS.md](PRODUCTION_STATUS.md)**: Current deployment status and achievements

