#!/usr/bin/env python3
"""
Three-Way Unit Validation Engine
Cross-references Key Three database with scraped web data to identify discrepancies
Provides comprehensive data quality audit with action flags for commissioners
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

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
        
    def load_key_three_data(self, file_path: str = 'data/raw/key_three_foundation_units.json') -> bool:
        """Load Key Three foundation data (169 units)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.key_three_units = data.get('units', [])
                print(f"📋 Loaded {len(self.key_three_units)} Key Three units")
                return True
        except Exception as e:
            print(f"❌ Failed to load Key Three data: {e}")
            return False
    
    def load_scraped_data(self, file_path: str = 'data/raw/scraped_units_comprehensive.json') -> bool:
        """Load comprehensive scraped data (163 units)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.scraped_units = data.get('scraped_units', [])
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
        print(f"\n🔍 Starting Three-Way Validation")
        print(f"   Key Three units: {len(self.key_three_units)}")
        print(f"   Scraped units: {len(self.scraped_units)}")
        
        # Create lookup sets for efficient validation
        key_three_keys = {unit['unit_key'] for unit in self.key_three_units}
        scraped_keys = {unit['unit_key'] for unit in self.scraped_units}
        
        # Create lookup dictionaries for detailed data
        key_three_dict = {unit['unit_key']: unit for unit in self.key_three_units}
        scraped_dict = {unit['unit_key']: unit for unit in self.scraped_units}
        
        validation_results = []
        
        # Get all unique unit keys from both sources
        all_unit_keys = key_three_keys | scraped_keys
        
        print(f"   Total unique units: {len(all_unit_keys)}")
        
        # Validate each unit
        for unit_key in sorted(all_unit_keys):
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
            
            # Create validation result
            result = ValidationResult(
                unit_key=unit_key,
                status=status,
                key_three_data=key_three_dict.get(unit_key),
                scraped_data=scraped_dict.get(unit_key),
                issues=[]
            )
            
            # Identify specific issues
            self._analyze_unit_issues(result)
            
            validation_results.append(result)
        
        self.validation_results = validation_results
        return validation_results
    
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
    
    print("🚀 Three-Way Unit Validation Engine")
    
    validator = ThreeWayValidator()
    
    # Load data sources
    if not validator.load_key_three_data():
        return
    
    if not validator.load_scraped_data():
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
    output_file = validator.save_validation_results()
    
    print(f"\n🎯 Validation Complete - Commissioner Action Required:")
    print(f"   • Review {summary['status_breakdown']['key_three_only']} units missing from web")
    print(f"   • Investigate {summary['status_breakdown']['web_only']} web-only units")
    print(f"   • Address {summary['units_with_issues']} units with data quality issues")
    
    return output_file

if __name__ == "__main__":
    main()