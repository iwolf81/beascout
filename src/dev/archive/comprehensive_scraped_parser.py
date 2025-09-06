#!/usr/bin/env python3
"""
Comprehensive Scraped Data Parser
Processes all available scraped JSON files to create complete scraped unit registry
Matches Key Three parsing sophistication for reliable cross-referencing
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import glob

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.parsing.fixed_scraped_data_parser import FixedScrapedDataParser

class ComprehensiveScrapedParser:
    """
    Processes all scraped data files to create comprehensive unit registry
    Handles deduplication and provides statistics across all sources
    """
    
    def __init__(self):
        self.parser = FixedScrapedDataParser()
        self.all_units = []
        self.file_stats = {}
        
    def process_all_scraped_files(self, pattern: str = "data/raw/all_units_*.json") -> List[Dict[str, Any]]:
        """
        Process all scraped JSON files matching the pattern
        
        Args:
            pattern: Glob pattern for scraped files
            
        Returns:
            List of all parsed units from all files
        """
        # Find all matching files
        scraped_files = glob.glob(pattern)
        
        # Filter out scored files and other processed files
        raw_files = [f for f in scraped_files if not any(skip in f for skip in [
            '_scored', '_final', '_authoritative', '_parsed', '_comprehensive'
        ])]
        
        print(f"🔍 Found {len(raw_files)} scraped data files to process")
        
        all_units = []
        unit_keys_seen = set()  # For deduplication
        
        for file_path in sorted(raw_files):
            zip_code = self._extract_zip_from_filename(file_path)
            
            units = self.parser.parse_json_file(file_path)
            
            # Deduplicate units (same unit might appear in multiple zip codes)
            unique_units = []
            duplicates = 0
            
            for unit in units:
                unit_key = unit.get('unit_key')
                if unit_key and unit_key not in unit_keys_seen:
                    unit_keys_seen.add(unit_key)
                    unique_units.append(unit)
                else:
                    duplicates += 1
            
            all_units.extend(unique_units)
            
            # Track per-file statistics
            self.file_stats[zip_code] = {
                'file_path': file_path,
                'total_units': len(units),
                'unique_units': len(unique_units),
                'duplicates': duplicates
            }
            
            print(f"  📁 {zip_code}: {len(units)} units ({len(unique_units)} unique, {duplicates} duplicates)")
        
        self.all_units = all_units
        
        print(f"\n📊 Comprehensive Parsing Results:")
        print(f"   Files processed: {len(raw_files)}")
        print(f"   Total unique units: {len(all_units)}")
        
        return all_units
    
    def _extract_zip_from_filename(self, file_path: str) -> str:
        """Extract ZIP code from filename like 'all_units_01720.json'"""
        import re
        match = re.search(r'all_units_(\d{5})\.json', file_path)
        return match.group(1) if match else Path(file_path).stem
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive parsing statistics"""
        base_stats = self.parser.get_parsing_stats()
        
        # Add file-level stats
        total_files = len(self.file_stats)
        total_raw_units = sum(stats['total_units'] for stats in self.file_stats.values())
        total_duplicates = sum(stats['duplicates'] for stats in self.file_stats.values())
        
        # District distribution
        district_counts = {}
        for unit in self.all_units:
            district = unit.get('district', 'Unknown')
            district_counts[district] = district_counts.get(district, 0) + 1
        
        return {
            **base_stats,
            'file_stats': {
                'files_processed': total_files,
                'total_raw_units': total_raw_units,
                'unique_units': len(self.all_units),
                'duplicates_removed': total_duplicates
            },
            'district_distribution': district_counts,
            'per_zip_stats': self.file_stats
        }
    
    def save_comprehensive_results(self, output_path: str = 'data/raw/scraped_units_comprehensive.json'):
        """Save comprehensive parsing results"""
        output_data = {
            'total_unique_units': len(self.all_units),
            'scraped_units': self.all_units,
            'parsing_stats': self.get_comprehensive_stats(),
            'data_sources': list(self.file_stats.keys())
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved comprehensive results to: {output_path}")
        return output_path

def main():
    """Process all scraped data files comprehensively"""
    
    print("🚀 Comprehensive Scraped Data Processing")
    
    parser = ComprehensiveScrapedParser()
    
    # Process all scraped files
    units = parser.process_all_scraped_files()
    
    if not units:
        print("❌ No units parsed from scraped data")
        return
    
    # Get comprehensive statistics
    stats = parser.get_comprehensive_stats()
    
    print(f"\n📈 Comprehensive Statistics:")
    print(f"   Files processed: {stats['file_stats']['files_processed']}")
    print(f"   Raw units found: {stats['file_stats']['total_raw_units']}")
    print(f"   Unique units: {stats['file_stats']['unique_units']}")
    print(f"   Duplicates removed: {stats['file_stats']['duplicates_removed']}")
    
    print(f"\n🏛️ District Distribution:")
    for district, count in stats['district_distribution'].items():
        print(f"   {district}: {count} units")
    
    print(f"\n🔍 Town Extraction Success:")
    for method, count in stats['town_extraction_methods'].items():
        if count > 0:
            percentage = (count / stats['successfully_parsed'] * 100) if stats['successfully_parsed'] > 0 else 0
            print(f"   {method}: {count} units ({percentage:.1f}%)")
    
    # Save comprehensive results
    output_file = parser.save_comprehensive_results()
    
    # Show sample units
    print(f"\n📋 Sample Parsed Units:")
    for i, unit in enumerate(units[:5], 1):
        print(f"   {i}. {unit['unit_key']} → {unit['district']}")
        print(f"      Meeting: {unit.get('meeting_day', 'N/A')} {unit.get('meeting_time', 'N/A')}")
        print(f"      Contact: {unit.get('contact_email', 'N/A')}")
    
    return output_file

if __name__ == "__main__":
    main()