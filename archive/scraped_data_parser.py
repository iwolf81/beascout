#!/usr/bin/env python3
"""
Enhanced Scraped Data Parser
Sophisticated town extraction matching Key Three parser quality
Creates consistent unit_key identifiers for reliable cross-referencing
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mapping.district_mapping import get_district_for_town
from src.core.unit_identifier import UnitIdentifierNormalizer

class ScrapedDataParser:
    """
    Advanced parser for scraped BeAScout and JoinExploring data
    Implements sophisticated town extraction from address and description fields
    """
    
    def __init__(self):
        self.parsed_units = []
        self.parsing_stats = {
            'total_processed': 0,
            'successfully_parsed': 0,
            'town_extraction_methods': {
                'address_field': 0,
                'description_parsing': 0,
                'fallback_methods': 0,
                'failed': 0
            }
        }
    
    def parse_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a scraped data JSON file
        
        Args:
            file_path: Path to JSON file containing scraped unit data
            
        Returns:
            List of parsed and normalized unit records
        """
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
                parsed_unit = self.parse_unit_record(unit)
                if parsed_unit:
                    parsed_units.append(parsed_unit)
                    self.parsing_stats['successfully_parsed'] += 1
                self.parsing_stats['total_processed'] += 1
            
            print(f"Successfully parsed {len(parsed_units)} units")
            return parsed_units
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def parse_unit_record(self, unit: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse individual unit record with sophisticated town extraction
        
        Args:
            unit: Raw unit data from scraped source
            
        Returns:
            Normalized unit record with unit_key or None if parsing fails
        """
        # Extract basic unit information
        unit_type = self._extract_unit_type(unit)
        unit_number = self._extract_unit_number(unit)
        
        if not unit_type or not unit_number:
            return None
        
        # Sophisticated town extraction
        town = self._extract_town_from_unit(unit)
        
        if not town:
            self.parsing_stats['town_extraction_methods']['failed'] += 1
            return None
        
        # Create normalized unit record
        try:
            normalized_record = UnitIdentifierNormalizer.create_unit_record(
                unit_type=unit_type,
                unit_number=unit_number,
                town=town,
                chartered_org=unit.get('chartered_organization', ''),
                # Scraped data specific fields
                data_source='Web Scraped',
                meeting_location=unit.get('meeting_location', ''),
                meeting_day=unit.get('meeting_day', ''),
                meeting_time=unit.get('meeting_time', ''),
                contact_email=unit.get('contact_email', ''),
                contact_person=unit.get('contact_person', ''),
                phone_number=unit.get('phone_number', ''),
                website=unit.get('website', ''),
                description=unit.get('description', ''),
                unit_composition=unit.get('unit_composition', ''),
                specialty=unit.get('specialty', ''),
                # Raw data preservation
                original_scraped_data=unit
            )
            
            return normalized_record
            
        except Exception as e:
            print(f"Error creating normalized record: {e}")
            return None
    
    def _extract_unit_type(self, unit: Dict[str, Any]) -> Optional[str]:
        """Extract unit type from various possible fields"""
        # Try different field names
        type_fields = ['unit_type', 'type', 'program_type']
        
        for field in type_fields:
            if field in unit and unit[field]:
                unit_type = str(unit[field]).strip()
                # Normalize unit type names
                type_map = {
                    'pack': 'Pack',
                    'troop': 'Troop', 
                    'crew': 'Crew',
                    'ship': 'Ship',
                    'post': 'Post',
                    'club': 'Club'
                }
                return type_map.get(unit_type.lower(), unit_type.capitalize())
        
        # Try to extract from primary identifier
        primary_id = unit.get('primary_identifier', '')
        if primary_id:
            match = re.match(r'^(Pack|Troop|Crew|Ship|Post|Club)', primary_id, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        
        return None
    
    def _extract_unit_number(self, unit: Dict[str, Any]) -> Optional[str]:
        """Extract unit number from various possible fields"""
        # Try different field names  
        number_fields = ['unit_number', 'number', 'unit_num']
        
        for field in number_fields:
            if field in unit and unit[field]:
                return str(unit[field]).strip()
        
        # Try to extract from primary identifier
        primary_id = unit.get('primary_identifier', '')
        if primary_id:
            match = re.match(r'^(?:Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)', primary_id, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_town_from_unit(self, unit: Dict[str, Any]) -> Optional[str]:
        """
        Sophisticated town extraction from address and description fields
        Implements multiple extraction strategies with validation
        """
        # Strategy 1: Address field parsing (highest confidence)
        town = self._extract_town_from_address(unit)
        if town and self._validate_town(town):
            self.parsing_stats['town_extraction_methods']['address_field'] += 1
            return town
        
        # Strategy 2: Description parsing  
        town = self._extract_town_from_description(unit)
        if town and self._validate_town(town):
            self.parsing_stats['town_extraction_methods']['description_parsing'] += 1
            return town
        
        # Strategy 3: Meeting location parsing
        town = self._extract_town_from_meeting_location(unit)
        if town and self._validate_town(town):
            self.parsing_stats['town_extraction_methods']['description_parsing'] += 1
            return town
        
        # Strategy 4: Chartered organization parsing
        town = self._extract_town_from_chartered_org(unit)
        if town and self._validate_town(town):
            self.parsing_stats['town_extraction_methods']['fallback_methods'] += 1
            return town
        
        # Strategy 5: Unit town field (if present)
        if 'unit_town' in unit and unit['unit_town']:
            town = str(unit['unit_town']).strip()
            if self._validate_town(town):
                self.parsing_stats['town_extraction_methods']['address_field'] += 1
                return town
        
        return None
    
    def _extract_town_from_address(self, unit: Dict[str, Any]) -> Optional[str]:
        """
        Extract town from address field
        Handles formats: "123 Main St, Acton, MA 01720"
        """
        address_fields = ['address', 'meeting_location', 'location']
        
        for field in address_fields:
            address = unit.get(field, '')
            if not address:
                continue
                
            address = str(address).strip()
            
            # Skip PO Box addresses (unreliable for town extraction)
            if 'P.O. Box' in address or 'PO Box' in address:
                continue
            
            # Pattern 1: "Street, City, State ZIP"
            match = re.match(r'^[^,]+,\s*([A-Za-z\s]+),\s*[A-Z]{2}', address)
            if match:
                potential_town = match.group(1).strip()
                return self._normalize_town_name(potential_town)
            
            # Pattern 2: "Street, City State ZIP" 
            match = re.match(r'^[^,]+,\s*([A-Za-z\s]+)\s+[A-Z]{2}', address)
            if match:
                potential_town = match.group(1).strip()
                return self._normalize_town_name(potential_town)
            
            # Pattern 3: Just "City, State" (no street)
            match = re.match(r'^([A-Za-z\s]+),\s*[A-Z]{2}', address)
            if match:
                potential_town = match.group(1).strip()
                return self._normalize_town_name(potential_town)
        
        return None
    
    def _extract_town_from_description(self, unit: Dict[str, Any]) -> Optional[str]:
        """
        Extract town from description text
        Looks for phrases like "in Acton", "Acton area", "serving Leominster"
        """
        description = unit.get('description', '')
        if not description:
            return None
        
        description = str(description)
        
        # Pattern 1: "in [Town]" or "In [Town]"
        match = re.search(r'\bin\s+([A-Za-z\s]+?)(?:\s|,|\.|\?|!|$)', description, re.IGNORECASE)
        if match:
            potential_town = match.group(1).strip()
            if len(potential_town.split()) <= 2:  # Avoid long phrases
                normalized = self._normalize_town_name(potential_town)
                if self._validate_town(normalized):
                    return normalized
        
        # Pattern 2: "[Town] area" or "[Town] community"
        match = re.search(r'([A-Za-z\s]+?)\s+(?:area|community|region)', description, re.IGNORECASE)
        if match:
            potential_town = match.group(1).strip()
            if len(potential_town.split()) <= 2:
                normalized = self._normalize_town_name(potential_town)
                if self._validate_town(normalized):
                    return normalized
        
        # Pattern 3: "serving [Town]" or "located in [Town]"
        match = re.search(r'(?:serving|located in|based in)\s+([A-Za-z\s]+?)(?:\s|,|\.|\?|!|$)', description, re.IGNORECASE)
        if match:
            potential_town = match.group(1).strip()
            if len(potential_town.split()) <= 2:
                normalized = self._normalize_town_name(potential_town)
                if self._validate_town(normalized):
                    return normalized
        
        return None
    
    def _extract_town_from_meeting_location(self, unit: Dict[str, Any]) -> Optional[str]:
        """Extract town from meeting location if it contains town name"""
        meeting_location = unit.get('meeting_location', '')
        if not meeting_location:
            return None
        
        location = str(meeting_location)
        
        # Look for known town names in the meeting location
        from src.mapping.district_mapping import TOWN_TO_DISTRICT
        
        for town in TOWN_TO_DISTRICT.keys():
            if town.lower() in location.lower():
                return town
        
        # Also check aliases
        from src.mapping.district_mapping import TOWN_ALIASES
        for alias, canonical in TOWN_ALIASES.items():
            if alias.lower() in location.lower():
                return canonical
        
        return None
    
    def _extract_town_from_chartered_org(self, unit: Dict[str, Any]) -> Optional[str]:
        """
        Extract town from chartered organization name
        Similar to Key Three parsing logic
        """
        org_name = unit.get('chartered_organization', '')
        if not org_name:
            return None
        
        org_name = str(org_name)
        
        # Pattern 1: "Town-Organization Name"
        match = re.match(r'^([A-Za-z\s]+)-(.+)$', org_name)
        if match:
            potential_town = match.group(1).strip()
            normalized = self._normalize_town_name(potential_town)
            if self._validate_town(normalized):
                return normalized
        
        # Pattern 2: Look for known towns in org name
        from src.mapping.district_mapping import TOWN_TO_DISTRICT
        
        for town in TOWN_TO_DISTRICT.keys():
            if town.lower() in org_name.lower():
                return town
        
        return None
    
    def _normalize_town_name(self, town: str) -> str:
        """Normalize town name using same rules as Key Three parser"""
        return UnitIdentifierNormalizer._normalize_town_name(town)
    
    def _validate_town(self, town: str) -> bool:
        """Validate that town is a recognized HNE Council town"""
        return get_district_for_town(town) != "Unknown"
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return self.parsing_stats.copy()

def main():
    """Test the scraped data parser"""
    parser = ScrapedDataParser()
    
    # Test with sample unit data
    sample_units = [
        {
            'primary_identifier': 'Pack 0001 Acton-The Church of The Good Shepherd',
            'unit_type': 'Pack',
            'unit_number': '0001',
            'meeting_location': '123 Main St, Acton, MA 01720',
            'contact_email': 'pack1@example.com',
            'description': 'Great pack in Acton serving the community'
        },
        {
            'unit_type': 'Troop', 
            'unit_number': '123',
            'address': '456 Oak Ave, Leominster, MA 01453',
            'meeting_day': 'Wednesday',
            'description': 'Active troop based in Leominster area'
        },
        {
            'unit_type': 'Crew',
            'unit_number': '250', 
            'meeting_location': 'Harvard Community Center',
            'chartered_organization': 'Harvard-Sportsmens Club',
            'specialty': 'HIGH ADVENTURE'
        }
    ]
    
    print("🧪 Testing Scraped Data Parser")
    
    for i, unit in enumerate(sample_units, 1):
        parsed = parser.parse_unit_record(unit)
        if parsed:
            print(f"\n✅ Unit {i}: {parsed['unit_key']} → {parsed['district']}")
            print(f"   Data source: {parsed['data_source']}")
        else:
            print(f"\n❌ Unit {i}: Failed to parse")
    
    # Show parsing statistics
    stats = parser.get_parsing_stats()
    print(f"\n📊 Parsing Statistics:")
    print(f"   Total processed: {stats['total_processed']}")
    print(f"   Successfully parsed: {stats['successfully_parsed']}")
    print(f"   Town extraction methods:")
    for method, count in stats['town_extraction_methods'].items():
        print(f"     {method}: {count}")

if __name__ == "__main__":
    main()