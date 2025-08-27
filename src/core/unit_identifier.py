#!/usr/bin/env python3
"""
Consistent Unit Identifier Normalization System
Creates standardized unit_key format across all data sources for reliable joining
Implements the architecture from Rethinking_Processing.md
"""

import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mapping.district_mapping import get_district_for_town

class UnitIdentifierNormalizer:
    """
    Standardizes unit identifiers across Key Three and scraped data sources
    Ensures consistent format for reliable data joining and deduplication
    """
    
    @staticmethod
    def normalize_unit_identifier(unit_type: str, unit_number: str, town: str) -> str:
        """
        Create consistent identifier: <unit type> <unit number> <unit town>
        
        Args:
            unit_type: Unit type (Pack, Troop, Crew, Ship, Post, Club)
            unit_number: Unit number (removes leading zeros)
            town: Town name (normalized to canonical form)
            
        Returns:
            Normalized identifier string (e.g., "Pack 3 Leominster")
        """
        # Normalize unit type (capitalize first letter)
        clean_type = str(unit_type).strip().capitalize()
        
        # Normalize unit number (remove leading zeros, keep at least '0')
        clean_number = str(unit_number).lstrip('0') or '0'
        
        # Normalize town name (handle variations and aliases)
        clean_town = UnitIdentifierNormalizer._normalize_town_name(str(town).strip())
        
        return f"{clean_type} {clean_number} {clean_town}"
    
    @staticmethod
    def _normalize_town_name(town: str) -> str:
        """
        Normalize town name to canonical form
        Handles common variations and aliases
        """
        if not town:
            return ""
            
        # Handle common abbreviations and variations
        town_map = {
            "E Brookfield": "East Brookfield",
            "W Brookfield": "West Brookfield", 
            "N Brookfield": "North Brookfield",
            "W Boylston": "West Boylston",
            "Fiskdale": "Sturbridge",  # Village mapping
        }
        
        # Direct mapping first
        if town in town_map:
            return town_map[town]
        
        # Handle case variations
        for variant, canonical in town_map.items():
            if town.lower() == variant.lower():
                return canonical
        
        return town
    
    @staticmethod
    def create_unit_record(unit_type: str, unit_number: str, town: str, 
                          chartered_org: str = "", **additional_fields) -> Dict[str, Any]:
        """
        Create standardized unit record with unit_key field
        
        Args:
            unit_type: Unit type
            unit_number: Unit number
            town: Town name
            chartered_org: Chartered organization name
            **additional_fields: Additional unit data
            
        Returns:
            Standardized unit record dictionary
        """
        # Debug logging before creating unit_key with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_filename = f'data/debug/unit_identifier_debug_{timestamp}.log'
        
        with open(debug_filename, 'a', encoding='utf-8') as f:
            f.write(f"  unit_type: '{unit_type}', ")
            f.write(f"  unit_number: '{unit_number}', ")
            f.write(f"  unit_town: '{town}', ")
            f.write(f"  chartered_org: '{chartered_org}'\n")
        
        # Create normalized identifier
        unit_key = UnitIdentifierNormalizer.normalize_unit_identifier(unit_type, unit_number, town)
        
        # Get district assignment
        district = get_district_for_town(town)
        
        # Create base record structure
        record = {
            'unit_key': unit_key,
            'unit_type': unit_type.strip().capitalize(),
            'unit_number': str(unit_number).lstrip('0') or '0',
            'unit_town': UnitIdentifierNormalizer._normalize_town_name(town),
            'chartered_organization': chartered_org.strip() if chartered_org else "",
            'district': district,
        }
        
        # Add additional fields
        record.update(additional_fields)
        
        return record
    
    @staticmethod
    def extract_components_from_identifier(identifier: str) -> Optional[Dict[str, str]]:
        """
        Extract components from various identifier formats
        Handles both primary identifiers and unit keys
        
        Args:
            identifier: Unit identifier string
            
        Returns:
            Dictionary with extracted components or None if parsing fails
        """
        if not identifier:
            return None
        
        # Handle primary identifier format: "Pack 0001 Acton-The Church of The Good Shepherd"
        primary_pattern = r'^(Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)\s+(.+?)(?:-(.+))?$'
        match = re.match(primary_pattern, identifier.strip())
        
        if match:
            unit_type = match.group(1)
            unit_number = match.group(2)
            town_org = match.group(3)
            extra_org = match.group(4) if match.group(4) else ""
            
            # For primary identifiers, town and org are combined
            # Try to extract town from the beginning
            town_match = re.match(r'^([A-Za-z\s]+)', town_org)
            town = town_match.group(1).strip() if town_match else town_org
            
            return {
                'unit_type': unit_type,
                'unit_number': unit_number,
                'town': town,
                'org_info': extra_org or town_org
            }
        
        # Handle unit key format: "Pack 3 Leominster"
        key_pattern = r'^(Pack|Troop|Crew|Ship|Post|Club)\s+(\d+)\s+([A-Za-z\s]+)$'
        match = re.match(key_pattern, identifier.strip())
        
        if match:
            return {
                'unit_type': match.group(1),
                'unit_number': match.group(2),
                'town': match.group(3).strip(),
                'org_info': ""
            }
        
        return None
    
    @staticmethod
    def validate_unit_key(unit_key: str) -> Dict[str, Any]:
        """
        Validate unit key format and extract validation info
        
        Args:
            unit_key: Unit key to validate
            
        Returns:
            Dictionary with validation results
        """
        components = UnitIdentifierNormalizer.extract_components_from_identifier(unit_key)
        
        if not components:
            return {
                'valid': False,
                'error': 'Could not parse unit key format',
                'components': None
            }
        
        # Check if town is recognized
        town = components.get('town', '')
        district = get_district_for_town(town)
        
        return {
            'valid': district != "Unknown",
            'error': f"Unknown town: {town}" if district == "Unknown" else None,
            'components': components,
            'district': district
        }

def main():
    """Test the unit identifier normalization system"""
    
    print("🔧 Unit Identifier Normalization System Test")
    
    # Test cases from Key Three data
    test_cases = [
        ("Pack", "0001", "Acton"),
        ("Troop", "7", "Clinton"), 
        ("Crew", "204", "West Boylston"),
        ("Ship", "375", "Groton"),
        ("Post", "2012", "Holden"),
        ("Club", "1129", "Worcester")
    ]
    
    print(f"\n📊 Normalization Test Results:")
    for unit_type, number, town in test_cases:
        unit_key = UnitIdentifierNormalizer.normalize_unit_identifier(unit_type, number, town)
        validation = UnitIdentifierNormalizer.validate_unit_key(unit_key)
        status = "✅" if validation['valid'] else "❌"
        print(f"   {status} {unit_type} {number} {town} → {unit_key} ({validation.get('district', 'Unknown')})")
    
    # Test record creation
    print(f"\n📋 Record Creation Test:")
    record = UnitIdentifierNormalizer.create_unit_record(
        "Pack", "0001", "Acton", "The Church of The Good Shepherd",
        meeting_day="Wednesday", contact_email="pack1@example.com"
    )
    
    print(f"   Unit Key: {record['unit_key']}")
    print(f"   District: {record['district']}")
    print(f"   Additional fields: {len([k for k in record.keys() if k not in ['unit_key', 'unit_type', 'unit_number', 'unit_town', 'district']])}")
    
    # Test identifier parsing
    print(f"\n🔍 Identifier Parsing Test:")
    test_identifiers = [
        "Pack 0001 Acton-The Church of The Good Shepherd",
        "Pack 3 Leominster", 
        "Troop 7001 Harvard"
    ]
    
    for identifier in test_identifiers:
        components = UnitIdentifierNormalizer.extract_components_from_identifier(identifier)
        if components:
            print(f"   ✅ {identifier}")
            print(f"      → {components['unit_type']} {components['unit_number']} {components['town']}")
        else:
            print(f"   ❌ Could not parse: {identifier}")

if __name__ == "__main__":
    main()