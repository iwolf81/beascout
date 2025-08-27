#!/usr/bin/env python3
"""
Enhanced Key Three Parser - Foundation of Processing Pipeline
Implements sophisticated town extraction based on key_three_unit_analysis.md edge cases
Creates definitive 169-unit registry as source of truth
"""

import pandas as pd
import re
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mapping.district_mapping import get_district_for_town
from src.core.unit_identifier import UnitIdentifierNormalizer

class KeyThreeParser:
    """
    Advanced parser for Key Three database with sophisticated town extraction
    Handles all edge cases identified in key_three_unit_analysis.md
    """
    
    def __init__(self, excel_file_path: str):
        self.excel_file_path = excel_file_path
        self.raw_data = None
        self.parsed_units = []
        
    def load_excel_data(self):
        """Load Key Three Excel data with proper structure"""
        try:
            # Load with header row at index 3 (after report headers)
            df = pd.read_excel(self.excel_file_path, header=None, skiprows=3)
            
            # Set proper column names based on Key Three structure
            df.columns = [
                'district', 'unit_id', 'fullname', 'address', 'citystate', 'zipcode',
                'email', 'phone', 'position', 'unitcommorgname', 'status'
            ]
            
            # Include all records - status refers to Key Three member training, not unit status
            # All units in the Key Three database are considered active units
            self.raw_data = df.copy()
            
            print(f"Loaded {len(self.raw_data)} Key Three records (all member statuses)")
            return True
            
        except Exception as e:
            print(f"Error loading Key Three data: {e}")
            return False
    
    def extract_town_from_unitcommorgname(self, unitcommorgname: str) -> str:
        """
        Extract unit town from unitcommorgname field
        Implements all edge cases from key_three_unit_analysis.md
        """
        if not unitcommorgname or pd.isna(unitcommorgname):
            return ""
        
        orgname = str(unitcommorgname).strip()
        
        # Remove unit designation and gender markers first to get clean org name
        # Pattern: "Pack 0001 (F) - Acton-The Church of The Good Shepherd"
        clean_match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)\s*(\d+)(?:\s*\([BFG]\))?\s*-?\s*(.+)', orgname)
        if clean_match:
            clean_orgname = clean_match.group(3).strip()
        else:
            clean_orgname = orgname
        
        # Now work with the clean org name for town extraction
        
        # Pattern 1: "Worcester - Heart of New England Council" 
        # Town clearly before dash and space
        match = re.match(r'^([A-Za-z\s]+)\s+-\s+(.+)$', clean_orgname)
        if match:
            potential_town = match.group(1).strip()
            # Validate it's actually a town name
            if self._is_valid_town(potential_town):
                return self._normalize_town_name(potential_town)
        
        # Pattern 2: "Pepperell-Fire Firefighters Association" or "Acton-Church Name"
        # Town before dash (no spaces), this is the most common pattern
        match = re.match(r'^([A-Za-z\s]+)-(.+)$', clean_orgname)
        if match:
            potential_town = match.group(1).strip()
            if self._is_valid_town(potential_town):
                return self._normalize_town_name(potential_town)
        
        # Pattern 3: "Clinton Heart of New England Council"
        # Town at start, no separating dash
        words = clean_orgname.split()
        if len(words) >= 2:
            # Try first word as town
            potential_town = words[0]
            if self._is_valid_town(potential_town):
                return self._normalize_town_name(potential_town)
            
            # Try first two words as compound town
            potential_town = f"{words[0]} {words[1]}"
            if self._is_valid_town(potential_town):
                return self._normalize_town_name(potential_town)
        
        # Pattern 4: "Acton-Group Of Citizens, Inc"
        # Town matches chartered org name
        for word in words:
            if self._is_valid_town(word):
                return self._normalize_town_name(word)
        
        # Pattern 5: "Acton-Boxborough Rotary Club"
        # Multiple towns in org name - need fallback logic
        town_candidates = []
        for word in words:
            if self._is_valid_town(word):
                town_candidates.append(self._normalize_town_name(word))
        
        if len(town_candidates) == 1:
            return town_candidates[0]
        elif len(town_candidates) > 1:
            # Multiple town candidates - this needs Key Three member address fallback
            # For now, return first candidate
            return town_candidates[0]
        
        # Pattern 6: "E Brookfield - Howe Lumber Co Inc"
        # Handle abbreviated directions
        abbreviated_match = re.match(r'^([NESW])\s+([A-Za-z\s]+)', clean_orgname)
        if abbreviated_match:
            direction = abbreviated_match.group(1)
            town_part = abbreviated_match.group(2).split()[0]  # Take first word after direction
            direction_map = {'N': 'North', 'S': 'South', 'E': 'East', 'W': 'West'}
            full_town = f"{direction_map[direction]} {town_part}"
            if self._is_valid_town(full_town):
                return self._normalize_town_name(full_town)
        
        # Pattern 7: "Oxford First Congregational Church of Oxford"
        # Missing separating dash, town repeated
        if clean_orgname.count(' ') >= 2:
            first_word = words[0]
            if self._is_valid_town(first_word):
                return self._normalize_town_name(first_word)
        
        # Pattern 8: "Veterans Of Foreign Wars Westminster Post"
        # Town embedded near end
        for i, word in enumerate(words):
            if self._is_valid_town(word):
                return self._normalize_town_name(word)
        
        # Pattern 9: Village name handling
        # Villages are now treated as separate towns for unit correlation
        village_match = re.match(r'^([A-Za-z]+)', clean_orgname)
        if village_match:
            potential_village = village_match.group(1)
            # Check if it's a valid HNE town (including villages)
            if self._is_valid_town(potential_village):
                return self._normalize_town_name(potential_village)
        
        # If no pattern matches, return empty - will be flagged for manual review
        print(f"Warning: Could not extract town from: {orgname}")
        return ""
    
    def _is_valid_town(self, town_candidate: str) -> bool:
        """Check if candidate is a valid HNE Council town"""
        from src.mapping.district_mapping import get_district_for_town
        return get_district_for_town(town_candidate) != "Unknown"
    
    def _normalize_town_name(self, town: str) -> str:
        """Normalize town name to canonical form"""
        # Handle common variations and village mappings
        town_map = {
            "E Brookfield": "East Brookfield",
            "W Brookfield": "West Brookfield", 
            "N Brookfield": "North Brookfield",
            "W Boylston": "West Boylston",
            "Jefferson": "Jefferson",  # Village within Holden, treated as separate HNE town
            # Fiskdale: No mapping needed - treated as separate HNE town
        }
        normalized = town_map.get(town, town)
        
        # Handle Boxborough compound name issue
        if "Boxborough" in town:
            return "Boxborough" 
            
        return normalized
    
    def extract_unit_info_from_unitcommorgname(self, unitcommorgname: str) -> dict:
        """
        Extract unit type, number, and town from unitcommorgname
        Returns structured unit information
        """
        if not unitcommorgname or pd.isna(unitcommorgname):
            return {}
        
        orgname = str(unitcommorgname).strip()
        
        # Extract unit type and number from beginning
        # Handle gender designations like (F), (B), (G)
        unit_pattern = r'^(Pack|Troop|Crew|Ship|Post|Club)\s*(\d+)(?:\s*\([BFG]\))?'
        unit_match = re.match(unit_pattern, orgname)
        
        if not unit_match:
            return {}
        
        unit_type = unit_match.group(1)
        unit_number = unit_match.group(2).lstrip('0') or '0'  # Remove leading zeros, keep at least '0'
        
        # Extract town using sophisticated logic
        town = self.extract_town_from_unitcommorgname(orgname)
        
        # Extract chartered organization (everything after unit designation)
        org_match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)\s*(\d+)(?:\s*\([BFG]\))?\s*-?\s*(.+)', orgname)
        chartered_org = org_match.group(3).strip() if org_match else ""
        
        return {
            'unit_type': unit_type,
            'unit_number': unit_number,
            'unit_town': town,
            'chartered_org': chartered_org,
            'original_unitcommorgname': orgname
        }
    
    def parse_all_units(self) -> list:
        """
        Parse all unique units from Key Three database
        Returns list of 169 units as definitive registry
        """
        if self.raw_data is None:
            if not self.load_excel_data():
                return []
        
        # Get unique unitcommorgname values (should be 169)
        unique_orgs = self.raw_data['unitcommorgname'].dropna().unique()
        print(f"Found {len(unique_orgs)} unique unitcommorgname values")
        
        self.parsed_units = []
        
        for org_name in unique_orgs:
            unit_info = self.extract_unit_info_from_unitcommorgname(org_name)
            
            if unit_info and unit_info.get('unit_town'):
                # Create standardized unit record using normalizer
                standardized_record = UnitIdentifierNormalizer.create_unit_record(
                    unit_info['unit_type'],
                    unit_info['unit_number'], 
                    unit_info['unit_town'],
                    unit_info.get('chartered_org', ''),
                    original_unitcommorgname=unit_info.get('original_unitcommorgname', '')
                )
                
                self.parsed_units.append(standardized_record)
            else:
                print(f"Warning: Could not parse unit from: {org_name}")
        
        print(f"Successfully parsed {len(self.parsed_units)} units from Key Three")
        return self.parsed_units
    
    def get_unit_registry(self) -> dict:
        """
        Get structured unit registry for pipeline foundation
        Returns dict with units organized by unit_key for efficient lookup
        """
        if not self.parsed_units:
            self.parse_all_units()
        
        registry = {}
        for unit in self.parsed_units:
            unit_key = unit.get('unit_key')
            if unit_key:
                registry[unit_key] = unit
        
        return registry
    
    def validate_parsing(self) -> dict:
        """
        Validate that parsing produces expected 169 units
        Returns validation statistics
        """
        if not self.parsed_units:
            self.parse_all_units()
        
        # Count by district
        district_counts = {}
        unknown_towns = []
        
        for unit in self.parsed_units:
            district = unit.get('district', 'Unknown')
            district_counts[district] = district_counts.get(district, 0) + 1
            
            if district == 'Unknown':
                unknown_towns.append(unit.get('unit_key', 'Unknown'))
        
        return {
            'total_units': len(self.parsed_units),
            'expected_units': 169,
            'district_counts': district_counts,
            'unknown_towns': unknown_towns,
            'parsing_success': len(self.parsed_units) == 169
        }

def main():
    """Test the Key Three parser"""
    parser = KeyThreeParser('data/input/Key 3 08-22-2025.xlsx')
    
    # Parse all units
    units = parser.parse_all_units()
    
    # Validate parsing
    validation = parser.validate_parsing()
    
    print(f"\n📊 Key Three Parsing Validation:")
    print(f"   Expected units: {validation['expected_units']}")
    print(f"   Parsed units: {validation['total_units']}")
    print(f"   Parsing success: {'✅' if validation['parsing_success'] else '❌'}")
    
    print(f"\n🏛️ District Distribution:")
    for district, count in validation['district_counts'].items():
        print(f"   {district}: {count} units")
    
    if validation['unknown_towns']:
        print(f"\n⚠️ Units with Unknown district ({len(validation['unknown_towns'])}):")
        for unit_key in validation['unknown_towns'][:5]:  # Show first 5
            print(f"   - {unit_key}")
    
    # Show sample parsed units
    print(f"\n📋 Sample Parsed Units:")
    for unit in units[:3]:
        print(f"   {unit['unit_key']} → {unit['district']}")
        print(f"      Original: {unit['original_unitcommorgname']}")

if __name__ == "__main__":
    main()