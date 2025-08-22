#!/usr/bin/env python3
"""
Improved meeting information extraction with better pattern matching
"""
import re
import json

def extract_meeting_info_improved(description):
    """Extract meeting day, time, and location with improved patterns"""
    day = ""
    time = ""
    location = ""
    
    # Improved meeting day patterns
    day_patterns = [
        # "meets most Wednesdays", "meet on Tuesdays"
        r'meets?\s+(?:most\s+)?(?:on\s+)?([A-Za-z]+day)s?',  
        
        # "Wednesdays at", "Monday nights", "Thursday evenings", "Tues. night"
        r'([A-Za-z]+\.?\s*night|[A-Za-z]+day)s?\s+(?:at|from|night|evening)',
        
        # "first Friday", "fourth Tuesday", "2nd & 4th Tuesday", "3rd Friday" 
        r'(?:first|second|third|fourth|last|\d+(?:st|nd|rd|th))\s+(?:&\s*\d+(?:st|nd|rd|th)\s+)?([A-Za-z]+day)',
        
        # "Thursday's 7:00", "Monday from", "Tuesday nights"
        r'([A-Za-z]+day)\'?s?\s+(?:at\s+)?\d',
        r'([A-Za-z]+day)\s+(?:night|evening)s?',
        
        # "We meet Monday", "meet every Monday", "Meetings are on Thursday"
        r'(?:meet|meetings?\s+are)\s+(?:every\s+)?(?:on\s+)?([A-Za-z]+day)',
        
        # Shortened days: "Tues", "Wed", "Thurs"
        r'(Mon|Tue|Tues|Wed|Thu|Thurs|Fri|Sat|Sun)\.?\s+(?:night|evening|\d)',
    ]
    
    # Improved meeting time patterns  
    time_patterns = [
        # "7:00 - 8:30 p.m.", "7pm - 8.30pm", "7-8:30pm"
        r'(\d{1,2}(?::\d{2})?)\s*[-–]\s*(\d{1,2}:\d{2})\s*([ap]\.?m\.?)?',
        
        # "from 7:00 - 8:30", "from 7 - 8:30"  
        r'from\s+(\d{1,2}(?::\d{2})?)\s*[-–]\s*(\d{1,2}:\d{2})\s*([ap]\.?m\.?)?',
        
        # Single times: "6:30pm", "7:00 PM", "at 6:30"
        r'(?:at\s+)?(\d{1,2}:\d{2})\s*([ap]\.?m\.?)',
        
        # Times without colons: "7pm", "630pm"  
        r'(?:at\s+)?(\d{1,4})\s*([ap]\.?m\.?)',
        
        # "starting at 6:30 PM"
        r'starting\s+at\s+(\d{1,2}:\d{2})\s*([ap]\.?m\.?)',
    ]
    
    # Extract day using all patterns
    for pattern in day_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            day_text = match.group(1)
            
            # Expand abbreviations
            day_expansions = {
                'Mon': 'Monday', 'Tue': 'Tuesday', 'Tues': 'Tuesday',
                'Wed': 'Wednesday', 'Thu': 'Thursday', 'Thurs': 'Thursday', 
                'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'
            }
            
            # Handle "night" suffix 
            if 'night' in day_text.lower():
                day_text = day_text.replace(' night', '').replace('.', '')
                
            day_clean = day_expansions.get(day_text, day_text).capitalize()
            if day_clean.endswith('day'):
                day = day_clean
                break
    
    # Extract time using all patterns
    for pattern in time_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            if match.lastindex >= 2 and match.group(2):
                # Range format: "7:00 - 8:30" or "7 - 8:30"
                start_time = match.group(1)
                end_time = match.group(2)
                suffix = match.group(3) if match.lastindex >= 3 else ""
                
                # Ensure start time has colons
                if ':' not in start_time and len(start_time) <= 2:
                    start_time = start_time + ":00"
                
                time = f"{start_time} - {end_time}" + (f" {suffix}" if suffix else "")
            else:
                # Single time: "6:30pm"
                single_time = match.group(1)
                suffix = match.group(2) if match.lastindex >= 2 else ""
                
                # Handle times without colons (like "7pm" -> "7:00pm")
                if ':' not in single_time:
                    if len(single_time) <= 2:
                        single_time = single_time + ":00"
                    elif len(single_time) == 3:
                        single_time = single_time[0] + ":" + single_time[1:]
                    elif len(single_time) == 4:
                        single_time = single_time[:2] + ":" + single_time[2:]
                
                time = single_time + (f" {suffix}" if suffix else "")
            break
    
    return day, time, location

def test_extraction_on_all_units():
    """Test improved extraction on all units"""
    with open('data/raw/all_units_01720.json', 'r') as f:
        data = json.load(f)
    
    print("=== IMPROVED MEETING INFO EXTRACTION ===\n")
    
    improved_extractions = 0
    day_extractions = 0  
    time_extractions = 0
    both_extractions = 0
    
    for i, unit in enumerate(data['all_units']):
        unit_id = unit['primary_identifier']
        description = unit.get('description', '')
        
        # Original extraction
        original_day = unit.get('meeting_day', '')
        original_time = unit.get('meeting_time', '')
        
        # Improved extraction
        new_day, new_time, new_location = extract_meeting_info_improved(description)
        
        # Check if we improved anything
        day_improved = new_day and not original_day
        time_improved = new_time and not original_time
        
        if day_improved or time_improved or new_day or new_time:
            print(f"\n[{i:2d}] {unit_id}")
            
            if day_improved:
                print(f"     ✓ Day: '{original_day}' -> '{new_day}' [IMPROVED]")
                day_extractions += 1
            elif new_day:
                print(f"     ✓ Day: '{new_day}' [SAME]")
                
            if time_improved:
                print(f"     ✓ Time: '{original_time}' -> '{new_time}' [IMPROVED]")  
                time_extractions += 1
            elif new_time:
                print(f"     ✓ Time: '{new_time}' [SAME]")
                
            if new_day and new_time:
                both_extractions += 1
                
            if day_improved or time_improved:
                improved_extractions += 1
                print(f"     Description: {description[:100]}...")
    
    print(f"\n=== SUMMARY ===")
    print(f"Units with improved extractions: {improved_extractions}")
    print(f"Total day extractions: {day_extractions}")
    print(f"Total time extractions: {time_extractions}")
    print(f"Total both day & time: {both_extractions}")

if __name__ == "__main__":
    test_extraction_on_all_units()