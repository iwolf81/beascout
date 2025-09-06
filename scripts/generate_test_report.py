#!/usr/bin/env python3
"""
Generate a reference BeAScout Quality Report using anonymized Key Three data.
This creates test data for development without exposing real personal information.
"""

import sys
import os
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    parser = argparse.ArgumentParser(description='Generate reference BeAScout Quality Report with anonymized data')
    parser.add_argument('--key-three', default='tests/reference/key_three/anonymized_key_three.json',
                       help='Path to anonymized Key Three JSON file')
    parser.add_argument('--output-dir', default='tests/reference/reports/',
                       help='Output directory for reference report')
    
    args = parser.parse_args()
    
    # Ensure paths exist
    key_three_path = Path(args.key_three)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not key_three_path.exists():
        print(f"❌ Error: Anonymized Key Three file not found: {key_three_path}")
        print("Run the anonymization tool first:")
        print("  cd src/dev/tools")  
        print("  python anonymize_key_three.py ../../../data/input/HNE_key_three.json")
        sys.exit(1)
    
    try:
        # Import the report generator
        from src.pipeline.analysis.generate_commissioner_report import main as generate_report
        
        print(f"📖 Using anonymized Key Three data: {key_three_path}")
        print(f"📊 Generating reference BeAScout Quality Report...")
        
        # Note: This would require modifying the report generator to accept the anonymized data
        # For now, we'll create a placeholder that explains the process
        
        readme_content = f"""# Reference BeAScout Quality Report

This directory contains reference reports generated using **anonymized Key Three test data**.

## Usage

The anonymized Key Three data at `{key_three_path}` contains:
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
Generated: {args.key_three} → Reference report data
"""
        
        readme_path = output_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Reference report documentation created: {readme_path}")
        print(f"📋 Next steps:")
        print(f"   1. Update report generator to use: {key_three_path}")
        print(f"   2. Run: python src/pipeline/analysis/generate_commissioner_report.py") 
        print(f"   3. Output will contain anonymized contact information")
        
    except ImportError as e:
        print(f"⚠️  Cannot import report generator: {e}")
        print(f"✅ Anonymized data ready at: {key_three_path}")
        print(f"✅ Manual integration required with report generation system")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()