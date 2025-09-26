# Regression Test Pipeline Documentation

Complete end-to-end pipeline using stable reference data for development, testing, and regression validation.

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
# Output: data/output/three_way_validation_results.json (unit presence correlation)

python src/pipeline/analysis/three_way_validator.py --key-three tests/reference/key_three/anonymized_key_three.json
```

### **Step 3: Generate Commissioner Report**
```bash
# Input: processed unit data + validated correlation data + reference Key Three
# Output: data/output/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx

python src/pipeline/analysis/generate_commissioner_report.py --key-three tests/reference/key_three/anonymized_key_three.json 2>&1 | tee data/logs/generate_commissioner_report_$(date +%Y%m%d_%H%M%S).log
```

### **Step 4: Generate Unit Emails**
```bash
# Input: processed unit data + reference Key Three Excel file
# Output: data/output/emails/ (personalized improvement emails)

python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json tests/reference/key_three/anonymized_key_three.xlsx 2>&1 | tee data/logs/generate_unit_emails_$(date +%Y%m%d_%H%M%S).log
```

---

## **🧪 Regression Testing Framework**

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
ediff data/output/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx
# Expected: "PASS: Excel reports are functionally identical"

# Manual comparison (if needed for debugging):
python tests/tools/compare_excel_files.py \
  tests/reference/reports/BeAScout_Quality_Report_anonymized.xlsx \
  data/output/reports/BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx \
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
- **Unit Correlation**: 97.6% success rate between web data and Key Three registry
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