# Bug: Discarded Unit Logging Regressions

**Title**: Fix town extraction regressions in discarded unit debug logs

**Labels**: bug, data-quality, low-priority

**Component**: processing (HTML→JSON)

## Bug Description
While the unified location extraction successfully fixed all regressions for HNE units, some regressions remain in the discarded units debug log, causing misclassification of non-HNE units in debug logging.

## Component Affected
- [x] processing (HTML→JSON)

## Current Behavior
- HNE units are correctly identified and processed ✅
- Some non-HNE units show inconsistent town extraction in `discarded_unit_identifier_debug_*.log`
- Debug logs show regressions in discarded unit classification patterns

## Expected Behavior  
- Consistent town extraction logic for both HNE and non-HNE units
- Clean debug logs with proper unit classification
- No regressions in discarded unit town identification

## Impact Assessment
- **Scope**: Only affects debug logging of discarded (non-HNE) units
- **Severity**: Low (does not affect production functionality)
- **Production Impact**: No impact - HNE unit identification works correctly

## Steps to Reproduce
1. Run HTML extraction on scraped data
2. Check `discarded_unit_identifier_debug_scraped_*.log` for town extraction inconsistencies
3. Compare with previous runs to identify specific regression patterns

## Root Cause Analysis
The unified `extract_location_components()` function correctly extracts towns for HNE units, but some edge cases in non-HNE unit town extraction may still exist. There may be additional extraction logic paths that affect discarded unit logging consistency.

## Technical Details
- **File Location**: `src/pipeline/processing/html_extractor.py`
- **Function/Method**: Unified location extraction logic and town extraction code paths
- **Debug Logs**: Located in `data/debug/discarded_*.log`

## Additional Context
**Technical Note**: The issue is isolated to discarded (non-HNE) units and does not affect the primary business objective of accurate HNE unit identification and quality scoring.

**User Note**: This is a post-production cleanup issue - all production functionality works correctly.

## Priority: Low
Does not affect production functionality or HNE unit identification. Can be addressed during next maintenance cycle.

## Files to Modify
- `src/pipeline/processing/html_extractor.py` - Review all town extraction code paths
- Add comprehensive unit testing for town extraction edge cases
- Improve debug logging consistency

## Success Criteria
- No regressions in discarded unit debug logs compared to baseline
- Consistent town extraction logic across all unit processing paths
- Comprehensive unit tests for edge cases in location extraction
- Clean debug logs with accurate unit classification patterns