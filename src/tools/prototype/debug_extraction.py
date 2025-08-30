#!/usr/bin/env python3
"""
Debug extraction logic for unit identifiers.
"""
from bs4 import BeautifulSoup

with open('data/raw/debug_page_01720.html', 'r') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

# Find all unit-body containers
unit_bodies = soup.find_all('div', class_='unit-body')
print(f"Found {len(unit_bodies)} unit-body containers")

# Test first few to understand structure
for i, wrapper in enumerate(unit_bodies[:3]):
    print(f"\n=== Unit {i} ===")
    
    # Try to find unit name through parent traversal
    card_body = wrapper.find_parent('div', class_='card-body')
    print(f"Found card-body: {card_body is not None}")
    
    if card_body:
        card = card_body.find_parent('div', class_='card')
        print(f"Found card: {card is not None}")
        
        if card:
            row = card.find_parent('div', class_='row')
            print(f"Found row: {row is not None}")
            
            if row:
                # Look for unit-name in this row
                name_elem = row.find('div', class_='unit-name')
                print(f"Found unit-name in row: {name_elem is not None}")
                
                if name_elem:
                    h5_elem = name_elem.find('h5')
                    print(f"Found h5: {h5_elem is not None}")
                    if h5_elem:
                        print(f"H5 text: '{h5_elem.get_text()}'")
                
                # Also check for all unit-name divs in this row
                all_unit_names = row.find_all('div', class_='unit-name')
                print(f"All unit-name divs in row: {len(all_unit_names)}")
                for j, name_div in enumerate(all_unit_names):
                    h5 = name_div.find('h5')
                    if h5:
                        print(f"  {j}: {h5.get_text()}")

# Let's also check for all unit-name divs in the entire document
all_unit_names = soup.find_all('div', class_='unit-name')
print(f"\nTotal unit-name divs in document: {len(all_unit_names)}")
print("First 10 unit names:")
for i, name_div in enumerate(all_unit_names[:10]):
    h5 = name_div.find('h5')
    if h5:
        print(f"  {i}: {h5.get_text()}")