# Regression Testing Framework Plan

## **Objective**: Create automated regression tests to detect changes in email and Excel report generation

## **Implementation Strategy**:

### **Phase 1: Excel Workbook Regression Testing**

#### **Export-to-CSV Approach**: Convert Excel sheets to CSV format for text-based comparison
- Use pandas/openpyxl to read Excel files and export each sheet as CSV
- Compare CSV files using standard diff tools with dynamic content filtering
- Handle timestamps, file paths, and generated IDs through normalization

#### **Comparison Script**: Build tool that:
- Reads reference Excel file and new Excel file  
- Exports all sheets to temporary CSV files
- Filters/normalizes dynamic content (dates, paths, IDs)
- Performs line-by-line comparison and reports differences
- Focuses on business-critical data: unit counts, quality scores, recommendations

### **Phase 2: Email Regression Testing**  

#### **Text-Based Comparison**: Direct text file comparison with content normalization
- Strip timestamps, file paths, generated identifiers
- Compare core content: unit details, recommendations, contact information
- Use standard diff tools with filtered content

### **Phase 3: Integration**

#### **Reference Data Creation**: Generate reference files from current known-good system

#### **Test Automation**: Create regression test runner that:
- Runs pipeline with same input data
- Generates new outputs  
- Compares against reference files
- Reports any differences with clear categorization (structural vs content changes)

## **Dynamic Content Handling Strategy**:
- Replace timestamps with placeholder patterns
- Normalize file paths and generated identifiers  
- Sort data consistently to avoid order-based differences
- Focus comparison on business logic outputs rather than presentation formatting

## **Detailed Technical Approach**

### **Excel Comparison Implementation**
```python
# Conceptual approach - not actual code
def compare_excel_files(reference_path, new_path):
    # 1. Load both Excel files
    # 2. For each sheet:
    #    - Export to CSV with normalized content
    #    - Compare CSV files
    #    - Report differences
    # 3. Summary report of all changes
```

### **Email Comparison Implementation**
```python
# Conceptual approach - not actual code  
def compare_email_files(reference_dir, new_dir):
    # 1. Load all email files from both directories
    # 2. For each email:
    #    - Normalize dynamic content (timestamps, paths)
    #    - Compare core content
    #    - Report differences
    # 3. Summary report of all changes
```

### **Dynamic Content Normalization**
- **Timestamps**: Replace `2025-09-09_14:30:15` with `<TIMESTAMP>`
- **File Paths**: Replace `/full/path/file.xlsx` with `<FILEPATH>/file.xlsx`
- **Generated IDs**: Replace auto-generated identifiers with `<GENERATED_ID>`
- **Dates**: Replace `September 9, 2025` with `<DATE>`

## **Expected Benefits**
1. **Detect Functional Regressions**: Catch changes in business logic outputs
2. **Ignore Presentation Changes**: Focus on content, not formatting
3. **Automated Validation**: Run before/after code changes
4. **Clear Reporting**: Distinguish between expected vs unexpected changes

## **Implementation Priority**
1. **Start with Excel comparison** (most complex, highest value)
2. **Add email comparison** (simpler, validation of approach)
3. **Integrate into workflow** (automation and reporting)

This approach prioritizes detecting functional regressions while being robust to expected dynamic content changes.