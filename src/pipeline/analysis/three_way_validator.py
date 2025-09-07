#!/usr/bin/env python3
"""
Three-Way Unit Validation Engine
Cross-references Key Three database with scraped web data to identify discrepancies
Provides comprehensive data quality audit with action flags for commissioners
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.pipeline.core.unit_identifier import UnitIdentifierNormalizer
from src.pipeline.processing.scraped_data_parser import ScrapedDataParser
from src.dev.parsing.key_three_parser import KeyThreeParser

class ValidationStatus(Enum):
    """Unit validation status categories"""
    BOTH_SOURCES = "both_sources"  # ✅ In Key Three + Web presence
    KEY_THREE_ONLY = "key_three_only"  # ⚠️ In Key Three but missing from web
    WEB_ONLY = "web_only"  # ❌ On web but not in Key Three (flag for removal)

@dataclass
class ValidationResult:
    """Individual unit validation result"""
    unit_key: str
    status: ValidationStatus
    key_three_data: Dict[str, Any] = None
    scraped_data: Dict[str, Any] = None
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []

class ThreeWayValidator:
    """
    Comprehensive unit validation engine
    Cross-references Key Three database (169 units) with scraped web data (163 units)
    """
    
    def __init__(self):
        self.key_three_units = []
        self.scraped_units = []
        self.validation_results = []
        
    def load_key_three_data(self, file_path: str) -> bool:
        """Load Key Three foundation data (169 units)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both data structures: key_three_units or key_three_members
                self.key_three_units = data.get('key_three_units', data.get('key_three_members', []))
                print(f"📋 Loaded {len(self.key_three_units)} Key Three units with member data")
                return True
        except Exception as e:
            print(f"❌ Failed to load Key Three data: {e}")
            return False
    
    def load_scraped_data(self, file_path: str = 'data/raw/all_units_comprehensive_scored.json') -> bool:
        """Load comprehensive scraped data (165 units)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.scraped_units = data.get('units_with_scores', [])
                print(f"🌐 Loaded {len(self.scraped_units)} scraped units")
                return True
        except Exception as e:
            print(f"❌ Failed to load scraped data: {e}")
            return False
    
    def validate_all_units(self) -> List[ValidationResult]:
        """
        Perform comprehensive three-way validation
        Returns list of validation results for all units
        """
        from datetime import datetime
        import os
        
        print(f"\n🔍 Starting Three-Way Validation")
        print(f"   Key Three units: {len(self.key_three_units)}")
        print(f"   Scraped units: {len(self.scraped_units)}")
        
        # Use same approach as current pipeline - Key Three unit_display vs scraped unit_key
        # But normalize both to same format for proper matching
        key_three_keys = set()
        key_three_dict = {}
        for unit in self.key_three_units:
            unit_display = unit.get('unit_display', '')  # e.g., "Pack 0007"
            unit_org_name = unit.get('unit_org_name', '')  # e.g., "Pack 0007 (B) - Clinton - Heart of New England Council"
            
            if unit_display and unit_org_name:
                # Use existing KeyThreeParser to extract unit info properly
                parser = KeyThreeParser("")  # Don't need to load data, just use parsing logic
                unit_info = parser.extract_unit_info_from_unitcommorgname(unit_org_name)
                
                if unit_info and unit_info.get('unit_town'):
                    town = unit_info['unit_town']
                    unit_key = f"{unit_display} {town}"
                    key_three_keys.add(unit_key)
                    key_three_dict[unit_key] = unit
        
        # Normalize scraped units to ensure 4-digit unit numbers
        scraped_keys = set()
        scraped_dict = {}
        for unit in self.scraped_units:
            unit_key = unit.get('unit_key', '')
            if unit_key:
                # Convert "Crew 204 West Boylston" -> "Crew 0204 West Boylston"
                parts = unit_key.split()
                if len(parts) >= 3:
                    unit_type = parts[0]
                    unit_number = parts[1].zfill(4)  # Pad to 4 digits
                    town = ' '.join(parts[2:])
                    normalized_key = f"{unit_type} {unit_number} {town}"
                    scraped_keys.add(normalized_key)
                    scraped_dict[normalized_key] = unit
        
        # Create debug log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = f'data/debug/cross_reference_validation_debug_{timestamp}.log'
        os.makedirs('data/debug', exist_ok=True)
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write("=== CROSS-REFERENCE VALIDATION DEBUG LOG ===\n\n")
            f.write(f"Key Three units loaded: {len(self.key_three_units)}\n")
            f.write(f"Scraped units loaded: {len(self.scraped_units)}\n\n")
            
            # Log all Key Three unit keys
            f.write("KEY THREE UNIT KEYS:\n")
            for unit_key in sorted(key_three_keys):
                f.write(f"  {unit_key}\n")
            
            f.write(f"\nSCRAPED UNIT KEYS:\n")
            for unit_key in sorted(scraped_keys):
                f.write(f"  {unit_key}\n")
            
            # Log units only in Key Three
            key_three_only = key_three_keys - scraped_keys
            f.write(f"\nUNITS ONLY IN KEY THREE ({len(key_three_only)}):\n")
            for unit_key in sorted(key_three_only):
                f.write(f"  {unit_key}\n")
            
            # Log units only in scraped data
            scraped_only = scraped_keys - key_three_keys
            f.write(f"\nUNITS ONLY IN SCRAPED DATA ({len(scraped_only)}):\n")
            for unit_key in sorted(scraped_only):
                f.write(f"  {unit_key}\n")
            
            # Log matching units
            matches = key_three_keys & scraped_keys
            f.write(f"\nMATCHING UNITS ({len(matches)}):\n")
            for unit_key in sorted(matches):
                f.write(f"  {unit_key}\n")
            
            f.write(f"\nCROSS-REFERENCE SUMMARY:\n")
            f.write(f"  Expected Key Three: 169 units\n")
            f.write(f"  Expected Scraped: 165 units\n")
            f.write(f"  Expected Matches: 165 units\n")
            f.write(f"  Expected Key Three Only: 4 units\n")
            f.write(f"  Expected Scraped Only: 0 units\n\n")
            f.write(f"  Actual Key Three: {len(key_three_keys)} units\n")
            f.write(f"  Actual Scraped: {len(scraped_keys)} units\n")
            f.write(f"  Actual Matches: {len(matches)} units\n")
            f.write(f"  Actual Key Three Only: {len(key_three_only)} units\n")
            f.write(f"  Actual Scraped Only: {len(scraped_only)} units\n")
        
        print(f"📋 Cross-reference debug log saved: {debug_file}")
        
        validation_results = []
        
        # Analyze all Key Three units (this should be 169)
        print(f"   Total unique units: {len(key_three_keys)}")
        
        # Validate each Key Three unit
        for unit_key in sorted(key_three_keys):
            in_key_three = unit_key in key_three_keys
            in_scraped = unit_key in scraped_keys
            
            # Determine validation status
            if in_key_three and in_scraped:
                status = ValidationStatus.BOTH_SOURCES
            elif in_key_three and not in_scraped:
                status = ValidationStatus.KEY_THREE_ONLY
            elif not in_key_three and in_scraped:
                status = ValidationStatus.WEB_ONLY
            else:
                # This shouldn't happen but included for completeness
                continue
            
            # Create validation result with enhanced Key Three data
            key_three_data = key_three_dict.get(unit_key)
            if key_three_data:
                key_three_data = self._enhance_key_three_data_with_members(key_three_data)
            
            result = ValidationResult(
                unit_key=unit_key,
                status=status,
                key_three_data=key_three_data,
                scraped_data=scraped_dict.get(unit_key),
                issues=[]
            )
            
            # Identify specific issues
            self._analyze_unit_issues(result)
            
            validation_results.append(result)
        
        self.validation_results = validation_results
        return validation_results
    
    def _enhance_key_three_data_with_members(self, key_three_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance Key Three data with formatted member information for reporting
        """
        enhanced_data = key_three_data.copy()
        members = key_three_data.get('key_three_members', [])
        
        # Extract specific roles from members for commissioner report
        for member in members:
            position = member.get('position', '').lower()
            
            if 'committee chair' in position:
                enhanced_data['committee_chair_name'] = member.get('fullname', 'N/A')
                enhanced_data['committee_chair_email'] = member.get('email', 'N/A')
                enhanced_data['committee_chair_phone'] = member.get('phone', 'N/A')
            elif 'cubmaster' in position or 'scoutmaster' in position:
                enhanced_data['unit_leader_name'] = member.get('fullname', 'N/A')
                enhanced_data['unit_leader_email'] = member.get('email', 'N/A')
                enhanced_data['unit_leader_phone'] = member.get('phone', 'N/A')
            elif 'chartered org' in position:
                enhanced_data['chartered_org_rep_name'] = member.get('fullname', 'N/A')
                enhanced_data['chartered_org_rep_email'] = member.get('email', 'N/A')
                enhanced_data['chartered_org_rep_phone'] = member.get('phone', 'N/A')
        
        # Map chartered_organization to expected field name for commissioner report  
        enhanced_data['chartered_org_name'] = enhanced_data.get('chartered_organization', 'Unknown')
        
        # Ensure all expected fields exist for the commissioner report
        if 'committee_chair_name' not in enhanced_data:
            enhanced_data['committee_chair_name'] = 'N/A'
            enhanced_data['committee_chair_email'] = 'N/A'
            enhanced_data['committee_chair_phone'] = 'N/A'
            
        if 'unit_leader_name' not in enhanced_data:
            enhanced_data['unit_leader_name'] = 'N/A'
            enhanced_data['unit_leader_email'] = 'N/A'
            enhanced_data['unit_leader_phone'] = 'N/A'
        
        return enhanced_data
    
    def _analyze_unit_issues(self, result: ValidationResult):
        """Analyze specific issues for a unit validation result"""
        
        if result.status == ValidationStatus.KEY_THREE_ONLY:
            result.issues.append("Missing from web - no online visibility for families")
            result.issues.append("Commissioner action: Contact unit leaders about web presence")
        
        elif result.status == ValidationStatus.WEB_ONLY:
            result.issues.append("Unit on web but not in Key Three database")
            result.issues.append("Commissioner action: Verify unit status and registration")
        
        elif result.status == ValidationStatus.BOTH_SOURCES:
            # Check for data quality issues
            scraped = result.scraped_data
            key_three = result.key_three_data
            
            if scraped:
                # Check for missing critical fields
                if not scraped.get('meeting_location'):
                    result.issues.append("Missing meeting location")
                
                if not scraped.get('meeting_day'):
                    result.issues.append("Missing meeting day")
                
                if not scraped.get('meeting_time'):
                    result.issues.append("Missing meeting time")
                
                if not scraped.get('contact_email'):
                    result.issues.append("Missing contact email")
                
                # Check for data inconsistencies
                if key_three and scraped.get('unit_town') != key_three.get('unit_town'):
                    result.issues.append(f"Town mismatch: Web={scraped.get('unit_town')} vs Key Three={key_three.get('unit_town')}")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation summary statistics"""
        if not self.validation_results:
            return {}
        
        # Count by status
        status_counts = {}
        for status in ValidationStatus:
            status_counts[status.value] = len([r for r in self.validation_results if r.status == status])
        
        # Count units with issues
        units_with_issues = len([r for r in self.validation_results if r.issues])
        
        # District breakdown for Key Three only units
        key_three_only_districts = {}
        for result in self.validation_results:
            if result.status == ValidationStatus.KEY_THREE_ONLY and result.key_three_data:
                district = result.key_three_data.get('district', 'Unknown')
                key_three_only_districts[district] = key_three_only_districts.get(district, 0) + 1
        
        return {
            'total_units': len(self.validation_results),
            'status_breakdown': status_counts,
            'units_with_issues': units_with_issues,
            'key_three_only_by_district': key_three_only_districts,
            'validation_percentages': {
                'both_sources': (status_counts.get('both_sources', 0) / len(self.validation_results)) * 100,
                'key_three_only': (status_counts.get('key_three_only', 0) / len(self.validation_results)) * 100,
                'web_only': (status_counts.get('web_only', 0) / len(self.validation_results)) * 100
            }
        }
    
    def get_units_by_status(self, status: ValidationStatus) -> List[ValidationResult]:
        """Get all units with specific validation status"""
        return [r for r in self.validation_results if r.status == status]
    
    def save_validation_results(self, output_path: str = 'data/output/three_way_validation_results.json'):
        """Save comprehensive validation results"""
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.validation_results:
            serializable_results.append({
                'unit_key': result.unit_key,
                'status': result.status.value,
                'key_three_data': result.key_three_data,
                'scraped_data': result.scraped_data,
                'issues': result.issues
            })
        
        output_data = {
            'validation_summary': self.get_validation_summary(),
            'validation_results': serializable_results,
            'data_sources': {
                'key_three_units': len(self.key_three_units),
                'scraped_units': len(self.scraped_units)
            }
        }
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved validation results to: {output_path}")
        return output_path

def main():
    """Main validation execution"""
    parser = argparse.ArgumentParser(
        description='Three-Way Unit Validation Engine - Cross-reference Key Three data with scraped web data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use converted JSON Key Three data (real data)
  python %(prog)s --key-three "data/input/Key 3 08-22-2025.json"
  
  # Use anonymized Key Three data for testing
  python %(prog)s --key-three tests/reference/key_three/anonymized_key_three.json
  
  # Multiple units with different scraped data
  python %(prog)s --key-three "data/input/Key 3 08-22-2025.json" --scraped-data data/raw/custom_units.json
  
  # Specify custom scraped data file
  python %(prog)s --key-three "data/input/Key 3 08-22-2025.json" --scraped-data data/raw/all_units_comprehensive_scored.json
        ''')
    
    parser.add_argument('--key-three', 
                       required=True,
                       help='Path to Key Three data file (JSON) - REQUIRED')
    parser.add_argument('--scraped-data',
                       default='data/raw/all_units_comprehensive_scored.json', 
                       help='Path to scraped units data (JSON) [default: %(default)s]')
    parser.add_argument('--output',
                       default='data/output/three_way_validation_results.json',
                       help='Output validation results file [default: %(default)s]')
    
    args = parser.parse_args()
    
    print("🚀 Three-Way Unit Validation Engine")
    print(f"📁 Key Three data: {args.key_three}")
    print(f"📁 Scraped data: {args.scraped_data}")
    
    validator = ThreeWayValidator()
    
    # Load data sources
    if not validator.load_key_three_data(args.key_three):
        return
    
    if not validator.load_scraped_data(args.scraped_data):
        return
    
    # Perform validation
    results = validator.validate_all_units()
    
    if not results:
        print("❌ No validation results generated")
        return
    
    # Display summary
    summary = validator.get_validation_summary()
    
    print(f"\n📊 Validation Summary:")
    print(f"   Total units analyzed: {summary['total_units']}")
    print(f"   ✅ Both sources: {summary['status_breakdown']['both_sources']} ({summary['validation_percentages']['both_sources']:.1f}%)")
    print(f"   ⚠️  Key Three only: {summary['status_breakdown']['key_three_only']} ({summary['validation_percentages']['key_three_only']:.1f}%)")
    print(f"   ❌ Web only: {summary['status_breakdown']['web_only']} ({summary['validation_percentages']['web_only']:.1f}%)")
    print(f"   🔍 Units with issues: {summary['units_with_issues']}")
    
    # Show Key Three only units by district
    if summary['key_three_only_by_district']:
        print(f"\n⚠️  Key Three Only Units by District:")
        for district, count in summary['key_three_only_by_district'].items():
            print(f"   {district}: {count} units")
    
    # Show sample units needing attention
    key_three_only = validator.get_units_by_status(ValidationStatus.KEY_THREE_ONLY)
    web_only = validator.get_units_by_status(ValidationStatus.WEB_ONLY)
    
    if key_three_only:
        print(f"\n⚠️  Sample Key Three Only Units (Missing from Web):")
        for result in key_three_only[:5]:
            print(f"   • {result.unit_key}")
            for issue in result.issues[:2]:  # Show first 2 issues
                print(f"     - {issue}")
    
    if web_only:
        print(f"\n❌ Sample Web Only Units (Not in Key Three):")
        for result in web_only[:3]:
            print(f"   • {result.unit_key}")
            for issue in result.issues[:1]:  # Show first issue
                print(f"     - {issue}")
    
    # Save results
    output_file = validator.save_validation_results(args.output)
    
    print(f"\n🎯 Validation Complete - Commissioner Action Required:")
    print(f"   • Review {summary['status_breakdown']['key_three_only']} units missing from web")
    print(f"   • Investigate {summary['status_breakdown']['web_only']} web-only units")
    print(f"   • Address {summary['units_with_issues']} units with data quality issues")
    
    return output_file

if __name__ == "__main__":
    main()