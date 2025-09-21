# BeAScout Pipeline Manager

Pipeline Manager Design: beascout/src/pipeline/operation/generate_weekly_report.py

Key Features for Quick Issue Resolution:

1. Granular Stage Control

# Run specific stages only
python generate_weekly_report.py --stage scraping
python generate_weekly_report.py --stage processing
python generate_weekly_report.py --stage reporting
python generate_weekly_report.py --stage all  # default

2. Detailed Status Tracking

- Real-time progress display with timestamps
- Detailed logs saved to beascout/data/logs/generate_weekly_report_YYYYMMDD_HHMMSS.log
- Stage completion status saved to resume from failures
- Clear error messages with suggested fixes

3. Smart Recovery Options

# Resume from last successful stage
python generate_weekly_report.py --resume

# Skip problematic zip codes and continue
python generate_weekly_report.py --skip-failed-zips

# Use cached data if fresh scraping fails
python generate_weekly_report.py --fallback-to-cache

4. Validation & Health Checks

- Pre-flight checks (data sources exist, disk space, network)
- Post-stage validation (expected file counts, data quality)
- Automatic rollback to previous good state if needed

5. Output Management

- Output directory: beascout/data/output/reports/weekly
- Standardized filename: BeAScout_Weekly_Quality_Report_<YYYYMMDD>_<HHMMSS>.xlsx
- Backup of previous week's report
- Email draft preparation with distribution list
- Success/failure notifications

# Statistics Goals

- In the weekly email, it would be good to identify the changes in the QUALITY OVERVIEW statistics in the Executive Summary sheet in the report.
- It would also be good to identify units that improved their scores from the prior week as well as units whose score decreased.
- This would be useful information to track in the first pass and then get customer feedback before making more changes.
- The data/output/reports/weekly directory is good for the weekly reports.
- The filename should be BeAScout_Weekly_Quality_Report_<YYYYMMDD>_<HHMMSS>.xlsx. All reports should be in same directory.
- Would a .../weekly/analytics directory be the place to store the json files for each week, perhaps named BeAScout_Weekly_Quality_Analytics_<YYYYMMDD>_<HHMMSS>.json? I am asking, not directing. Propose alternatives.

# Ongoing Instructions
- Do NOT modify any files tagged with BEASCOUT_1.0.1_main_ef0e3cf.
  - If a change is necessary, clearly inform me that a tagged file is being changed.
  - I do not want to introduce any regressions especially since end-to-end regression testing is not yet implemented.
- After scraping completes, execute the 'udiff' alias on the new debug log.
  - This is a manual regression testing tool for scraping results.
  - Output the results to the pipeline log file.
  - Add a pass/fail message pipeline log file.