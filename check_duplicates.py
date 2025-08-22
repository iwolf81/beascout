#!/usr/bin/env python3
"""
Check for duplicate units in the extracted data.
"""
from bs4 import BeautifulSoup
from collections import Counter

with open('data/raw/debug_page_01720.html', 'r') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

# Get all unit names
unit_names = soup.find_all('div', class_='unit-name')
unit_identifiers = []

for name_div in unit_names:
    h5 = name_div.find('h5')
    if h5:
        identifier = h5.get_text(separator=' ').replace('\n', ' ').strip()
        unit_identifiers.append(identifier)

print(f"Total unit entries: {len(unit_identifiers)}")

# Count duplicates
counter = Counter(unit_identifiers)
print(f"Unique units: {len(counter)}")

# Show duplicates
duplicates = {k: v for k, v in counter.items() if v > 1}
print(f"Units with duplicates: {len(duplicates)}")

if duplicates:
    print("\nDuplicate units:")
    for unit, count in sorted(duplicates.items()):
        print(f"  {unit}: {count} occurrences")

# Show first 10 unique units
print(f"\nFirst 10 unique units:")
unique_units = list(counter.keys())
for i, unit in enumerate(unique_units[:10]):
    print(f"  {i}: {unit}")