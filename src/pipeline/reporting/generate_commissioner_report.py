#!/usr/bin/env python3
"""
BeAScout Quality Report Generator
Creates comprehensive Excel reports with quality scores, grades, and recommendations
Organized by district sheets with detailed unit information for commissioners
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from typing import Dict, List, Any

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.pipeline.analysis.quality_scorer import UnitQualityScorer
except ImportError:
    # Fallback for when running from different directory
    import os
    current_dir = Path(__file__).parent
    quality_scorer_path = current_dir.parent / "analysis" / "quality_scorer.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("quality_scorer", quality_scorer_path)
    quality_scorer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quality_scorer_module)
    UnitQualityScorer = quality_scorer_module.UnitQualityScorer

class BeAScoutQualityReportGenerator:
    """
    Generates comprehensive BeAScout Quality Reports organized by district
    Includes quality scores, grades, recommendations, and Key Three contact information
    """
    
    def __init__(self):
        self.quality_data = None
        self.key_three_data = None
        self.scorer = UnitQualityScorer()
        
    def load_quality_data(self, quality_file: str = 'data/raw/all_units_comprehensive_scored.json',
                          validation_file: str = 'data/output/enhanced_three_way_validation_results.json') -> bool:
        """Load quality-scored unit data and Key Three information"""
        try:
            # Load quality-scored units
            with open(quality_file, 'r', encoding='utf-8') as f:
                self.quality_data = json.load(f)
                print(f"📊 Loaded quality data: {len(self.quality_data['units_with_scores'])} units")
            
            # Load Key Three data from validation results
            with open(validation_file, 'r', encoding='utf-8') as f:
                validation_data = json.load(f)
                # Create lookup for Key Three member information
                self.key_three_data = {}
                for result in validation_data['validation_results']:
                    if 'key_three_data' in result:
                        unit_key = result['unit_key']
                        self.key_three_data[unit_key] = result['key_three_data']
                print(f"📊 Loaded Key Three data for {len(self.key_three_data)} units")
            
            return True
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            return False
    
    def create_quality_report(self, output_path: str = None) -> str:
        """
        Create comprehensive BeAScout Quality Report organized by district
        
        Returns:
            Path to generated Excel file
        """
        if not self.quality_data:
            raise ValueError("No quality data loaded")
        
        # Generate timestamped filename if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/reports/BeAScout_Quality_Report_{timestamp}.xlsx"
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create workbook
        workbook = Workbook()
        workbook.remove(workbook.active)  # Remove default sheet
        
        # Create Executive Summary first
        self._create_executive_summary_sheet(workbook)
        
        # Create district-specific sheets
        self._create_district_sheets(workbook)
        
        # Save workbook
        workbook.save(output_path)
        print(f"\n📋 BeAScout Quality Report saved: {output_path}")
        
        return output_path
    
    def _create_executive_summary_sheet(self, workbook):
        """Create executive summary sheet with quality metrics and legend"""
        ws = workbook.create_sheet("Executive Summary")
        
        # Title
        ws['A1'] = "BeAScout Quality Report"
        ws['A1'].font = Font(size=16, bold=True)
        
        # Council name and details
        ws['A2'] = "Heart of New England Council"
        ws['A2'].font = Font(size=14, bold=True)
        
        # Report generation info
        ws['A3'] = f"Generation Date/Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        ws['A3'].font = Font(size=12)
        
        # Data sources
        ws['A4'] = "Data Sources: BeAScout.org (10-mile radius) + JoinExploring.org (20-mile)"
        ws['A4'].font = Font(size=10)
        
        ws['A5'] = f"Last Complete Data Retrieval: {self.quality_data.get('extraction_timestamp', 'Unknown')[:10]}"
        ws['A5'].font = Font(size=10)
        
        # Quality metrics
        row = 7
        ws[f'A{row}'] = "QUALITY OVERVIEW"
        ws[f'A{row}'].font = Font(size=14, bold=True)
        
        # Calculate metrics from quality data
        total_units = self.quality_data['total_units']
        avg_score = self.quality_data.get('average_completeness_score', 0)
        
        # Count units by district
        district_counts = {}
        town_counts = set()
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for unit in self.quality_data['units_with_scores']:
            district = unit.get('district', 'Unknown')
            district_counts[district] = district_counts.get(district, 0) + 1
            town_counts.add(unit.get('unit_town', 'Unknown'))
            grade = unit.get('completeness_grade', 'F')
            if grade in grade_counts:
                grade_counts[grade] += 1
        
        row += 2
        metrics = [
            ("Total Units Analyzed", total_units),
            ("Units across Towns", f"{total_units} units across {len(town_counts)} towns"),
            ("Average Quality Score", f"{avg_score}%"),
            ("Quality Grade Distribution:", ""),
            ("  • Grade A (90%+)", f"{grade_counts['A']} units ({grade_counts['A']/total_units*100:.1f}%)"),
            ("  • Grade B (80-89%)", f"{grade_counts['B']} units ({grade_counts['B']/total_units*100:.1f}%)"),
            ("  • Grade C (70-79%)", f"{grade_counts['C']} units ({grade_counts['C']/total_units*100:.1f}%)"),
            ("  • Grade D (60-69%)", f"{grade_counts['D']} units ({grade_counts['D']/total_units*100:.1f}%)"),
            ("  • Grade F (<60%)", f"{grade_counts['F']} units ({grade_counts['F']/total_units*100:.1f}%)"),
        ]
        
        for metric, value in metrics:
            ws[f'A{row}'] = metric
            ws[f'B{row}'] = str(value)
            if not metric.startswith('  •'):
                ws[f'A{row}'].font = Font(bold=True)
            row += 1
        
        # District breakdown
        row += 2
        ws[f'A{row}'] = "UNITS BY DISTRICT"
        ws[f'A{row}'].font = Font(size=14, bold=True)
        
        row += 2
        for district, count in sorted(district_counts.items()):
            ws[f'A{row}'] = district
            ws[f'B{row}'] = f"{count} units"
            ws[f'A{row}'].font = Font(bold=True)
            row += 1
        
        # Legend
        row += 2
        ws[f'A{row}'] = "QUALITY TAG LEGEND"
        ws[f'A{row}'].font = Font(size=14, bold=True)
        
        row += 2
        legend_items = [
            ("REQUIRED_xxx tags:", "Missing critical information needed for unit operations"),
            ("  • REQUIRED_MISSING_LOCATION", "Add meeting location with street address"),
            ("  • REQUIRED_MISSING_DAY", "Add meeting day"),
            ("  • REQUIRED_MISSING_TIME", "Add meeting time"),
            ("  • REQUIRED_MISSING_EMAIL", "Add contact email address"),
            ("QUALITY_xxx tags:", "Information present but needs improvement"),
            ("  • QUALITY_POBOX_LOCATION", "Replace PO Box with physical meeting location"),
            ("  • QUALITY_PERSONAL_EMAIL", "Use unit-specific email instead of personal email"),
            ("RECOMMENDED_xxx tags:", "Additional information that enhances unit visibility"),
            ("  • RECOMMENDED_MISSING_CONTACT", "Add contact person name"),
            ("  • RECOMMENDED_MISSING_PHONE", "Add contact phone number"),
            ("  • RECOMMENDED_MISSING_WEBSITE", "Add unit-specific website"),
        ]
        
        for tag, description in legend_items:
            ws[f'A{row}'] = tag
            ws[f'B{row}'] = description
            if not tag.startswith('  •'):
                ws[f'A{row}'].font = Font(bold=True)
            row += 1
        
        # Auto-fit columns
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 60
    
    def _create_district_sheets(self, workbook):
        """Create separate sheets for each district with detailed unit information"""
        # Group units by district
        units_by_district = {}
        for unit in self.quality_data['units_with_scores']:
            district = unit.get('district', 'Unknown')
            if district not in units_by_district:
                units_by_district[district] = []
            units_by_district[district].append(unit)
        
        # Create sheet for each district
        for district_name in sorted(units_by_district.keys()):
            if district_name != 'Unknown':  # Skip unknown districts
                self._create_district_sheet(workbook, district_name, units_by_district[district_name])
    
    def _create_district_sheet(self, workbook, district_name: str, units: List[Dict]):
        """Create individual district sheet with detailed unit information"""
        ws = workbook.create_sheet(district_name)
        
        # Header section
        ws['A1'] = "BeAScout Quality Report"
        ws['A1'].font = Font(size=16, bold=True)
        
        ws['A2'] = "Heart of New England Council"
        ws['A2'].font = Font(size=14, bold=True)
        
        ws['A3'] = f"{district_name} District"
        ws['A3'].font = Font(size=14, bold=True)
        
        ws['A4'] = f"Generation Date/Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        ws['A4'].font = Font(size=10)
        
        ws['A5'] = "Data Sources: BeAScout.org (10-mile radius) + JoinExploring.org (20-mile)"
        ws['A5'].font = Font(size=10)
        
        ws['A6'] = f"Last Complete Data Retrieval: {self.quality_data.get('extraction_timestamp', 'Unknown')[:10]}"
        ws['A6'].font = Font(size=10)
        
        # Count units and towns for this district
        towns = set(unit.get('unit_town', 'Unknown') for unit in units)
        ws['A7'] = f"{len(units)} Units across {len(towns)} towns"
        ws['A7'].font = Font(size=12, bold=True)
        
        # Create column headers (row 9)
        headers = [
            "Unit Identifier", "Chartered Organization", "Town", "Quality Score", "Quality Grade",
            "Missing Information", "Quality Issues", "Recommended Improvements", "Meeting Location",
            "Meeting Day", "Meeting Time", "Contact Email", "Contact Person", "Contact Phone Number",
            "Unit Website", "Key Three - First Person", "Key Three - Second Person", "Key Three - Third Person"
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=9, column=col_num)
            cell.value = header
            cell.font = Font(bold=True, size=10)
            cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
            cell.alignment = Alignment(wrap_text=True, vertical='top')
        
        # Add unit data starting from row 10
        for row_num, unit in enumerate(units, 10):
            self._populate_unit_row(ws, row_num, unit)
        
        # Auto-adjust column widths
        column_widths = [20, 30, 15, 12, 12, 25, 25, 25, 25, 12, 12, 20, 18, 18, 20, 35, 35, 35]
        for col_num, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(col_num)].width = width
        
        # Freeze header rows
        ws.freeze_panes = 'A10'
    
    def _populate_unit_row(self, ws, row_num: int, unit: Dict):
        """Populate a single unit row with all required information"""
        # Get Key Three information if available
        unit_key = unit.get('unit_key', '')
        key_three_info = self.key_three_data.get(unit_key, {})
        key_three_members = key_three_info.get('key_three_members', [])
        
        # Categorize recommendations
        recommendations = unit.get('recommendations', [])
        missing_info = [rec for rec in recommendations if rec.startswith('REQUIRED_')]
        quality_issues = [rec for rec in recommendations if rec.startswith('QUALITY_')]
        recommended_improvements = [rec for rec in recommendations if rec.startswith('RECOMMENDED_') or rec.startswith('CONTENT_')]
        
        # Get readable descriptions
        missing_descriptions = self.scorer.get_recommendation_descriptions(missing_info)
        quality_descriptions = self.scorer.get_recommendation_descriptions(quality_issues)
        recommended_descriptions = self.scorer.get_recommendation_descriptions(recommended_improvements)
        
        # Format Key Three member information
        def format_key_three_member(member_info):
            if not member_info or member_info.get('fullname') == 'None':
                return "None"
            return f"{member_info.get('position', 'N/A')}: {member_info.get('fullname', 'N/A')}\nEmail: {member_info.get('email', 'N/A')}\nPhone: {member_info.get('phone', 'N/A')}"
        
        key_three_1 = format_key_three_member(key_three_members[0] if len(key_three_members) > 0 else {})
        key_three_2 = format_key_three_member(key_three_members[1] if len(key_three_members) > 1 else {})
        key_three_3 = format_key_three_member(key_three_members[2] if len(key_three_members) > 2 else {})
        
        # Populate row data
        row_data = [
            unit_key,
            unit.get('chartered_organization', ''),
            unit.get('unit_town', ''),
            unit.get('completeness_score', 0),
            unit.get('completeness_grade', 'F'),
            '; '.join(missing_descriptions),
            '; '.join(quality_descriptions),
            '; '.join(recommended_descriptions),
            unit.get('meeting_location', ''),
            unit.get('meeting_day', ''),
            unit.get('meeting_time', ''),
            unit.get('contact_email', ''),
            unit.get('contact_person', ''),
            unit.get('phone_number', ''),
            unit.get('website', ''),
            key_three_1,
            key_three_2,
            key_three_3
        ]
        
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = str(value) if value else ""
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            
            # Color code quality grades
            if col_num == 5:  # Quality Grade column
                grade = str(value)
                if grade == 'A':
                    cell.fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                elif grade == 'B':
                    cell.fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
                elif grade == 'C':
                    cell.fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
                elif grade == 'D':
                    cell.fill = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
                elif grade == 'F':
                    cell.fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
    

def main():
    """Generate BeAScout Quality Report organized by districts"""
    
    print("📋 Generating BeAScout Quality Report")
    
    generator = BeAScoutQualityReportGenerator()
    
    # Load quality and Key Three data
    if not generator.load_quality_data():
        return
    
    # Generate report
    report_path = generator.create_quality_report()
    
    # Get statistics for display
    total_units = generator.quality_data['total_units']
    avg_score = generator.quality_data.get('average_completeness_score', 0)
    
    # Count districts
    districts = set()
    for unit in generator.quality_data['units_with_scores']:
        district = unit.get('district', 'Unknown')
        if district != 'Unknown':
            districts.add(district)
    
    print(f"\n✅ BeAScout Quality Report Generated Successfully!")
    print(f"📁 Report saved to: {report_path}")
    print(f"\n📊 Report Contents:")
    print(f"   • Executive Summary with quality metrics and legend")
    print(f"   • {len(districts)} District sheets with detailed unit information")
    print(f"   • {total_units} total units with quality scores (avg: {avg_score}%)")
    print(f"   • 18-column format with quality grades, recommendations, and Key Three contacts")
    
    return report_path

if __name__ == "__main__":
    main()