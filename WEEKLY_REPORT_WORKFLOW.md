# Weekly BeAScout Quality Report Workflow

## Overview
Automated system for generating weekly quality reports for manual email distribution to Council and District leadership. Designed for Sunday evening execution with robust error handling and recovery capabilities.

## Quick Start
```bash
# Run complete pipeline (recommended for Sunday evenings)
python src/pipeline/operation/generate_weekly_report.py

# Run with specific Key Three file
python src/pipeline/operation/generate_weekly_report.py --key-three-file "data/input/key_3_08-22-2025.xlsx"

# Run with explicit baseline for analytics comparison
python src/pipeline/operation/generate_weekly_report.py --baseline BeAScout_Weekly_Quality_Report_20250904_154530.json

# Or if you encounter issues, run stage by stage:
python src/pipeline/operation/generate_weekly_report.py --stage scraping
python src/pipeline/operation/generate_weekly_report.py --stage processing
python src/pipeline/operation/generate_weekly_report.py --stage validation
python src/pipeline/operation/generate_weekly_report.py --stage reporting
python src/pipeline/operation/generate_weekly_report.py --stage analytics
python src/pipeline/operation/generate_weekly_report.py --stage email_draft
```

## Pipeline Arguments Reference

### Main Pipeline Script: `generate_weekly_report.py`

**All Available Arguments**:
```bash
python src/pipeline/operation/generate_weekly_report.py [OPTIONS]

--stage {scraping,processing,validation,reporting,analytics,email_draft,all}
    Pipeline stage to run [default: all]

--resume
    Resume from last successful stage in previous session

--skip-failed-zips
    Skip zip codes that fail during scraping and continue

--fallback-to-cache
    Use cached data if fresh scraping fails

--session-id SESSION_ID
    Resume specific session ID

--key-three-file KEY_THREE_FILE
    Path to Key Three file (e.g., "data/input/Key_3_08-22-2025.xlsx")

--scraped-dir SCRAPED_DIR
    Path to scraped session directory (e.g., "data/scraped/20250920_191632")

--baseline BASELINE
    Baseline analytics file for week-over-week comparison
    (e.g., "BeAScout_Weekly_Quality_Report_20250904_154530.json")
```

**Common Usage Patterns**:
```bash
# Complete pipeline with custom Key Three file
python src/pipeline/operation/generate_weekly_report.py \
  --key-three-file "data/input/key_3_08-22-2025.xlsx"

# Resume from failure point
python src/pipeline/operation/generate_weekly_report.py --resume

# Use existing scraped data (skip scraping stage)
python src/pipeline/operation/generate_weekly_report.py \
  --scraped-dir "data/scraped/20250920_124820" \
  --key-three-file "data/input/key_3_08-22-2025.xlsx"

# Generate analytics with specific baseline
python src/pipeline/operation/generate_weekly_report.py \
  --stage analytics \
  --baseline BeAScout_Weekly_Quality_Report_20250904_154530.json

# Skip problematic zip codes during scraping
python src/pipeline/operation/generate_weekly_report.py \
  --skip-failed-zips --fallback-to-cache
```

## Individual Scripts Called by Pipeline

### 1. Scraping: `multi_zip_scraper.py`
```bash
# Called by pipeline as:
python src/pipeline/acquisition/multi_zip_scraper.py full [--skip-failed] [--fallback-cache]

# Manual usage:
python src/pipeline/acquisition/multi_zip_scraper.py {test|full}
  test: Scrape 3 zip codes for testing
  full: Scrape all 71 HNE zip codes
  --skip-failed: Continue if some zip codes fail
  --fallback-cache: Use cached data if scraping fails
```

### 2. Processing: `process_full_dataset.py`
```bash
# Called by pipeline as:
python src/pipeline/processing/process_full_dataset.py SCRAPED_DIR

# Manual usage:
python src/pipeline/processing/process_full_dataset.py SCRAPED_DIRECTORY
  SCRAPED_DIRECTORY: Path to directory containing HTML files (e.g., data/scraped/20250920_124820)
```

### 3. Key Three Conversion: `convert_key_three_to_json.py`
```bash
# Called by pipeline as:
python src/dev/tools/convert_key_three_to_json.py KEY_THREE_FILE

# Manual usage:
python src/dev/tools/convert_key_three_to_json.py KEY_THREE_FILE
  KEY_THREE_FILE: Path to Key Three Excel/CSV file (e.g., data/input/key_3_08-22-2025.xlsx)
```

### 4. Validation: `enhanced_validator.py`
```bash
# Called by pipeline as:
python src/pipeline/analysis/enhanced_validator.py --key-three KEY_THREE_JSON

# Manual usage:
python src/pipeline/analysis/enhanced_validator.py [OPTIONS]
  --quality-data PATH: Quality data JSON file [default: data/raw/all_units_comprehensive_scored.json]
  --key-three PATH: Key Three JSON file (required for pipeline)
  --output PATH: Output validation results file [default: data/output/enhanced_three_way_validation_results.json]
```

### 5. Reporting: `generate_commissioner_report.py`
```bash
# Called by pipeline as:
python src/pipeline/analysis/generate_commissioner_report.py \
  --session-id SESSION_ID \
  --key-three KEY_THREE_FILE \
  --scraped-session SCRAPED_SESSION_ID

# Manual usage:
python src/pipeline/analysis/generate_commissioner_report.py [OPTIONS]
  --quality-data PATH: Quality data JSON [default: data/raw/all_units_comprehensive_scored.json]
  --validation-file PATH: Validation results JSON [default: data/output/enhanced_three_way_validation_results.json]
  --key-three PATH: Key Three data file (JSON/Excel) for accurate filename display
  --output-dir PATH: Output directory [default: auto-determined]
  --session-id ID: Session ID for pipeline mode (generates weekly report path)
  --scraped-session ID: Scraped session ID for accurate data timestamp display
```

### 6. Analytics: `generate_weekly_analytics.py`
```bash
# Called by pipeline as:
python src/pipeline/analysis/generate_weekly_analytics.py [--baseline BASELINE_FILE]

# Manual usage:
python src/pipeline/analysis/generate_weekly_analytics.py [OPTIONS]
  --excel-file PATH: Excel report file [default: find latest in weekly reports directory]
  --output PATH: Output analytics JSON [default: same directory as Excel file]
  --baseline PATH: Baseline analytics file for comparison [default: auto-detect most recent]
```

### 7. Email Draft: `generate_weekly_email_draft.py`
```bash
# Called by pipeline as:
python src/pipeline/analysis/generate_weekly_email_draft.py [--scraped-session SCRAPED_SESSION_ID]

# Manual usage:
python src/pipeline/analysis/generate_weekly_email_draft.py [OPTIONS]
  --analytics-file PATH: Analytics JSON file [default: find latest in weekly reports directory]
  --output PATH: Output email draft [default: same directory as analytics file]
  --scraped-session ID: Scraped session ID for accurate data timestamp display
```

## Pipeline Stages

### 1. Scraping Stage
- **Purpose**: Scrape BeAScout and JoinExploring data for all 71 HNE zip codes
- **Duration**: ~90-120 minutes
- **Output**: `data/scraped/` directory with JSON files
- **Recovery**: `--skip-failed-zips` to continue if some zip codes fail

### 2. Processing Stage
- **Purpose**: Convert HTML to structured unit data with quality scoring
- **Duration**: ~5-10 minutes
- **Output**: `data/raw/all_units_comprehensive_scored.json`
- **Dependencies**: Scraping stage completion

### 3. Validation Stage
- **Purpose**: Correlate scraped data with Key Three registry
- **Duration**: ~2-3 minutes
- **Output**: `data/output/enhanced_three_way_validation_results.json`
- **Dependencies**: Processing stage + Key Three CSV file

### 4. Reporting Stage
- **Purpose**: Generate Excel quality report for leadership distribution
- **Duration**: ~1-2 minutes
- **Output**: `data/output/reports/weekly/BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.xlsx`
- **Dependencies**: Processing + Validation stages

### 5. Analytics Stage
- **Purpose**: Generate weekly analytics and compare with previous week
- **Duration**: ~1 minute
- **Output**: `data/output/reports/weekly/BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.json`
- **Dependencies**: Reporting stage completion

### 6. Email Draft Stage
- **Purpose**: Create complete email draft for copy/paste distribution
- **Duration**: ~30 seconds
- **Output**: `data/output/reports/weekly/BeAScout_Weekly_Email_Draft_YYYYMMDD_HHMMSS.txt`
- **Dependencies**: Analytics stage + Email configuration

## Error Recovery Options

### Resume from Failure
```bash
# Resume from last successful stage
python src/pipeline/operation/generate_weekly_report.py --resume

# Resume specific session by ID
python src/pipeline/operation/generate_weekly_report.py --resume --session-id 20250920_124820
```

### Skip Problem Areas
```bash
# Skip zip codes that fail during scraping
python src/pipeline/operation/generate_weekly_report.py --skip-failed-zips

# Use cached data if fresh scraping fails
python src/pipeline/operation/generate_weekly_report.py --fallback-to-cache

# Combine both for maximum resilience
python src/pipeline/operation/generate_weekly_report.py --skip-failed-zips --fallback-to-cache
```

### Use Existing Data
```bash
# Use existing scraped data (skip scraping completely)
python src/pipeline/operation/generate_weekly_report.py \
  --scraped-dir "data/scraped/20250920_124820" \
  --key-three-file "data/input/key_3_08-22-2025.xlsx"

# Process existing scraped data only
python src/pipeline/operation/generate_weekly_report.py \
  --stage processing \
  --scraped-dir "data/scraped/20250920_124820"

# Generate report with specific Key Three file
python src/pipeline/operation/generate_weekly_report.py \
  --stage reporting \
  --key-three-file "data/input/key_3_08-22-2025.xlsx" \
  --scraped-dir "data/scraped/20250920_124820"
```

### Run Individual Stages
```bash
# If scraping fails, try processing existing data
python src/pipeline/operation/generate_weekly_report.py --stage processing

# Generate report from existing data with specific Key Three file
python src/pipeline/operation/generate_weekly_report.py \
  --stage reporting \
  --key-three-file "data/input/key_3_08-22-2025.xlsx"

# Generate analytics with explicit baseline comparison
python src/pipeline/operation/generate_weekly_report.py \
  --stage analytics \
  --baseline BeAScout_Weekly_Quality_Report_20250904_154530.json

# Generate weekly email draft with correct scraped timestamp
python src/pipeline/operation/generate_weekly_report.py \
  --stage email_draft \
  --scraped-dir "data/scraped/20250920_124820"
```

## Manual Distribution Workflow

### 1. Report Generation (Sunday Evening)
1. **Execute pipeline**:
   ```bash
   cd /path/to/beascout
   python src/pipeline/operation/generate_weekly_report.py
   ```

2. **Monitor progress**:
   - Watch console output for real-time status
   - Check `data/logs/generate_weekly_report_YYYYMMDD_HHMMSS.log` for detailed logs
   - Pipeline saves status to `data/logs/pipeline_status_YYYYMMDD_HHMMSS.json`

3. **Verify completion**:
   - Look for "🎉 Pipeline completed successfully!" message
   - Check that all files exist in `data/output/reports/weekly/`:
     - Excel report: `BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.xlsx`
     - Analytics data: `BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.json`
     - Email draft: `BeAScout_Weekly_Email_Draft_YYYYMMDD_HHMMSS.txt`
   - Excel file size should be >100KB (typically 1-3MB)

### 2. Report Review
1. **Open generated Excel file**:
   - Latest file: `data/output/reports/weekly/BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.xlsx`

2. **Review Executive Summary sheet**:
   - Quality metrics and grade distribution
   - Units by district breakdown
   - Data source information and timestamps

3. **Spot-check district sheets**:
   - Verify unit information looks accurate
   - Check quality grades and recommendations
   - Confirm Key Three contact information is present

### 3. Email Distribution

**UPDATED WORKFLOW - Copy/Paste from Generated Draft**:

1. **Open email draft file**:
   - Latest file: `data/output/reports/weekly/BeAScout_Weekly_Email_Draft_YYYYMMDD_HHMMSS.txt`

2. **Copy/paste email components**:
   - **Recipients**: Copy from "EMAIL RECIPIENTS" section and paste into To: field
   - **Subject**: Copy from "EMAIL SUBJECT" section and paste into Subject: field
   - **Body**: Copy from "EMAIL BODY" section and paste into message body
   - **Attachment**: Attach the Excel file listed in "ATTACHMENT" section

3. **Review and send**:
   - Verify all statistics look reasonable
   - Confirm attachment is correct Excel file
   - Send to leadership distribution list

**Email draft includes**:
- Pre-populated recipient list with actual email addresses
- Formatted subject line with current date
- Body with week-over-week statistics and unit improvements/declines
- Clear attachment filename for easy identification

## Troubleshooting Guide

### Common Issues

**🔥 "Network connectivity failed"**
- Check internet connection
- Try `--fallback-to-cache` to use existing data
- BeAScout.org may be temporarily unavailable

**🔥 "No Key Three CSV files found"**
- Place latest Key Three export in `data/input/Key_3_*.csv`
- Ensure filename matches pattern `Key_3_YYYY-MM-DD.csv`

**🔥 "Scraping stage failed"**
- Use `--skip-failed-zips` to continue with partial data
- Check specific zip code errors in detailed log
- Some zip codes may have temporary issues

**🔥 "Quality scoring incomplete"**
- Usually indicates HTML parsing issues
- Review processing stage logs for specific errors
- May need to re-run scraping stage

**🔥 "Report generation failed"**
- Check that all input files exist and are valid JSON
- Verify Excel dependencies are installed (`openpyxl`)
- Check disk space in output directory

**🔥 "Key Three filename not specified"**
- Use `--key-three-file` parameter to specify exact file
- Ensure Key Three file exists in `data/input/` directory
- File must be .xlsx or .csv format

**🔥 "Analytics baseline not found"**
- Use `--baseline` parameter to specify exact baseline file
- Check that baseline analytics JSON file exists
- Baseline file should be in `data/output/reports/weekly/` directory

**🔥 "Email shows wrong data timestamp"**
- Use `--scraped-dir` parameter to specify correct scraped session
- Verify scraped session contains `session_summary.json`
- Pipeline automatically passes scraped timestamps when run completely

### Recovery Strategies

**Partial Pipeline Failure**:
1. Use `--resume` to continue from last successful stage
2. Check logs to identify root cause
3. Fix underlying issue and re-run failed stage only

**Complete Pipeline Failure**:
1. Check pre-flight requirements (network, dependencies, disk space)
2. Verify required data files exist in `data/input/`
3. Run with `--fallback-to-cache` if network issues persist

**Sunday Evening Time Pressure**:
1. If scraping fails, use most recent cached data
2. Generate report from existing processed data
3. Note data freshness in distribution email

## File Locations

**Logs**: `data/logs/generate_weekly_report_YYYYMMDD_HHMMSS.log`
**Status**: `data/logs/pipeline_status_YYYYMMDD_HHMMSS.json`
**Reports**: `data/output/reports/weekly/BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.xlsx`
**Analytics**: `data/output/reports/weekly/BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.json`
**Email Draft**: `data/output/reports/weekly/BeAScout_Weekly_Email_Draft_YYYYMMDD_HHMMSS.txt`
**Scraped Data**: `data/scraped/session_summary.json` + individual zip code files
**Processed Data**: `data/raw/all_units_comprehensive_scored.json`
**Validation Results**: `data/output/enhanced_three_way_validation_results.json`
**Email Config**: `data/config/email_distribution.json`

## Performance Expectations

**Full Pipeline Runtime**: ~2-3 hours (mostly scraping)
**Report Generation Only**: ~5 minutes (if data already exists)
**Analytics + Email Generation**: ~1-2 minutes (if report already exists)
**Expected File Sizes**:
- Scraped data: ~50-100MB total
- Processed data: ~5-10MB
- Excel report: ~1-3MB
- Analytics JSON: ~50-200KB
- Email draft: ~5-15KB

## Success Criteria (Issue #30)

✅ **Automated data extraction**: Pipeline pulls latest ScoutBook data automatically
✅ **Quality metrics calculation**: Comprehensive quality analysis with A-F grading
✅ **XLSX report generation**: Professional Excel format with multiple sheets
✅ **Manual distribution**: Ready-to-attach file for email distribution
✅ **Professional formatting**: Headers, styling, charts, hyperlinks
✅ **Data completeness**: All current quality metrics included
✅ **Filename convention**: Standardized naming with timestamp
✅ **Error handling**: Graceful failure with clear error messages and recovery options

## BONUS FEATURES IMPLEMENTED

✅ **Weekly analytics**: Week-over-week comparison of quality metrics and unit improvements
✅ **Email draft generation**: Complete copy/paste email with recipients, subject, and statistics
✅ **Simplified workflow**: Single command generates report, analytics, and email draft
✅ **Configuration management**: Email addresses and templates stored in configuration files
✅ **Accurate timestamps**: Reports and emails show actual scraped data timestamp, not generation time
✅ **Baseline analytics**: Explicit baseline comparison for week-over-week analysis
✅ **Key Three integration**: Automatic Key Three filename display in reports

## Future Enhancements

- **Automated scheduling**: Cron job for Sunday evening execution
- **Email integration**: Direct email sending with distribution lists
- **Delta reporting**: Compare with previous week's data for trend analysis
- **Mobile notifications**: SMS/push alerts for pipeline completion/failure