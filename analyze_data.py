#!/usr/bin/env python3
"""
Analyze captured HTML data to understand unit field patterns.

Valid inputs: HTML file path
Expected outputs: Data structure analysis and field completeness report
"""
import re
from bs4 import BeautifulSoup
import json


def analyze_html_data(html_file):
    """
    Analyze captured HTML to understand unit data structure.
    
    Valid inputs: html_file (string path)
    Expected outputs: Dictionary with analysis results
    """
    with open(html_file, 'r') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    print("=== BeaScout HTML Data Analysis ===\n")
    
    # Find all unit containers - card-body contains the relevant information
    unit_wrappers = soup.find_all('div', class_='card-body')
    print(f"Total unit containers found: {len(unit_wrappers)}")
    
    if not unit_wrappers:
        print("No unit containers found. Checking for alternative selectors...")
        # Look for other possible containers
        candidates = [
            soup.find_all('div', class_='unit-body'),
            soup.find_all('div', class_='unit'),
            soup.find_all('div', class_='card'),
        ]
        for i, candidate_list in enumerate(candidates):
            print(f"  Alternative {i+1}: {len(candidate_list)} elements")
        return {}
    
    # Analyze first few units for structure
    analysis = {
        'total_units': len(unit_wrappers),
        'unit_samples': [],
        'field_patterns': {},
        'completeness_stats': {}
    }
    
    # Get all unit names for pairing
    unit_names = soup.find_all('div', class_='unit-name')
    print(f"Found {len(unit_names)} unit name containers")
    
    # Sample first 5 units for detailed analysis
    for i, wrapper in enumerate(unit_wrappers[:5]):
        # Pass the corresponding unit name if available
        unit_name_elem = unit_names[i] if i < len(unit_names) else None
        unit_data = extract_unit_fields(wrapper, i, unit_name_elem)
        analysis['unit_samples'].append(unit_data)
    
    # Analyze all units for field completeness
    all_units = []
    for i, wrapper in enumerate(unit_wrappers):
        # Pass the corresponding unit name if available  
        unit_name_elem = unit_names[i] if i < len(unit_names) else None
        unit_data = extract_unit_fields(wrapper, i, unit_name_elem)
        all_units.append(unit_data)
    
    # Deduplicate units based on primary identifier
    unique_units = deduplicate_units(all_units)
    print(f"After deduplication: {len(unique_units)} unique units")
    
    # Update analysis with deduplicated data
    analysis['total_units'] = len(unique_units)
    analysis['unit_samples'] = unique_units[:5]  # First 5 unique units
    
    # Calculate field completeness statistics
    analysis['completeness_stats'] = calculate_completeness_stats(unique_units)
    
    return analysis


def extract_unit_fields(wrapper, index, unit_name_elem=None):
    """
    Extract all possible fields from a unit wrapper.
    
    Valid inputs: wrapper (BeautifulSoup element), index (integer), unit_name_elem (optional BeautifulSoup element)
    Expected outputs: Dictionary with extracted unit data
    """
    unit_data = {
        'index': index,
        'primary_identifier': '',
        'unit_type': '',
        'unit_number': '',
        'chartered_organization': '',
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
                # Extract text and clean up, splitting on <br> tags
                full_name = h5_elem.get_text(separator=' ').replace('\n', ' ').strip()
                unit_data['primary_identifier'] = full_name
                
                # Parse unit type, number, and organization
                # Format: "Pack 0070 Acton-Congregational Church"
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    unit_data['unit_type'] = name_parts[0]  # Pack, Troop, Crew, etc.
                    unit_data['unit_number'] = name_parts[1]  # Number like 0070
                    if len(name_parts) > 2:
                        # Everything after unit number is chartered organization
                        unit_data['chartered_organization'] = ' '.join(name_parts[2:])
        
        # Extract distance from the same row as the unit name
        if unit_name_elem:
            # Find the parent row and look for unit-miles
            row = unit_name_elem.find_parent('div', class_='row')
            if row:
                distance_elem = row.find('div', class_='unit-miles')
                if distance_elem:
                    distance_text = distance_elem.get_text(strip=True)
                    # Clean up distance text (remove duplicate miles indicators)
                    unit_data['distance'] = distance_text.split()[0] + ' miles'
        
        # Now extract from the card-body container (wrapper)
        # Find unit-body within this card-body for detailed information
        unit_body = wrapper.find('div', class_='unit-body')
        if not unit_body:
            unit_body = wrapper  # fallback to card-body itself
        
        # Extract contact email
        email_links = unit_body.find_all('a', href=re.compile(r'mailto:'))
        if email_links:
            email_href = email_links[0].get('href', '')
            unit_data['contact_email'] = email_href.replace('mailto:', '')
        
        # Extract website
        website_links = unit_body.find_all('a', target='_blank')
        for link in website_links:
            href = link.get('href', '')
            if href and not href.startswith('mailto:') and not 'scouting.org' in href:
                unit_data['website'] = href
                break
        
        # Extract contact person from raw text
        raw_text = unit_body.get_text()
        contact_match = re.search(r'Contact:\s*(.+?)(?:\n|Phone:|Email:|$)', raw_text, re.IGNORECASE)
        if contact_match:
            unit_data['contact_person'] = contact_match.group(1).strip()
        
        # Extract phone number from raw text
        phone_match = re.search(r'Phone:\s*(\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4})', raw_text, re.IGNORECASE)
        if phone_match:
            unit_data['phone_number'] = phone_match.group(1).strip()
        
        # Extract meeting location from address pattern in raw text
        # Look for full address patterns like "12 Concord Rd" or "435 Central Street"
        address_patterns = [
            r'(\d+\s+[A-Za-z\s]+(?:Rd|Road|St|Street|Ave|Avenue|Dr|Drive|Ln|Lane|Way|Blvd|Boulevard|Ct|Court))',
            r'(\d+\s+[A-Za-z\s]+(Street|Road|Avenue|Drive|Lane|Court|Way|Boulevard))',
        ]
        for pattern in address_patterns:
            address_match = re.search(pattern, raw_text, re.IGNORECASE)
            if address_match:
                location = address_match.group(1).strip()
                # Make sure it's not just the unit number + "Act"
                if not location.endswith(' Act') and len(location) > 8:
                    unit_data['meeting_location'] = location
                    break
        
        # Extract unit composition from icons and text patterns
        composition_imgs = unit_body.find_all('img', alt=re.compile(r'Boy|Girl|Boys|Girls'))
        compositions = []
        for img in composition_imgs:
            alt_text = img.get('alt', '')
            if alt_text and alt_text not in compositions:
                compositions.append(alt_text)
        
        # Also look for text patterns indicating composition
        if not compositions:
            composition_patterns = [
                r'Boy\s+Troop',
                r'Girl\s+Troop', 
                r'Boys?\s+and\s+Girls?',
                r'Coed',
                r'Co-ed'
            ]
            for pattern in composition_patterns:
                if re.search(pattern, raw_text, re.IGNORECASE):
                    compositions.append(re.search(pattern, raw_text, re.IGNORECASE).group(0))
                    break
        
        unit_data['unit_composition'] = ', '.join(compositions)
        
        # Extract description
        desc_div = unit_body.find('div', class_='unit-description')
        if desc_div:
            # Get description text, excluding links and contact info
            desc_paras = desc_div.find_all('p')
            desc_texts = []
            for para in desc_paras:
                text = para.get_text(strip=True)
                if not text.startswith(('Email:', 'Website:', 'Contact:')):
                    desc_texts.append(text)
            unit_data['description'] = ' '.join(desc_texts)
        
        # Extract meeting information from description and raw text
        full_text = unit_data.get('description', '') + ' ' + raw_text
        
        # Meeting day patterns
        day_patterns = [
            r'meets?\s+(?:most\s+)?(?:on\s+)?([A-Za-z]+day)s?',  # "meets Wednesdays", "meets most Wednesdays", "meets on Wednesday"
            r'([A-Za-z]+day)s?\s+(?:at|from)',  # "Wednesdays at" or "Wednesday from"
            r'(?:first|second|third|fourth|last)\s+([A-Za-z]+day)',  # "first Friday"
        ]
        
        for pattern in day_patterns:
            day_match = re.search(pattern, full_text, re.IGNORECASE)
            if day_match:
                unit_data['meeting_day'] = day_match.group(1).capitalize()
                break
        
        # Meeting time patterns - improved to capture full times
        time_patterns = [
            r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2}\s*[ap]\.?m\.?)',  # "7:00 - 8:30 p.m." or "7:00 - 8:30 PM"
            r'(\d{1,2}:\d{2}\s*[ap]\.?m\.?)',  # "6:30pm", "7:00 PM", "6:30p.m."
            r'at\s+(\d{1,2}:\d{2}\s*[ap]\.?m\.?)',  # "at 6:30pm" or "at 7:00 p.m."
            r'from\s+(\d{1,2}:\d{2}\s*[ap]\.?m\.?)',  # "from 7:00 PM" or "from 7:00 p.m."
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, full_text, re.IGNORECASE)
            if time_match:
                if time_match.lastindex == 2:  # Range pattern
                    unit_data['meeting_time'] = f"{time_match.group(1)} - {time_match.group(2)}"
                else:
                    unit_data['meeting_time'] = time_match.group(1)
                break
        
        # Store raw content for debugging
        unit_data['raw_content'] = unit_body.get_text()[:200] + "..."
        
    except Exception as e:
        print(f"Error extracting unit {index}: {e}")
    
    return unit_data


def deduplicate_units(units):
    """
    Remove duplicate units based on primary identifier.
    
    Valid inputs: units (list of dictionaries)
    Expected outputs: List of unique units (keeps first occurrence)
    """
    seen_identifiers = set()
    unique_units = []
    
    for unit in units:
        identifier = unit.get('primary_identifier', '').strip()
        if identifier and identifier not in seen_identifiers:
            seen_identifiers.add(identifier)
            unique_units.append(unit)
    
    return unique_units


def calculate_completeness_stats(units):
    """
    Calculate field completeness statistics across all units.
    
    Valid inputs: units (list of dictionaries)
    Expected outputs: Dictionary with completeness statistics
    """
    stats = {}
    total_units = len(units)
    
    # Define required and recommended fields based on CLAUDE.md
    required_fields = ['primary_identifier', 'meeting_location', 'meeting_day', 
                      'meeting_time', 'contact_email', 'unit_composition']
    recommended_fields = ['contact_person', 'phone_number', 'website', 'description']
    
    # Calculate completeness for each field
    for field in required_fields + recommended_fields:
        filled_count = sum(1 for unit in units if unit.get(field, '').strip())
        stats[field] = {
            'filled': filled_count,
            'total': total_units,
            'percentage': round((filled_count / total_units) * 100, 1),
            'field_type': 'required' if field in required_fields else 'recommended'
        }
    
    return stats


def print_analysis_report(analysis):
    """
    Print formatted analysis report.
    
    Valid inputs: analysis (dictionary)
    Expected outputs: Formatted report printed to console
    """
    print(f"\n=== UNIT SAMPLES (First 5 of {analysis['total_units']}) ===")
    
    for unit in analysis['unit_samples']:
        print(f"\n--- Unit {unit['index']} ---")
        print(f"Primary ID: {unit['primary_identifier']}")
        print(f"Type/Number: {unit['unit_type']} {unit['unit_number']}")
        print(f"Organization: {unit['chartered_organization']}")
        print(f"Distance: {unit['distance']}")
        print(f"Email: {unit['contact_email']}")
        print(f"Website: {unit['website']}")
        print(f"Contact: {unit['contact_person']}")
        print(f"Composition: {unit['unit_composition']}")
        print(f"Description: {unit['description'][:100]}...")
    
    print(f"\n=== FIELD COMPLETENESS STATISTICS ===")
    stats = analysis['completeness_stats']
    
    print("\nRequired Fields:")
    for field, data in stats.items():
        if data['field_type'] == 'required':
            print(f"  {field:20} {data['filled']:3}/{data['total']:3} ({data['percentage']:5.1f}%)")
    
    print("\nRecommended Fields:")
    for field, data in stats.items():
        if data['field_type'] == 'recommended':
            print(f"  {field:20} {data['filled']:3}/{data['total']:3} ({data['percentage']:5.1f}%)")


if __name__ == "__main__":
    html_file = "data/raw/debug_page_01720.html"
    
    try:
        analysis = analyze_html_data(html_file)
        if analysis:
            print_analysis_report(analysis)
            
            # Save analysis to JSON for further use
            with open("data/raw/analysis_01720.json", "w") as f:
                json.dump(analysis, f, indent=2)
            print(f"\nAnalysis saved to: data/raw/analysis_01720.json")
        else:
            print("Analysis failed - no data extracted")
            
    except FileNotFoundError:
        print(f"HTML file not found: {html_file}")
        print("Run test_scraper.py first to capture HTML data")
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()