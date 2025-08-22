# CLAUDE.md - AI Development Context

## Context Initialization
Process the markdown files in https://github.com/iwolf81/ai-context.

## Project Mission
Improve Scouting America unit information quality for the Heart of New England Council by building an automated system that monitors, analyzes, and reports on unit data completeness across beascout.scouting.org and joinexploring.org.

## Development Guidelines
- **Conservative approach**: Respectful scraping with rate limiting to avoid blocking
- **100% coverage**: All 48 HNE Council zip codes must be processed successfully  
- **Board authority**: Developer is HNE Council Board member using data for legitimate council benefit
- **Rapid prototyping**: Current development phase, files remain in root directory for flexibility

## Key Technical Constraints
- **Scale considerations**: ~3,000 units across 48 zip codes requires efficient processing
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
- ✅ Single zip code extraction working (01720 Acton - 62 units)
- ✅ Meeting info extraction: 42% day, 39% time (improved regex patterns)
- ✅ Deduplication logic for primary identifier matching
- 🔄 Multi-zip code processing system (in development)
- ⏳ Ongoing monitoring and reporting system (design phase)

**Key Technical Patterns:**
- HTML containers: `div.card-body` contains unit info, `div.unit-name` has identifier
- Meeting extraction: Complex regex patterns for various description formats
- Error handling: Exponential backoff, session resets, cooling periods
- Data flow: Raw HTML → JSON → SQLite → Reports

**Reference URLs:**
- beascout.scouting.org example: `?zip=01720&program[0]=pack&program[1]=scoutsBSA&program[2]=crew&program[3]=ship&cubFilter=all&scoutsBSAFilter=all&miles=10`
- joinexploring.org example: `?zip=01720&program[0]=post&program[1]=club&miles=20`

## Related Documentation
- **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: Complete business requirements and operational workflows
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical implementation details and system design
- **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)**: Current project state and recent achievements 