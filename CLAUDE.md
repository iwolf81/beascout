# CLAUDE.md

## Session Handoff Management

### Automatic Updates to SESSION_HANDOFF.md
You MUST update SESSION_HANDOFF.md whenever ANY of the following occurs:

#### 🔴 Critical Updates (Always Update)
- Implementation of new major features (scrapers, analysis modules, data processing)
- Changes to extraction logic or data models (field definitions, parsing patterns)  
- Architecture modifications (database schema, file structure, technology stack)
- Significant bug fixes that alter system behavior
- Performance improvements with measurable impact
- Dependency changes (requirements.txt, new libraries, version updates)

#### 🟡 Important Updates (Update During Session)
- Discovery of new technical insights (HTML structure, data patterns)
- Changes to success metrics or completeness criteria
- New known issues or limitations identified
- Configuration changes affecting extraction or analysis
- Test coverage improvements or new testing approaches

#### 🟢 Session Boundary Updates (End of Work Session)
- Before committing major milestones or feature completions
- When switching contexts or concluding work sessions
- After completing analysis phases or data collection cycles
- When next steps or priorities change significantly

### Update Process
1. Read existing SESSION_HANDOFF.md to understand current state
2. Update relevant sections with new information:
   - Current State Summary (achievements, metrics)
   - Key Technical Discoveries (patterns, insights, fixes)
   - Files & Artifacts (new files, changed logic)
   - Immediate Next Steps (updated priorities)
   - Known Issues & Limitations (new problems found)
3. Commit SESSION_HANDOFF.md with descriptive commit message
4. Ensure handoff preserves all context for future sessions

### Decision Rule
Update if changes would take >30 minutes to explain to someone picking up the work fresh.

## Context Initialization
Process the markdown files in https://github.com/iwolf81/ai-context.

## Project Overview
1. Improve information for Scouting America units in the Heart of New England Council (Massachusetts) that is published in https://beascout.scouting.org/ and https://joinexploring.org/ toward best assisting prospective Scouts find their appropriate unit.
2. Continue exploring best practices for interacting with Claude.

## Plan of Attack
1. Collect published information for Scouting America units (e.g., Cub Scout Packs, Scouting Troops, Venturing Crews, Sea Scouts Boats) in the Heart of New England Council (Massachusetts) from https://beascout.scouting.org/.
2. Collect published information for Scouting America Exploring units (e.g., Exploring Post, Exploring Club) in the Heart of New England Council (Massachusetts) from https://joinexploring.org/.
4. Analyze unit information for completeness according to a set of criteria.
6. Recommended improvements to contact information for each unit.
7. Review recommended changes with developer.
8. Developer obtains a list of each unit's Key Three members who are authorized to update information on the aforementioned websites.
9. Send email containing reviewed and approved recommended changes to each unit's Key Three members that encourage them to implement the recommended changes.

## Usage
1. CLI interface
2. Application executes normally twice a year: January and June.

## Information Completeness Criteria
1. Required: Unit meeting location. (Note: a PO box is not a valid meeting location)
2. Required: Unit meeting day and time.
3. Required: Contact email; prefer unit specific (e.g., T32-Scoutmaster@actonscouts.org) over personal (e.g., irawolf81@gmail.com).
4. Required: Unit composition (e.g., Boys, Girls, Boys and Girls)
5. Required (for Venturing Crews only): Specialty
6. Recommended: Contact person
7. Recommended: Phone number
8. Recommended: Website
9. Recommended: Informative and inviting description.
 
## Notes
1. There is no available API access to data in https://beascout.scouting.org/ and https://joinexploring.org/.
2. The Council Office for Heart of New England Council will provide list of Key Three member for each unit to the developer. This will be an input to the application.
3. The list of towns in the Heart of New England Council is specified in the map of central Massachusetts located in https://hnescouting.org/about/.
4. The Zip Code is the search key for https://beascout.scouting.org/ and https://joinexploring.org/.
5. The primary unit identifier in the search results is formatted as <unit type> <unit number> <chartered organization name>; the chartered organization name might contain the unit type and unit number.
6. The primary unit identifier uniquely identifies a unit.
7. A town may have multiple Zip Codes.
8. Search a 10 mile radius for https://beascout.scouting.org/ and a 20 mile radius for https://joinexploring.org/.
9. The same unit is likely to appear in the search results for multiple Zip Codes.
10. Information for a specific unit should be consistent across multiple searches. 
11. Do not present duplicate units.
12. The following web query finds all Explorer Posts in a 20 mile radius of Acton MA (01720): https://joinexploring.org/list/?zip=01720&program%5B0%5D=post&program%5B1%5D=club&miles=20
13. The following web query finds all unit types in a 10 mile radius of Acton MA 
  (01720): https://beascout.scouting.org/list/?zip=01720&program%5B0%5D=pack&program%5B1%5D=scoutsBSA&program%5B2%5D=crew&program%5B3%5D=ship&cubFilter=all&scoutsBSAFilter=all&miles=10

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system design and technical specifications. 