# Regression Test Pipeline Documentation

Complete end-to-end pipeline using stable reference data for development, testing, and regression validation.

## **🔒 Data Isolation**

**CRITICAL: Regression tests use separate output directories to prevent contaminating production data.**

| File Type | Production Path | Regression Test Path |
|-----------|----------------|---------------------|
| Validation Results | `data/output/enhanced_three_way_validation_results.json` | `data/output/regression/enhanced_three_way_validation_results.json` |
| Excel Reports | `data/output/reports/*.xlsx` | `data/output/regression/reports/*.xlsx` |
| Unit Emails | `data/output/unit_emails/*.md` | `data/output/regression/unit_emails/*.md` |

**Why This Matters:**
- Production uses real Key Three data from `data/input/Key_3_09-29-2025.xlsx`
- Regression tests use anonymized data from `tests/reference/key_three/anonymized_key_three.json`
- Without separation, regression tests would overwrite production files with anonymized data

## **⚡ Quick Start**

**Run complete regression test suite:**
```bash
python tests/run_regression_tests.py
```

**Run with detailed logging:**
```bash
python tests/run_regression_tests.py --log --verbose
```

**Expected result:** All tests pass (6/6 steps) with clear PASS/FAIL reporting.

## **📁 Reference Data Sources**

### **Available Reference Data:**
- **Scraped Unit Data**: `tests/reference/units/scraped/*.html` (72+ HTML files from BeAScout/JoinExploring)
- **Key Three Data**: `tests/reference/key_three/anonymized_key_three.xlsx` & `.json` (169 units with anonymized contacts)
- **HNE Territory**: `tests/reference/towns/hne_council_zipcodes.json` (65 towns, 75 zip codes)

### **Reference Data Benefits:**
- **No Network Dependency**: Uses pre-scraped stable reference data
- **Fast Development**: Complete pipeline in minutes vs hours of scraping
- **Safe Data**: Anonymized test data prevents accidental exposure of personal information
- **Consistent Results**: Same input data produces reproducible outputs for regression testing

---

## **🔄 Complete Reference Pipeline Commands**

Execute these commands in sequence to run the complete pipeline with reference data:

### **Step 1: Process Reference Scraped HTML Data**
```bash
# Input: tests/reference/units/scraped/*.html (pre-scraped reference data)
# Output: data/raw/all_units_comprehensive_scored.json (processed units with quality scores)

python -u src/pipeline/processing/process_full_dataset.py tests/reference/units/scraped/ 2>&1 | tee data/logs/process_full_dataset_$(date +%Y%m%d_%H%M%S).log
```

### **Step 2: Three-Way Unit Validation**
```bash
# Input: data/raw/all_units_comprehensive_scored.json + reference Key Three data
# Output: data/output/regression/enhanced_three_way_validation_results.json (unit presence correlation)

python src/pipeline/analysis/three_way_validator.py \
  --key-three tests/reference/key_three/anonymized_key_three.json \
  --output data/output/regression/enhanced_three_way_validation_results.json
```

### **Step 3: Generate Commissioner Report**
```bash
# Input: processed unit data + validated correlation data + reference Key Three
# Output: data/output/regression/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx

python src/pipeline/analysis/generate_commissioner_report.py \
  --key-three tests/reference/key_three/anonymized_key_three.json \
  --validation-file data/output/regression/enhanced_three_way_validation_results.json \
  --output-dir data/output/regression/reports \
  2>&1 | tee data/logs/generate_commissioner_report_$(date +%Y%m%d_%H%M%S).log
```

### **Step 4: Generate Unit Emails**
```bash
# Input: validation results with joined Key Three data
# Output: data/output/regression/unit_emails/ (personalized improvement emails)

python src/pipeline/analysis/generate_unit_emails.py \
  data/output/regression/enhanced_three_way_validation_results.json \
  --output-dir data/output/regression/unit_emails \
  2>&1 | tee data/logs/generate_unit_emails_$(date +%Y%m%d_%H%M%S).log
```

---

## **🤖 Automated Regression Testing**

### **Automated Test Runner (Recommended)**

The automated regression test runner executes all pipeline components and validates outputs in a single command:

**Basic Usage:**
```bash
# Run complete regression test suite (recommended)
python tests/run_regression_tests.py

# Run with detailed output
python tests/run_regression_tests.py --verbose

# Run with session logging
python tests/run_regression_tests.py --log

# Run unit processing test only (faster)
python tests/run_regression_tests.py --unit-only
```

**Example Output:**
```
================================================================================
REGRESSION TEST SUMMARY
================================================================================
✅ ALL TESTS PASSED
📊 Steps: 6/6 passed (100.0%)
🔍 Session ID: 20250929_083029

📁 Generated Files:
  - data/debug/cross_reference_validation_debug_20250929_083041.log
  - data/debug/unit_identifier_debug_scraped_20250929_083029.log
  - data/output/regression/reports/BeAScout_Quality_Report_20250929_083029.xlsx
  - data/output/regression/enhanced_three_way_validation_results.json
  - data/output/regression/unit_emails/*.md

📄 Log Files:
  - data/logs/process_full_dataset_20250929_083029.log
  - data/logs/three_way_validator_20250929_083029.log

Detailed Results:
  ✅ PASS - Step 1/6: Process Full Dataset
  ✅ PASS - Step 2/6: Unit Processing Regression Test (udiff)
  ✅ PASS - Step 3/6: Three-Way Validation
  ✅ PASS - Step 4/6: Three-Way Validation Regression Test (vdiff)
  ✅ PASS - Step 5/6: Generate Commissioner Report
  ✅ PASS - Step 6/6: Excel Report Regression Test (ediff)
```

**Test Components:**
1. **Process Full Dataset** - HTML processing with quality scoring
2. **Unit Processing Regression** - Validates unit extraction consistency
3. **Three-Way Validation** - Unit presence correlation analysis
4. **Validation Regression** - Validates correlation logic consistency
5. **Commissioner Report** - Excel report generation
6. **Excel Report Regression** - Validates report format and data consistency

**Session Management:**
- Uses unified session timestamps for file correlation
- Supports `--log` flag for detailed debug logging
- Generates session-correlated files for easy debugging
- Tracks all generated files and provides summary

**Available Command Line Options:**
```bash
python tests/run_regression_tests.py [options]

Options:
  --unit-only    Run only unit processing test (faster development cycle)
  --verbose      Show detailed test execution information
  --log          Enable session logging with detailed debug output
  --session-id   Specify custom session ID for file correlation
```

**Troubleshooting Automated Tests:**
- **Import errors**: Ensure running from project root (`/Users/iwolf/Repos/beascout`)
- **Missing reference files**: Run `ls tests/reference/units/scraped/*.html | wc -l` (should show 70+ files)
- **Test failures**: Check specific step output and compare with manual regression commands
- **Session correlation**: Use `--log` to generate correlated debug files for investigation

---

## **🧪 Manual Regression Testing Framework**

### **Prerequisites**
Load regression testing aliases from `~/.zshrc`:
```bash
source ~/.zshrc
```

### **Regression Test Status:**

#### **✅ 1. Unit Processing Regression Test (READY)**
```bash
# Compare process_full_dataset.py debug log for HNE units to reference
cd data/debug/
udiff unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log
# Expected: "PASS: No differences with reference log"
```

#### **✅ 2. Three-Way Validation Regression Test (READY)**
```bash
# Compare three_way_validator.py debug log to reference output
cd data/debug/
vdiff cross_reference_validation_debug_YYYYMMDD_HHMMSS.log
# Expected: "PASS: No differences with reference log"
```

#### **✅ 3. Excel Report Regression Test (READY)**
```bash
# Compare generated Excel report to reference baseline using ediff alias
ediff data/output/regression/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx
# Expected: "PASS: Excel reports are functionally identical"

# Manual comparison (if needed for debugging):
python tests/tools/compare_excel_files.py \
  tests/reference/reports/BeAScout_Quality_Report_anonymized.xlsx \
  data/output/regression/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx \
  --exit-code --quiet

# Exit codes:
# 0 = Reports are functionally identical (PASS)
# 1 = Reports have content differences (FAIL - investigate)
# 2 = Comparison tool error (FAIL - fix issue)

# NOTE: Timestamps use consistent YYYY-MM-DD HH:MM:SS format
# Tool normalizes: "2025-09-25 20:06:54" → "[NORMALIZED_DATETIME]"
```

#### **❌ 4. Discarded Units Test (NOT READY - Open Defect)**
```bash
# NOTE: dudiff disabled due to open defect with discarded units output
# See: beascout issue #5 (unit town names)
#
# When fixed, this test will work:
# dudiff discarded_unit_identifier_debug_scraped_YYYYMMDD_HHMMSS.log
```

### **Regression Test Aliases**

These aliases are defined in `~/.zshrc` for convenient regression testing:

```bash
# Unit processing comparison with improved pass/fail output
alias udiff='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}" && echo "PASS: No differences with reference log"; }; f'

# Three-way validation comparison
alias vdiff='f() { diff ~/Repos/beascout/tests/reference/reports/cross_reference_validation_debug_reference.log "$1" && echo "PASS: No differences with reference log"; }; f'

# Excel report regression test
alias ediff='f() { python tests/tools/compare_excel_files.py tests/reference/reports/BeAScout_Quality_Report_anonymized.xlsx "$1" --exit-code --quiet && echo "PASS: Excel reports are functionally identical"; }; f'

# Discarded units comparison (DISABLED - pending defect fix)
# alias dudiff='f() { fname="$1"; base="${fname%.*}"; ext="${fname##*.}"; sort -u "$fname" > "${base}_u.${ext}"; diff ~/Repos/beascout/tests/reference/units/discarded_unit_identifier_debug_scraped_reference_u.log "${base}_u.${ext}"; }; f'
```

---

## **📊 Expected Reference Pipeline Results**

### **Data Processing Results:**
- **Scraped Units**: ~165 HNE units processed from reference HTML files
- **Unit Correlation**: Complete correlation analysis between web data and Key Three registry
- **Quality Score**: ~60% average completeness across reference units
- **Missing Web Presence**: 4 units identified lacking web visibility

### **Generated Outputs:**
- **Excel Commissioner Report**: Professional district-organized quality report with Key Three contacts
- **Unit Improvement Emails**: 169 personalized emails with specific improvement recommendations
- **Validation Results**: Complete unit presence correlation analysis
- **Debug Logs**: Comprehensive processing logs for regression validation

### **Safe Development Features:**
- **Anonymized Data**: All personal information replaced with fake data
- **Git Safe**: No real personal data, safe to commit and share
- **Pipeline Compatible**: Maintains all unit relationships and organizational structure
- **Reproducible**: Same reference data produces consistent results

---

## **🔧 Troubleshooting**

### **Common Issues:**

#### **Import Errors**
If you see `ModuleNotFoundError: No module named 'src'`, ensure you're running from the project root:
```bash
cd /Users/iwolf/Repos/beascout
python src/pipeline/processing/process_full_dataset.py tests/reference/units/scraped/
```

#### **Missing Reference Files**
Verify all reference data exists:
```bash
ls tests/reference/units/scraped/*.html | wc -l  # Should show 72+ files
ls tests/reference/key_three/anonymized_key_three.*  # Should show .xlsx and .json
ls tests/reference/towns/hne_council_zipcodes.json   # Should exist
```

#### **Regression Test Failures**
If regression tests fail:
1. Check if changes are intentional improvements vs actual regressions
2. Review debug logs for specific differences
3. Update reference files if changes are valid improvements
4. Investigate code changes if differences indicate bugs

---

## **📋 Development Workflow**

### **Standard Development Cycle:**
1. **Make Code Changes**: Modify pipeline components
2. **Run Reference Pipeline**: Execute complete pipeline with reference data
3. **Run Regression Tests**: Validate against known good baselines
4. **Investigate Differences**: Determine if changes are improvements or regressions
5. **Update References**: If changes are improvements, update reference baselines
6. **Commit Changes**: Only after regression validation passes

### **Before Production Deployment:**
1. **Complete Reference Pipeline**: Verify all steps execute successfully
2. **All Regression Tests**: Ensure `udiff` and `vdiff` pass (when `dudiff` and Excel comparison are ready)
3. **Manual Spot Checks**: Review sample outputs for quality
4. **Documentation Updates**: Update any changed processes or outputs

This regression test pipeline provides a complete, safe, and reproducible testing environment for all BeAScout system development and validation.