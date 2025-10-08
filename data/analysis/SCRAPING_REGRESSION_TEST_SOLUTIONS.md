# Scraping Regression Test Solutions Analysis

**Date**: September 28, 2025
**Context**: Analysis of regression testing solutions for HTML scraping components
**Project**: BeAScout Unit Information Analysis System

## Current Architecture Analysis

### Scraping Components
- **`src/pipeline/acquisition/browser_scraper.py`**: Playwright-based scraping with retry logic
- **`src/pipeline/acquisition/multi_zip_scraper.py`**: Multi-zip batch processing with rate limiting
- **`src/dev/scraping/url_generator.py`**: URL generation for BeAScout and JoinExploring *(misplaced)*

### Reference Data Available
- **`tests/reference/units/scraped/`**: 142 HTML files (71 BeAScout + 71 JoinExploring)
- Contains complete post-Ajax rendered HTML from live scraping sessions
- Covers all HNE Council zip codes with real unit data

### Architecture Issue Identified
**`url_generator.py` location**: Currently in `src/dev/scraping/` but used by production `browser_scraper.py`
- Should be moved to `src/pipeline/acquisition/` or `src/pipeline/core/`
- Violates separation between development and production code

## Proposed Solutions

### Solution 1: Mock URL Generator with File Loading (Recommended)

**Approach**: Replace URL generation with direct file loading during test mode

**Implementation**:
```python
# In browser_scraper.py
class BrowserScraper:
    def __init__(self, test_mode=False, test_data_path=None):
        self.test_mode = test_mode
        self.test_data_path = test_data_path or "tests/reference/units/scraped"
        if not test_mode:
            self.url_generator = DualSourceURLGenerator()

    async def scrape_beascout(self, zip_code, output_file=None):
        if self.test_mode:
            return self._load_test_file(f"beascout_{zip_code}.html")
        # Normal scraping logic...

    def _load_test_file(self, filename):
        file_path = Path(self.test_data_path) / filename
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        return None
```

**Pros**:
- ✅ Simple and direct implementation
- ✅ Uses existing reference files without modification
- ✅ Fast test execution (no network calls)
- ✅ Tests all scraping logic except URL generation
- ✅ Easy to implement and maintain

**Cons**:
- ❌ Doesn't test URL generation logic
- ❌ Doesn't test Playwright browser automation
- ❌ Limited to existing zip codes in reference data

### Solution 2: HTTP Response Interception with Playwright

**Approach**: Intercept network requests and return saved responses

**Implementation**:
```python
# In browser_scraper.py
class BrowserScraper:
    async def setup_test_interception(self, test_data_path):
        """Setup network interception for test mode"""
        async def handle_route(route, request):
            # Parse URL to extract zip code
            zip_code = self._extract_zip_from_url(request.url)

            # Determine site type and load appropriate test file
            if 'beascout.scouting.org' in request.url:
                file_path = Path(test_data_path) / f"beascout_{zip_code}.html"
            elif 'joinexploring.org' in request.url:
                file_path = Path(test_data_path) / f"joinexploring_{zip_code}.html"

            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                await route.fulfill(body=content, content_type='text/html')
            else:
                await route.continue_()

        await self.page.route("**/*", handle_route)
```

**Pros**:
- ✅ Tests complete Playwright automation flow
- ✅ Tests URL generation logic
- ✅ Tests browser setup, wait logic, selectors
- ✅ More comprehensive coverage

**Cons**:
- ❌ More complex implementation
- ❌ Playwright overhead (slower tests)
- ❌ Requires URL parsing to match files
- ❌ More brittle (dependent on URL patterns)

### Solution 3: Hybrid Approach with URL Validation

**Approach**: Combine file loading with URL generation testing

**Implementation**:
```python
class BrowserScraper:
    def __init__(self, test_mode=False, validate_urls=False):
        self.test_mode = test_mode
        self.validate_urls = validate_urls
        self.url_generator = DualSourceURLGenerator()

    async def scrape_beascout(self, zip_code, output_file=None):
        if self.test_mode:
            # Still generate URL for validation if requested
            if self.validate_urls:
                url = self.url_generator.generate_beascout_url(zip_code)
                self._validate_url_format(url, zip_code)

            # Load test file instead of scraping
            return self._load_test_file(f"beascout_{zip_code}.html")
        # Normal scraping...

    def _validate_url_format(self, url, zip_code):
        """Validate URL contains expected parameters"""
        assert zip_code in url
        assert 'program[0]=pack' in url
        # Additional validations...
```

**Pros**:
- ✅ Fast test execution (file loading)
- ✅ Optional URL generation testing
- ✅ Separates concerns cleanly
- ✅ Flexible test coverage

**Cons**:
- ❌ Still doesn't test browser automation
- ❌ URL validation is separate from actual usage
- ❌ More complex configuration

## Recommendation: Solution 1 (Mock URL Generator)

**Rationale**:
1. **Simplicity**: Direct file loading is straightforward and maintainable
2. **Speed**: Fast test execution suitable for regular regression testing
3. **Coverage**: Tests 95% of scraping functionality (parsing, file handling, retry logic)
4. **Reliability**: No network dependencies or Playwright complexity
5. **Implementation ease**: Minimal changes to existing code

**Missing Coverage Addressed Separately**:
- **URL generation**: Unit tests for `DualSourceURLGenerator` class
- **Browser automation**: Integration tests run periodically (not on every commit)

## Implementation Plan

### Phase 1: Code Organization
1. **Move `url_generator.py`** from `src/dev/scraping/` to `src/pipeline/core/`
2. **Update imports** in `browser_scraper.py` and `multi_zip_scraper.py`
3. **Verify existing functionality** still works

### Phase 2: Add Test Mode
1. **Add test mode parameters** to `BrowserScraper.__init__()`
2. **Implement file loading methods** for test mode
3. **Add test mode support** to both `scrape_beascout()` and `scrape_joinexploring()`

### Phase 3: Regression Test Integration
1. **Update `tests/run_regression_tests.py`** to include scraping step
2. **Add test case** that runs complete pipeline with test mode enabled
3. **Verify end-to-end** pipeline works with mocked scraping

### Phase 4: Unit Tests (Separate)
1. **Create unit tests** for `DualSourceURLGenerator`
2. **Add URL format validation** tests
3. **Test edge cases** and parameter encoding

## Expected Benefits

1. **Complete pipeline testing**: End-to-end regression from scraping through reports
2. **Fast execution**: Sub-second scraping tests vs. minutes for live scraping
3. **Reliable results**: No flaky network issues or site changes
4. **Safe testing**: No risk of being blocked by websites
5. **Maintainable**: Simple mock implementation easy to understand and modify

## Files Requiring Modification

- `src/pipeline/acquisition/browser_scraper.py` - Add test mode support
- `src/pipeline/acquisition/multi_zip_scraper.py` - Add test mode support
- `tests/run_regression_tests.py` - Include scraping in test pipeline
- `src/dev/scraping/url_generator.py` - Move to appropriate location