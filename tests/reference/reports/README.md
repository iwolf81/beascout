# Reference BeAScout Quality Report

This directory contains reference reports generated using **anonymized Key Three test data**.

## Usage

The anonymized Key Three data at `tests/reference/key_three/anonymized_key_three.json` contains:
- ✅ **Real unit information** (types, numbers, organizations, districts)  
- ✅ **Real geographic data** (towns, zip codes, addresses)
- ✅ **Real position data** (Cubmaster, Committee Chair, etc.)
- ❌ **Fake personal information** (names, emails, phone numbers)

## Generating Reports

To generate a test report using anonymized data:

1. **Update Key Three source in configuration**:
   ```python
   # In generate_commissioner_report.py, use:
   KEY_THREE_PATH = "tests/reference/key_three/anonymized_key_three.json"
   ```

2. **Run report generation**:
   ```bash
   python src/pipeline/analysis/generate_commissioner_report.py
   ```

3. **Output**: Excel report with anonymized contact information

## Benefits

- ✅ **Safe development**: No risk of exposing real Scout leader personal data
- ✅ **Consistent testing**: Same test data across all development environments  
- ✅ **Realistic structure**: Maintains all data relationships and formatting
- ✅ **Privacy compliant**: Can be safely shared in repositories and with other developers

## Phone Number Format

All phone numbers use Massachusetts area codes with 555 exchange:
- `(617) 555-XXXX` 
- `(978) 555-XXXX`
- `(508) 555-XXXX`
- etc.

This clearly identifies them as test data while maintaining realistic formatting.

---
Generated: tests/reference/key_three/anonymized_key_three.json → Reference report data
