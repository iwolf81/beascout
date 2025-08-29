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

    @classmethod
    def reset_debug_session(cls, source='scraped'):
        """Reset debug session for new execution"""
        if hasattr(cls, '_debug_filename'):
            delattr(cls, '_debug_filename')
        if hasattr(cls, '_discarded_debug_filename'):
            delattr(cls, '_discarded_debug_filename')
        cls._debug_source = source
    
    @classmethod
    def log_discarded_unit(cls, unit_type: str, unit_number: str, town: str, 
                          chartered_org: str, reason: str):
        """Log units that were discarded during parsing"""
        import datetime
        import os
        
        # Use same timestamp as main debug file
        if not hasattr(cls, '_discarded_debug_filename'):
            # Get timestamp from main debug file or create new one
            if hasattr(cls, '_debug_filename'):
                # Extract source and timestamp from existing debug filename
                filename_parts = cls._debug_filename.split('_')
                if len(filename_parts) >= 4:
                    source = filename_parts[-3]  # e.g., 'scraped' or 'keythree'
                    datestamp = filename_parts[-2]  # e.g., '20250827'
                    timestamp = filename_parts[-1].replace('.log', '')  # e.g., '145748'
                    full_timestamp = f'{datestamp}_{timestamp}'
                else:
                    source = getattr(cls, '_debug_source', 'scraped')
                    # Use shared timestamp from environment if available
                    shared_timestamp = os.environ.get('UNIT_DEBUG_TIMESTAMP')
                    full_timestamp = shared_timestamp if shared_timestamp else datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            else:
                source = getattr(cls, '_debug_source', 'scraped')
                # Use shared timestamp from environment if available  
                shared_timestamp = os.environ.get('UNIT_DEBUG_TIMESTAMP')
                full_timestamp = shared_timestamp if shared_timestamp else datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            cls._discarded_debug_filename = f'data/debug/discarded_unit_identifier_debug_{source}_{full_timestamp}.log'
            
            # Ensure debug directory exists
            os.makedirs('data/debug', exist_ok=True)
        
        with open(cls._discarded_debug_filename, 'a', encoding='utf-8') as f:
            f.write(f"  unit_type: '{unit_type}', ")
            f.write(f"  unit_number: '{unit_number}', ")
            f.write(f"  unit_town: '{town}', ")
            f.write(f"  chartered_org: '{chartered_org}', ")
            f.write(f"  reason: '{reason}'\n")

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

        # For unit_key, use display format (no leading zeros)
        clean_number = UnitIdentifierNormalizer.get_display_unit_number(
            UnitIdentifierNormalizer._normalize_unit_number(unit_number)
        )

        # Normalize town name (handle variations and aliases)
        clean_town = UnitIdentifierNormalizer._normalize_town_name(str(town).strip())

        return f"{clean_type} {clean_number} {clean_town}"

    @staticmethod
    def _normalize_unit_number(unit_number: str) -> str:
        """
        Normalize unit number to 4-digit format with leading zeros for consistent debugging
        
        Args:
            unit_number: Raw unit number (string or number)
            
        Returns:
            4-digit unit number with leading zeros (e.g., "0003", "0070", "1234")
        """
        # Convert to string and remove any existing leading zeros
        clean_number = str(unit_number).lstrip('0') or '0'
        
        # Pad to 4 digits with leading zeros
        return clean_number.zfill(4)
    
    @staticmethod
    def get_display_unit_number(unit_number: str) -> str:
        """
        Get display-friendly unit number with leading zeros removed
        Used for reports, emails, and user-facing output
        
        Args:
            unit_number: Normalized 4-digit unit number
            
        Returns:
            Unit number without leading zeros (e.g., "3", "70", "1234")
        """
        return str(unit_number).lstrip('0') or '0'

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
            # Standard abbreviation expansions for HNE towns
            "E Brookfield": "East Brookfield",
            "W Brookfield": "West Brookfield", 
            "N Brookfield": "North Brookfield",
            "W Boylston": "West Boylston",
            
            # Additional common variations
            "East Brookfield": "East Brookfield",  # Already correct
            "West Brookfield": "West Brookfield",  # Already correct
            "North Brookfield": "North Brookfield", # Already correct
            "West Boylston": "West Boylston",      # Already correct
            
            # Villages with separate ZIP codes - NO MAPPING to parent towns
            # These are treated as independent HNE towns for unit correlation:
            # "Fiskdale" stays "Fiskdale" (village within Sturbridge, ZIP 01518)
            # "Jefferson" stays "Jefferson" (village within Holden, ZIP 01522) 
            # "Whitinsville" stays "Whitinsville" (village within Northbridge, ZIP 01588)
            # This preserves village identity while maintaining HNE territory recognition
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
    def _extract_town_from_chartered_org(chartered_org: str) -> str:
        """
        Extract town name from chartered organization name
        
        Args:
            chartered_org: Chartered organization name
            
        Returns:
            Extracted town name or empty string if not found
        """
        if not chartered_org:
            return ""
        
        import re
        
        # Try to get HNE towns list
        try:
            from src.mapping.district_mapping import get_district_for_town
            
            # Define HNE towns (from district mapping)
            hne_towns = [
                "Ashby", "Townsend", "Pepperell", "Groton", "Ayer", "Littleton", "Acton", "Boxborough",
                "Fitchburg", "Lunenburg", "Shirley", "Harvard", "Bolton", "Berlin", "Lancaster", "Leominster",
                "Sterling", "Clinton", "West Boylston", "Boylston", "Shrewsbury", "Worcester", 
                "Holden", "Rutland", "Princeton", "Paxton", "Leicester", "Auburn", "Millbury",
                "Royalston", "Winchendon", "Ashburnham", "Gardner", "Templeton", "Phillipston", "Athol", "Orange",
                "Westminster", "Hubbardston", "Barre", "Petersham", "Hardwick", "New Braintree",
                "Oakham", "Ware", "West Brookfield", "East Brookfield", "North Brookfield", "Brookfield", "Spencer",
                "Warren", "Sturbridge", "Charlton", "Oxford", "Dudley", "Webster", "Douglas", "Sutton", "Grafton", 
                "Upton", "Northbridge", "Southbridge", "Jefferson", "Whitinsville", "Fiskdale"
            ]
            
            org_lower = chartered_org.lower()
            
            # Look for town names in the organization name
            # Sort by length (longest first) to match "West Boylston" before "Boylston"
            sorted_towns = sorted(hne_towns, key=len, reverse=True)
            
            for town in sorted_towns:
                town_lower = town.lower()
                if town_lower in org_lower:
                    # Additional check: make sure it's not part of a person's name
                    # Look for patterns like "FirstName TownName" which indicate a person
                    if re.search(rf'\b[A-Z][a-z]+\s+{re.escape(town)}\b', chartered_org):
                        continue  # Skip this match - likely a person's name
                    return town
                        
        except ImportError:
            pass  # Fallback if district mapping not available
            
        # Could not determine town
        return ""

    @staticmethod
    def create_unit_record(unit_type: str, unit_number: str, town: str,
                          chartered_org: str = "", **additional_fields) -> Dict[str, Any]:
        """
        Create standardized unit record with unit_key field

        Args:
            unit_type: Unit type
            unit_number: Unit number
            town: Town name (if empty, will be extracted from chartered_org)
            chartered_org: Chartered organization name
            **additional_fields: Additional unit data

        Returns:
            Standardized unit record dictionary
        """
        # Extract town from chartered org if town is empty
        if not town or not town.strip():
            town = UnitIdentifierNormalizer._extract_town_from_chartered_org(chartered_org)
        
        # Final check: if town is still empty after all extraction attempts, discard unit
        if not town or not town.strip():
            UnitIdentifierNormalizer.log_discarded_unit(
                unit_type, unit_number, 'Unknown', chartered_org,
                'Could not extract town'
            )
            return None
        
        # Create normalized identifier (automatically uses display format)
        unit_key = UnitIdentifierNormalizer.normalize_unit_identifier(unit_type, unit_number, town)

        # Get district assignment
        district = get_district_for_town(town)

        # Create base record structure
        record = {
            'unit_key': unit_key,
            'unit_type': unit_type.strip().capitalize(),
            'unit_number': UnitIdentifierNormalizer._normalize_unit_number(unit_number),
            'unit_town': UnitIdentifierNormalizer._normalize_town_name(town),
            'chartered_organization': chartered_org.strip() if chartered_org else "",
            'district': district,
        }

        # Add additional fields
        record.update(additional_fields)

        # Debug logging AFTER normalization with session timestamp
        import datetime
        import os

        # Use a session-based timestamp (created once per execution)
        if not hasattr(UnitIdentifierNormalizer, '_debug_filename'):
            # Use shared timestamp from environment if available (for subprocess coordination)
            import os
            shared_timestamp = os.environ.get('UNIT_DEBUG_TIMESTAMP')
            if shared_timestamp:
                timestamp = shared_timestamp
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            source = getattr(UnitIdentifierNormalizer, '_debug_source', 'scraped')
            UnitIdentifierNormalizer._debug_filename = f'data/debug/unit_identifier_debug_{source}_{timestamp}.log'

            # Ensure debug directory exists
            os.makedirs('data/debug', exist_ok=True)

        with open(UnitIdentifierNormalizer._debug_filename, 'a', encoding='utf-8') as f:
            f.write(f"  unit_type: '{record['unit_type']}', ")
            f.write(f"  unit_number: '{record['unit_number']}', ")
            f.write(f"  unit_town: '{record['unit_town']}', ")
            f.write(f"  chartered_org: '{record['chartered_organization']}'\n")

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