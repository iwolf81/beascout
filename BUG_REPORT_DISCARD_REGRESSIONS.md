# Bug Report: Remaining Discard Regressions

**Date**: 2025-09-04
**Priority**: Low (does not affect HNE unit identification)
**Status**: Identified, not blocking production

## Issue Description
While the unified location extraction successfully fixed all regressions for HNE units (no regressions in `unit_identifier_debug_scraped_20250904_072351_u.log`), some regressions remain in the discarded units log (`discarded_unit_identifier_debug_scraped_20250904_072351_u.log`).

## Impact Assessment
- **HNE Unit Processing**: ✅ No impact - all HNE units are correctly identified
- **Non-HNE Unit Classification**: ⚠️ Some non-HNE units may be misclassified in debug logs
- **Production Reports**: ✅ No impact - only affects discarded units logging

## Root Cause Analysis
The unified `extract_location_components()` function correctly extracts towns for HNE units, but some edge cases in non-HNE unit town extraction may still exist. The duplicate town extraction in HNE filtering has been eliminated, but there may be additional extraction logic elsewhere that affects discarded unit logging.

## Reproduction
1. Run HTML extraction on scraped data
2. Check `discarded_unit_identifier_debug_scraped_*.log` for town extraction inconsistencies
3. Compare with previous runs to identify specific regression patterns

## Workaround
None needed - this does not affect production functionality or HNE unit identification.

## Next Steps
1. Post-production analysis of discarded unit patterns
2. Review all town extraction code paths for consistency
3. Implement comprehensive unit testing for edge cases

## Files Affected
- `/Users/iwolf/Repos/beascout/src/pipeline/parsing/html_extractor.py` - unified extraction logic
- Debug logs in `/Users/iwolf/Repos/beascout/data/debug/discarded_*.log`

## Technical Notes
The issue is isolated to discarded (non-HNE) units and does not affect the primary business objective of accurate HNE unit identification and quality scoring.