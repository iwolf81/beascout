# CLAUDE.md - AI Development Context

## Context Initialization
Process the markdown files in https://github.com/iwolf81/ai-context at the start of each new session.

## Project Mission
Improve Scouting America unit information quality for the Heart of New England Council by building an automated system that monitors, analyzes, and reports on unit data completeness across beascout.scouting.org and joinexploring.org.

## Development Guidelines
- **Business value first**: Build recommendation system with current data before scaling
- **Conservative approach**: Respectful scraping with rate limiting to avoid blocking
- **100% coverage**: All 71 HNE Council zip codes must be processed successfully  
- **Board authority**: Developer is HNE Council Board member using data for legitimate council benefit
- **Production ready**: System operational with dual-source scraping and automated reporting
- **Transparent reasoning**: Present analytical thinking process for complex technical decisions

## Key Technical Constraints
- **Scale considerations**: 165 HNE units across 71 zip codes requires efficient processing
- **Detection avoidance**: 8-12 second delays, session limits, human-like patterns
- **Tiered extraction**: Regex primary, LLM fallback for complex cases
- **Ongoing monitoring**: System must support periodic re-scraping and change detection

## Core Business Rules
**See SYSTEM_DESIGN.md for complete requirements and success metrics**

**Primary Unit Identifier Format:** `<unit type> <unit number> <unit town>`
- Example: "Pack 0070 Acton-Congregational Church" 
- Used for deduplication across zip codes and platforms

**Quality Scoring:**
- Required fields: 100% of score (meeting location/day/time, contact email, specialty for Crews)
- Informational fields: No scoring impact (contact person, phone, website, description - tracked for recommendations)
- Grade scale: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)

**Search Parameters:**
- beascout.scouting.org: 10-mile radius
- joinexploring.org: 20-mile radius  
- All unit types: Packs, Troops, Crews, Ships, Posts, Clubs
 
## Development Context
**See data/zipcodes/hne_council_zipcodes.json for complete 71 zip code list**

**Current Implementation Status:**
- ✅ **Dual-source browser automation**: Playwright-based scraping for BeAScout and JoinExploring with retry logic
- ✅ **Explorer unit integration**: Posts and Clubs fully supported alongside traditional units (Packs, Troops, Crews, Ships)
- ✅ **Robust HNE filtering**: Enhanced territory classification with unit_town prioritization over chartered org matching
- ✅ **Production-ready data pipeline**: End-to-end processing from fresh scraping through final reports
- ✅ **Quality scoring system**: Specialized unit scoring with A-F grading and recommendation categorization
- ✅ **BeAScout Quality Reports**: District-organized Excel reports with professional formatting, quality grades, and Key Three contacts
- ✅ **Key Three email generation**: Personalized emails with actual contact information and improvement recommendations
- ✅ **Production pipeline**: Main operational files organized in `src/pipeline/` with single source of truth mapping in `src/pipeline/core/`
- ✅ **Three-way validation**: Cross-reference system between Key Three database (169 units) and web data (165 units) with 97.6% match rate
- ✅ **Unit key normalization**: Fixed format consistency between 4-digit internal processing and display format for reports
- ✅ **Complete anonymization support**: Email generation works with both real and anonymized data for safe development
- ✅ **Comprehensive test data**: Full anonymized datasets for regression testing and development
- ✅ **GitHub issue management**: 8 issues created (#12-19) for systematic development planning
- 🎯 **v1.0.0 tagging ready**: Production-ready milestone with complete core functionality
- ⏳ **Development workflow optimization**: Systematic code quality improvements (issues #15-17)
- ⏳ **Cloud deployment planning**: Infrastructure scaling strategy (issue #19)

**Key Technical Patterns:**
- **Dual-source scraping**: `src/pipeline/acquisition/browser_scraper.py` with common retry logic for both BeAScout and JoinExploring  
- **URL generation**: `src/dev/scraping/url_generator.py` handles proper parameter encoding for both platforms
- **HNE filtering**: Enhanced `src/pipeline/processing/html_extractor.py` with unit_town prioritization over org name matching
- **Quality scoring**: `src/pipeline/core/quality_scorer.py` with specialized unit support (Crews, Posts, Clubs at 14% vs 17.5%)
- **Data flow**: Browser automation → HTML → JSON → Quality scoring → BeAScout Quality Reports → Personalized emails

**Quality Scoring Implementation:**
- **Required Fields (100% of score)**: Standard units: 25% each (location, day, time, email); Crews: 20% each (+ specialty)
- **Informational Fields (no scoring impact)**: Contact person, phone, website, description (tracked for recommendations)
- **Quality Penalties**: Half credit for PO Box locations, personal emails
- **Grade Scale**: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- **Current Results**: 165 HNE units, 60.2% average completeness, 97.6% Key Three cross-validation accuracy, comprehensive district-based reporting implemented

**Reference URLs:**
- beascout.scouting.org example: `?zip=01720&program[0]=pack&program[1]=scoutsBSA&program[2]=crew&program[3]=ship&cubFilter=all&scoutsBSAFilter=all&miles=10`
- joinexploring.org example: `?zip=01720&program[0]=post&program[1]=club&miles=20`

## Project Documentation Structure
Review and process the following markdown files **in their entirety** in the listed order:
1. **[CLAUDE.md](CLAUDE.md)**: AI development context and technical constraints
1. **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)**: Current session state and context preservation
1. **[README.md](README.md)**: Usage examples, getting started, system overview
1. **[OPERATIONAL_WORKFLOW.md](OPERATIONAL_WORKFLOW.md)**: Complete operational pipeline commands and workflows
1. **[COLLABORATION_LOG.md](COLLABORATION_LOG.md)**: AI-human collaboration insights and lessons learned
1. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: Business requirements, success metrics, operational workflows
1. **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical system design and component architecture
1. **[PRODUCTION_STATUS.md](PRODUCTION_STATUS.md)**: Current deployment status and achievements

