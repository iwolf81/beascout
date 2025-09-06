# Enhancement: Website Validation and HTTPS Enforcement

**Title**: Implement website URL validation and HTTPS enforcement

**Labels**: enhancement, data-quality, security, medium-priority

**Component**: analysis (reports/emails)

## Enhancement Description
Implement website URL validation to ensure websites exist, are properly formatted, and enforce secure HTTPS protocol instead of unsecure HTTP.

## Problem/Opportunity
**Specific Issue**: Pack 148 East Brookfield (Soaring Eagle) has invalid website in scraped HTML data: `http://n/A`

Current system does not validate website URLs, leading to:
- Invalid or broken website links provided to families
- Security concerns with insecure HTTP protocol usage
- Poor user experience when families encounter non-functional links
- Data quality issues with malformed URLs

## Proposed Solution
Implement comprehensive website validation with three components:

1. **Website Existence Validation**:
   - Validate that provided website URLs are reachable via HTTP/HTTPS head requests
   - Add `QUALITY_INVALID_WEBSITE` tag for unreachable URLs
   - Catch patterns like: `http://n/A`, `https://website.com/notfound`, `http://invalidurl`

2. **HTTPS Protocol Enforcement**:
   - Flag websites using insecure HTTP protocol
   - Add `QUALITY_INSECURE_WEBSITE` tag for HTTP (non-HTTPS) URLs  
   - Recommendation: "Update website to use secure HTTPS protocol"

3. **Website Format Validation**:
   - Ensure website URLs follow proper format (protocol, domain structure)
   - Add `QUALITY_MALFORMED_WEBSITE` tag for format issues
   - Catch patterns like: `website.com` (missing protocol), `http://` (incomplete)

## User Story
As a **Scout family**, I want **all unit website links to be valid and secure** so that **I can reliably access unit information without security warnings or broken links**.

## Acceptance Criteria
- [ ] Invalid/unreachable websites flagged with `QUALITY_INVALID_WEBSITE` tag
- [ ] HTTP websites receive `QUALITY_INSECURE_WEBSITE` tag and HTTPS upgrade recommendations
- [ ] Malformed URLs identified with `QUALITY_MALFORMED_WEBSITE` tag
- [ ] Website validation integrated into quality scoring system
- [ ] No significant performance degradation in processing pipeline
- [ ] Respectful rate limiting to avoid overwhelming target websites

## Implementation Notes

**Performance Considerations**:
- Website validation requires network requests - implement async validation
- Add timeout handling for slow/unresponsive sites
- Consider caching validation results to avoid repeat checks

**Rate Limiting**:
- Implement respectful checking with delays between requests
- Batch processing to avoid overwhelming target websites

**False Positive Handling**:
- Some legitimate websites may have temporary downtime
- Consider retry logic or marking as "needs verification" rather than invalid

**Technical Approach**:
```python
async def validate_website_url(url):
    """Validate website existence and security"""
    # Format validation
    # HTTP HEAD request with timeout
    # Protocol security check  
    # Return validation results and recommendations
```

## Files to Create/Modify
- `src/pipeline/core/quality_scorer.py` - Add website validation scoring logic
- `src/pipeline/processing/html_extractor.py` - Optional: validate during extraction phase
- Quality tag definitions and recommendation text for website issues

## Benefits
- **User Impact**: Families receive valid, secure website links for unit information
- **System Impact**: Improved data quality and security compliance
- **Business Impact**: Enhanced credibility and user trust in Scout unit data

## Success Criteria
- Pack 148 East Brookfield's `http://n/A` website properly flagged as invalid
- All HTTP websites receive HTTPS upgrade recommendations
- Malformed URLs identified and tagged for correction
- Website validation runs efficiently without pipeline performance impact
- Quality scores accurately reflect website validity and security status

## Priority: Medium
Directly affects user experience and data quality for families searching for Scout units.