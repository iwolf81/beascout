#!/usr/bin/env python3
"""
Compare different approaches for meeting info extraction
"""
import json
import re
from datetime import datetime
# import dateutil.parser as dateparser  # Not available, skip for now

def test_with_sample_descriptions():
    """Test different extraction approaches on sample descriptions"""
    
    # Sample descriptions from our data
    test_cases = [
        "Pack meetings are the first Friday of the month at 6:30pm. Visitors are always welcome!",
        "Meets most Wednesdays 7:00 - 8:30 p.m. when school is in session.",
        "We meet on Wednesday nights from 7:00 - 8:30 At the United Church of Christ, Boxborough",
        "Meet every Tues. night from 6:30 p.m. to 8:00 p.m., Sept. thru June, excluding school vacations.",
        "Troop meetings are on Thursday's 7:00-8:30pm at FPCU. Visitors always welcome!",
        "Boy Scout Troop 195 was founded in 1995. We meet on Tuesdays (when school is in) from 7pm - 8.30pm.",
        "Crew 23 meets on the 2nd & 4th Tuesday of each month, at 6:45pm.",
        "Pack meets approx once per month on Sundays at 330 PM.",
    ]
    
    print("=== EXTRACTION APPROACH COMPARISON ===\n")
    
    for i, description in enumerate(test_cases):
        print(f"[{i}] {description}")
        
        # 1. Current regex approach
        regex_result = extract_with_regex(description)
        print(f"    Regex:    {regex_result}")
        
        # 2. NLP/dateutil approach  
        nlp_result = extract_with_nlp(description)
        print(f"    NLP:      {nlp_result}")
        
        # 3. Hybrid approach
        hybrid_result = extract_with_hybrid(description)
        print(f"    Hybrid:   {hybrid_result}")
        
        print()

def extract_with_regex(description):
    """Current regex-based approach"""
    day = ""
    time = ""
    location = ""
    
    # Simplified day patterns for testing
    day_patterns = [
        r'(?:first|second|third|fourth|last|\d+(?:st|nd|rd|th))\s+(?:&\s*\d+(?:st|nd|rd|th)\s+)?([A-Za-z]+day)',
        r'meets?\s+(?:most\s+)?(?:on\s+)?([A-Za-z]+day)s?',
        r'([A-Za-z]+day)s?\s+(?:at|from|night)',
        r'(Mon|Tue|Tues|Wed|Thu|Thurs|Fri|Sat|Sun)\.?\s+(?:night|\d)',
    ]
    
    for pattern in day_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            day = match.group(1).capitalize()
            # Expand abbreviations
            expansions = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Tues': 'Tuesday',
                         'Wed': 'Wednesday', 'Thu': 'Thursday', 'Thurs': 'Thursday', 
                         'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
            day = expansions.get(day, day)
            break
    
    # Simplified time patterns
    time_patterns = [
        r'(\d{1,2}(?::\d{2})?)\s*[-–]\s*(\d{1,2}:\d{2})\s*([ap]\.?m\.?)?',
        r'(?:at\s+)?(\d{1,2}:\d{2})\s*([ap]\.?m\.?)',
        r'(?:at\s+)?(\d{1,4})\s*([ap]\.?m\.?)',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match and match.group(1):
            if match.lastindex >= 2 and match.group(2) and not match.group(2).lower().startswith(('a', 'p')):
                # Range
                time = f"{match.group(1)} - {match.group(2)}"
                if match.lastindex >= 3 and match.group(3):
                    time += f" {match.group(3)}"
            else:
                # Single time
                time = match.group(1)
                if match.lastindex >= 2 and match.group(2):
                    time += f" {match.group(2)}"
            break
    
    return {"day": day, "time": time, "location": location}

def extract_with_nlp(description):
    """NLP-based approach using dateutil and simple heuristics"""
    day = ""
    time = ""
    location = ""
    
    # Day extraction with word matching
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_abbrevs = {'mon': 'Monday', 'tue': 'Tuesday', 'tues': 'Tuesday', 
                   'wed': 'Wednesday', 'thu': 'Thursday', 'thurs': 'Thursday',
                   'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday'}
    
    desc_lower = description.lower()
    for day_name in days:
        if day_name in desc_lower:
            day = day_name.capitalize()
            break
    
    # Check abbreviations
    if not day:
        for abbrev, full_name in day_abbrevs.items():
            if abbrev in desc_lower:
                day = full_name
                break
    
    # Time extraction using regex (simpler patterns)
    time_matches = re.findall(r'\d{1,2}(?::\d{2})?\s*(?:-|to)\s*\d{1,2}(?::\d{2})?\s*[ap]\.?m\.?|\d{1,2}(?::\d{2})?\s*[ap]\.?m\.?', description, re.IGNORECASE)
    if time_matches:
        time = time_matches[0]
    
    # Location extraction (very basic)
    location_keywords = ['at', 'church', 'school', 'center', 'hall', 'club']
    for keyword in location_keywords:
        pattern = rf'{keyword}\s+([A-Za-z\s]+?)(?:\.|,|$)'
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            break
    
    return {"day": day, "time": time, "location": location}

def extract_with_hybrid(description):
    """Hybrid approach combining regex precision with NLP flexibility"""
    day = ""
    time = ""
    location = ""
    
    # Use regex for precise patterns first
    regex_result = extract_with_regex(description)
    
    # Fall back to NLP approach for missed items
    nlp_result = extract_with_nlp(description)
    
    # Combine results (prefer regex when available)
    day = regex_result["day"] or nlp_result["day"]
    time = regex_result["time"] or nlp_result["time"]
    location = regex_result["location"] or nlp_result["location"]
    
    return {"day": day, "time": time, "location": location}

if __name__ == "__main__":
    test_with_sample_descriptions()