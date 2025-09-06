#!/usr/bin/env python3
"""
Multi-Town Data Architecture Prototype
Implements simplified unit identification: <unit_type> <unit_number> <town>

Key Innovation: Eliminates chartered organization complexity for deduplication
while maintaining it for display and Key Three matching.
"""

import json
import os
from typing import Dict, List, Set
from collections import defaultdict

class MultiTownRegistry:
    """Manages units across multiple zip codes with simplified deduplication."""
    
    def __init__(self):
        self.units_by_simple_id = {}  # "Pack 0070 Acton" -> unit_data
        self.units_by_zip = defaultdict(list)  # zip_code -> [unit_ids]
        self.duplicate_tracking = defaultdict(list)  # simple_id -> [zip_codes]
        
    def generate_simple_identifier(self, unit_data: Dict) -> str:
        """Generate simplified identifier: unit_type unit_number town"""
        unit_type = unit_data.get('unit_type', '')
        unit_number = unit_data.get('unit_number', '').lstrip('0') or '0'  # Remove leading zeros
        unit_town = unit_data.get('unit_town', '')
        
        return f"{unit_type} {unit_number} {unit_town}"
    
    def add_unit(self, unit_data: Dict, zip_code: str) -> bool:
        """
        Add unit to registry with deduplication.
        Returns True if new unit, False if duplicate.
        """
        simple_id = self.generate_simple_identifier(unit_data)
        
        # Track which zip codes this unit appears in
        self.duplicate_tracking[simple_id].append(zip_code)
        self.units_by_zip[zip_code].append(simple_id)
        
        if simple_id not in self.units_by_simple_id:
            # New unit - store it
            unit_data['simple_identifier'] = simple_id
            unit_data['found_in_zips'] = [zip_code]
            self.units_by_simple_id[simple_id] = unit_data
            return True
        else:
            # Duplicate - update zip tracking
            existing_unit = self.units_by_simple_id[simple_id]
            if zip_code not in existing_unit['found_in_zips']:
                existing_unit['found_in_zips'].append(zip_code)
            return False
    
    def get_deduplication_stats(self) -> Dict:
        """Generate statistics about deduplication across zip codes."""
        total_units = len(self.units_by_simple_id)
        total_appearances = sum(len(zips) for zips in self.duplicate_tracking.values())
        duplicates_found = total_appearances - total_units
        
        # Find units appearing in multiple zips
        multi_zip_units = {
            simple_id: zip_list 
            for simple_id, zip_list in self.duplicate_tracking.items()
            if len(zip_list) > 1
        }
        
        return {
            'total_unique_units': total_units,
            'total_appearances': total_appearances,
            'duplicates_eliminated': duplicates_found,
            'multi_zip_units': len(multi_zip_units),
            'multi_zip_details': multi_zip_units
        }
    
    def export_registry(self, output_path: str):
        """Export deduplicated registry to JSON."""
        export_data = {
            'registry_info': {
                'deduplication_method': 'unit_type + unit_number + town',
                'stats': self.get_deduplication_stats()
            },
            'units': list(self.units_by_simple_id.values())
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


def test_simplified_identifier_concept():
    """Test the simplified identifier approach with current 01720 data."""
    print("Multi-Town Data Architecture Prototype")
    print("=" * 50)
    
    # Load current test data
    data_file = 'data/raw/all_units_01720_scored.json'
    if not os.path.exists(data_file):
        print(f"❌ Test data not found: {data_file}")
        return
    
    with open(data_file, 'r') as f:
        test_data = json.load(f)
    
    registry = MultiTownRegistry()
    
    print(f"📊 Processing {test_data['total_units']} units from ZIP 01720...")
    
    # Process all units as if they came from 01720
    new_units = 0
    for unit in test_data['units_with_scores']:
        if registry.add_unit(unit, '01720'):
            new_units += 1
    
    print(f"✅ Processed {new_units} unique units")
    
    # Show identifier mapping
    print("\n📋 Simplified Identifier Examples:")
    print("Current Primary ID → Simplified ID")
    print("-" * 60)
    
    for simple_id, unit_data in list(registry.units_by_simple_id.items())[:10]:
        primary_id = unit_data['primary_identifier']
        print(f"{primary_id}")
        print(f"  → {simple_id}")
    
    # Test duplicate detection by simulating same units from different zip
    print(f"\n🔄 Testing duplicate detection...")
    print("Simulating same units from ZIP 01721...")
    
    duplicates_found = 0
    for unit in test_data['units_with_scores'][:5]:  # Test first 5 units
        if not registry.add_unit(unit, '01721'):
            duplicates_found += 1
    
    print(f"✅ Correctly identified {duplicates_found} duplicates")
    
    # Show deduplication stats
    stats = registry.get_deduplication_stats()
    print(f"\n📈 Deduplication Statistics:")
    print(f"  Unique units: {stats['total_unique_units']}")
    print(f"  Total appearances: {stats['total_appearances']}")
    print(f"  Duplicates eliminated: {stats['duplicates_eliminated']}")
    print(f"  Multi-zip units: {stats['multi_zip_units']}")
    
    # Export test registry
    output_file = 'data/raw/multi_town_registry_test.json'
    registry.export_registry(output_file)
    print(f"💾 Registry exported to: {output_file}")
    
    return registry


def analyze_current_identifiers():
    """Analyze how current primary identifiers would map to simplified ones."""
    data_file = 'data/raw/all_units_01720_scored.json'
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("🔍 Current vs Simplified Identifier Analysis")
    print("=" * 60)
    
    registry = MultiTownRegistry()
    
    identifier_comparison = []
    for unit in data['units_with_scores']:
        simple_id = registry.generate_simple_identifier(unit)
        primary_id = unit['primary_identifier']
        
        identifier_comparison.append({
            'current': primary_id,
            'simplified': simple_id,
            'unit_type': unit['unit_type'],
            'unit_number': unit['unit_number'],
            'town': unit['unit_town']
        })
    
    # Show all mappings
    for comparison in identifier_comparison:
        print(f"📋 {comparison['current']}")
        print(f"   → {comparison['simplified']}")
        print()
    
    # Check for any collisions in simplified identifiers
    simplified_ids = [c['simplified'] for c in identifier_comparison]
    unique_simplified = set(simplified_ids)
    
    if len(simplified_ids) != len(unique_simplified):
        print("⚠️  COLLISION DETECTED in simplified identifiers!")
        # Find collisions
        id_counts = {}
        for sid in simplified_ids:
            id_counts[sid] = id_counts.get(sid, 0) + 1
        
        collisions = {sid: count for sid, count in id_counts.items() if count > 1}
        print(f"Colliding identifiers: {collisions}")
    else:
        print("✅ No collisions detected - simplified approach is safe")


if __name__ == '__main__':
    # Run analysis
    analyze_current_identifiers()
    print()
    
    # Run test
    test_registry = test_simplified_identifier_concept()