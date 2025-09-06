# Version Suffix Analysis Report

*Generated: 2025-09-04*
*Scope: Analysis of _vN suffixes for removal*

## Executive Summary

Analysis reveals that files with "_v2" suffixes are **not legacy versioned files**, but rather **current active implementations**. The versioning pattern represents iterative development where v2 became the production version without a corresponding v1 cleanup.

## Files Found with Version Suffixes

### Active Production Files (DO NOT RENAME)
These are current active implementations:

1. **`src/pipeline/reporting/generate_unit_emails_v2.py`**
   - Status: **ACTIVE** - Imported by `src/scripts/generate_all_unit_emails.py`
   - Function: Current email generation system
   - No corresponding v1 file exists
   - Contains latest business logic for email generation

2. **`src/tools/utilities/process_full_dataset_v2.py`**
   - Status: **ACTIVE** - Referenced by test scripts
   - Function: Current dataset processing utility
   - Used by verification framework
   - Implements current pipeline architecture

### Output Directories with Version Suffixes

3. **`data/output/unit_emails_v2/`**
   - Status: **STALE** - Contains 166 files from 11:39 today
   - Function: Earlier email generation output 
   - Current output is in `data/output/emails/` (19:03 today)
   - Safe to rename or remove

4. **`data/output/test_emails_v2/`**
   - Status: **TEST DATA** - Contains 42 test email files
   - Function: Test output from development
   - Can be cleaned up safely

### Other Versioned Files

5. **`data/feedback/process_full_dataset_v2.out`**
   - Status: **LOG FILE** - Output from processing
   - Safe to clean up

## Root Cause Analysis

The "_v2" suffixes exist because:

1. **Iterative Development**: Original implementations were replaced by improved versions
2. **No v1 Cleanup**: When v2 became production, v1 files were removed but v2 kept the suffix
3. **Import Dependencies**: Active code imports these v2 files, preventing simple renaming

## Recommendations

### Phase 1: Safe Cleanup (No Risk)
Remove stale output directories and log files:

```bash
# Remove stale email output directories
rm -rf data/output/unit_emails_v2/
rm -rf data/output/test_emails_v2/

# Remove log files
rm -f data/feedback/process_full_dataset_v2.out
```

### Phase 2: Active File Renaming (Requires Import Updates)
Rename active files and update imports:

1. **Rename `generate_unit_emails_v2.py`**:
   ```bash
   mv src/pipeline/reporting/generate_unit_emails_v2.py src/pipeline/reporting/generate_unit_emails.py
   ```
   
   **Update import in:**
   - `src/scripts/generate_all_unit_emails.py:18`
   
   **Change:**
   ```python
   from src.pipeline.reporting.generate_unit_emails_v2 import UnitEmailGenerator
   ```
   **To:**
   ```python
   from src.pipeline.reporting.generate_unit_emails import UnitEmailGenerator
   ```

2. **Rename `process_full_dataset_v2.py`**:
   ```bash
   mv src/tools/utilities/process_full_dataset_v2.py src/tools/utilities/process_full_dataset.py
   ```
   
   **Update references in:**
   - `tests/verify_all.py:74,110`

### Phase 3: Verification
After renaming:
1. Run unit tests to ensure imports work
2. Test main email generation scripts
3. Verify test framework still functions

## Implementation Commands

### Safe Cleanup (Execute Immediately):
```bash
# Remove stale output directories
rm -rf data/output/unit_emails_v2/
rm -rf data/output/test_emails_v2/

# Remove log files  
rm -f data/feedback/process_full_dataset_v2.out

# Clean __pycache__ files
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
```

### Active File Renaming (Execute After Testing):
```bash
# Rename active Python files
mv src/pipeline/reporting/generate_unit_emails_v2.py src/pipeline/reporting/generate_unit_emails.py
mv src/tools/utilities/process_full_dataset_v2.py src/tools/utilities/process_full_dataset.py

# Update import in generate_all_unit_emails.py
sed -i 's/generate_unit_emails_v2/generate_unit_emails/g' src/scripts/generate_all_unit_emails.py

# Update references in test files
sed -i 's/process_full_dataset_v2/process_full_dataset/g' tests/verify_all.py
```

## Risk Assessment

### Low Risk (Phase 1 - Safe Cleanup)
- **Impact**: None - removing stale output and log files
- **Dependencies**: No active code dependencies
- **Rollback**: Not needed

### Medium Risk (Phase 2 - Active File Renaming)  
- **Impact**: Import statements must be updated simultaneously
- **Dependencies**: 2+ files import these modules
- **Rollback**: Revert file renames and import changes
- **Testing**: Essential before deployment

## Verification Steps

After implementing changes:

1. **Test imports**:
   ```bash
   python -c "from src.pipeline.reporting.generate_unit_emails import UnitEmailGenerator"
   ```

2. **Run email generation**:
   ```bash
   python src/scripts/generate_all_unit_emails.py --test
   ```

3. **Run verification tests**:
   ```bash
   python tests/verify_all.py --quick
   ```

## Summary

Version suffix removal is **partially safe**:
- **3 output directories and 1 log file** can be removed immediately
- **2 active Python files** require careful renaming with import updates
- The "_v2" suffixes represent current production code, not legacy versions

This cleanup will eliminate the confusion around versioning and create a cleaner file structure without functional changes to the system.