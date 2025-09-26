# Key Three Data Anonymization Workflow

## Overview

This workflow converts real Key Three leadership data containing personal information (names, emails, phone numbers, addresses) into anonymized test data that preserves all organizational structure and relationships while replacing personal details with fake data.

**Purpose**: Enable safe development, testing, and code sharing without exposing real personal information.

**Safety**: Anonymized data can be safely committed to git repositories and shared publicly.

## Data Flow Architecture

```
Real Key Three Data (Personal Information)
    ↓
Step 1: Excel Anonymization
    ↓
Anonymized Excel File (Fake Personal Data)
    ↓
Step 2: JSON Conversion
    ↓
Anonymized JSON File (Pipeline Ready)
```

## Two-Step Process

### Step 1: Anonymize Excel File

**Purpose**: Replace all personal information while preserving unit structure and relationships

#### Input:
- **Real Key Three data**: `data/input/Key 3 08-22-2025.xlsx` (contains real personal information)

#### Output:
- **Anonymized Excel file**: `tests/reference/key_three/anonymized_key_three.xlsx`

#### Command:
```bash
# Anonymize personal data while preserving organizational structure
# NOTE: Each run generates new random fake data (names, emails, phones, addresses)
python src/dev/tools/anonymize_key_three.py "data/input/Key 3 08-22-2025.xlsx" --verify
```

#### What Gets Anonymized:
- **Names**: Real names → Fake names (John Smith → Michael Johnson)
- **Email addresses**: Real emails → Fake emails preserving domain patterns
- **Phone numbers**: Real phones → Fake phone numbers in proper format
- **Addresses**: Real addresses → Fake addresses maintaining geographic consistency
- **Personal identifiers**: Any other personal information

#### What Gets Preserved:
- **Unit structure**: Pack/Troop/Crew numbers and types
- **Organizational relationships**: Charter organizations and unit associations
- **Geographic mappings**: Towns and districts (using fake addresses within correct towns)
- **Data relationships**: All cross-references between units and leadership roles

### Step 2: Convert to JSON for Pipeline Use

**Purpose**: Convert anonymized Excel data to clean JSON format expected by the processing pipeline

#### Input:
- **Anonymized Excel file**: `tests/reference/key_three/anonymized_key_three.xlsx`

#### Output:
- **Anonymized JSON file**: `tests/reference/key_three/anonymized_key_three.json`

#### Command:
```bash
# Convert anonymized Excel to clean JSON format expected by pipeline
python src/dev/tools/convert_key_three_to_json.py tests/reference/key_three/anonymized_key_three.xlsx
```

#### Processing Details:
- **Clean data structure**: Converts Excel format to normalized JSON
- **Pipeline compatibility**: Output format matches expectations of `three_way_validator.py` and other pipeline components
- **No further anonymization**: Only format conversion, personal data already anonymized in Step 1

## Important Notes

### Regeneration Guidelines
- **Only regenerate when real Key Three data is updated** (typically monthly)
- **Each anonymization run produces different fake data** - new random names, emails, addresses generated each time
- **For regression testing**: Use current baseline files (`anonymized_key_three.xlsx` and `anonymized_key_three.json`) which were generated with cleaned-up code

### Safety and Security
- **Safe for commits**: Anonymized data contains no real personal information
- **Safe for sharing**: Repository can be shared publicly without privacy concerns
- **Realistic testing**: Maintains all data relationships needed for comprehensive testing
- **Development workflow**: Enables full pipeline testing without accessing real personal data

### Quality Assurance
- **Verification option**: Use `--verify` flag to validate anonymization completeness
- **Structure preservation**: All unit relationships and organizational structure maintained
- **Format consistency**: Output compatible with all existing pipeline components
- **Data integrity**: No loss of business logic or functional relationships

## Pipeline Integration

### For Development/Testing (Default):
```bash
# Use anonymized data in pipeline commands
python src/pipeline/analysis/three_way_validator.py --key-three tests/reference/key_three/anonymized_key_three.json
python src/pipeline/analysis/generate_commissioner_report.py --key-three tests/reference/key_three/anonymized_key_three.json
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json tests/reference/key_three/anonymized_key_three.xlsx
```

### For Production (Real Data):
```bash
# Use real data in pipeline commands (DO NOT COMMIT OUTPUTS)
python src/pipeline/analysis/three_way_validator.py --key-three "data/input/Key 3 08-22-2025.json"
python src/pipeline/analysis/generate_commissioner_report.py --key-three "data/input/Key 3 08-22-2025.json"
python src/pipeline/analysis/generate_unit_emails.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx"
```

## File Locations

### Input Files (Real Data - Local Only):
- `data/input/Key 3 08-22-2025.xlsx` - Real Key Three data (DO NOT COMMIT)

### Output Files (Anonymized Data - Safe to Commit):
- `tests/reference/key_three/anonymized_key_three.xlsx` - Anonymized Excel format
- `tests/reference/key_three/anonymized_key_three.json` - Anonymized JSON format for pipeline

### Processing Scripts:
- `src/dev/tools/anonymize_key_three.py` - Step 1: Excel anonymization
- `src/dev/tools/convert_key_three_to_json.py` - Step 2: JSON conversion

## Troubleshooting

### Common Issues:

**"Real data detected in anonymized output"**:
- Verify anonymization script completed successfully
- Check that input file was the real data file, not already anonymized data
- Review output files to confirm all personal information was replaced

**"Pipeline components can't read anonymized JSON"**:
- Ensure Step 2 (JSON conversion) was completed after Step 1 (Excel anonymization)
- Verify JSON file structure matches expected pipeline format
- Test with a pipeline component like `three_way_validator.py`

**"Different results each run"**:
- This is expected behavior - each anonymization generates new random fake data
- For consistent testing, use established baseline files rather than regenerating
- Only regenerate when real Key Three data is updated

**"Import errors when running scripts"**:
- Run commands from project root directory: `/Users/iwolf/Repos/beascout`
- Ensure virtual environment is activated
- Verify required dependencies are installed

## Development Best Practices

1. **Default to anonymized data** for all development work
2. **Only use real data** for final production report generation
3. **Never commit real data outputs** to git repository
4. **Regenerate anonymized data** only when real Key Three data is updated
5. **Test with anonymized data** to ensure pipeline compatibility
6. **Use established baselines** for regression testing rather than regenerating

This workflow enables safe, comprehensive development and testing while maintaining strict privacy protection for real Key Three member personal information.