# Enhancement: Commissioner Report Comparison Tool

**Title**: Create tool for automatically comparing Commissioner Reports

**Labels**: enhancement, reporting, tools, medium-priority

**Component**: analysis (reports)

## Enhancement Description
Create an automated tool to compare BeAScout Quality Reports between different generation runs to identify regressions and improvements.

## Problem/Opportunity
**User Request**: "A tool for automatically comparing Commissioners Reports is needed. It will help identify regressions and improvements"

Currently, report comparison is manual, making it difficult to:
- Detect data quality regressions between runs
- Track improvement trends over time
- Validate that system changes don't negatively impact reports
- Provide objective metrics on data quality changes

## Proposed Solution
Develop a report comparison utility that:

1. **Excel Report Comparison**:
   - Compare unit counts, quality scores, grade distributions
   - Identify units that changed grades (A→B, etc.)
   - Flag missing or new units between reports
   - Calculate statistical differences in quality metrics

2. **Automated Diff Analysis**:
   - Side-by-side comparison of key metrics
   - Highlight significant changes (threshold-based)
   - Generate summary report of differences

3. **Trend Analysis**:
   - Track quality score improvements/regressions over time
   - Identify patterns in data quality changes
   - District-level comparison metrics

## User Story
As a **system administrator**, I want to **automatically compare Commissioner Reports** so that **I can quickly identify regressions and validate system improvements**.

## Acceptance Criteria
- [ ] Compare two Excel reports and generate difference summary
- [ ] Identify units with grade changes between reports
- [ ] Calculate statistical differences in quality metrics
- [ ] Output comparison results in readable format (HTML/Excel)
- [ ] Flag significant regressions for immediate attention
- [ ] Support batch comparison of multiple report versions

## Implementation Notes

**Technical Approach**:
- Use `pandas` to read Excel reports
- Compare DataFrames with unit keys as index
- Statistical analysis of quality score distributions
- HTML/Excel output for visual comparison

**Proposed File Structure**:
```
src/dev/tools/report_comparison.py  # Main comparison tool
src/dev/tools/report_diff_analyzer.py  # Analysis logic
templates/report_comparison.html  # Output template
```

## Files to Create/Modify
- `src/dev/tools/report_comparison.py` - Main comparison utility
- `src/dev/tools/report_diff_analyzer.py` - Comparison analysis logic
- `templates/report_comparison_template.html` - HTML output template
- `scripts/compare_reports.py` - Command-line interface

## Benefits
- **User Impact**: Immediate identification of data quality changes
- **System Impact**: Automated validation of system improvements
- **Business Impact**: Confidence in data quality and system reliability

## Command-Line Interface
```bash
# Compare two specific reports
python src/dev/tools/report_comparison.py \
  --report1 "data/output/reports/BeAScout_Quality_Report_20250905.xlsx" \
  --report2 "data/output/reports/BeAScout_Quality_Report_20250906.xlsx" \
  --output "comparison_20250905_vs_20250906.html"

# Compare latest report with previous
python scripts/compare_reports.py --latest --output-dir "data/output/comparisons/"
```

## Success Criteria
- Tool successfully compares any two Commissioner Reports
- Clear identification of units with quality changes
- Statistical summary of overall data quality trends
- HTML output that's easy to review and share
- Integration into regular reporting workflow

## Priority: Medium
This tool directly addresses a user request and supports ongoing system validation and improvement tracking.