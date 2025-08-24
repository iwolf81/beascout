#!/usr/bin/env python3
"""
District BeAScout Report Generation System

Generates professional district reports for Heart of New England Council:
- Quinapoxet District and Soaring Eagle District reports
- Excel spreadsheet format for easy sorting and analysis
- Supportive guidance approach for unit improvement

Usage:
    python scripts/generate_district_reports.py data/raw/all_units_*_scored.json
    python scripts/generate_district_reports.py data/raw/all_units_01720_scored.json --output-dir reports/
"""

import json
import sys
import glob
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re


class DistrictReportGenerator:
    def __init__(self, key_three_file: str = "data/input/HNE_key_three.xlsx"):
        """Initialize with Key Three member data"""
        self.key_three_data = self._load_key_three_data(key_three_file)
        self.district_towns = self._load_district_towns()
        
    def _load_key_three_data(self, file_path: str) -> pd.DataFrame:
        """Load Key Three member data from Excel file"""
        try:
            df = pd.read_excel(file_path, header=8)
            print(f"Loaded {len(df)} Key Three member records")
            return df
        except Exception as e:
            print(f"Error loading Key Three data: {e}", file=sys.stderr)
            return pd.DataFrame()
    
    def _load_district_towns(self) -> Dict[str, List[str]]:
        """Load district town assignments"""
        try:
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'prototype'))
            from extract_hne_towns import get_hne_towns_and_zipcodes
            hne_towns, _ = get_hne_towns_and_zipcodes()
            
            # Get the actual district assignments from extract_hne_towns.py
            from extract_hne_towns import get_hne_towns_and_zipcodes
            
            # Read the source to get district breakdowns
            quinapoxet_towns = [
                "Ashby", "Townsend", "Pepperell", "Groton", "Ayer", "Littleton", "Acton", "Boxborough",
                "Fitchburg", "Lunenburg", "Shirley", "Harvard", "Bolton", "Berlin", "Lancaster", "Leominster",
                "Sterling", "Clinton", "West Boylston", "Boylston", "Shrewsbury", "Worcester", 
                "Holden", "Rutland", "Princeton", "Paxton", "Leicester", "Auburn", "Millbury"
            ]
            
            soaring_eagle_towns = [
                "Royalston", "Winchendon", "Ashburnham", "Gardner", "Templeton", "Phillipston", "Athol", "Orange",
                "Westminster", "Hubbardston", "Barre", "Petersham", "Hardwick", "New Braintree",
                "Oakham", "Ware", "West Brookfield", "East Brookfield", "North Brookfield", "Brookfield", "Spencer",
                "Warren", "Sturbridge", "Charlton", "Oxford", "Dudley", "Webster", "Douglas", "Sutton", "Grafton", 
                "Upton", "Northbridge", "Southbridge"
            ]
            
            return {
                "Quinapoxet": quinapoxet_towns,
                "Soaring Eagle": soaring_eagle_towns
            }
            
        except ImportError:
            print("Warning: Could not load HNE district data", file=sys.stderr)
            return {"Quinapoxet": [], "Soaring Eagle": []}
    
    def _classify_unit_district(self, unit: Dict[str, Any]) -> str:
        """Classify unit into district based on town"""
        unit_town = unit.get('unit_town', '').strip()
        
        if unit_town in self.district_towns["Quinapoxet"]:
            return "Quinapoxet"
        elif unit_town in self.district_towns["Soaring Eagle"]:
            return "Soaring Eagle"
        else:
            return "Unknown"
    
    def _get_unit_key_three(self, unit: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get Key Three members for a unit"""
        if self.key_three_data.empty:
            return [{"name": "None", "position": "None", "email": "None", "phone": "None"}] * 3
        
        # Get unit identifier for matching
        primary_identifier = unit.get('primary_identifier', '')
        
        # Normalize identifier for matching
        identifier_for_matching = self._normalize_unit_identifier(primary_identifier)
        
        # Find matching Key Three members
        key_three_members = []
        
        for _, row in self.key_three_data.iterrows():
            org_name = str(row.get('unitcommorgname', '')).strip()
            normalized_org = self._normalize_unit_identifier(org_name)
            
            if normalized_org == identifier_for_matching:
                member_data = {
                    'name': str(row.get('fullname', 'Missing')).strip(),
                    'position': str(row.get('position', 'Missing')).strip(), 
                    'email': str(row.get('email', 'Missing')).strip(),
                    'phone': str(row.get('phone', 'Missing')).strip()
                }
                
                # Clean up missing data
                for key, value in member_data.items():
                    if value in ['nan', 'None', '', 'NaT']:
                        member_data[key] = 'None'
                
                key_three_members.append(member_data)
        
        # Ensure we have exactly 3 members (pad with "None" if needed)
        while len(key_three_members) < 3:
            key_three_members.append({
                "name": "None", 
                "position": "None", 
                "email": "None", 
                "phone": "None"
            })
        
        return key_three_members[:3]  # Take only first 3
    
    def _normalize_unit_identifier(self, identifier: str) -> str:
        """Normalize unit identifier for matching"""
        if not identifier:
            return ""
        
        # Remove extra spaces and standardize
        normalized = re.sub(r'\s+', ' ', identifier.strip())
        
        # Remove gender indicators like "(F)", "(B)", "(G)" and associated dashes/spaces
        normalized = re.sub(r'\s*\([FBG]\)\s*-?\s*', ' ', normalized)
        
        # Remove Crew specialty information (everything after "Specialty:")
        if 'Specialty:' in normalized:
            normalized = normalized.split('Specialty:')[0].strip()
        
        # Clean up multiple spaces that may result from the above
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Ensure consistent format: "Type Number Organization"
        # This handles cases where there might be inconsistent spacing or punctuation
        parts = normalized.split()
        if len(parts) >= 2:
            unit_type = parts[0]
            unit_number = parts[1].lstrip('0')  # Remove leading zeros for comparison
            
            # Handle organization name - everything after unit number
            if len(parts) > 2:
                # Join all remaining parts and then clean
                org_name = ' '.join(parts[2:])
                
                # Remove leading dash and spaces that might result from "Type Number - OrgName" format
                org_name = org_name.lstrip('- ').strip()
                
                # Standardize common variations - remove punctuation and normalize spaces
                org_name = org_name.replace(',', '').replace('.', '').replace('  ', ' ')
                org_name = org_name.replace(' Inc', '').replace(' Inc.', '')  # Handle "Inc" variations
                
                # Normalize dashes - standardize spacing around dashes
                org_name = re.sub(r'\s*-\s*', '-', org_name)  # Remove spaces around dashes
                
                org_name = org_name.strip()
                
                return f"{unit_type} {unit_number} {org_name}"
            else:
                return f"{unit_type} {unit_number}"
        
        return normalized
    
    def _categorize_issues(self, recommendations: List[str]) -> Dict[str, List[str]]:
        """Categorize issues into Required, Quality, Recommended"""
        required_issues = []
        quality_issues = []
        recommended_issues = []
        
        for rec in recommendations:
            if rec.startswith('REQUIRED_MISSING_'):
                issue_name = rec.replace('REQUIRED_MISSING_', '').replace('_', ' ').title()
                required_issues.append(issue_name)
            elif rec.startswith('QUALITY_'):
                issue_name = rec.replace('QUALITY_', '').replace('_', ' ').title()
                quality_issues.append(issue_name)
            elif rec.startswith('RECOMMENDED_MISSING_'):
                issue_name = rec.replace('RECOMMENDED_MISSING_', '').replace('_', ' ').title()
                recommended_issues.append(issue_name)
        
        return {
            'required': required_issues,
            'quality': quality_issues, 
            'recommended': recommended_issues
        }
    
    def _create_legend_data(self) -> List[Dict[str, str]]:
        """Create legend data for issue descriptions"""
        return [
            {"Code": "Meeting Location", "Category": "Required", "Description": "Street address where unit meets - helps families find meetings and events"},
            {"Code": "Meeting Day", "Category": "Required", "Description": "Day of week when unit regularly meets - essential for family scheduling"},
            {"Code": "Meeting Time", "Category": "Required", "Description": "Time when meetings start and end - allows families to plan attendance"},
            {"Code": "Contact Email", "Category": "Required", "Description": "Email address for families to ask questions and get information"},
            {"Code": "Specialty", "Category": "Required", "Description": "Program focus area for Venturing Crews (e.g., High Adventure, STEM)"},
            {"Code": "Personal Email", "Category": "Quality", "Description": "Consider using unit-specific email address for better continuity as leaders change"},
            {"Code": "Po Box Location", "Category": "Quality", "Description": "Street address preferred over PO Box - helps families locate actual meeting place"},
            {"Code": "Contact Person", "Category": "Recommended", "Description": "Designated contact person's name - gives families specific person to reach out to"},
            {"Code": "Phone Number", "Category": "Recommended", "Description": "Phone contact for immediate questions and information"},
            {"Code": "Website", "Category": "Recommended", "Description": "Unit website with additional program information and updates"},
            {"Code": "Description", "Category": "Recommended", "Description": "Program description highlighting what makes the unit special and welcoming"}
        ]
    
    def generate_district_report(self, units: List[Dict[str, Any]], district_name: str, output_dir: str) -> str:
        """Generate Excel report for a specific district"""
        
        # Filter units for this district
        district_units = [unit for unit in units if self._classify_unit_district(unit) == district_name]
        
        if not district_units:
            print(f"No units found for {district_name} District")
            return ""
        
        # Sort units by type, number, town
        district_units.sort(key=lambda x: (
            x.get('unit_type', ''),
            int(x.get('unit_number', '0') or '0'),
            x.get('unit_town', '')
        ))
        
        # Prepare data for Excel
        report_data = []
        
        for unit in district_units:
            # Get Key Three members
            key_three_members = self._get_unit_key_three(unit)
            
            # Categorize issues
            recommendations = unit.get('recommendations', [])
            issues = self._categorize_issues(recommendations)
            
            # Format issues as comma-separated strings with 'None' for empty
            required_str = ', '.join(issues['required']) if issues['required'] else 'None'
            quality_str = ', '.join(issues['quality']) if issues['quality'] else 'None'
            recommended_str = ', '.join(issues['recommended']) if issues['recommended'] else 'None'
            
            # Build row data
            row_data = {
                'Unit Type': unit.get('unit_type', ''),
                'Unit Number': unit.get('unit_number', ''),
                'Town': unit.get('unit_town', ''),
                'BeAScout Score (%)': round(unit.get('completeness_score', 0), 1),
                'Missing Information': required_str,
                'Quality Issues': quality_str,
                'Recommended Information': recommended_str,
            }
            
            # Add Key Three members
            for i, member in enumerate(key_three_members, 1):
                row_data[f'Key Three #{i} Name'] = member['name']
                row_data[f'Key Three #{i} Position'] = member['position']
                row_data[f'Key Three #{i} Email'] = member['email']
                row_data[f'Key Three #{i} Phone'] = member['phone']
            
            report_data.append(row_data)
        
        # Create Excel file
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{district_name}_District_BeAScout_Report_{date_str}.xlsx"
        file_path = output_path / filename
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Main data sheet
            df_main = pd.DataFrame(report_data)
            df_main.to_excel(writer, sheet_name='Unit Data', index=False)
            
            # Legend sheet
            legend_data = self._create_legend_data()
            df_legend = pd.DataFrame(legend_data)
            df_legend.to_excel(writer, sheet_name='Issue Legend', index=False)
            
            # Summary sheet
            summary_data = self._create_summary_data(district_units, district_name)
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='District Summary', index=False)
        
        print(f"Generated: {filename}")
        return str(file_path)
    
    def _create_summary_data(self, units: List[Dict[str, Any]], district_name: str) -> List[Dict[str, Any]]:
        """Create summary statistics for the district"""
        if not units:
            return []
        
        total_units = len(units)
        scores = [unit.get('completeness_score', 0) for unit in units]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Grade distribution
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for score in scores:
            if score >= 90:
                grade_counts['A'] += 1
            elif score >= 80:
                grade_counts['B'] += 1
            elif score >= 70:
                grade_counts['C'] += 1
            elif score >= 60:
                grade_counts['D'] += 1
            else:
                grade_counts['F'] += 1
        
        # Unit type distribution
        unit_types = {}
        for unit in units:
            unit_type = unit.get('unit_type', 'Unknown')
            unit_types[unit_type] = unit_types.get(unit_type, 0) + 1
        
        summary = [
            {"Metric": "District", "Value": f"{district_name} District"},
            {"Metric": "Report Generated", "Value": datetime.now().strftime("%Y-%m-%d %H:%M")},
            {"Metric": "", "Value": ""},
            {"Metric": "OVERVIEW", "Value": ""},
            {"Metric": "Total Units", "Value": total_units},
            {"Metric": "Average BeAScout Score", "Value": f"{avg_score:.1f}%"},
            {"Metric": "", "Value": ""},
            {"Metric": "GRADE DISTRIBUTION", "Value": ""},
            {"Metric": "A (90-100%)", "Value": f"{grade_counts['A']} units ({grade_counts['A']/total_units*100:.1f}%)"},
            {"Metric": "B (80-89%)", "Value": f"{grade_counts['B']} units ({grade_counts['B']/total_units*100:.1f}%)"},
            {"Metric": "C (70-79%)", "Value": f"{grade_counts['C']} units ({grade_counts['C']/total_units*100:.1f}%)"},
            {"Metric": "D (60-69%)", "Value": f"{grade_counts['D']} units ({grade_counts['D']/total_units*100:.1f}%)"},
            {"Metric": "F (<60%)", "Value": f"{grade_counts['F']} units ({grade_counts['F']/total_units*100:.1f}%)"},
            {"Metric": "", "Value": ""},
            {"Metric": "UNIT TYPES", "Value": ""},
        ]
        
        for unit_type, count in sorted(unit_types.items()):
            summary.append({"Metric": f"{unit_type}s", "Value": f"{count} units"})
        
        return summary
    
    def generate_reports_from_files(self, json_files: List[str], output_dir: str = "data/output/reports/") -> List[str]:
        """Generate district reports from multiple JSON files"""
        all_units = []
        
        # Load all units from all files
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                units = data.get('units_with_scores', [])
                
                # Filter to only HNE Council units
                hne_units = []
                for unit in units:
                    unit_town = unit.get('unit_town', '')
                    if (unit_town in self.district_towns["Quinapoxet"] or 
                        unit_town in self.district_towns["Soaring Eagle"]):
                        hne_units.append(unit)
                
                all_units.extend(hne_units)
                print(f"Loaded {len(hne_units)} HNE units from {file_path}")
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}", file=sys.stderr)
                continue
        
        if not all_units:
            print("No HNE Council units found to process")
            return []
        
        print(f"Total HNE units loaded: {len(all_units)}")
        
        # Generate reports for each district
        generated_files = []
        
        for district_name in ["Quinapoxet", "Soaring Eagle"]:
            report_file = self.generate_district_report(all_units, district_name, output_dir)
            if report_file:
                generated_files.append(report_file)
        
        return generated_files


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_district_reports.py <json_file_pattern> [--output-dir output/]", file=sys.stderr)
        print("Examples:")
        print("  python scripts/generate_district_reports.py data/raw/all_units_01720_scored.json")
        print("  python scripts/generate_district_reports.py data/raw/all_units_*_scored.json --output-dir reports/")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    output_dir = "data/output/reports/"
    
    if "--output-dir" in args:
        output_idx = args.index("--output-dir")
        if output_idx + 1 < len(args):
            output_dir = args[output_idx + 1]
            args = args[:output_idx] + args[output_idx + 2:]
    
    # Handle glob patterns
    all_files = []
    for pattern in args:
        if '*' in pattern or '?' in pattern:
            all_files.extend(glob.glob(pattern))
        else:
            all_files.append(pattern)
    
    # Remove duplicates and check file existence
    all_files = list(set(all_files))
    valid_files = []
    for file_path in all_files:
        if Path(file_path).exists():
            valid_files.append(file_path)
        else:
            print(f"File not found: {file_path}", file=sys.stderr)
    
    if not valid_files:
        print("No valid files found to process", file=sys.stderr)
        sys.exit(1)
    
    # Generate reports
    generator = DistrictReportGenerator()
    generated_files = generator.generate_reports_from_files(valid_files, output_dir)
    
    print(f"\nGenerated {len(generated_files)} district reports in {output_dir}")
    for file_path in generated_files:
        print(f"  {Path(file_path).name}")


if __name__ == "__main__":
    main()