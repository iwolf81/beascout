# Enhancement Request: Website Validation and HTTPS Enforcement

**Date**: 2025-09-04  
**Priority**: Enhancement  
**Type**: Data Quality Improvement

## Request Description
Implement website URL validation to ensure websites exist and enforce secure HTTPS protocol instead of unsecure HTTP.

## Specific Issue Identified
Pack 148 East Brookfield (Soaring Eagle) has invalid website in scraped HTML data: `http://n/A`

## Proposed Enhancements

### 1. Website Existence Validation
- **Feature**: Validate that provided website URLs are reachable
- **Implementation**: HTTP/HTTPS head requests to verify URL responds
- **Quality Tag**: Add `QUALITY_INVALID_WEBSITE` for unreachable URLs
- **Examples to catch**: `http://n/A`, `https://website.com/notfound`, `http://invalidurl`

### 2. HTTPS Protocol Enforcement
- **Feature**: Flag websites using insecure HTTP protocol
- **Implementation**: URL protocol detection and recommendation
- **Quality Tag**: Add `QUALITY_INSECURE_WEBSITE` for HTTP (non-HTTPS) URLs  
- **Recommendation**: "Update website to use secure HTTPS protocol"

### 3. Website Format Validation
- **Feature**: Ensure website URLs follow proper format
- **Implementation**: URL format validation (protocol, domain structure)
- **Quality Tag**: Add `QUALITY_MALFORMED_WEBSITE` for format issues
- **Examples to catch**: `website.com` (missing protocol), `http://` (incomplete)

## Implementation Considerations

### Performance Impact
- Website validation requires network requests
- Consider async validation or caching to avoid performance issues
- May need timeout handling for slow/unresponsive sites

### Rate Limiting
- Implement respectful checking to avoid overwhelming target websites
- Consider batch processing with delays

### False Positives
- Some legitimate websites may have temporary downtime
- Consider retry logic or marking as "needs verification"

## Priority Justification
- **Data Quality**: Improves accuracy of unit information for families
- **Security**: Promotes secure HTTPS adoption  
- **User Experience**: Prevents families from encountering broken/invalid links

## Files to Modify
- `src/pipeline/analysis/quality_scorer.py`: Add website validation scoring
- `src/pipeline/parsing/html_extractor.py`: Optional - validate during extraction
- Quality tag definitions and recommendation text

## Success Criteria
- Invalid websites flagged with appropriate quality tags
- HTTP websites receive HTTPS upgrade recommendations
- Malformed URLs identified and corrected
- No performance degradation in processing pipeline