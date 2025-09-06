# Bug: Personal Email Detection Not Applied

**Title**: Fix personal email detection for quality scoring tags

**Labels**: bug, quality-scoring, low-priority

**Component**: analysis (reports/emails)

## Bug Description
Troop 180 Holden has contact email "straightshooters@mail.com" but is not receiving the `QUALITY_PERSONAL_EMAIL` tag, despite the email appearing to be a personal/generic email rather than unit-specific.

## Component Affected
- [x] analysis (reports/emails)

## Current Behavior
- **Unit**: Troop 180 Holden (Quinapoxet District)
- **Contact Email**: "straightshooters@mail.com"
- **Current Tags**: No `QUALITY_PERSONAL_EMAIL` tag applied
- **Quality Impact**: Unit receives full credit for contact email

## Expected Behavior  
- Should receive `QUALITY_PERSONAL_EMAIL` tag for non-unit-specific email
- Quality scoring should apply appropriate penalty for personal email
- Unit should receive email continuity guidance in recommendations

## Impact Assessment
- **Scope**: Only 1 unit affected (Troop 180 Holden)
- **Severity**: Low (functional behavior mostly correct)
- **Production Impact**: Minimal - unit still receives other quality recommendations

## Root Cause Analysis
The personal email detection patterns may not be catching "straightshooters@mail.com" pattern. Possible causes:
1. Domain ".com" not in personal domain list 
2. Email pattern doesn't match current detection rules
3. Logic precedence issue with other email classification rules

## Technical Details
- **File Location**: `src/pipeline/core/quality_scorer.py`
- **Function/Method**: Personal email detection logic in contact email scoring
- **Pattern Matching**: Email classification rules and domain detection

## Proposed Solution
```python
def detect_personal_email(email):
    """Enhanced personal email detection"""
    # Review current domain patterns and detection rules
    # Add common personal email patterns
    # Handle generic/descriptive email addresses
    # Check for unit-specific vs generic naming patterns
```

## Additional Context
**Risk Assessment**: LOW RISK - Fixing this now could introduce regressions in other email detection logic. Better to address comprehensively during planned quality scoring improvements.

**User Note**: Does not affect core functionality. Can be addressed during next quality scoring enhancement cycle to avoid introducing regressions.

## Priority: Low
This is a classification issue with minimal impact. Quality scoring mostly works correctly, just missing one tag category.

## Files to Modify
- `src/pipeline/core/quality_scorer.py` - Enhanced personal email detection logic
- Unit tests for email classification edge cases

## Success Criteria
- Troop 180 Holden receives `QUALITY_PERSONAL_EMAIL` tag for "straightshooters@mail.com"
- Quality scoring applies appropriate penalty for personal emails
- Enhanced detection handles generic and descriptive email patterns
- No regression in existing email classification functionality
- Unit receives email continuity guidance in recommendations