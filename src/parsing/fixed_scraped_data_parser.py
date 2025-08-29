#!/usr/bin/env python3
"""
Fixed Scraped Data Parser
Fixes town extraction issues identified in user feedback
Implements proper address parsing and HNE territory filtering
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mapping.district_mapping import get_district_for_town
from src.core.unit_identifier import UnitIdentifierNormalizer

class FixedScrapedDataParser:
    """
    Fixed parser addressing critical town extraction issues:
    1. Proper priority: unit-address -> unit-name -> unit-description -> chartered org
    2. Enhanced HNE territory filtering
    3. Proper 4-digit unit number handling
    4. Address parsing improvements
    """
    
    def __init__(self):
        self.parsed_units = []
        self.hne_towns = self._load_hne_towns()
        self.non_hne_patterns = [
            'daniel webster council', 'nashua nh', 'hudson nh', 'putnam ct',
            'bellingham', 'holliston', 'uxbridge', 'manchester nh'
        ]
        self.parsing_stats = {
            'total_processed': 0,
            'successfully_parsed': 0,
            'excluded_non_hne': 0,
            'town_extraction_methods': {
                'unit_address': 0,
                'unit_name': 0,
                'unit_description': 0,
                'chartered_org': 0,
                'failed': 0
            }
        }
    
    def _load_hne_towns(self) -> Set[str]:
        """Load HNE town names from centralized source"""
        from src.mapping.district_mapping import get_all_hne_towns
        return get_all_hne_towns()
    
    def parse_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse a scraped data JSON file with improved town extraction"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                units = data.get('all_units', data.get('units', data.get('scraped_units', [])))
            elif isinstance(data, list):
                units = data
            else:
                print(f"Unexpected JSON structure in {file_path}")
                return []
            
            print(f"Processing {len(units)} units from {file_path}")
            
            parsed_units = []
            for unit in units:
                self.parsing_stats['total_processed'] += 1
                
                # Check if unit is in HNE territory before processing
                if self._is_non_hne_unit(unit):
                    self.parsing_stats['excluded_non_hne'] += 1
                    # Log discarded non-HNE unit
                    UnitIdentifierNormalizer.log_discarded_unit(
                        str(unit.get('unit_type', 'Unknown')),
                        str(unit.get('unit_number', 'Unknown')), 
                        str(unit.get('chartered_organization', 'Unknown')),
                        str(unit.get('chartered_organization', 'Unknown')),
                        'Non-HNE unit (outside council territory)'
                    )
                    continue
                
                parsed_unit = self.parse_unit_record(unit)
                if parsed_unit:
                    parsed_units.append(parsed_unit)
                    self.parsing_stats['successfully_parsed'] += 1
            
            print(f"Successfully parsed {len(parsed_units)} units")
            print(f"Excluded {self.parsing_stats['excluded_non_hne']} non-HNE units")
            return parsed_units
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def _is_non_hne_unit(self, unit: Dict[str, Any]) -> bool:
        """Check if unit is clearly outside HNE territory"""
        # Check chartered organization for non-HNE indicators
        chartered_org = str(unit.get('chartered_organization', '')).lower()
        for pattern in self.non_hne_patterns:
            if pattern in chartered_org:
                return True
        
        # Check meeting location for non-HNE indicators  
        meeting_location = str(unit.get('meeting_location', '')).lower()
        for pattern in ['nashua nh', 'hudson nh', 'putnam ct']:
            if pattern in meeting_location:
                return True
        
        # Check address field for non-HNE indicators
        address = str(unit.get('address', '')).lower()
        for pattern in ['nashua nh', 'hudson nh', 'putnam ct', ' nh ', ' ct ']:
            if pattern in address:
                return True
        
        return False
    
    def parse_unit_record(self, unit: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse individual unit record with fixed town extraction"""
        
        # Extract basic unit information
        unit_type = self._extract_unit_type(unit)
        unit_number = self._extract_unit_number(unit)  # Keep as 4-digit string
        
        if not unit_type or not unit_number:
            # Log discarded unit
            UnitIdentifierNormalizer.log_discarded_unit(
                unit_type or 'Unknown', unit_number or 'Unknown', 
                'Unknown', str(unit.get('chartered_organization', '')), 
                'Missing unit type or number'
            )
            return None
        
        # Fixed town extraction following user's priority order
        town = self._extract_town_from_unit_fixed(unit)
        
        if not town:
            # Log discarded unit
            UnitIdentifierNormalizer.log_discarded_unit(
                unit_type, unit_number, 'Unknown',
                str(unit.get('chartered_organization', '')), 
                'Could not extract town'
            )
            self.parsing_stats['town_extraction_methods']['failed'] += 1
            return None
        
        # Validate town is in HNE territory
        if not self._validate_hne_town(town):
            self.parsing_stats['excluded_non_hne'] += 1
            # Log discarded unit with invalid town
            UnitIdentifierNormalizer.log_discarded_unit(
                unit_type, unit_number, town,
                str(unit.get('chartered_organization', '')).strip(),
                f'Invalid town: {town} not in HNE territory'
            )
            return None
        
        # Extract other unit data
        chartered_org = str(unit.get('chartered_organization', '')).strip()
        meeting_location = str(unit.get('meeting_location', '')).strip()
        meeting_day = str(unit.get('meeting_day', '')).strip()
        meeting_time = str(unit.get('meeting_time', '')).strip()
        contact_email = str(unit.get('contact_email', '')).strip()
        contact_person = str(unit.get('contact_person', '')).strip()
        phone_number = str(unit.get('phone_number', '')).strip()
        website = str(unit.get('website', '')).strip()
        description = str(unit.get('description', '')).strip()
        specialty = str(unit.get('specialty', '')).strip()
        
        # Create standardized unit record using UnitIdentifierNormalizer
        record = UnitIdentifierNormalizer.create_unit_record(
            unit_type=unit_type,
            unit_number=unit_number,  # This will be normalized to remove leading zeros
            town=town,
            chartered_org=chartered_org,
            data_source='scraped',
            meeting_location=meeting_location,
            meeting_day=meeting_day,
            meeting_time=meeting_time,
            contact_email=contact_email,
            contact_person=contact_person,
            phone_number=phone_number,
            website=website,
            description=description,
            specialty=specialty,
            original_scraped_data=unit
        )
        
        return record
    
    def _extract_unit_type(self, unit: Dict[str, Any]) -> Optional[str]:
        """Extract unit type from various possible fields"""
        # Try direct field
        if 'unit_type' in unit and unit['unit_type']:
            return str(unit['unit_type']).strip().capitalize()
        
        # Try to extract from primary identifier
        primary_id = unit.get('primary_identifier', '')
        if primary_id:
            match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)', primary_id, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        
        return None
    
    def _extract_unit_number(self, unit: Dict[str, Any]) -> Optional[str]:
        """Extract unit number and preserve as 4-digit string for better matching"""
        # Try different field names
        number_fields = ['unit_number', 'number', 'unit_num']
        
        for field in number_fields:
            if field in unit and unit[field]:
                number = str(unit[field]).strip()
                # Ensure it's a 4-digit string with leading zeros
                try:
                    num_int = int(number)
                    return f"{num_int:04d}"
                except ValueError:
                    continue
        
        # Try to extract from primary identifier
        primary_id = unit.get('primary_identifier', '')
        if primary_id:
            match = re.match(r'^(?:Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)', primary_id, re.IGNORECASE)
            if match:
                number = match.group(1)
                try:
                    num_int = int(number)
                    return f"{num_int:04d}"
                except ValueError:
                    pass
        
        return None
    
    def _extract_town_from_unit_fixed(self, unit: Dict[str, Any]) -> Optional[str]:
        """
        Fixed town extraction with village priority handling:
        Special case: If unit name contains village names (Fiskdale, Jefferson), 
        prioritize unit name over address for cross-validation with Key Three.
        
        Standard priority order:
        1. <div class="unit-address"> (from HTML parsing)
        2. <div class="unit-name"> (from HTML parsing)  
        3. <div class="unit-description"> (from HTML parsing)
        4. Chartered organization parsing (fallback)
        """
        
        # CRITICAL EXCEPTION: Troop 0132 meets in Mendon but is chartered in Upton (HNE territory)
        # Must be checked BEFORE standard precedence to avoid incorrect filtering
        unit_type = self._extract_unit_type(unit)
        unit_number = self._extract_unit_number(unit)
        
        if (unit_type == 'Troop' and unit_number == '0132' and 
            'chartered_organization' in unit and unit['chartered_organization'] and
            'Upton' in str(unit['chartered_organization'])):
            # Override meeting location town with chartered organization town
            if self._validate_hne_town('Upton'):
                self.parsing_stats['town_extraction_methods']['special_exception'] = (
                    self.parsing_stats['town_extraction_methods'].get('special_exception', 0) + 1
                )
                return 'Upton'
        
        # Special Exception: Village priority for Key Three cross-validation
        # Villages: Fiskdale, Jefferson, Whitinsville
        # Check both unit name and chartered organization for villages
        
        # Check unit name for villages
        if 'unit_name' in unit and unit['unit_name']:
            unit_name_lower = str(unit['unit_name']).lower()
            if 'fiskdale' in unit_name_lower:
                if self._validate_hne_town('Fiskdale'):
                    self.parsing_stats['town_extraction_methods']['unit_name'] += 1
                    return 'Fiskdale'
            elif 'whitinsville' in unit_name_lower:
                if self._validate_hne_town('Whitinsville'):
                    self.parsing_stats['town_extraction_methods']['unit_name'] += 1
                    return 'Whitinsville'
            elif 'jefferson' in unit_name_lower:
                if self._validate_hne_town('Jefferson'):
                    self.parsing_stats['town_extraction_methods']['unit_name'] += 1
                    return 'Jefferson'
        
        # Check chartered organization for villages (highest priority!)
        if 'chartered_organization' in unit and unit['chartered_organization']:
            org_name_lower = str(unit['chartered_organization']).lower()
            if 'fiskdale' in org_name_lower:
                if self._validate_hne_town('Fiskdale'):
                    self.parsing_stats['town_extraction_methods']['chartered_org'] += 1
                    return 'Fiskdale'
            elif 'whitinsville' in org_name_lower:
                if self._validate_hne_town('Whitinsville'):
                    self.parsing_stats['town_extraction_methods']['chartered_org'] += 1
                    return 'Whitinsville'
            elif 'jefferson' in org_name_lower:
                if self._validate_hne_town('Jefferson'):
                    self.parsing_stats['town_extraction_methods']['chartered_org'] += 1
                    return 'Jefferson'
        
        # Priority 1: unit-address field (standard priority)
        if 'unit_address' in unit and unit['unit_address']:
            town = self._parse_town_from_address(str(unit['unit_address']))
            if town:
                # Check if town is outside HNE territory
                if self._is_outside_hne_territory(town):
                    # Skip units outside HNE territory
                    return None
                elif self._validate_hne_town(town) or town:  # Accept any town extracted from address
                    self.parsing_stats['town_extraction_methods']['unit_address'] += 1
                    return town
        
        # Also check common address field names
        address_fields = ['address', 'meeting_location', 'location']
        for field in address_fields:
            if field in unit and unit[field]:
                town = self._parse_town_from_address(str(unit[field]))
                if town:
                    # Check if town is outside HNE territory
                    if self._is_outside_hne_territory(town):
                        # Skip units outside HNE territory
                        return None
                    elif self._validate_hne_town(town) or town:  # Accept any town extracted from address
                        self.parsing_stats['town_extraction_methods']['unit_address'] += 1
                        return town
        
        # Priority 2: unit-name field (standard parsing)
        name_fields = ['unit_name', 'primary_identifier']
        for field in name_fields:
            if field in unit and unit[field]:
                town = self._parse_town_from_text(str(unit[field]))
                if town and self._validate_hne_town(town):
                    self.parsing_stats['town_extraction_methods']['unit_name'] += 1
                    return town
        
        # Priority 3: unit-description field
        if 'unit_description' in unit and unit['unit_description']:
            town = self._parse_town_from_text(str(unit['unit_description']))
            if town and self._validate_hne_town(town):
                self.parsing_stats['town_extraction_methods']['unit_description'] += 1
                return town
        
        # Also check common description field names
        desc_fields = ['description', 'desc', 'unit_desc']
        for field in desc_fields:
            if field in unit and unit[field]:
                description_text = str(unit[field])
                # Skip description if it primarily contains contact information to avoid extracting person names as towns
                if not re.search(r'Contact:\s*[A-Za-z\s]+\s*Email:', description_text, re.IGNORECASE):
                    town = self._parse_town_from_text(description_text)
                    if town and self._validate_hne_town(town):
                        self.parsing_stats['town_extraction_methods']['unit_description'] += 1
                        return town
        
        # Priority 4: Chartered organization parsing (fallback)
        if 'chartered_organization' in unit and unit['chartered_organization']:
            town = self._parse_town_from_chartered_org(str(unit['chartered_organization']))
            if town:
                # Check if town is outside HNE territory
                if self._is_outside_hne_territory(town):
                    # Skip units outside HNE territory
                    return None
                elif self._validate_hne_town(town):
                    self.parsing_stats['town_extraction_methods']['chartered_org'] += 1
                    return town
        
        return None
    
    def _parse_town_from_address(self, address: str) -> Optional[str]:
        """
        Parse town from address string
        Examples:
        - "20 Summer St., Shrewsbury MA 01545" → "Shrewsbury" 
        - "159 Hartwell St, West, Boylston MA 01583" → "West Boylston"
        - "West Boylston MA" → "West Boylston"
        """
        address = address.strip()
        
        if not address or 'P.O. Box' in address or 'PO Box' in address:
            return None
        
        # Pattern 0: Simple "Town MA/CT" format (highest priority)
        simple_match = re.match(r'^([A-Za-z\s]+)\s+(MA|CT)\s*\d*$', address)
        if simple_match:
            town = simple_match.group(1).strip()
            normalized = self._normalize_town_name(town)
            return normalized  # Return without HNE validation to capture CT units
        
        # Pattern 1: "Street, City, State ZIP"
        match = re.search(r',\s*([A-Za-z\s]+),\s*(MA|CT)\s+\d{5}', address)
        if match:
            town = match.group(1).strip()
            return self._normalize_town_name(town)
        
        # Pattern 2: "Street, City State ZIP" (no comma before state) 
        # Handle "159 Hartwell St, West, Boylston MA 01583" by looking for last comma group
        match = re.search(r',\s*([A-Za-z\s,]+?)\s+(MA|CT)\s+\d{5}', address)
        if match:
            town_part = match.group(1).strip()
            # If there's a comma in the town part, it might be "West, Boylston"
            if ',' in town_part:
                parts = [p.strip() for p in town_part.split(',')]
                if len(parts) == 2 and parts[0].lower() in ['west', 'east', 'north', 'south']:
                    return self._normalize_town_name(f"{parts[0]} {parts[1]}")
                # Otherwise use the last part
                return self._normalize_town_name(parts[-1])
            return self._normalize_town_name(town_part)
        
        # Pattern 3: Find "West, Boylston" pattern (comma in middle of town name)
        match = re.search(r',\s*([A-Za-z]+),\s*([A-Za-z]+)\s+(MA|CT)', address)
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            # Check if this looks like a directional town name pattern
            if part1.lower() in ['west', 'east', 'north', 'south']:
                combined = f"{part1} {part2}"
                return self._normalize_town_name(combined)
            # Otherwise use just the second part
            return self._normalize_town_name(part2)
        
        # Pattern 4: Extract concatenated street+town patterns like "159 Hartwell StWest Boylston MA"
        # Look for pattern: StreetName + TownName + MA/CT + ZIP
        concatenated_match = re.search(r'([A-Za-z\s]+St|[A-Za-z\s]+Ave|[A-Za-z\s]+Rd|[A-Za-z\s]+Dr|[A-Za-z\s]+Ln|[A-Za-z\s]+Way|[A-Za-z\s]+Blvd)([A-Za-z\s]+)\s+(MA|CT)\s+\d{5}', address)
        if concatenated_match:
            potential_town = concatenated_match.group(2).strip()
            # Clean up common concatenated patterns
            if potential_town:
                return self._normalize_town_name(potential_town)
        
        # Pattern 5: Extract any MA/CT town names
        ma_ct_match = re.search(r'([A-Za-z\s]+)\s+(MA|CT)\s+\d{5}', address)
        if ma_ct_match:
            potential_town = ma_ct_match.group(1).strip()
            # Remove street parts
            words = potential_town.split()
            if len(words) >= 2:
                # Try last two words (handles "West Boylston")
                town_candidate = ' '.join(words[-2:])
                normalized = self._normalize_town_name(town_candidate)
                return normalized  # Return without HNE validation to capture CT units
        
        # Pattern 6: Handle building/facility names before town
        # "77 Mendon St.St. Mary Parish HallUxbridge MA 01569"
        facility_match = re.search(r'([A-Za-z\s]*Hall|[A-Za-z\s]*Church|[A-Za-z\s]*Center)([A-Za-z\s]+)\s+(MA|CT)\s+\d{5}', address)
        if facility_match:
            potential_town = facility_match.group(2).strip()
            if potential_town:
                return self._normalize_town_name(potential_town)
        
        return None
    
    def _parse_town_from_text(self, text: str) -> Optional[str]:
        """Parse town name from general text (name/description fields)"""
        text = text.strip().lower()
        
        # Look for HNE town names in the text
        for town in self.hne_towns:
            if town.lower() in text:
                return self._normalize_town_name(town)
        
        return None
    
    def _parse_town_from_chartered_org(self, org_name: str) -> Optional[str]:
        """
        Parse town from chartered organization name
        Examples:
        - "West Boylston-American Legion Post 204" → "West Boylston"
        - "Grafton - Our Lady of Hope Parish" → "Grafton"
        - "Sturbridge-Fiskdale Community Club" → "Fiskdale" (village priority)
        """
        org_name = org_name.strip()
        
        # Special Exception: Village priority for Key Three cross-validation
        # Villages: Fiskdale, Jefferson, Whitinsville
        org_name_lower = org_name.lower()
        if 'fiskdale' in org_name_lower:
            if self._validate_hne_town('Fiskdale'):
                return 'Fiskdale'
        elif 'whitinsville' in org_name_lower:
            if self._validate_hne_town('Whitinsville'):
                return 'Whitinsville'
        elif 'jefferson' in org_name_lower:
            if self._validate_hne_town('Jefferson'):
                return 'Jefferson'
        
        # Pattern 1: "Town-Organization" or "Town - Organization"
        match = re.match(r'^([A-Za-z\s]+?)\s*-\s*(.+)$', org_name)
        if match:
            potential_town = match.group(1).strip()
            normalized = self._normalize_town_name(potential_town)
            if self._validate_hne_town(normalized):
                return normalized
        
        # Pattern 2: Look for multi-word HNE town names first (more specific)
        multi_word_towns = [town for town in self.hne_towns if ' ' in town]
        multi_word_towns.sort(key=len, reverse=True)  # Longest first
        
        for town in multi_word_towns:
            if town.lower() in org_name.lower():
                return self._normalize_town_name(town)
        
        # Pattern 3: Look for single-word HNE town names
        single_word_towns = [town for town in self.hne_towns if ' ' not in town]
        for town in single_word_towns:
            if town.lower() in org_name.lower():
                return self._normalize_town_name(town)
        
        return None
    
    def _normalize_town_name(self, town: str) -> str:
        """
        Normalize town name with enhanced rules from user feedback
        Handles N, S, E, W prefixes properly
        """
        if not town:
            return ""
        
        town = town.strip()
        
        # Handle directional abbreviations
        town_map = {
            "E Brookfield": "East Brookfield",
            "W Brookfield": "West Brookfield", 
            "N Brookfield": "North Brookfield",
            "S Brookfield": "South Brookfield",
            "W Boylston": "West Boylston",
            "E Boylston": "East Boylston",
            "N Worcester": "North Worcester", 
            "S Worcester": "South Worcester",
            # Fiskdale: No mapping needed - treated as separate HNE town for Key Three correlation
            "Whitinsville": "Northbridge",  # Village mapping
        }
        
        # Direct mapping first
        if town in town_map:
            return town_map[town]
        
        # Case-insensitive matching
        for variant, canonical in town_map.items():
            if town.lower() == variant.lower():
                return canonical
        
        # Expand single letter directions
        town = re.sub(r'^N\s+', 'North ', town)
        town = re.sub(r'^S\s+', 'South ', town) 
        town = re.sub(r'^E\s+', 'East ', town)
        town = re.sub(r'^W\s+', 'West ', town)
        
        return town.title()
    
    def _validate_hne_town(self, town: str) -> bool:
        """Validate that town is a recognized HNE Council town"""
        if not town:
            return False
        
        normalized = self._normalize_town_name(town)
        return normalized.lower() in self.hne_towns or get_district_for_town(normalized) != "Unknown"
    
    def _is_outside_hne_territory(self, town: str) -> bool:
        """Check if town is outside HNE territory (like CT or non-HNE MA towns)"""
        if not town:
            return False
            
        # Known out-of-territory towns
        out_of_territory = {
            'uxbridge': True,  # Not in HNE territory despite being MA
            'putnam': True,   # Connecticut
            'danielson': True, # Connecticut
            'thompson': True,  # Connecticut
        }
        
        return town.lower() in out_of_territory
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get enhanced parsing statistics"""
        return self.parsing_stats.copy()

def main():
    """Test the fixed scraped data parser"""
    parser = FixedScrapedDataParser()
    
    # Test with problematic units from user feedback
    test_units = [
        {
            'unit_type': 'Pack',
            'unit_number': '106',
            'chartered_organization': 'Grafton - Our Lady of Hope Parish Grafton @ St. Mary',
            'meeting_location': "St Mary's Catholic Church, 17 Waterville St, North, Grafton MA 01536",
            'unit_address': 'Grafton MA'
        },
        {
            'unit_type': 'Pack', 
            'unit_number': '158',
            'chartered_organization': 'Shrewsbury - St. Marys Roman Catholic Church',
            'meeting_location': 'St. Marys Roman Catholic Church, 20 Summer St., Shrewsbury MA 01545',
            'unit_address': 'Shrewsbury MA'
        },
        {
            'unit_type': 'Crew',
            'unit_number': '204',
            'chartered_organization': 'West Boylston-American Legion Post 204',
            'meeting_location': '159 Hartwell St, West, Boylston MA 01583',
            'unit_address': 'West Boylston MA'
        }
    ]
    
    print("🔧 Testing Fixed Scraped Data Parser")
    
    for i, unit in enumerate(test_units, 1):
        parsed = parser.parse_unit_record(unit)
        if parsed:
            print(f"\n✅ Unit {i}: {parsed['unit_key']} → {parsed['district']}")
            print(f"   Original town issue should be fixed")
        else:
            print(f"\n❌ Unit {i}: Failed to parse")
    
    # Show parsing statistics
    stats = parser.get_parsing_stats()
    print(f"\n📊 Parsing Statistics:")
    print(f"   Total processed: {stats['total_processed']}")
    print(f"   Successfully parsed: {stats['successfully_parsed']}")
    print(f"   Excluded non-HNE: {stats['excluded_non_hne']}")
    
    for method, count in stats['town_extraction_methods'].items():
        if count > 0:
            print(f"   {method}: {count}")

if __name__ == "__main__":
    main()