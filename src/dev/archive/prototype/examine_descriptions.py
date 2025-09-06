#!/usr/bin/env python3
"""
Examine all unit descriptions to manually verify meeting info extraction patterns
"""
import json
import re

def load_analysis_data():
    """Load the analysis JSON data"""
    with open('data/raw/all_units_01720.json', 'r') as f:
        return json.load(f)

def analyze_descriptions():
    """Examine all descriptions for meeting information patterns"""
    data = load_analysis_data()
    
    print(f"Examining descriptions from {data['total_units']} units\n")
    print("=" * 80)
    
    # Counters
    has_meeting_info = 0
    has_day_only = 0
    has_time_only = 0
    has_both = 0
    
    # Patterns to look for
    day_keywords = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 
                   'meets', 'meeting', 'gather', 'assemble']
    time_keywords = ['pm', 'am', ':', 'p.m.', 'a.m.', 'evening', 'afternoon', 'morning', 'noon']
    
    for i, unit in enumerate(data['all_units']):
        unit_id = unit['primary_identifier']
        description = unit.get('description', '').lower()
        extracted_day = unit.get('meeting_day', '')
        extracted_time = unit.get('meeting_time', '')
        
        # Check if description contains potential meeting info
        has_day_words = any(keyword in description for keyword in day_keywords)
        has_time_words = any(keyword in description for keyword in time_keywords)
        
        # Print units with potential meeting info
        if has_day_words or has_time_words or extracted_day or extracted_time:
            print(f"\n[{i:2d}] {unit_id}")
            print(f"     Extracted Day: '{extracted_day}'")
            print(f"     Extracted Time: '{extracted_time}'")
            print(f"     Description: {unit.get('description', 'N/A')}")
            print(f"     Has day words: {has_day_words}, Has time words: {has_time_words}")
            
            has_meeting_info += 1
            if extracted_day and not extracted_time:
                has_day_only += 1
            elif extracted_time and not extracted_day:
                has_time_only += 1
            elif extracted_day and extracted_time:
                has_both += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"Units with potential meeting info: {has_meeting_info}/{data['total_units']}")
    print(f"Successfully extracted day only: {has_day_only}")
    print(f"Successfully extracted time only: {has_time_only}")  
    print(f"Successfully extracted both: {has_both}")
    print(f"Total successful extractions: {has_day_only + has_time_only + has_both}")

if __name__ == "__main__":
    analyze_descriptions()