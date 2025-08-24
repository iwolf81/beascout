#!/usr/bin/env python3
"""
Extract ALL units from HTML for manual verification of meeting info patterns
"""
import re
from bs4 import BeautifulSoup
import json

def format_meeting_location(raw_location):
    """Format meeting location with proper comma separators"""
    # Expected format: Building Name, Street Address, City State ZIP
    
    # Remove extra spaces and normalize
    location = re.sub(r'\s+', ' ', raw_location.strip())
    
    # Add comma before city/state/zip pattern (e.g., "Littleton MA 01460")
    location = re.sub(r'([^,\s])\s*([A-Z][a-z]+\s+[A-Z]{2}\s+\d{5})', r'\1, \2', location)
    
    # Add comma and space between building name and street address
    # Handle two patterns: Building Name + Street Address OR Street Address + Building Name
    
    # Pattern 1: Building name followed by street number (Building NameSTREET)
    location = re.sub(r'([A-Za-z][A-Za-z\s\'&.-]+[A-Za-z])(\d+\s+[A-Za-z\s]+(?:St|Street|Rd|Road|Ave|Avenue|Ln|Lane|Dr|Drive|Blvd|Boulevard|Way|Place|Court|Ct))', r'\1, \2', location)
    
    # Pattern 2: Street address followed by building name (435 Central StreetSt. Matthew's Church)
    location = re.sub(r'(\d+\s+[A-Za-z\s]+(?:St|Street|Rd|Road|Ave|Avenue|Ln|Lane|Dr|Drive|Blvd|Boulevard|Way|Place|Court|Ct))([A-Z][A-Za-z\s\'&.-]+)', r'\1, \2', location)
    
    # Fix cases where comma exists but no space after it
    location = re.sub(r',(\d)', r', \1', location)
    
    return location

def format_meeting_time(time_str):
    """Format meeting time consistently"""
    if not time_str:
        return ""
    
    # Clean up common issues
    time_str = time_str.replace('.', '').strip()
    
    # Handle 3-4 digit times (e.g., "330" -> "3:30", "1230" -> "12:30")
    digit_match = re.match(r'^(\d{3,4})\s*([ap])\.?m?\.?$', time_str, re.IGNORECASE)
    if digit_match:
        digits = digit_match.group(1)
        am_pm = digit_match.group(2)
        if len(digits) == 3:
            hour = digits[0]
            minute = digits[1:]
        else:  # len(digits) == 4
            hour = digits[:2]
            minute = digits[2:]
        time_str = f"{hour}:{minute} {am_pm}M"
    
    # Convert to standard format - check for already formatted times first
    if not re.search(r'\d{1,2}:\d{2}\s*[ap]m', time_str, re.IGNORECASE):
        time_str = re.sub(r'(\d{1,2}):(\d{2})\s*([ap])\.?m?\.?', r'\1:\2 \3M', time_str, flags=re.IGNORECASE)
        time_str = re.sub(r'(\d{1,2})\s*([ap])\.?m?\.?', r'\1:00 \2M', time_str, flags=re.IGNORECASE)
    
    return time_str.upper()

def extract_town_from_address(meeting_location):
    """Extract town name from meeting location address
    
    Most reliable method - uses actual meeting location
    """
    if not meeting_location:
        return ""
    
    # Common patterns for addresses ending with town and state/zip
    address_patterns = [
        r',\s*([A-Za-z\s]+)\s+MA\s+\d{5}',  # ", Town MA 12345"
        r',\s*([A-Za-z\s]+)\s+MA',           # ", Town MA"
        r',\s*([A-Za-z\s]+)\s*$',            # ", Town" at end
    ]
    
    for pattern in address_patterns:
        match = re.search(pattern, meeting_location)
        if match:
            return match.group(1).strip()
    
    return ""

def extract_town_from_org(chartered_org):
    """Extract town name from chartered organization field
    
    Handles two main formats:
    1. "Town-Organization Name" (e.g., "Acton-Congregational Church")
    2. "Organization Name" with town in name (e.g., "Maynard Rod and Gun Club")
    
    Note: This method is less reliable than address-based extraction
    """
    if not chartered_org:
        return ""
    
    # Method 1: Dash-based extraction (most reliable)
    if '-' in chartered_org:
        town = chartered_org.split('-')[0].strip()
        return town
    
    # Method 2: Search for HNE town names in organization
    # Import HNE towns data
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from extract_hne_towns import get_hne_towns_and_zipcodes
        hne_towns, _ = get_hne_towns_and_zipcodes()
        
        org_lower = chartered_org.lower()
        
        # Look for town names in the organization name
        # Sort by length (longest first) to match "West Boylston" before "Boylston"
        sorted_towns = sorted(hne_towns, key=len, reverse=True)
        
        for town in sorted_towns:
            # Avoid matching names that are part of historical figures
            # e.g., "Joseph Warren" should not match "Warren" the town
            town_lower = town.lower()
            if town_lower in org_lower:
                # Additional check: make sure it's not part of a person's name
                # Look for patterns like "FirstName TownName" which indicate a person
                if re.search(rf'\b[A-Z][a-z]+\s+{re.escape(town)}\b', chartered_org):
                    continue  # Skip this match - likely a person's name
                return town
        
    except ImportError:
        pass  # Fallback if HNE towns data not available
    
    # Method 3: Common patterns for non-HNE towns
    org_lower = chartered_org.lower()
    common_towns = ['stow', 'concord', 'maynard', 'sudbury', 'westford', 'chelmsford', 
                   'hudson', 'marlborough', 'wayland', 'carlisle']
    
    for town in common_towns:
        if town in org_lower:
            return town.title()
    
    # Could not determine town
    return ""

def parse_crew_specialty(primary_id, chartered_org):
    """Parse specialty from Crew primary identifier"""
    if 'Specialty:' not in primary_id:
        return chartered_org, ""
    
    # Split at "Specialty:" and extract components
    parts = primary_id.split('Specialty:')
    if len(parts) >= 2:
        # Clean up chartered org (remove specialty part)
        clean_org = parts[0].strip()
        # Remove unit info from org name
        clean_org = re.sub(r'^(Crew|Pack|Troop)\s+\d+\s+', '', clean_org).strip()
        
        # Extract specialty
        specialty = parts[1].strip()
        return clean_org, specialty
    
    return chartered_org, ""

def extract_unit_fields(wrapper, index, unit_name_elem=None):
    """Extract all possible fields from a unit wrapper"""
    unit_data = {
        'index': index,
        'primary_identifier': '',
        'unit_type': '',
        'unit_number': '',
        'unit_town': '',  # New field for extracted town name
        'chartered_organization': '',
        'specialty': '',
        'meeting_location': '',
        'meeting_day': '',
        'meeting_time': '',
        'contact_email': '',
        'contact_person': '',
        'phone_number': '',
        'website': '',
        'description': '',
        'unit_composition': '',
        'distance': '',
        'raw_content': ''
    }
    
    try:
        # Use the provided unit_name_elem for more accurate pairing
        if unit_name_elem:
            h5_elem = unit_name_elem.find('h5')
            if h5_elem:
                full_name = h5_elem.get_text(separator=' ').replace('\n', ' ').strip()
                unit_data['primary_identifier'] = full_name
                
                # Parse unit type, number, and organization
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    unit_data['unit_type'] = name_parts[0]
                    unit_data['unit_number'] = name_parts[1]
                    if len(name_parts) > 2:
                        chartered_org = ' '.join(name_parts[2:])
                        
                        # Extract town name from chartered organization
                        unit_data['unit_town'] = extract_town_from_org(chartered_org)
                        
                        # Handle Crew specialty parsing
                        if unit_data['unit_type'] == 'Crew':
                            clean_org, specialty = parse_crew_specialty(full_name, chartered_org)
                            unit_data['chartered_organization'] = clean_org
                            unit_data['specialty'] = specialty
                        else:
                            unit_data['chartered_organization'] = chartered_org
        
        # Extract distance
        if unit_name_elem:
            row = unit_name_elem.find_parent('div', class_='row')
            if row:
                distance_elem = row.find('div', class_='unit-miles')
                if distance_elem:
                    distance_text = distance_elem.get_text(strip=True)
                    unit_data['distance'] = distance_text.split()[0] + ' miles'
        
        # Extract from card-body container
        unit_body = wrapper.find('div', class_='unit-body')
        if not unit_body:
            unit_body = wrapper
        
        # Contact email
        email_links = unit_body.find_all('a', href=re.compile(r'mailto:'))
        if email_links:
            email_href = email_links[0].get('href', '')
            unit_data['contact_email'] = email_href.replace('mailto:', '')
        
        # Contact person - look for text near "Contact:"
        contact_labels = unit_body.find_all(text=re.compile(r'Contact:', re.IGNORECASE))
        for label in contact_labels:
            next_element = label.parent.next_sibling
            if next_element and hasattr(next_element, 'get_text'):
                contact_text = next_element.get_text(strip=True)
                if contact_text and not re.match(r'^[\s\n]*$', contact_text):
                    unit_data['contact_person'] = contact_text
                    break
        
        # Phone number - look for phone patterns and format consistently
        phone_links = unit_body.find_all('a', href=re.compile(r'tel:'))
        if phone_links:
            phone_text = phone_links[0].get_text(strip=True)
            # Extract just the digits
            digits = re.sub(r'[^\d]', '', phone_text)
            # Format as (XXX) XXX-XXXX if we have 10 digits
            if len(digits) == 10:
                unit_data['phone_number'] = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                unit_data['phone_number'] = phone_text
        
        # Website - exclude online registration and generic URLs
        website_links = unit_body.find_all('a', href=re.compile(r'^https?://'))
        for link in website_links:
            href = link.get('href', '')
            # Skip mailto, tel, and online registration links
            if ('mailto:' not in href and 'tel:' not in href and 
                'OnlineReg' not in href and 'my.scouting.org' not in href):
                unit_data['website'] = href
                break
        
        # Description - usually in a larger text block
        desc_container = unit_body.find('div', class_='unit-description')
        if not desc_container:
            # Look for any div or p with substantial text content
            text_containers = unit_body.find_all(['div', 'p'])
            for container in text_containers:
                text = container.get_text(strip=True)
                if len(text) > 50:  # Substantial text
                    unit_data['description'] = text
                    break
        else:
            unit_data['description'] = desc_container.get_text(strip=True)
        
        # Unit composition (Boy Troop, Girl Troop, etc.)
        composition_elem = unit_body.find(text=re.compile(r'(Boy|Girl|Boys|Girls|Coed)'))
        if composition_elem:
            # Get the parent element's text
            parent_text = composition_elem.parent.get_text(strip=True)
            if 'Troop' in parent_text or 'Pack' in parent_text or 'Crew' in parent_text:
                unit_data['unit_composition'] = parent_text
        
        # Meeting info extraction from description - prioritize over address extraction
        if unit_data['description']:
            day, time, location = extract_meeting_info(unit_data['description'])
            if day:
                unit_data['meeting_day'] = day
            if time:
                unit_data['meeting_time'] = time
            if location:
                unit_data['meeting_location'] = location
        
        # Meeting location from address - only if not already found in description
        if not unit_data['meeting_location']:
            address_containers = unit_body.find_all('div', class_='unit-address')
            raw_location = ""
            
            if address_containers:
                raw_location = address_containers[0].get_text(strip=True)
            else:
                # Look for address patterns in text
                full_text = unit_body.get_text()
                address_patterns = [
                    r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd)[^,]*',
                    r'[A-Za-z\s]+\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd)[^,]*'
                ]
                for pattern in address_patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        raw_location = match.group().strip()
                        break
            
            if raw_location and not re.match(r'(?i)p\.?o\.?\s*box', raw_location):
                # Check if location starts with unit number (invalid pattern)
                unit_num = unit_data.get('unit_number', '')
                if unit_num and raw_location.startswith(unit_num):
                    # Invalid location - likely just unit number + org name
                    unit_data['meeting_location'] = ""
                else:
                    # Format location with proper separators
                    formatted_location = format_meeting_location(raw_location)
                    unit_data['meeting_location'] = formatted_location
        
        # Extract town name - prioritize meeting location address over organization name
        if not unit_data.get('unit_town'):
            # Method 1: Extract from meeting location address (most reliable)
            if unit_data.get('meeting_location'):
                town_from_address = extract_town_from_address(unit_data['meeting_location'])
                if town_from_address:
                    unit_data['unit_town'] = town_from_address
            
            # Method 2: Fallback to organization name extraction (less reliable)
            if not unit_data.get('unit_town') and unit_data.get('chartered_organization'):
                town_from_org = extract_town_from_org(unit_data['chartered_organization'])
                if town_from_org:
                    unit_data['unit_town'] = town_from_org
        
        # Raw content for debugging
        unit_data['raw_content'] = wrapper.get_text()[:200] + "..."
        
    except Exception as e:
        print(f"Error processing unit {index}: {e}")
        unit_data['raw_content'] = f"Error: {e}"
    
    return unit_data

def extract_meeting_info(description):
    """Extract meeting day, time, and location from description text"""
    day = ""
    time = ""
    location = ""
    
    # Meeting day patterns - enhanced to capture more variations including abbreviations
    day_patterns = [
        r'meets?\s+(?:most\s+)?(?:on\s+)?([A-Za-z]+day)s?',  # "meets most Wednesdays"
        r'([A-Za-z]+day)s?\s+(?:at|from|nights?)',  # "Wednesday nights", "Mondays at"
        r'(?:every\s+)?([A-Za-z]+day)\s+(?:night|evening)',  # "every Monday night"
        r'(?:first|second|third|fourth|1st|2nd|3rd|4th|last)\s+(?:and\s+(?:second|third|fourth|2nd|3rd|4th)\s+)?([A-Za-z]+day)',  # "1st & 3rd Tuesday"
        r'([A-Za-z]+day)s?\s+\d{1,2}:\d{2}',  # "Monday 7:00"
        r'\d{1,2}:\d{2}\s*[ap]?m?\s*([A-Za-z]+day)s?',  # "7pm Tuesdays", "6:30 PM Wednesdays"
        r'(?:meet|meets)\s+\d{1,2}[ap]?m?\s*([A-Za-z]+day)s?',  # "Meet 7pm Tuesdays"
        # Day abbreviations - capture and expand to full day names
        r'(?:every\s+)?(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.?\s+(?:night|evening)',  # "every Tue. night"
        r'(?:meet|meets)\s+(?:every\s+)?(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.?',  # "Meet every Tues."
        r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.?\s+(?:night|evening)',  # "Tues. night"
        r'(Tues|Thurs)\.?',  # Common abbreviations "Tues." or "Thurs."
    ]
    
    # Meeting time patterns - enhanced for more formats
    time_patterns = [
        r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*([ap])\.?m?\.?',  # "7:00 - 8:30 p.m."
        r'(\d{1,2}:\d{2})\s*([ap])\.?m?\.?\s*-\s*(\d{1,2}:\d{2})\s*([ap])\.?m?\.?',  # "6:30 p.m. - 8:00 p.m."
        r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})',  # "7:00 - 8:30" (full time range, no AM/PM)
        r'(?:\s|,)\s*(\d{1,2})\s*-\s*(\d{1,2}:\d{2})',  # " 7 - 8:30" (simple time range after space/comma)
        r'(?:at\s+)?(\d{1,2}:\d{2})\s*([ap])\.?m?\.?',  # "at 6:30pm", "7:00 PM"
        r'(?:at\s+)?(\d{3,4})\s*([ap])\.?m?\.?',  # "at 330pm", "1230 PM" (3-4 digit times)
        r'(?:at\s+)?(\d{1,2})\s*([ap])\.?m?\.?',  # "at 7pm"
        r'(?:from\s+)?(\d{1,2}:\d{2})\s*(?:to\s+(\d{1,2}:\d{2}))?\s*([ap])\.?m?\.?',  # "from 7:00 to 8:30 PM"
    ]
    
    # Extract day
    for pattern in day_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            day_match = match.group(1).capitalize()
            
            # Expand common abbreviations to full day names
            abbreviation_map = {
                'Mon': 'Monday',
                'Tue': 'Tuesday', 
                'Tues': 'Tuesday',
                'Wed': 'Wednesday',
                'Thu': 'Thursday',
                'Thurs': 'Thursday', 
                'Fri': 'Friday',
                'Sat': 'Saturday',
                'Sun': 'Sunday'
            }
            
            # Use full day name if abbreviation found, otherwise keep original
            day = abbreviation_map.get(day_match, day_match)
            break
    
    # Extract time - handle various formats and clean up
    for pattern in time_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            groups = match.groups()
            # Handle different pattern types based on number of groups
            if len(groups) == 2 and ':' in groups[0] and ':' in groups[1]:
                # Full time range without AM/PM: "7:00 - 8:30"
                # Assume PM for evening times (6 PM or later)
                start_hour = int(groups[0].split(':')[0])
                ampm = "PM" if start_hour >= 6 else "AM"
                time = f"{groups[0]} {ampm} - {groups[1]} {ampm}"
            elif len(groups) == 2 and ':' in groups[1] and ':' not in groups[0]:
                # Simple range like "7 - 8:30" - assume PM if in evening range
                start_hour = int(groups[0])
                time1 = f"{start_hour}:00 PM" if start_hour >= 6 else f"{start_hour}:00 AM"
                time2 = f"{groups[1]} PM" if not groups[1].endswith('M') else groups[1]
                time = f"{time1} - {time2}"
            elif len(groups) >= 4 and groups[2] and groups[3]:  # Full range with both AM/PM
                time1 = format_meeting_time(f"{groups[0]} {groups[1]}M")
                time2 = format_meeting_time(f"{groups[2]} {groups[3]}M")
                time = f"{time1} - {time2}"
            elif len(groups) >= 3 and groups[2]:  # Range format
                time1 = format_meeting_time(f"{groups[0]} {groups[2]}M")
                time2 = format_meeting_time(f"{groups[1]} {groups[2]}M")
                time = f"{time1} - {time2}"
            elif len(groups) >= 2 and groups[1]:  # Single time with AM/PM
                time = format_meeting_time(f"{groups[0]} {groups[1]}M")
            else:
                time = format_meeting_time(groups[0])
            break
    
    return day, time, location

def deduplicate_units(units):
    """Remove duplicate units based on primary identifier"""
    seen_identifiers = set()
    unique_units = []
    
    for unit in units:
        identifier = unit['primary_identifier']
        if identifier and identifier not in seen_identifiers:
            seen_identifiers.add(identifier)
            unique_units.append(unit)
    
    return unique_units

def main():
    html_file = 'data/raw/debug_page_01720.html'
    
    with open(html_file, 'r') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all unit containers
    unit_wrappers = soup.find_all('div', class_='card-body')
    unit_names = soup.find_all('div', class_='unit-name')
    
    print(f"Found {len(unit_wrappers)} unit containers")
    print(f"Found {len(unit_names)} unit names")
    
    # Extract all units
    all_units = []
    for i, wrapper in enumerate(unit_wrappers):
        unit_name_elem = unit_names[i] if i < len(unit_names) else None
        unit_data = extract_unit_fields(wrapper, i, unit_name_elem)
        all_units.append(unit_data)
    
    # Deduplicate
    unique_units = deduplicate_units(all_units)
    print(f"After deduplication: {len(unique_units)} unique units")
    
    # Save all units to JSON
    output_data = {
        'total_units': len(unique_units),
        'all_units': unique_units
    }
    
    with open('data/raw/all_units_01720.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved all {len(unique_units)} units to data/raw/all_units_01720.json")

if __name__ == "__main__":
    main()