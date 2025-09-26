#!/usr/bin/env python3
"""
Excel File Regression Testing Tool

Compares two Excel files by converting sheets to CSV format and performing
content-normalized comparison suitable for regression testing.

Key Features:
- Export Excel sheets to CSV with normalized content
- Filter dynamic timestamps, file paths, generated IDs
- Compare business-critical data: unit counts, quality scores, recommendations
- Generate detailed diff reports

Usage:
    python compare_excel_files.py reference.xlsx current.xlsx
    python compare_excel_files.py --help
"""

import argparse
import pandas as pd
import sys
from pathlib import Path
import tempfile
import re
import difflib
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime


class ExcelComparer:
    """Excel file comparison tool for regression testing"""

    def __init__(self):
        self.differences = []
        self.normalization_rules = self._define_normalization_rules()

    def _define_normalization_rules(self) -> Dict[str, str]:
        """Define patterns for normalizing dynamic content"""
        return {
            # Timestamps - normalize to placeholder
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}': '[TIMESTAMP]',
            r'\d{8}_\d{6}': '[SESSION_ID]',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': '[DATETIME]',

            # File paths - normalize to relative paths
            r'/Users/[^/]+/[^/]+/beascout/': '[PROJECT_ROOT]/',

            # Generated IDs and session identifiers
            r'data/scraped/\d{8}_\d{6}/': 'data/scraped/[SESSION]/',
            r'BeAScout_Quality_Report_\d{8}_\d{6}': 'BeAScout_Quality_Report_[SESSION]',

            # Runtime-specific content
            r'Generated on: [^\n]+': 'Generated on: [NORMALIZED_DATE]',
            r'Report generated: [^\n]+': 'Report generated: [NORMALIZED_DATE]',
            r'Generation Date/Time: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': 'Generation Date/Time: [NORMALIZED_DATETIME]',
            r'Last Complete BeAScout Data Retrieval: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': 'Last Complete BeAScout Data Retrieval: [NORMALIZED_DATETIME]',
        }

    def normalize_content(self, content: str) -> str:
        """Apply normalization rules to content"""
        normalized = content
        for pattern, replacement in self.normalization_rules.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized

    def excel_to_csv_data(self, excel_path: Path) -> Dict[str, str]:
        """Convert Excel file to CSV data for each sheet"""
        csv_data = {}

        try:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(excel_path)

            for sheet_name in excel_file.sheet_names:
                try:
                    # Read sheet data
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)

                    # Convert to CSV string
                    csv_content = df.to_csv(index=False)

                    # Normalize dynamic content
                    normalized_content = self.normalize_content(csv_content)

                    csv_data[sheet_name] = normalized_content

                except Exception as e:
                    print(f"⚠️  Warning: Could not process sheet '{sheet_name}': {e}")
                    csv_data[sheet_name] = f"ERROR: {e}"

        except Exception as e:
            raise Exception(f"Could not read Excel file {excel_path}: {e}")

        return csv_data

    def compare_csv_content(self, reference_csv: str, current_csv: str, sheet_name: str) -> Dict:
        """Compare two CSV content strings and return detailed results"""

        # Split into lines for comparison
        ref_lines = reference_csv.strip().split('\n')
        cur_lines = current_csv.strip().split('\n')

        # Generate unified diff
        diff = list(difflib.unified_diff(
            ref_lines,
            cur_lines,
            fromfile=f'reference/{sheet_name}',
            tofile=f'current/{sheet_name}',
            lineterm=''
        ))

        # Count changes
        additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))

        return {
            'sheet_name': sheet_name,
            'identical': len(diff) == 0,
            'additions': additions,
            'deletions': deletions,
            'diff_lines': diff
        }

    def compare_excel_files(self, reference_path: Path, current_path: Path) -> Dict:
        """Compare two Excel files and return comprehensive results"""

        print(f"📊 Comparing Excel files...")
        print(f"   Reference: {reference_path.name}")
        print(f"   Current:   {current_path.name}")

        # Validate files exist
        if not reference_path.exists():
            raise FileNotFoundError(f"Reference file not found: {reference_path}")
        if not current_path.exists():
            raise FileNotFoundError(f"Current file not found: {current_path}")

        # Convert both files to CSV data
        try:
            ref_csv_data = self.excel_to_csv_data(reference_path)
            cur_csv_data = self.excel_to_csv_data(current_path)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'identical': False
            }

        # Compare sheet structure
        ref_sheets = set(ref_csv_data.keys())
        cur_sheets = set(cur_csv_data.keys())

        missing_sheets = ref_sheets - cur_sheets
        extra_sheets = cur_sheets - ref_sheets
        common_sheets = ref_sheets & cur_sheets

        # Compare content of common sheets
        sheet_comparisons = []
        overall_identical = True

        for sheet_name in sorted(common_sheets):
            comparison = self.compare_csv_content(
                ref_csv_data[sheet_name],
                cur_csv_data[sheet_name],
                sheet_name
            )
            sheet_comparisons.append(comparison)

            if not comparison['identical']:
                overall_identical = False

        # Handle missing/extra sheets
        if missing_sheets or extra_sheets:
            overall_identical = False

        return {
            'success': True,
            'identical': overall_identical,
            'reference_file': str(reference_path),
            'current_file': str(current_path),
            'reference_sheets': sorted(ref_sheets),
            'current_sheets': sorted(cur_sheets),
            'missing_sheets': sorted(missing_sheets),
            'extra_sheets': sorted(extra_sheets),
            'common_sheets': sorted(common_sheets),
            'sheet_comparisons': sheet_comparisons,
            'total_sheets_compared': len(common_sheets),
            'total_differences': sum(len(comp['diff_lines']) for comp in sheet_comparisons)
        }

    def generate_report(self, comparison_results: Dict, output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive comparison report"""

        if not comparison_results['success']:
            return f"❌ Comparison failed: {comparison_results['error']}"

        lines = []
        lines.append("=" * 80)
        lines.append("EXCEL FILE COMPARISON REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # File information
        lines.append("📁 FILES COMPARED:")
        lines.append(f"   Reference: {comparison_results['reference_file']}")
        lines.append(f"   Current:   {comparison_results['current_file']}")
        lines.append("")

        # Overall result
        if comparison_results['identical']:
            lines.append("✅ RESULT: Files are functionally identical")
        else:
            lines.append("❌ RESULT: Files have differences")
        lines.append("")

        # Sheet structure analysis
        lines.append("📋 SHEET STRUCTURE:")
        lines.append(f"   Reference sheets: {len(comparison_results['reference_sheets'])}")
        lines.append(f"   Current sheets:   {len(comparison_results['current_sheets'])}")
        lines.append(f"   Common sheets:    {len(comparison_results['common_sheets'])}")

        if comparison_results['missing_sheets']:
            lines.append(f"   ❌ Missing sheets: {', '.join(comparison_results['missing_sheets'])}")
        if comparison_results['extra_sheets']:
            lines.append(f"   ➕ Extra sheets:   {', '.join(comparison_results['extra_sheets'])}")
        lines.append("")

        # Sheet-by-sheet analysis
        lines.append("📊 SHEET COMPARISON DETAILS:")
        for comp in comparison_results['sheet_comparisons']:
            sheet_name = comp['sheet_name']
            if comp['identical']:
                lines.append(f"   ✅ {sheet_name}: Identical")
            else:
                lines.append(f"   ❌ {sheet_name}: {comp['additions']} additions, {comp['deletions']} deletions")

        # Detailed differences
        if not comparison_results['identical']:
            lines.append("")
            lines.append("🔍 DETAILED DIFFERENCES:")
            lines.append("-" * 60)

            for comp in comparison_results['sheet_comparisons']:
                if not comp['identical']:
                    lines.append(f"\n📄 Sheet: {comp['sheet_name']}")
                    lines.append("-" * 40)

                    # Show first 20 diff lines to avoid overwhelming output
                    diff_lines = comp['diff_lines']
                    if len(diff_lines) > 20:
                        lines.extend(diff_lines[:20])
                        lines.append(f"... ({len(diff_lines) - 20} more lines)")
                    else:
                        lines.extend(diff_lines)

        # Summary
        lines.append("")
        lines.append("📈 SUMMARY:")
        lines.append(f"   Total sheets compared: {comparison_results['total_sheets_compared']}")
        lines.append(f"   Total differences: {comparison_results['total_differences']}")
        lines.append("")

        report = "\n".join(lines)

        # Save to file if requested
        if output_file:
            output_file.write_text(report, encoding='utf-8')
            print(f"📄 Report saved to: {output_file}")

        return report


def main():
    """CLI interface for Excel comparison tool"""
    parser = argparse.ArgumentParser(
        description="Compare two Excel files for regression testing",
        epilog="""
Examples:
  # Compare two Excel files
  python compare_excel_files.py reference.xlsx current.xlsx

  # Save detailed report to file
  python compare_excel_files.py reference.xlsx current.xlsx --output report.txt

  # Exit with code 0 if identical, 1 if different
  python compare_excel_files.py reference.xlsx current.xlsx --exit-code
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('reference_file', help='Reference Excel file path')
    parser.add_argument('current_file', help='Current Excel file path to compare')
    parser.add_argument('--output', '-o', help='Output report file path')
    parser.add_argument('--exit-code', action='store_true',
                       help='Exit with code 0 if identical, 1 if different')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress detailed output, show only summary')

    args = parser.parse_args()

    # Initialize comparer
    comparer = ExcelComparer()

    try:
        # Perform comparison
        results = comparer.compare_excel_files(
            Path(args.reference_file),
            Path(args.current_file)
        )

        # Generate report
        output_path = Path(args.output) if args.output else None
        report = comparer.generate_report(results, output_path)

        # Display results
        if not args.quiet:
            print(report)
        else:
            # Quiet mode - just show summary
            if results['identical']:
                print("✅ Files are functionally identical")
            else:
                print(f"❌ Files differ: {results['total_differences']} differences across {len([c for c in results['sheet_comparisons'] if not c['identical']])} sheets")

        # Exit with appropriate code
        if args.exit_code:
            sys.exit(0 if results['identical'] else 1)

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.exit_code:
            sys.exit(2)


if __name__ == "__main__":
    main()