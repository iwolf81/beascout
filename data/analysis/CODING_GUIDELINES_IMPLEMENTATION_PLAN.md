# Coding Guidelines Implementation Plan for BeAScout

**Date**: September 28, 2025
**Context**: Systematic application of coding guidelines to improve maintainability and safety
**Project**: BeAScout Unit Information Analysis System

## Executive Summary

This plan applies Google Python Style Guide, Clean Code principles, and safety-critical practices to the BeAScout codebase while maintaining production operations for the Heart of New England Council's 165 unit monitoring system.

**Approach**: Pipeline-by-pipeline refactoring with regression testing at each stage to ensure continuous operation.

## Implementation Strategy

### Core Principles
1. **Safety First**: No breaking changes to production functionality
2. **Incremental Progress**: One pipeline step at a time with full regression testing
3. **Regression Protection**: Complete test coverage before modifications
4. **Documentation Concurrency**: Update documentation with each change
5. **AI-Human Collaboration**: Clear handoffs and transparent reasoning

### Pipeline Processing Order
```
Phase 1: Acquisition (Scraping) →
Phase 2: Processing (HTML→JSON) →
Phase 3: Analysis (Reports/Emails) →
Phase 4: Core Infrastructure →
Phase 5: Testing Framework
```

## Phase 1: Acquisition Pipeline Refactoring

### 1.1 Scraping Regression Tests (Issue #18)
**Priority**: CRITICAL - Required before any acquisition changes

**Tasks**:
1. **Implement Solution 1** from SCRAPING_REGRESSION_TEST_SOLUTIONS.md
2. **Move `url_generator.py`** from `src/dev/scraping/` to `src/pipeline/core/`
3. **Add test mode** to `BrowserScraper` class
4. **Update regression pipeline** to include scraping step

**Implementation Details**:
```python
# browser_scraper.py modifications
class BrowserScraper:
    def __init__(self, test_mode=False, test_data_path="tests/reference/units/scraped"):
        self.test_mode = test_mode
        self.test_data_path = test_data_path
        if not test_mode:
            self.url_generator = DualSourceURLGenerator()

    async def scrape_beascout(self, zip_code, output_file=None):
        if self.test_mode:
            return self._load_test_file(f"beascout_{zip_code}.html")
        # Existing logic...
```

**Acceptance Criteria**:
- [ ] All existing functionality preserved
- [ ] Regression tests include scraping step
- [ ] Test execution time < 30 seconds
- [ ] 100% pass rate on existing test suite

### 1.2 Code Quality Improvements

**File**: `src/pipeline/acquisition/browser_scraper.py` (14 functions, 400+ lines)

**Critical Issues**:
1. **Generic Exception Handling**:
```python
# Current (lines 208-211)
if len(html_content) < 10000:
    raise Exception(f"Page content too small")

# Target
class InsufficientContentError(Exception):
    """Raised when scraped content is below minimum threshold"""
    pass

if len(html_content) < self.MIN_CONTENT_SIZE:
    raise InsufficientContentError(
        f"Content size {len(html_content)} below minimum {self.MIN_CONTENT_SIZE}"
    )
```

2. **Magic Numbers to Constants**:
```python
# Current - scattered throughout file
wait_timeout=45000, max_retries=3

# Target
class ScrapingConfig:
    WAIT_TIMEOUT_MS = 45000
    MAX_RETRIES = 3
    MIN_CONTENT_SIZE = 10000
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...'
```

3. **Function Documentation**:
```python
# Target template for all functions
async def scrape_beascout(self, zip_code: str, output_file: Optional[str] = None) -> Optional[str]:
    """
    Scrape BeAScout website for traditional scouting units.

    Inputs:
    - zip_code: 5-digit ZIP code for geographic search (00000-99999)
    - output_file: Optional file path for saving HTML content

    Outputs:
    - HTML content string or None if scraping failed
    - Side effects: May create output file, modifies browser state

    Raises:
    - NetworkTimeoutError: When page load exceeds timeout
    - InsufficientContentError: When content below minimum size
    - PlaywrightError: For browser automation failures
    """
```

### 1.3 Multi-Zip Scraper Refactoring

**File**: `src/pipeline/acquisition/multi_zip_scraper.py` (25 functions, 600+ lines)

**Critical Issues**:
1. **Missing argparse support** (Issue #22 requirement)
2. **Complex rate limiting logic** needs extraction
3. **Duplicate configuration patterns**

**Implementation**:
```python
# Add missing CLI arguments
def add_cli_arguments(self, parser):
    """Add multi-zip scraper arguments to parser"""
    parser.add_argument('--zip-codes-file',
                       default='data/zipcodes/hne_council_zipcodes.json',
                       help='JSON file containing zip codes to scrape')
    parser.add_argument('--mode', choices=['batch', 'single', 'resume'],
                       default='batch', help='Scraping execution mode')
    parser.add_argument('--output-dir',
                       default='data/scraped',
                       help='Directory for scraped HTML files')
```

## Phase 2: Processing Pipeline Refactoring

### 2.1 HTML Extractor Refactoring
**File**: `src/pipeline/processing/html_extractor.py` (919 lines - LARGEST FILE)

**Critical Issues**:
1. **Massive function complexity** - `extract_unit_fields()` (251 lines)
2. **Code duplication** across 3 files
3. **Mixed responsibilities** (parsing + validation + scoring)

**Extraction Strategy**:
```python
# Break into focused classes
class UnitFieldExtractor:
    """Handles extraction of individual unit fields"""

class MeetingInfoExtractor:
    """Specializes in meeting time/location parsing"""

class DescriptionProcessor:
    """Processes unit descriptions and contact info"""

class HTMLUnitParser:
    """Orchestrates the extraction process"""
```

**Specific Extractions**:
1. **Extract meeting info processing** (lines 671-786, 115 lines) → `MeetingInfoExtractor`
2. **Extract location formatting** (lines 29-89, 60 lines) → `LocationProcessor`
3. **Extract unit field parsing** (lines 414-664, 251 lines) → `UnitFieldExtractor`

### 2.2 Remove Code Duplication

**Target Files for Deletion**:
- `src/dev/archive/html_extractor_obsolete.py` (665 lines)
- `src/dev/archive/extract_all_units.py` (665 lines)

**Process**:
1. **Verify no references** to obsolete files
2. **Archive content** in git history
3. **Update imports** if any dependencies found
4. **Test regression suite** after removal

## Phase 3: Analysis Pipeline Refactoring

### 3.1 Quality Scorer Refactoring
**File**: `src/pipeline/core/quality_scorer.py` (420 lines)

**Critical Issues**:
1. **50+ email regex patterns** without organization
2. **Complex scoring logic** needs documentation
3. **Missing type safety** in critical functions

**Refactoring Plan**:
```python
class EmailValidator:
    """Centralized email validation with categorized patterns"""
    PERSONAL_PATTERNS = [...]
    BUSINESS_PATTERNS = [...]
    INVALID_PATTERNS = [...]

class QualityScorer:
    """Unit quality assessment with documented scoring rules"""

    def score_unit(self, unit: Dict[str, Any]) -> ScoringResult:
        """
        Calculate unit completeness score and quality tags.

        Inputs:
        - unit: Dictionary containing unit information fields

        Outputs:
        - ScoringResult: NamedTuple with score, grade, tags, details

        Raises:
        - ValidationError: When required fields missing or invalid
        """
```

### 3.2 Report Generation Refactoring
**File**: `src/pipeline/operation/generate_weekly_report.py` (997 lines - SECOND LARGEST)

**Critical Issues**:
1. **Mixed orchestration and configuration**
2. **Long pipeline function** (103 lines)
3. **Complex error handling** across subprocess calls

**Extraction Strategy**:
```python
class PipelineStage:
    """Base class for pipeline stage execution"""

class ScrapedDataProcessor(PipelineStage):
    """Handles HTML processing stage"""

class QualityAnalyzer(PipelineStage):
    """Handles analysis and reporting stage"""

class WeeklyReportOrchestrator:
    """Coordinates pipeline execution with error handling"""
```

## Phase 4: Core Infrastructure Refactoring

### 4.1 Unit Identifier Normalization
**File**: `src/pipeline/core/unit_identifier.py` (403 lines)

**Critical Issues**:
1. **Complex regex patterns** for unit key generation
2. **Town matching logic** scattered across methods
3. **Debug logging** mixed with business logic

### 4.2 Exception Handling Standardization

**Create Exception Hierarchy**:
```python
# src/pipeline/core/exceptions.py
class BeAScoutError(Exception):
    """Base exception for BeAScout operations"""
    def __init__(self, message: str, location: str, context: Dict[str, Any] = None):
        self.location = location
        self.context = context or {}
        super().__init__(f"{location}: {message}")

class ScrapingError(BeAScoutError):
    """Errors during web scraping operations"""

class NetworkTimeoutError(ScrapingError):
    """Network timeout during scraping"""

class ParsingError(BeAScoutError):
    """Errors during HTML parsing"""

class ValidationError(BeAScoutError):
    """Data validation failures"""
```

### 4.3 Configuration Management

**Create Centralized Configuration**:
```python
# src/pipeline/core/config.py
@dataclass
class ScrapingConfig:
    wait_timeout_ms: int = 45000
    max_retries: int = 3
    min_content_size: int = 10000
    batch_size: int = 8

@dataclass
class QualityConfig:
    passing_score_threshold: float = 0.8
    grade_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'A': 0.9, 'B': 0.8, 'C': 0.7, 'D': 0.6
    })
```

## Phase 5: Testing Framework Implementation

### 5.1 Unit Testing Infrastructure

**Create Test Structure**:
```
tests/
├── unit/
│   ├── test_quality_scorer.py
│   ├── test_unit_identifier.py
│   ├── test_html_extractor.py
│   └── test_url_generator.py
├── integration/
│   ├── test_pipeline_end_to_end.py
│   └── test_scraping_integration.py
└── fixtures/
    ├── sample_html/
    └── expected_outputs/
```

### 5.2 Critical Unit Tests

**Priority Functions for Testing**:
1. **Quality scoring algorithm** - All scoring rules and edge cases
2. **Unit identifier generation** - Key normalization and deduplication
3. **HTML field extraction** - Parse accuracy and error handling
4. **URL generation** - Parameter encoding and format validation

## Implementation Timeline

### Sprint 1 (Week 1): Scraping Regression Protection
- [ ] Implement scraping test mode
- [ ] Move url_generator.py to proper location
- [ ] Update regression tests to include scraping
- [ ] Verify 100% test pass rate

### Sprint 2 (Week 2): Acquisition Pipeline Cleanup
- [ ] Add exception hierarchy
- [ ] Extract magic numbers to constants
- [ ] Add comprehensive function documentation
- [ ] Add missing CLI arguments

### Sprint 3 (Week 3): Processing Pipeline Refactoring
- [ ] Break down html_extractor.py into focused classes
- [ ] Remove obsolete duplicate files
- [ ] Extract reusable parsing components
- [ ] Add unit tests for extraction logic

### Sprint 4 (Week 4): Analysis Pipeline Improvements
- [ ] Refactor quality scorer organization
- [ ] Simplify report generation orchestration
- [ ] Add comprehensive type hints
- [ ] Create configuration management

### Sprint 5 (Week 5): Testing and Documentation
- [ ] Complete unit test coverage for critical functions
- [ ] Update all documentation concurrently
- [ ] Perform final regression validation
- [ ] Create coding standards enforcement tools

## Risk Mitigation

### Production Safety Measures
1. **Backup Current State**: Git tag before each phase
2. **Regression First**: Never modify code without passing regression tests
3. **Incremental Changes**: Small, focused modifications with immediate testing
4. **Rollback Plan**: Keep previous versions available for immediate revert

### Quality Assurance
1. **Peer Review**: All changes require review against guidelines
2. **Automated Validation**: Run regression tests after each modification
3. **Documentation Updates**: Update docs concurrently with code changes
4. **Performance Monitoring**: Ensure no degradation in processing time

## Success Metrics

### Code Quality Improvements
- [ ] McCabe complexity ≤ 10 for all functions
- [ ] 100% type hint coverage for public APIs
- [ ] Zero duplicate code across active files
- [ ] Comprehensive function documentation

### Safety and Reliability
- [ ] Specific exception handling (no generic Exception catches)
- [ ] Unit test coverage ≥ 90% for critical business logic
- [ ] Zero regression test failures
- [ ] Clear error messages with unique identification

### Maintainability
- [ ] Single responsibility for all classes and functions
- [ ] Clear separation between pipeline stages
- [ ] Centralized configuration management
- [ ] Consistent coding patterns throughout codebase

This plan ensures systematic improvement while maintaining the production system serving the Heart of New England Council's 165 unit monitoring requirements.