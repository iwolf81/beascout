# Bug: Meeting Time Validation Issues

**Title**: Fix meeting time parsing and validation errors

**Labels**: bug, data-quality, high-priority

**Component**: processing (HTML→JSON)

## Bug Description
Meeting time parsing has multiple validation issues including invalid times, AM/PM confusion, and unit number contamination.

## Component Affected
- [x] processing (HTML→JSON)

## Current Behavior
**Invalid Times Generated**:
- Troop 7338 Charlton shows `73:38 AM` (invalid - hours > 24)
- Multiple units showing morning times that should be evening
- Mixed formats like `16:00 AM` (24-hour format with AM suffix)

## Expected Behavior
- All times should be valid (hours 1-12, minutes 0-59)
- Appropriate AM/PM designation based on Scout meeting patterns
- Consistent time format throughout
- No unit number contamination in time fields

## Impact Assessment
- **Scope**: Multiple units affected across different districts
- **Severity**: High (data accuracy)
- **Production Impact**: Yes - affects quality and credibility of reports

## Specific Examples from Pass 3 Feedback
**Source**: `SESSION_HANDOFF.md` lines 780-781, `data/debug/feedback_01Sep2025.md`

**Invalid Times Identified**:
- Troop 7338 Charlton: `73:38 AM` (unit number contamination)
- Multiple units: Morning times that should be evening meetings
- Format inconsistencies: `16:00 AM` combinations

## Root Cause Analysis
1. **Unit Number Contamination**: Unit numbers bleeding into time parsing
2. **AM/PM Logic Issues**: Insufficient validation for reasonable Scout meeting times
3. **Format Mixing**: 24-hour format mixed with AM/PM suffixes
4. **Edge Case Handling**: Poor validation for invalid time components

## Technical Details
- **File Location**: `src/pipeline/processing/html_extractor.py` and/or `src/pipeline/processing/scraped_data_parser.py`
- **Function/Method**: Time parsing and extraction logic
- **Pattern Matching**: Time regex patterns may be too permissive

## Proposed Solution
```python
def validate_and_fix_time(time_str):
    """Validate and fix common time parsing errors"""
    # Fix invalid times (hour > 24 or minute > 59)
    # Fix 24-hour format with AM/PM (16:00 AM → 4:00 PM) 
    # Fix unlikely Scout meeting times (5 AM → 5 PM)
    # NOTE: Pack meetings can start early on weekends (3 PM acceptable)
```

## Implementation Plan
1. **Enhanced Time Validation**: Add comprehensive time format validation
2. **Scout Meeting Logic**: Apply reasonable time constraints for Scout meetings
3. **Unit Number Filtering**: Prevent unit numbers from contaminating time fields
4. **Format Standardization**: Consistent time format output
5. **Edge Case Testing**: Test with problematic examples

## Additional Context
**User Note**: "Pack meetings can start early on weekend days such as 3 PM" - important context for validation logic

## Priority: High
This directly affects data accuracy and report credibility, making it a high-priority fix for data quality.

## Files to Modify
- `src/pipeline/processing/html_extractor.py` - Time extraction patterns
- `src/pipeline/processing/scraped_data_parser.py` - Time validation logic
- Add unit tests for time parsing edge cases

## Success Criteria
- All meeting times are valid and properly formatted
- No unit number contamination in time fields
- Appropriate AM/PM assignment based on Scout meeting patterns
- Edge cases handled gracefully with logging for review