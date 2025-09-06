# Pipeline Code Duplication Analysis

*Generated: 2025-09-04*
*Analysis Focus: Active src/pipeline/ code only*

## Executive Summary

Analysis of the `src/pipeline/` directory reveals significant code duplication across 11 Python files in 6 functional areas. Key patterns of duplication include:

1. **Town extraction logic** - 4 different implementations
2. **JSON data loading** - 8 repetitive patterns  
3. **Unit identifier normalization** - 3 separate implementations
4. **HNE territory validation** - 4 duplicated functions
5. **Address parsing** - 2 similar implementations
6. **File path resolution** - Multiple hardcoded patterns

## Detailed Duplication Patterns

### 1. Town Extraction Logic (High Priority)
**Files affected:** 4 files  
**Duplication level:** High - Same logic implemented 4 different ways

- `src/pipeline/parsing/html_extractor.py:174` - `extract_town_from_address()`
- `src/pipeline/parsing/html_extractor.py:196` - `extract_town_from_org()`  
- `src/pipeline/parsing/key_three_parser.py:55` - `extract_town_from_unitcommorgname()`
- `src/pipeline/core/unit_identifier.py:149` - `_extract_town_from_chartered_org()`
- `src/pipeline/parsing/scraped_data_parser.py:420` - `_parse_town_from_address()`

**Common patterns:**
- Regex patterns for address parsing: `,\s*([A-Za-z\s]+)\s+MA\s+\d{5}`
- Town validation using `TOWN_TO_DISTRICT` mapping
- Special handling for compound towns (e.g., "West Boylston")
- Dash-based organization name parsing

**Consolidation opportunity:** Create single `TownExtractor` class with methods for different source types.

### 2. JSON Data Loading (Medium Priority) 
**Files affected:** 8 files  
**Duplication level:** Medium - Similar patterns with minor variations

Repetitive pattern across files:
```python
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

**Files with identical patterns:**
- `src/pipeline/validation/three_way_validator.py:52,64`
- `src/pipeline/parsing/scraped_data_parser.py:65`
- `src/pipeline/reporting/generate_commissioner_report.py:178,193,226`
- `src/pipeline/reporting/generate_unit_emails_v2.py:45`
- `src/pipeline/analysis/quality_scorer.py:396`

**Consolidation opportunity:** Create `DataLoader` utility class with error handling, encoding management, and format validation.

### 3. Unit Identifier Processing (High Priority)
**Files affected:** 3 files  
**Duplication level:** High - Core business logic duplicated

- `src/pipeline/core/unit_identifier.py` - Primary implementation
- `src/pipeline/parsing/key_three_parser.py:168` - `extract_unit_info_from_unitcommorgname()`
- `src/pipeline/parsing/scraped_data_parser.py:237,252` - `_extract_unit_type()`, `_extract_unit_number()`

**Common logic:**
- Unit type extraction from various formats
- Unit number normalization (removing leading zeros)
- Town name standardization
- Unit identifier validation

**Consolidation opportunity:** Already partially centralized in `UnitIdentifierNormalizer`, but usage is inconsistent.

### 4. HNE Territory Validation (Medium Priority)
**Files affected:** 4 files  
**Duplication level:** Medium - Same validation logic repeated

- `src/pipeline/parsing/scraped_data_parser.py:586` - `_validate_hne_town()`
- `src/pipeline/parsing/scraped_data_parser.py:594` - `_is_outside_hne_territory()`
- `src/pipeline/parsing/key_three_parser.py:162` - `_is_valid_town()`
- `src/pipeline/parsing/html_extractor.py:292` - `filter_hne_units()`

**Common patterns:**
- Loading `TOWN_TO_DISTRICT` mapping
- Town name normalization before validation
- ZIP code to territory mapping

### 5. Address Parsing (Low Priority)
**Files affected:** 2 files  
**Duplication level:** Low - Similar regex patterns

- `src/pipeline/parsing/html_extractor.py:654` - `extract_address_from_text()`
- `src/pipeline/parsing/scraped_data_parser.py:420` - `_parse_town_from_address()`

**Common patterns:**
- Address format detection
- State/ZIP code handling
- PO Box filtering

### 6. File Path Resolution (Low Priority)
**Files affected:** Multiple files  
**Duplication level:** Low - Hardcoded paths repeated

**Hardcoded paths found:**
- `data/raw/key_three_enhanced_with_members.json` (3 files)
- `data/raw/all_units_comprehensive_scored.json` (4 files)
- `data/zipcodes/hne_council_zipcodes.json` (2 files)
- `data/output/three_way_validation_results.json` (2 files)

## Impact Analysis

### Current Problems
1. **Maintenance burden:** Bug fixes require changes in multiple locations
2. **Inconsistent behavior:** Different implementations may handle edge cases differently  
3. **Code bloat:** ~500+ lines of duplicate code across pipeline
4. **Testing complexity:** Each implementation needs separate test coverage

### Business Impact
- **Low reliability:** Inconsistent town extraction could cause unit matching failures
- **Technical debt:** Reduces development velocity for new features
- **Data quality issues:** Different parsing logic may produce inconsistent results

## Consolidation Recommendations

### Phase 1: High Priority (Immediate Action Required)
1. **Create `TownExtractor` utility class**
   - Consolidate all 4 town extraction implementations
   - Location: `src/pipeline/utils/town_extractor.py`
   - Estimated effort: 1-2 days

2. **Standardize `UnitIdentifierNormalizer` usage**
   - Update all files to use centralized unit processing
   - Remove duplicate implementations in parsers
   - Estimated effort: 1 day

### Phase 2: Medium Priority (Next 2 weeks)
3. **Create `DataLoader` utility class**
   - Centralize JSON loading with error handling
   - Location: `src/pipeline/utils/data_loader.py`
   - Estimated effort: 0.5 days

4. **Create `HNETerritoryValidator` class**  
   - Consolidate territory validation logic
   - Location: `src/pipeline/utils/territory_validator.py`
   - Estimated effort: 0.5 days

### Phase 3: Low Priority (Future refactoring)
5. **Create `AddressParser` utility class**
   - Consolidate address parsing patterns
   - Estimated effort: 0.5 days

6. **Create configuration constants file**
   - Centralize hardcoded file paths
   - Location: `src/pipeline/config/file_paths.py`
   - Estimated effort: 0.25 days

## File Structure Recommendations

```
src/pipeline/
├── utils/
│   ├── __init__.py
│   ├── town_extractor.py      # Consolidates 4 implementations
│   ├── data_loader.py         # Consolidates 8 JSON patterns
│   ├── territory_validator.py # Consolidates 4 HNE validators
│   └── address_parser.py      # Consolidates 2 address parsers
├── config/
│   └── file_paths.py         # Centralized path constants
└── [existing directories...]
```

## Success Metrics

### Before Consolidation
- **11 files** with duplicated functionality
- **~500 lines** of duplicate code
- **4 different** town extraction implementations
- **8 repetitive** JSON loading patterns

### After Consolidation (Target)
- **4 utility classes** handling common functionality
- **~200 lines** of duplicate code eliminated  
- **1 centralized** town extraction system
- **1 standardized** data loading pattern

## Next Steps

1. **Review this analysis** with development team
2. **Prioritize consolidation phases** based on business impact
3. **Create detailed implementation plan** for Phase 1 items
4. **Set up testing framework** for utility classes
5. **Plan migration strategy** for existing code