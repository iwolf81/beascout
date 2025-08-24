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
- **Rapid prototyping**: Current development phase, files remain in root directory for flexibility

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
- ✅ Single zip code extraction refined (01720 Acton - 62 units)
- ✅ Meeting info extraction: Enhanced pattern coverage including 3-4 digit times, range formats, day abbreviation expansion
- ✅ Manual review process established with direct annotation feedback in `data/feedback/`
- ✅ Quality scoring system operational with A-F grading and 10 human-readable recommendation identifiers
- ✅ Sophisticated email classification system with 5-pass refinement addressing edge cases
- ✅ Email analysis script for systematic review and validation (`scripts/email_analysis.py`)
- ✅ **Production-ready Key Three email generation system** with cross-referencing and organization matching
- ✅ **Automated personalized email generation** (23 HNE emails with actual Key Three contact information)
- ✅ **Enhanced town extraction system** with address-based prioritization and HNE filtering
- ✅ **Accurate HNE Council territory classification** (23 HNE units, 39 non-HNE units properly filtered)
- ✅ **98%+ Key Three cross-referencing accuracy** (only 1 HNE unit missing data)
- ✅ **Email generation cleanup system** (auto-removes old emails before regeneration)
- 🎯 **System ready for production deployment** across all ~200 HNE Council units
- ⏳ Multi-zip code processing system (deployment phase)
- ⏳ Council reporting dashboard and analytics

**Key Technical Patterns:**
- HTML containers: `div.card-body` contains unit info, `div.unit-name` has identifier
- Meeting extraction: Complex regex patterns for various description formats including 3-4 digit times
- Personal email detection: Cross-domain patterns to identify emails needing unit-specific replacements
- Error handling: Exponential backoff, session resets, cooling periods
- Data flow: Raw HTML → JSON → Quality Scoring → Recommendations → Key Three Reports

**Quality Scoring Implementation:**
- **Required Fields (70% weight)**: Non-Crews: 17.5% each (location, day, time, email); Crews: 14% each (+ specialty)
- **Recommended Fields (30% weight)**: 7.5% each (contact person, phone, website, description)
- **Quality Penalties**: Half credit for PO Box locations, personal emails
- **Grade Scale**: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- **Current Results**: 62 units, 61.0% average, 54.8% F grades with sophisticated email classification and edge case resolution

**Reference URLs:**
- beascout.scouting.org example: `?zip=01720&program[0]=pack&program[1]=scoutsBSA&program[2]=crew&program[3]=ship&cubFilter=all&scoutsBSAFilter=all&miles=10`
- joinexploring.org example: `?zip=01720&program[0]=post&program[1]=club&miles=20`

## Related Documentation
Refer to the Project Documentation section in **[README.md](README.md)**.
