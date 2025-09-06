# Bug: PO Box Detection Logic Not Applied

**Title**: Fix PO Box detection for quality scoring tags

**Labels**: bug, quality-scoring, low-priority

**Component**: analysis (reports/emails)

## Bug Description
Post 4879 Groton has unit-address containing only a PO Box address but is not receiving the `QUALITY_POBOX_LOCATION` tag. Instead, it receives `REQUIRED_MISSING_LOCATION`.

## Component Affected
- [x] analysis (reports/emails)

## Current Behavior
- **Unit**: Post 4879 Groton
- **Unit Address**: "PO Box 314 Groton MA 01450" 
- **Current Tags**: `REQUIRED_MISSING_LOCATION`
- **Quality Impact**: Still receives half credit for PO Box location per scoring rules

## Expected Behavior  
- Should receive `QUALITY_POBOX_LOCATION` tag instead of `REQUIRED_MISSING_LOCATION`
- Quality scoring should remain the same (half credit for PO Box)
- More accurate categorization for reporting purposes

## Impact Assessment
- **Scope**: Only 1 unit affected (Post 4879 Groton)
- **Severity**: Low (functional behavior correct, just tag classification)
- **Production Impact**: Minimal - Key Three still receives appropriate guidance

## Root Cause Analysis
The presence of the town name 'Groton' in the unit-address field `"PO Box 314<br>Groton MA 01450"` may be preventing the PO Box detection logic from triggering properly in the location parsing.

## Technical Details
- **File Location**: `src/pipeline/core/quality_scorer.py`
- **Function/Method**: PO Box detection logic in meeting location scoring
- **Pattern Matching**: PO Box regex patterns may not account for town names in same field

## Proposed Solution
```python
def detect_pobox_location(address_text):
    """Enhanced PO Box detection with town name handling"""
    # Current: May only check for "PO Box" at start of string
    # Enhanced: Check for "PO Box" anywhere in address field
    # Handle cases with embedded town names and formatting
```

## Additional Context
**User Note**: Current behavior is functionally correct - unit will still receive appropriate guidance to provide street address instead of PO Box only. Quality scoring already applies half credit correctly.

## Priority: Low
This is a classification issue rather than functional defect. Quality scoring works correctly, just different tag categorization.

## Files to Modify
- `src/pipeline/core/quality_scorer.py` - Enhanced PO Box detection logic
- Unit tests for edge cases in address parsing

## Success Criteria
- Post 4879 Groton receives `QUALITY_POBOX_LOCATION` tag instead of `REQUIRED_MISSING_LOCATION`
- Quality scoring remains unchanged (half credit for PO Box locations)
- Enhanced detection handles town names and formatting variations
- No regression in existing PO Box detection functionality