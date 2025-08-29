#!/usr/bin/env python3
"""
Enhanced Three-Way Unit Validation Engine
Addresses critical town matching and geographic normalization issues
Fixes false positives/negatives identified in commissioner feedback
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
    matching_notes: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.matching_notes is None:
            self.matching_notes = []

class EnhancedValidator:
    """
    Enhanced unit validation engine with improved geographic matching
    Addresses false positives/negatives from commissioner feedback
    """
    
    def __init__(self):
        self.key_three_units = []
        self.scraped_units = []
        self.validation_results = []
        self.town_aliases = self._load_town_aliases()
        self.hne_towns = self._load_hne_towns()
        
    def _load_town_aliases(self) -> Dict[str, str]:
        """Load town name aliases and variations"""
        return {
            # Villages and neighborhoods that map to main towns
            "fiskdale": "sturbridge", ## @claude verify this is correct
            "whitinsville": "northbridge", 
            "east brookfield": "brookfield",
            "west brookfield": "brookfield",
            "west boylston": "west boylston",  # Normalize spelling
            "west boyston": "west boylston",   # Common misspelling
            
            # Common alternate spellings
            "gardner": "gardner",
            "leominster": "leominster",
            "worcester": "worcester",
            "grafton": "grafton",
            "athol": "athol",
            "boylston": "boylston",
            
            # Villages within HNE towns
            "jefferson": "jefferson",  # Verify this is correct
        }
    
    def _load_hne_towns(self) -> Set[str]:
        """Load definitive HNE town list"""
        hne_towns = {
            "acton", "ashby", "ayer", "berlin", "bolton", "boxborough", "boylston",
            "brookfield", "charlton", "clinton", "douglas", "dudley", "fitchburg",
            "gardner", "grafton", "groton", "harvard", "holden", "hubbardston",
            "lancaster", "leicester", "leominster", "littleton", "lunenburg",
            "millbury", "northbridge", "oakham", "orange", "oxford", "paxton",
            "pepperell", "phillipston", "princeton", "rutland", "shirley",
            "spencer", "sterling", "sturbridge", "sutton", "templeton", "townsend",
            "upton", "ware", "warren", "webster", "west boylston", "westborough",
            "westminster", "winchendon", "worcester", "athol", "barre", "hardwick",
            "new braintree", "north brookfield", "west brookfield", "petersham",
            "royalston", "east brookfield"
        }
        return hne_towns
    
    def _normalize_town_name(self, town_name: str) -> str:
        """Normalize town name using aliases and standard formatting"""
        if not town_name:
            return ""
        
        # Clean and normalize
        clean_town = town_name.lower().strip()
        
        # Apply aliases
        normalized = self.town_aliases.get(clean_town, clean_town)
        
        # Title case for consistency
        return normalized.title()
    
    def _is_hne_town(self, town_name: str) -> bool:
        """Check if a town is within HNE Council territory"""
        normalized = self._normalize_town_name(town_name)
        return normalized.lower() in self.hne_towns
    
    def _extract_unit_info(self, unit_key: str) -> Tuple[str, str, str]:
        """Extract unit type, number, and town from unit_key"""
        parts = unit_key.split(' ', 2)
        if len(parts) >= 3:
            return parts[0], parts[1], parts[2]
        return "", "", ""
    
    def _create_alternate_keys(self, unit_type: str, unit_number: str, town: str) -> List[str]:
        """Create alternate unit keys for fuzzy matching"""
        alternates = []
        
        # Original key
        base_key = f"{unit_type} {unit_number} {town}"
        alternates.append(base_key)
        
        # Try town aliases
        normalized_town = self._normalize_town_name(town)
        if normalized_town != town:
            alternates.append(f"{unit_type} {unit_number} {normalized_town}")
        
        # Try reverse aliases (in case the input is the alias)
        for alias, canonical in self.town_aliases.items():
            if town.lower() == canonical.lower():
                alternates.append(f"{unit_type} {unit_number} {alias.title()}")
        
        return list(set(alternates))  # Remove duplicates
    
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
    
    def load_scraped_data(self, file_path: str = 'data/raw/scraped_units_corrected.json') -> bool:
        """Load comprehensive scraped data (163 units)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.scraped_units = data.get('scraped_units', [])
                
                # Filter out non-HNE units based on meeting location analysis
                hne_scraped = []
                excluded_units = []
                
                for unit in self.scraped_units:
                    unit_town = unit.get('unit_town', '')
                    meeting_location = unit.get('meeting_location', '')
                    
                    # Skip units clearly outside HNE territory
                    if self._is_non_hne_unit(unit_town, meeting_location, unit.get('unit_key', '')):
                        excluded_units.append(unit)
                        continue
                    
                    # Only include units in confirmed HNE towns
                    if self._is_hne_town(unit_town):
                        hne_scraped.append(unit)
                    else:
                        excluded_units.append(unit)
                
                self.scraped_units = hne_scraped
                print(f"🌐 Loaded {len(self.scraped_units)} HNE scraped units ({len(excluded_units)} excluded)")
                return True
        except Exception as e:
            print(f"❌ Failed to load scraped data: {e}")
            return False
    
    def _is_non_hne_unit(self, unit_town: str, meeting_location: str, unit_key: str) -> bool:
        """Detect units that are clearly outside HNE territory"""
        
        # Check for obvious non-HNE locations
        non_hne_indicators = [
            "nashua nh", "hudson nh", "manchester nh", "putnam ct", 
            "bellingham", "holliston", "uxbridge", "daniel webster council"
        ]
        
        location_text = f"{unit_town} {meeting_location}".lower()
        
        for indicator in non_hne_indicators:
            if indicator in location_text:
                return True
        
        # Special cases from commissioner feedback
        if "troop 252" in unit_key.lower() and "hudson" in location_text:
            return True
        if "troop 272" in unit_key.lower() and "nashua" in location_text:
            return True
            
        return False
    
    def validate_all_units(self) -> List[ValidationResult]:
        """
        Perform enhanced three-way validation with improved matching
        Returns list of validation results for all units
        """
        print(f"\n🔍 Starting Enhanced Three-Way Validation")
        print(f"   Key Three units: {len(self.key_three_units)}")
        print(f"   Scraped units: {len(self.scraped_units)}")
        
        # Create enhanced lookup structures
        key_three_lookup = {}
        scraped_lookup = {}
        
        # Build Key Three lookup with alternates
        for unit in self.key_three_units:
            unit_key = unit['unit_key']
            unit_type, unit_number, town = self._extract_unit_info(unit_key)
            
            # Store under primary key
            key_three_lookup[unit_key] = unit
            
            # Store under alternate keys
            alternates = self._create_alternate_keys(unit_type, unit_number, town)
            for alt_key in alternates:
                if alt_key != unit_key:  # Don't overwrite primary
                    key_three_lookup[alt_key] = unit
        
        # Build scraped data lookup with alternates
        for unit in self.scraped_units:
            unit_key = unit['unit_key']
            unit_type, unit_number, town = self._extract_unit_info(unit_key)
            
            # Store under primary key
            scraped_lookup[unit_key] = unit
            
            # Store under alternate keys
            alternates = self._create_alternate_keys(unit_type, unit_number, town)
            for alt_key in alternates:
                if alt_key != unit_key:  # Don't overwrite primary
                    scraped_lookup[alt_key] = unit
        
        validation_results = []
        
        # Get all unique unit keys (using primary keys only)
        key_three_primary_keys = {unit['unit_key'] for unit in self.key_three_units}
        scraped_primary_keys = {unit['unit_key'] for unit in self.scraped_units}
        all_primary_keys = key_three_primary_keys | scraped_primary_keys
        
        print(f"   Total unique primary keys: {len(all_primary_keys)}")
        
        # Validate each unit
        for primary_key in sorted(all_primary_keys):
            # Try to find matches using enhanced lookup
            key_three_match = None
            scraped_match = None
            matching_notes = []
            
            # Check for Key Three match (try primary key and alternates)
            unit_type, unit_number, town = self._extract_unit_info(primary_key)
            alternates = self._create_alternate_keys(unit_type, unit_number, town)
            
            for key in [primary_key] + alternates:
                if key in key_three_lookup:
                    key_three_match = key_three_lookup[key]
                    if key != primary_key:
                        matching_notes.append(f"Key Three matched via alternate: {key}")
                    break
            
            # Check for scraped match (try primary key and alternates)
            for key in [primary_key] + alternates:
                if key in scraped_lookup:
                    scraped_match = scraped_lookup[key]
                    if key != primary_key:
                        matching_notes.append(f"Scraped matched via alternate: {key}")
                    break
            
            # Determine validation status
            if key_three_match and scraped_match:
                status = ValidationStatus.BOTH_SOURCES
            elif key_three_match and not scraped_match:
                status = ValidationStatus.KEY_THREE_ONLY
            elif not key_three_match and scraped_match:
                status = ValidationStatus.WEB_ONLY
            else:
                # This shouldn't happen but included for completeness
                continue
            
            # Create validation result
            result = ValidationResult(
                unit_key=primary_key,
                status=status,
                key_three_data=key_three_match,
                scraped_data=scraped_match,
                issues=[],
                matching_notes=matching_notes
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
                
                # Check for data inconsistencies (but be more lenient with town matching)
                if key_three and scraped.get('unit_town') != key_three.get('unit_town'):
                    scraped_town = self._normalize_town_name(scraped.get('unit_town', ''))
                    key_three_town = self._normalize_town_name(key_three.get('unit_town', ''))
                    
                    if scraped_town.lower() != key_three_town.lower():
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
        
        # Count units with matching notes
        units_with_alternates = len([r for r in self.validation_results if r.matching_notes])
        
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
            'units_with_alternates': units_with_alternates,
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
    
    def save_validation_results(self, output_path: str = 'data/output/enhanced_three_way_validation_results.json'):
        """Save enhanced validation results"""
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.validation_results:
            serializable_results.append({
                'unit_key': result.unit_key,
                'status': result.status.value,
                'key_three_data': result.key_three_data,
                'scraped_data': result.scraped_data,
                'issues': result.issues,
                'matching_notes': result.matching_notes
            })
        
        output_data = {
            'validation_summary': self.get_validation_summary(),
            'validation_results': serializable_results,
            'data_sources': {
                'key_three_units': len(self.key_three_units),
                'scraped_units': len(self.scraped_units)
            },
            'enhancements': {
                'town_aliases_applied': len(self.town_aliases),
                'hne_territory_filtering': True,
                'alternate_key_matching': True
            }
        }
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved enhanced validation results to: {output_path}")
        return output_path

def main():
    """Main enhanced validation execution"""
    
    print("🚀 Enhanced Three-Way Unit Validation Engine")
    
    validator = EnhancedValidator()
    
    # Load data sources
    if not validator.load_key_three_data():
        return
    
    if not validator.load_scraped_data():
        return
    
    # Perform enhanced validation
    results = validator.validate_all_units()
    
    if not results:
        print("❌ No validation results generated")
        return
    
    # Display summary
    summary = validator.get_validation_summary()
    
    print(f"\n📊 Enhanced Validation Summary:")
    print(f"   Total units analyzed: {summary['total_units']}")
    print(f"   ✅ Both sources: {summary['status_breakdown']['both_sources']} ({summary['validation_percentages']['both_sources']:.1f}%)")
    print(f"   ⚠️  Key Three only: {summary['status_breakdown']['key_three_only']} ({summary['validation_percentages']['key_three_only']:.1f}%)")
    print(f"   ❌ Web only: {summary['status_breakdown']['web_only']} ({summary['validation_percentages']['web_only']:.1f}%)")
    print(f"   🔍 Units with issues: {summary['units_with_issues']}")
    print(f"   🔗 Units matched via alternates: {summary['units_with_alternates']}")
    
    # Show Key Three only units by district
    if summary['key_three_only_by_district']:
        print(f"\n⚠️  Key Three Only Units by District:")
        for district, count in summary['key_three_only_by_district'].items():
            print(f"   {district}: {count} units")
    
    # Show sample units with matching notes
    units_with_notes = [r for r in results if r.matching_notes]
    if units_with_notes:
        print(f"\n🔗 Sample Alternate Matches:")
        for result in units_with_notes[:5]:
            print(f"   • {result.unit_key}")
            for note in result.matching_notes:
                print(f"     - {note}")
    
    # Save results
    output_file = validator.save_validation_results()
    
    print(f"\n🎯 Enhanced Validation Complete:")
    print(f"   • Improved town matching with aliases and villages")
    print(f"   • Filtered out non-HNE units from scraped data") 
    print(f"   • Enhanced alternate key matching")
    
    return output_file

if __name__ == "__main__":
    main()