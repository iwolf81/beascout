#!/usr/bin/env python3
"""
Extract ALL units from HTML for manual verification of meeting info patterns
"""
import sys
from pathlib import Path

# Ensure project root is in Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import re
from bs4 import BeautifulSoup
import json

def load_location_exceptions():
    """Load location exception configuration for units without street numbers"""
    exception_file = Path(__file__).parent.parent.parent.parent / 'data/config/location_exceptions.json'
    try:
        with open(exception_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return set(config.get('units_without_street_numbers', {}).keys())
    except FileNotFoundError:
        return set()  # No exceptions if file doesn't exist
    except json.JSONDecodeError:
        print(f"Warning: Could not parse {exception_file}")
        return set()

# Cache exceptions at module level to avoid repeated file reads
_LOCATION_EXCEPTIONS = load_location_exceptions()

def check_location_exception(unit_data):
    """Check if unit is in location exception list (doesn't require street number)"""
    from src.pipeline.core.unit_identifier import UnitIdentifierNormalizer
    # Generate normalized identifier (e.g., "Troop 0123 Shirley")
    unit_key = UnitIdentifierNormalizer.normalize_unit_identifier(
        unit_data.get('unit_type', ''),
        unit_data.get('unit_number', ''),
        unit_data.get('unit_town', '')
    )
    # Convert spaces to underscores to match config file format
    unit_key_config_format = unit_key.replace(' ', '_')
    return unit_key_config_format in _LOCATION_EXCEPTIONS

def get_district_for_town(town):
    """Assign district based on town name using centralized mapping"""
    try:
        from src.pipeline.core.district_mapping import TOWN_TO_DISTRICT
    except ImportError:
        # Fallback for when called from different contexts
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent.parent))
        from src.pipeline.core.district_mapping import TOWN_TO_DISTRICT
    
    return TOWN_TO_DISTRICT.get(town, "Unknown")

def format_meeting_location(raw_location):
    """Format meeting location with proper comma separators"""
    # Expected format: Building Name, Street Address, City State ZIP
    
    # Remove extra spaces and normalize
    location = re.sub(r'\s+', ' ', raw_location.strip())
    
    # Add comma before city/state/zip pattern but handle periods properly
    # Pattern: "word Townname MA 12345" -> "word, Townname MA 12345" (but not if word ends with period)
    # First handle the normal case (no period before city/state)
    location = re.sub(r'([A-Za-z0-9])\s+([A-Z][a-z]+\s+[A-Z]{2}\s+\d{5})', r'\1, \2', location)
    # Then handle the period case: "E. Townname MA 12345" -> "E. Townname, MA 12345" 
    location = re.sub(r'(\.\s+)([A-Z][a-z]+)(\s+[A-Z]{2}\s+\d{5})', r'\1\2,\3', location)
    
    # Add comma and space between building name and street address
    # Handle two patterns: Building Name + Street Address OR Street Address + Building Name
    
    # Pattern 1: Building name followed by street number - use more specific patterns for common building types
    location = re.sub(r'([A-Za-z][A-Za-z\s\.\'&-]+(?:Church|Building|Hall|Center|School|Library))\s+(\d+\s+[A-Za-z\s]+(?:ST|St|Street|Rd|Road|Ave|Avenue|Ln|Lane|Dr|Drive|Blvd|Boulevard|Way|Place|Court|Ct))', r'\1, \2', location)
    
    # Pattern 1b: General building name pattern (fallback for other building types)
    location = re.sub(r'([A-Za-z][A-Za-z\s\'&.-]+[A-Za-z])\s+(\d+\s+[A-Za-z\s]+(?:St|Street|Rd|Road|Ave|Avenue|Ln|Lane|Dr|Drive|Blvd|Boulevard|Way|Place|Court|Ct))', r'\1, \2', location)
    
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

def extract_location_components(text, source_type='address'):
    """Universal location component extraction
    
    Extracts structured location information from any text source.
    Handles different source types with context-aware parsing.
    
    Args:
        text: Input text (unit-address, description, org name, etc.)
        source_type: 'address', 'description', 'org_name' for context-aware parsing
    
    Returns:
        dict with keys: 'full_location', 'address', 'town', 'state', 'zip'
        Returns empty values for components not found
    """
    if not text or not text.strip():
        return {
            'full_location': '',
            'address': '',
            'town': '',
            'state': '',
            'zip': ''
        }
    
    result = {
        'full_location': '',
        'address': '',
        'town': '',
        'state': '',
        'zip': ''
    }
    
    # For address and description sources, extract full location first
    if source_type in ['address', 'description']:
        # Use the same patterns from extract_address_from_text()
        location_patterns = [
            # Complete street addresses: number + street name + street type
            r'\b(\d+\s+[A-Za-z][A-Za-z\s]{2,}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Court|Ct|Place|Pl)\.?(?:\s*,?\s*[A-Za-z][A-Za-z\s]*\s*[A-Z]{0,2}\s*\d{0,5})*)',
            # Named venues with street addresses  
            r'\b([A-Z][A-Za-z][A-Za-z\s]{5,}(?:School|Church|Hall|Center|Centre|Building|Library|Post|Legion|VFW|Club|Association|Parish|Camp),?\s+\d+\s+[A-Za-z][A-Za-z\s]{2,}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr))',
            # Institutional locations with context
            r'\b(?:at\s+the\s+|meets?\s+at\s+the\s+|located\s+at\s+the\s+)([A-Z][A-Za-z][A-Za-z\s]{5,}(?:School|Church|Hall|Center|Centre|Building|Library|Station|Department))',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_location = match.group(1).strip()
                # Apply strict filtering to avoid sentence fragments
                if (len(potential_location) > 10 and
                    re.search(r'\b(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Court|Ct|Place|Pl|School|Church|Hall|Center|Centre|Building|Library|Station|Department)\b', potential_location, re.IGNORECASE) and
                    not re.search(r'\b(?:is|are|was|were|have|has|had|will|would|should|could|can|may|might|do|does|did|welcome|upcoming|chartered|located|serves|meet|when|where|what|who|why|how)\b', potential_location, re.IGNORECASE) and
                    not re.search(r'^\d+\s+(?:is|are|was|were|have|has|had|will|would|welcome|upcoming|for|with|of|in)', potential_location, re.IGNORECASE) and
                    not '@' in potential_location and
                    not re.match(r'^\d+$', potential_location) and
                    not potential_location.lower().startswith(('when ', 'where ', 'what ', 'who ', 'why ', 'how ', 'for ', 'with ', 'of '))):
                    result['full_location'] = potential_location
                    break
    
    # Extract town from full location or directly from text
    text_to_parse = result['full_location'] if result['full_location'] else text
    
    if source_type == 'org_name':
        # Organization name patterns (from extract_town_from_org)
        town_patterns = [
            r'^([A-Za-z\s]+)-',  # "Town-Organization"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:Rod and Gun|Fire|Police|American Legion|VFW|Lions|Rotary|Knights)',  # "Town Organization"
        ]
    else:
        # Address patterns (from extract_town_from_address)
        town_patterns = [
            r',\s*([A-Za-z\s]+)\s+MA\s+(\d{5})',  # ", Town MA 12345" - capture zip too
            r',\s*([A-Za-z\s]+)\s+([A-Z]{2})\s+(\d{5})',  # ", Town ST 12345" - capture state and zip
            r',\s*([A-Za-z\s]+)\s+MA',  # ", Town MA"
            r',\s*([A-Za-z\s]+)\s*$',  # ", Town" at end
        ]
    
    for pattern in town_patterns:
        match = re.search(pattern, text_to_parse)
        if match:
            result['town'] = match.group(1).strip()
            # Extract state and zip if captured
            if len(match.groups()) >= 2:
                if match.group(2).isalpha():  # State
                    result['state'] = match.group(2)
                    if len(match.groups()) >= 3:
                        result['zip'] = match.group(3)
                else:  # Zip (when state is MA)
                    result['state'] = 'MA'
                    result['zip'] = match.group(2)
            break
    
    return result

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
    
    # Skip if this looks like description text instead of an organization name
    description_indicators = [
        'we meet', 'meet on', 'meet at', 'meeting', 'active pack', 'active troop',
        'accepting children', 'established', 'dedicated to', 'contact:', 'phone:'
    ]
    
    org_lower = chartered_org.lower()
    if any(indicator in org_lower for indicator in description_indicators):
        return ""
    
    # Method 1: Dash-based extraction (most reliable for organizational names)
    if '-' in chartered_org:
        # Only use dash-based extraction for organizational naming patterns
        # Skip if this looks like a time range (e.g., "7:00pm-8:30pm") or description text
        if not re.search(r'\d{1,2}:\d{2}\s*[ap]?m?\s*-\s*\d{1,2}:\d{2}\s*[ap]?m?', chartered_org, re.IGNORECASE):
            # Also skip if the text is too long to be an organization name (likely description)
            if len(chartered_org) < 200:  # Reasonable organization name length limit
                town = chartered_org.split('-')[0].strip()
                # Check if the extracted town is an alias and resolve it
                try:
                    from src.pipeline.core.district_mapping import TOWN_ALIASES, TOWN_TO_DISTRICT
                    if town in TOWN_ALIASES:
                        canonical_town = TOWN_ALIASES[town]
                        if canonical_town in TOWN_TO_DISTRICT:
                            return canonical_town
                except ImportError:
                    pass
                return town
    
    # Method 2: Search for HNE town names in organization
    # Use centralized district mapping for HNE towns and aliases
    try:
        from src.pipeline.core.district_mapping import TOWN_TO_DISTRICT, TOWN_ALIASES
        hne_towns = list(TOWN_TO_DISTRICT.keys())
        
        org_lower = chartered_org.lower()
        
        # First check TOWN_ALIASES for abbreviated forms (e.g., "W Boylston" -> "West Boylston")
        for alias, canonical_town in TOWN_ALIASES.items():
            alias_lower = alias.lower()
            if re.search(rf'\b{re.escape(alias_lower)}\b', org_lower):
                # Verify the canonical town is actually an HNE town
                if canonical_town in TOWN_TO_DISTRICT:
                    return canonical_town
        
        # Then check full HNE town names
        # Sort by length (longest first) to match "West Boylston" before "Boylston"
        sorted_towns = sorted(hne_towns, key=len, reverse=True)
        
        for town in sorted_towns:
            # Avoid matching names that are part of historical figures
            # e.g., "Joseph Warren" should not match "Warren" the town
            town_lower = town.lower()
            # Use word boundary matching to prevent false positives like "athol" in "catholic"
            if re.search(rf'\b{re.escape(town_lower)}\b', org_lower):
                # Additional check: make sure it's not part of a person's name
                # Look for patterns like "FirstName LastName" where LastName is a town name
                # But exclude common organizational words that precede town names
                person_pattern = rf'\b[A-Z][a-z]+\s+{re.escape(town)}\b'
                if re.search(person_pattern, chartered_org):
                    # Check if it's preceded by common org words - if so, it's NOT a person
                    org_words = ['veterans', 'foreign', 'wars', 'american', 'legion', 'post', 'vfw']
                    preceding_text = chartered_org[:chartered_org.lower().find(town_lower)].lower()
                    if any(word in preceding_text for word in org_words):
                        return town  # Valid organizational context
                    else:
                        continue  # Likely a person's name
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

def filter_hne_units(units):
    """Filter units to only include those within HNE Council territory
    
    Args:
        units: List of unit dictionaries
        
    Returns:
        Filtered list containing only HNE Council units
    """
    # Load HNE towns list - CRITICAL DATA FOR TERRITORY FILTERING
    try:
        from src.pipeline.core.hne_towns import get_hne_towns_and_zipcodes
        hne_towns, _ = get_hne_towns_and_zipcodes()
        hne_towns_lower = [town.lower() for town in hne_towns]
    except ImportError as e:
        # CRITICAL FAILURE - Cannot proceed without HNE territory data
        raise RuntimeError(
            f"CRITICAL ERROR [{Path(__file__).name}]: Cannot load HNE towns data (TOWN_TO_DISTRICT mapping): {e}. "
            "This is required to filter units to HNE territory only. "
            "Without this data, non-HNE units could be included in reports. "
            "Pipeline must stop to prevent data integrity issues."
        )
    
    hne_units = []
    non_hne_units = []
    
    for unit in units:
        unit_town = unit.get('unit_town', '').lower().strip()
        chartered_org = unit.get('chartered_organization', '').lower()
        
        # Check if unit town is in HNE territory
        is_hne = False
        determined_town = unit_town  # Track the town name used for determination
        
        if unit_town:
            # Use centralized town normalization to resolve aliases
            from src.pipeline.core.unit_identifier import UnitIdentifierNormalizer
            normalized_town = UnitIdentifierNormalizer._normalize_town_name(unit_town)
            normalized_town_lower = normalized_town.lower()
            
            if normalized_town_lower in hne_towns_lower:
                # Unit town (after alias resolution) is in HNE territory
                is_hne = True
            else:
                # Unit town is clearly identified but is NOT in HNE territory
                # Do not override with chartered org matching - trust the extracted location
                is_hne = False
                determined_town = normalized_town  # Use normalized name for logging
        else:
            # No unit town identified - use chartered organization as fallback
            # Sort by length (longest first) to match "West Boylston" before "Boylston"
            sorted_towns = sorted(hne_towns, key=len, reverse=True)
            found_org_town = None
            for town in sorted_towns:
                town_lower = town.lower()
                if town_lower in chartered_org:
                    # Additional validation to avoid false positives
                    # Make sure it's a word boundary match
                    if re.search(rf'\b{re.escape(town_lower)}\b', chartered_org):
                        is_hne = True
                        found_org_town = town
                        # Update unit_town with the detected town
                        unit['unit_town'] = town
                        break
            
            # Use the already-extracted town from unified extraction
            determined_town = unit.get('unit_town', 'Unknown')
        
        if is_hne:
            hne_units.append(unit)
        else:
            # Log discarded non-HNE unit for debugging
            from src.pipeline.core.unit_identifier import UnitIdentifierNormalizer
            UnitIdentifierNormalizer.log_discarded_unit(
                unit.get('unit_type', 'Unknown'),
                unit.get('unit_number', 'Unknown'),
                unit.get('unit_town', 'Unknown'),
                unit.get('chartered_organization', 'Unknown'),
                f'Non-HNE unit filtered out (town: {determined_town})'
            )
            non_hne_units.append(unit)
    
    # Print filtering summary
    print(f"HNE Territory Filtering:")
    print(f"  HNE Council units: {len(hne_units)}")
    print(f"  Non-HNE units filtered out: {len(non_hne_units)}")
    
    if non_hne_units:
        print(f"  Filtered out units:")
        for unit in non_hne_units:
            town = unit.get('unit_town', 'Unknown')
            identifier = unit.get('primary_identifier', 'Unknown')
            print(f"    - {identifier} ({town})")
    
    return hne_units

def parse_specialty_info(primary_id, chartered_org):
    """Parse specialty from specialized unit primary identifier (Crew, Post, Club)"""
    if 'Specialty:' not in primary_id:
        return chartered_org, ""
    
    # Split at "Specialty:" and extract components
    parts = primary_id.split('Specialty:')
    if len(parts) >= 2:
        # Clean up chartered org (remove specialty part)
        clean_org = parts[0].strip()
        # Remove unit info from org name
        clean_org = re.sub(r'^(Crew|Post|Club|Pack|Troop)\s+\d+\s+', '', clean_org).strip()
        # Normalize whitespace (collapse multiple spaces to single space)
        clean_org = re.sub(r'\s+', ' ', clean_org)

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

                        # Handle specialty parsing for all unit types (BeAScout now provides specialty for Troops too)
                        clean_org, specialty = parse_specialty_info(full_name, chartered_org)
                        unit_data['chartered_organization'] = clean_org
                        unit_data['specialty'] = specialty
        
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
        contact_labels = unit_body.find_all(string=re.compile(r'Contact:', re.IGNORECASE))
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
        
        # Description - only from unit-description div (no fallback to administrative text)
        desc_container = unit_body.find('div', class_='unit-description')
        unit_data['_has_description_div'] = desc_container is not None
        
        if desc_container:
            # Replace <br> tags with spaces in description to preserve line breaks
            for br in desc_container.find_all("br"):
                br.replace_with(" ")
            unit_data['description'] = desc_container.get_text(separator=' ', strip=True)
        else:
            unit_data['description'] = ""
        
        # Unit composition (Boy Troop, Girl Troop, etc.)
        composition_elem = unit_body.find(string=re.compile(r'(Boy|Girl|Boys|Girls|Coed)'))
        if composition_elem:
            # Get the parent element's text
            parent_text = composition_elem.parent.get_text(strip=True)
            if any(unit_type in parent_text for unit_type in ['Troop', 'Pack', 'Crew', 'Post', 'Club']):
                unit_data['unit_composition'] = parent_text
        
        # Check if unit-address div is empty/missing for QUALITY_UNIT_ADDRESS logic
        address_containers = unit_body.find_all('div', class_='unit-address')
        unit_address_div_empty = not address_containers or not address_containers[0].get_text(strip=True)
        
        # Capture unit-address content for quality analysis
        unit_address = ""
        if address_containers:
            unit_address = address_containers[0].get_text(separator=' ', strip=True)
        
        
        # Meeting location extraction - try address field first, then description
        raw_location_from_address = ""
        raw_location_from_description = ""
        
        # 1. Try to extract from unit-address div
        if address_containers:
            # Replace <br> tags with spaces before extracting text to fix concatenation
            container = address_containers[0]
            for br in container.find_all("br"):
                br.replace_with(" ")
            raw_location_from_address = container.get_text(separator=' ', strip=True)
        
        # 2. Try to extract from description
        if unit_data['description']:
            day, time, location = extract_meeting_info(unit_data['description'])
            if day:
                unit_data['meeting_day'] = day
            if time:
                unit_data['meeting_time'] = time
            if location:
                raw_location_from_description = location
        
        # Unified location extraction - extract both meeting location and town from same sources
        meeting_location = ""
        meeting_location_source = "none"
        unit_town = ""
        
        # Priority 1: Extract from unit-address content (most reliable)
        if unit_address:
            address_components = extract_location_components(unit_address, 'address')
            if address_components['full_location']:
                meeting_location = address_components['full_location']
                meeting_location_source = "address"
            else:
                # FALLBACK: If no location extracted but unit_address contains street address,
                # use the entire unit_address value to preserve facility name + address

                # Check if unit is in exception list (doesn't require street number)
                is_exception = check_location_exception(unit_data)

                if is_exception:
                    # Exception unit - accept location without street number requirement
                    meeting_location = unit_address
                    meeting_location_source = "address_fallback_exception"
                elif re.search(r'\d+\s+[A-Za-z][A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Court|Ct|Place|Pl)',
                               unit_address, re.IGNORECASE):
                    # Normal fallback - requires street number
                    meeting_location = unit_address
                    meeting_location_source = "address_fallback"
            if address_components['town']:
                unit_town = address_components['town']
        
        # Priority 2: Extract from description if no unit-address location (still reliable)
        if not meeting_location and raw_location_from_description:
            meeting_location = raw_location_from_description
            meeting_location_source = "description"
            # Also try to extract town from description location
            if not unit_town:
                desc_components = extract_location_components(raw_location_from_description, 'description')
                if desc_components['town']:
                    unit_town = desc_components['town']
        
        # Set meeting location with proper formatting and source tracking
        if meeting_location:
            formatted_location = format_meeting_location(meeting_location)
            unit_data['meeting_location'] = formatted_location
            unit_data['meeting_location_source'] = meeting_location_source
        else:
            unit_data['meeting_location'] = ""
            unit_data['meeting_location_source'] = "none"
        
        # Set town if extracted from reliable sources
        if unit_town:
            unit_data['unit_town'] = unit_town
        
        # Conservative town extraction fallback - only if not already extracted above
        # Uses unified location extraction with correct precedence
        if not unit_data.get('unit_town'):
            # Method 3: Extract from description field (still reliable)
            if unit_data.get('description'):
                # Filter out contact information patterns to avoid extracting person names as towns
                description_text = unit_data['description']
                # Skip description if it primarily contains contact information  
                if not re.search(r'Contact:\s*[A-Za-z\s]+\s*Email:', description_text, re.IGNORECASE):
                    desc_components = extract_location_components(description_text, 'description')
                    if desc_components['town']:
                        unit_data['unit_town'] = desc_components['town']
            
            # Method 4: Extract from unit-name field (fallback only)  
            if not unit_data.get('unit_town') and unit_data.get('primary_identifier'):
                name_components = extract_location_components(unit_data['primary_identifier'], 'org_name')
                if name_components['town']:
                    unit_data['unit_town'] = name_components['town']
            
            # Method 5: Fallback to chartered organization extraction (last resort)
            if not unit_data.get('unit_town') and unit_data.get('chartered_organization'):
                org_components = extract_location_components(unit_data['chartered_organization'], 'org_name')
                if org_components['town']:
                    unit_data['unit_town'] = org_components['town']
        
        # Raw content for debugging
        unit_data['raw_content'] = wrapper.get_text()[:200] + "..."
        
    except Exception as e:
        print(f"Error processing unit {index}: {e}")
        unit_data['raw_content'] = f"Error: {e}"
    
    # Add district assignment based on unit_town
    unit_town = unit_data.get('unit_town', '').strip()
    unit_data['district'] = get_district_for_town(unit_town)
    
    # Integrate quality scoring - calculate score, grade, and quality tags during HTML parsing
    try:
        from src.pipeline.core.quality_scorer import UnitQualityScorer
        scorer = UnitQualityScorer()
        
        # Score this individual unit
        score, recommendations = scorer.score_unit(unit_data)
        
        # Add scoring results to unit data for single source of truth
        unit_data['completeness_score'] = round(score, 1)
        unit_data['completeness_grade'] = scorer.get_letter_grade(score)
        unit_data['quality_tags'] = recommendations
        
    except Exception as e:
        # Fallback if quality scoring fails - don't break HTML parsing
        print(f"Warning: Quality scoring failed for unit {index}: {e}")
        unit_data['completeness_score'] = 0.0
        unit_data['completeness_grade'] = 'F'
        unit_data['quality_tags'] = []
    
    # Add unit-address content to support simplified QUALITY_UNIT_ADDRESS logic
    unit_data['unit_address'] = unit_address
    
    return unit_data

def extract_address_from_text(text):
    """Universal address extraction function - uses unified location parser"""
    components = extract_location_components(text, 'description')
    return components['full_location']

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
    
    # Meeting time patterns - enhanced with boundary checks to avoid email/unit number contamination
    # while still capturing legitimate meeting times from descriptions
    time_patterns = [
        r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*([ap])\.?m?\.?',  # "7:00 - 8:30 p.m."
        r'(\d{1,2}:\d{2})\s*([ap])\.?m?\.?\s*-\s*(\d{1,2}:\d{2})\s*([ap])\.?m?\.?',  # "6:30 p.m. - 8:00 p.m."
        r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})',  # "7:00 - 8:30" (full time range, no AM/PM)
        r'(?:\s|,)\s*(\d{1,2})\s*-\s*(\d{1,2}:\d{2})',  # " 7 - 8:30" (simple time range after space/comma)
        r'(?:at\s+)?(\d{1,2}:\d{2})\s*([ap])\.?m?\.?',  # "at 6:30pm", "7:00 PM"
        r'(?:at\s+)(\d{3,4})\s*([ap])\.?m?\.?',  # "at 330pm", "at 1230 PM" - requires "at" context
        
        # ENHANCED: Legitimate time patterns with proper context to avoid unit identifier contamination
        r'(?:at|meets?)\s+(\d{1,2})\s*([ap])\.?m?\.?',  # "at 7pm" or "meets 6am" - requires context word
        r'(?:from\s+)?(\d{1,2}:\d{2})\s*(?:to\s+(\d{1,2}:\d{2}))?\s*([ap])\.?m?\.?',  # "from 7:00 to 8:30 PM"
        
        # NEW: Additional legitimate patterns for meeting descriptions
        r'(?:from\s+)(\d{1,2})\s*([ap])m?\s*-\s*(\d{1,2})\s*([ap])m?',  # "from 6pm - 7pm"
        r'(?:nights?\s+from\s+)(\d{1,2})\s*([ap])m?\s*-\s*(\d{1,2})\s*([ap])m?',  # "nights from 6pm - 7pm"
        r'(?:meetings?\s*-\s*)(\d{1,2})\s*-\s*(\d{1,2})\s*([ap])m?',  # "meetings - 7-8pm"  
        r'(?:on\s+\w+days?\s+)(\d{1,2})\s*([ap])m?(?:\s+at)',  # "on Tuesdays 6PM at"
        r'(?:meet(?:s|ing)?.*?)(\d{1,2}:\d{2})\s*-\s*(\d{1,2})\s*([ap])m?',  # "meets from 6:30-8 pm"
        r'(?:from\s+)(\d{1,2})\s*-\s*(\d{1,2})\s*([ap])m?',  # "from 4-6 pm"
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
            
            # Handle different pattern types based on number of groups and content
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
            elif len(groups) == 4 and groups[3]:  # New patterns: "from 6pm - 7pm" style
                time1 = format_meeting_time(f"{groups[0]} {groups[1]}M")
                time2 = format_meeting_time(f"{groups[2]} {groups[3]}M") 
                time = f"{time1} - {time2}"
            elif len(groups) == 3 and groups[2]:  # "meetings - 7-8pm" or "from 4-6 pm" style  
                if ':' in groups[0]:
                    # "meets from 6:30-8 pm" style
                    time1 = format_meeting_time(f"{groups[0]} {groups[2]}M")
                    time2 = format_meeting_time(f"{groups[1]} {groups[2]}M")
                    time = f"{time1} - {time2}"
                else:
                    # "from 4-6 pm" or "7-8pm" style
                    time1 = format_meeting_time(f"{groups[0]}:00 {groups[2]}M")
                    time2 = format_meeting_time(f"{groups[1]}:00 {groups[2]}M")
                    time = f"{time1} - {time2}"
            elif len(groups) >= 2 and groups[1]:  # Single time with AM/PM: "6PM", "at 7pm"
                time = format_meeting_time(f"{groups[0]} {groups[1]}M")
            else:
                time = format_meeting_time(groups[0])
            break
    
    # Extract location using common address extraction function
    location = extract_address_from_text(description)
    
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

def process_html_file(html_file_path, source_name=""):
    """Process a single HTML file and extract unit data"""
    print(f"\nProcessing {source_name}: {html_file_path}")
    
    try:
        with open(html_file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {html_file_path}")
        return []
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all unit containers
    unit_wrappers = soup.find_all('div', class_='card-body')
    unit_names = soup.find_all('div', class_='unit-name')
    
    print(f"Found {len(unit_wrappers)} unit containers")
    print(f"Found {len(unit_names)} unit names")
    
    # Extract all units
    units = []
    for i, wrapper in enumerate(unit_wrappers):
        unit_name_elem = unit_names[i] if i < len(unit_names) else None
        unit_data = extract_unit_fields(wrapper, i, unit_name_elem)
        
        # Add source information
        unit_data['data_source'] = source_name
        units.append(unit_data)
    
    print(f"Extracted {len(units)} units from {source_name}")
    return units


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/parsing/html_extractor.py <html_file> [additional_html_files...]")
        print("Examples:")
        print("  python src/parsing/html_extractor.py data/scraped/20250824_220843/beascout_01720.html")
        print("  python src/parsing/html_extractor.py data/scraped/20250824_220843/beascout_01720.html data/scraped/20250824_220843/joinexploring_01720.html")
        sys.exit(1)
    
    html_files = sys.argv[1:]
    all_units = []
    
    # Process each HTML file
    for html_file in html_files:
        # Determine source name from filename
        if 'beascout' in html_file.lower():
            source_name = "BeAScout"
        elif 'joinexploring' in html_file.lower():
            source_name = "JoinExploring" 
        else:
            source_name = "Unknown"
        
        units = process_html_file(html_file, source_name)
        all_units.extend(units)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total units extracted from all sources: {len(all_units)}")
    
    # Show breakdown by source
    source_counts = {}
    for unit in all_units:
        source = unit.get('data_source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in source_counts.items():
        print(f"  {source}: {count} units")
    
    # Deduplicate across all sources
    unique_units = deduplicate_units(all_units)
    print(f"After deduplication: {len(unique_units)} unique units")
    
    # Apply HNE Council territory filtering
    hne_filtered_units = filter_hne_units(unique_units)
    print(f"After HNE filtering: {len(hne_filtered_units)} HNE Council units")
    
    # Determine output filename based on input
    # Extract zip codes from filenames to create proper output filename
    import re
    zip_codes = set()
    for file in html_files:
        # Extract 5-digit zip codes from filename (look for beascout_##### or joinexploring_##### pattern)
        zip_match = re.search(r'(?:beascout|joinexploring)_(\d{5})\.html', file)
        if zip_match:
            zip_codes.add(zip_match.group(1))
    
    # Determine output directory based on session type
    import os
    session_type = os.environ.get('SESSION_TYPE', 'pipeline')
    if session_type == 'regression':
        output_dir = 'data/output/regression/raw'
    else:
        output_dir = 'data/raw'

    if zip_codes:
        # Use first zip code found for output filename
        zip_code = sorted(zip_codes)[0]  # Use first zip code alphabetically for consistency
        output_file = f'{output_dir}/all_units_{zip_code}.json'
    else:
        # Fallback to combined if no zip codes found
        output_file = f'{output_dir}/all_units_combined.json'
    
    # Save all units to JSON
    output_data = {
        'extraction_info': {
            'source_files': html_files,
            'source_counts': source_counts,
            'extraction_date': str(__import__('datetime').datetime.now())
        },
        'total_units': len(hne_filtered_units),
        'all_units': hne_filtered_units
    }
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved all {len(hne_filtered_units)} units to {output_file}")

if __name__ == "__main__":
    main()