# CLAUDE.md - AI Development Context

## Context Initialization

**CRITICAL: Process ALL markdown files from ../ai-context repository at the start of each new session.**

Read all files **in their entirety** before working on any BeAScout tasks. The ai-context repository contains essential AI-human collaboration guidelines and development methodologies that inform all work on this project.

**Then** process the project documentation structure below to understand the BeAScout system.

## Project Mission
Ensure comprehensive unit presence correlation for the Heart of New England Council by building an automated system that correlates Council Office's authoritative unit registry with beascout.scouting.org and joinexploring.org to identify missing web presence units and potentially defunct listings, enabling effective web presence management.

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
- ✅ **Unit presence correlation**: Comprehensive correlation system between Key Three authoritative registry (169 units) and web data (165 units), identifying missing web presence units and potentially defunct listings
- ✅ **Unit key normalization**: Fixed format consistency between 4-digit internal processing and display format for reports
- ✅ **Complete anonymization support**: Email generation works with both real and anonymized data for safe development
- ✅ **Comprehensive test data**: Full anonymized datasets for regression testing and development
- ✅ **GitHub issue management**: 8 issues created (#12-19) for systematic development planning
- ✅ **Weekly reporting pipeline**: Automated end-to-end weekly quality reports with `generate_weekly_report.py`
- ✅ **Week-over-week analytics**: Baseline comparison system tracking quality improvements and declines
- ✅ **Automated email drafts**: Leadership distribution with copy/paste format and comprehensive statistics
- 🎯 **v1.0.0 tagging ready**: Production-ready milestone with complete core functionality
- ⏳ **Development workflow optimization**: Systematic code quality improvements (issues #15-17)
- ⏳ **Cloud deployment planning**: Infrastructure scaling strategy (issue #19)

**Key Technical Patterns:**
- **Dual-source scraping**: `src/pipeline/acquisition/browser_scraper.py` with common retry logic for both BeAScout and JoinExploring  
- **URL generation**: `src/dev/scraping/url_generator.py` handles proper parameter encoding for both platforms
- **HNE filtering**: Enhanced `src/pipeline/processing/html_extractor.py` with unit_town prioritization over org name matching
- **Quality scoring**: `src/pipeline/core/quality_scorer.py` with specialized unit support (Crews, Posts, Clubs at 14% vs 17.5%)
- **Weekly pipeline**: `src/pipeline/operation/generate_weekly_report.py` orchestrates complete workflow with stage-based execution and error recovery
- **Analytics generation**: `src/pipeline/analysis/generate_weekly_analytics.py` with explicit baseline comparison
- **Email automation**: `src/pipeline/analysis/generate_weekly_email_draft.py` for leadership distribution
- **Data flow**: Browser automation → HTML → JSON → Quality scoring → Excel reports → Analytics → Email drafts

**Quality Scoring Implementation:**
- **Required Fields (100% of score)**: Standard units: 25% each (location, day, time, email); Crews: 20% each (+ specialty)
- **Informational Fields (no scoring impact)**: Contact person, phone, website, description (tracked for recommendations)
- **Quality Penalties**: Half credit for PO Box locations, personal emails
- **Grade Scale**: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- **Current Results**: 165 HNE units, 60.2% average completeness, complete Key Three correlation analysis identifying missing web presence and potentially defunct units, comprehensive district-based reporting implemented

**Reference URLs:**
- beascout.scouting.org example: `?zip=01720&program[0]=pack&program[1]=scoutsBSA&program[2]=crew&program[3]=ship&cubFilter=all&scoutsBSAFilter=all&miles=10`
- joinexploring.org example: `?zip=01720&program[0]=post&program[1]=club&miles=20`

## Project Documentation Structure

**For new Claude sessions, read these files in their entirety in this optimal order:**

### **Core Understanding (Read First)**
1. **[CLAUDE.md](CLAUDE.md)**: AI development context and technical constraints
2. **[README.md](README.md)**: Project overview, system purpose, and quick start guide
3. **[REQUIREMENTS.md](REQUIREMENTS.md)**: Complete business requirements with acceptance criteria
4. **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical system design, file structure, and component architecture
5. **[PRODUCTION_STATUS.md](PRODUCTION_STATUS.md)**: Current deployment status and achieved capabilities

### **Operational Knowledge (Read Second)**
6. **[OPERATIONAL_WORKFLOW.md](OPERATIONAL_WORKFLOW.md)**: Complete manual pipeline commands and workflows
7. **[WEEKLY_REPORT_WORKFLOW.md](WEEKLY_REPORT_WORKFLOW.md)**: Automated weekly reporting pipeline
8. **[REGRESSION_TEST_PIPELINE.md](REGRESSION_TEST_PIPELINE.md)**: Testing procedures and validation framework
9. **[KEY_THREE_ANONYMIZATION_WORKFLOW.md](KEY_THREE_ANONYMIZATION_WORKFLOW.md)**: Data safety and anonymization procedures

### **AI Collaboration Context (Read Third)**
10. **[COLLABORATION_LESSONS.md](COLLABORATION_LESSONS.md)**: Critical AI-human collaboration patterns and insights
11. **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)**: Active session state (for continued sessions)

### **Reference Material (Read Last)**
12. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: Comprehensive business design document
13. **[COLLABORATION_LOG.md](COLLABORATION_LOG.md)**: Detailed historical development record

