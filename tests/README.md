# BeAScout System Verification Tools

This directory contains verification tools to ensure that code changes don't break existing functionality. These tools should be run before committing changes or deploying updates.

## Quick Start

Run all verification tests:
```bash
python3 tests/verify_all.py
```

Run only critical tests (faster):
```bash
python3 tests/verify_all.py --quick
```

## Directory Structure

```
tests/
├── verify_all.py                    # Master verification script
├── reference/                       # Reference data for regression testing
│   ├── units/                      # Scraped HTML unit data verification
│   │   ├── input/                  # Reference scraped HTML files
│   │   ├── scripts/
│   │   │   └── verify_scraped_units.py
│   │   ├── unit_identifier_debug_scraped_reference_u.log
│   │   └── discarded_unit_identifier_debug_scraped_reference_u.log
│   ├── key_three/                  # Key Three data verification
│   │   ├── input/
│   │   │   └── HNE_key_three.xlsx  # Reference Key Three Excel file
│   │   ├── scripts/
│   │   │   └── verify_key_three.py
│   │   └── HNE_key_three.json      # Reference Key Three JSON output
│   └── towns/                      # HNE Towns data verification
│       └── input/
│           └── HNE_council_map.png # Reference district boundary map
└── README.md                       # This file
```

## Individual Verification Scripts

### 1. Scraped HTML Unit Data Verification

```bash
python3 tests/reference/units/scripts/verify_scraped_units.py
```

**What it does:**
- Runs the full scraping pipeline on reference HTML data
- Compares unit extraction results against reference debug logs
- Verifies critical fixes (e.g., Troop 7012 in Acton, Post 1872 filtered out)

**Reference data:**
- Input: `tests/reference/units/input/` (HTML files from 2025-08-24)
- Expected output: Unit identifier and discarded unit debug logs

### 2. Key Three Data Verification

```bash
python3 tests/reference/key_three/scripts/verify_key_three.py
```

**What it does:**
- Parses the reference Key Three Excel file
- Compares results against reference JSON output
- Verifies parsing logic for unit types, numbers, emails, etc.

**Reference data:**
- Input: `tests/reference/key_three/input/HNE_key_three.xlsx`
- Expected output: `tests/reference/key_three/HNE_key_three.json`

## How the Verification System Works

1. **Reference Data Creation**: Known-good input data and expected outputs are stored in `tests/reference/`

2. **Regression Testing**: Verification scripts run the current code on reference inputs and compare results

3. **Critical Test Cases**: Each script includes specific test cases for previously identified bugs:
   - Troop 7012 should be in "Acton" not "Boxborough"  
   - Post 1872 should be filtered out (non-HNE territory)
   - Unit number normalization (remove leading zeros)
   - Email parsing accuracy

4. **Automated Comparison**: Scripts use `diff` and custom logic to identify discrepancies

## When to Run Verification

**Always run before:**
- Committing changes to version control
- Deploying to production
- Releasing new versions

**Consider running after:**
- Modifying parsing logic
- Changing HNE territory filtering
- Updating data processing pipelines
- Adding new features that affect existing functionality

## Interpreting Results

### ✅ Success
All tests pass - your changes are safe to commit/deploy.

### ❌ Failure  
Some tests failed - review the output to identify:
- Missing or extra units compared to reference
- Changed unit properties (town, organization, etc.)
- Critical regression failures

### Common Failure Patterns

1. **Unit Count Changes**: May indicate filtering logic changes
2. **Town Name Changes**: Often indicates extraction logic regressions  
3. **Missing Critical Units**: May indicate HNE territory filtering issues
4. **Parsing Errors**: Could indicate Excel/HTML parsing regressions

## Updating Reference Data

If verification fails due to **intentional** changes (not bugs):

1. **Verify the changes are correct** by manual review
2. **Update reference files** with new expected outputs:
   ```bash
   # For scraped units (run after pipeline generates new debug files)
   sort -u data/debug/unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log > tests/reference/units/unit_identifier_debug_scraped_reference_u.log
   sort -u data/debug/discarded_unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log > tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log
   
   # For Key Three data
   cp data/input/HNE_key_three.json tests/reference/key_three/
   ```
3. **Document the changes** in commit messages and update logs

## Troubleshooting

**"Pipeline execution failed"**: Check that all dependencies are installed and paths are correct

**"Reference files not found"**: Make sure you're running from the project root directory

**"Import errors"**: Ensure Python path includes the project root and all dependencies are available

**Timeout errors**: Some verification tests have 5-10 minute timeouts. Large datasets may need timeout adjustments.