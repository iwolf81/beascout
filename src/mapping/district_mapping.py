#!/usr/bin/env python3
"""
HNE Council District Mapping
Definitive town-to-district mapping based on HNE_council_map.png visual analysis
Replaces Key Three district data to eliminate "Special 04" district issues
"""

# Definitive district mapping from HNE Council map image
# Blue = Quinapoxet District, Red = Soaring Eagle District
TOWN_TO_DISTRICT = {
    # Quinapoxet District (Blue region)
    "Acton": "Quinapoxet",
    "Ashby": "Quinapoxet", 
    "Ayer": "Quinapoxet",
    "Berlin": "Quinapoxet",
    "Bolton": "Quinapoxet",
    "Boxborough": "Quinapoxet",
    "Boylston": "Quinapoxet",
    "Clinton": "Quinapoxet",
    "Groton": "Quinapoxet",
    "Harvard": "Quinapoxet",
    "Holden": "Quinapoxet",
    "Lancaster": "Quinapoxet",
    "Leicester": "Quinapoxet",
    "Leominster": "Quinapoxet",
    "Littleton": "Quinapoxet",
    "Lunenburg": "Quinapoxet",
    "Paxton": "Quinapoxet",
    "Pepperell": "Quinapoxet",
    "Princeton": "Quinapoxet", 
    "Rutland": "Quinapoxet",
    "Shirley": "Quinapoxet",
    "Sterling": "Quinapoxet",
    "Townsend": "Quinapoxet",
    "West Boylston": "Quinapoxet",
    "Worcester": "Quinapoxet",
    
    # Soaring Eagle District (Red region)
    "Athol": "Soaring Eagle",
    "Auburn": "Soaring Eagle",
    "Barre": "Soaring Eagle",
    "Brookfield": "Soaring Eagle",
    "Charlton": "Soaring Eagle",
    "Douglas": "Soaring Eagle",
    "Dudley": "Soaring Eagle",
    "East Brookfield": "Soaring Eagle",
    "Fitchburg": "Soaring Eagle",
    "Gardner": "Soaring Eagle",
    "Grafton": "Soaring Eagle",
    "Hardwick": "Soaring Eagle",
    "Hubbardston": "Soaring Eagle",
    "Jefferson": "Soaring Eagle",  # Small town near other Soaring Eagle towns
    "Millbury": "Soaring Eagle",
    "New Braintree": "Soaring Eagle",
    "Northbridge": "Soaring Eagle",
    "North Brookfield": "Soaring Eagle",
    "Oakham": "Soaring Eagle",
    "Orange": "Soaring Eagle",
    "Oxford": "Soaring Eagle",
    "Petersham": "Soaring Eagle",
    "Phillipston": "Soaring Eagle",
    "Royalston": "Soaring Eagle",
    "Shrewsbury": "Soaring Eagle",
    "Spencer": "Soaring Eagle",
    "Sturbridge": "Soaring Eagle",
    "Sutton": "Soaring Eagle",
    "Templeton": "Soaring Eagle",
    "Upton": "Soaring Eagle",
    "Ware": "Soaring Eagle",
    "Warren": "Soaring Eagle",
    "Webster": "Soaring Eagle",
    "West Brookfield": "Soaring Eagle",
    "Westminster": "Soaring Eagle",
    "Winchendon": "Soaring Eagle",
    "Whitinsville": "Soaring Eagle",  # Village of Northbridge
}

# Common town name variations and aliases
TOWN_ALIASES = {
    # Handle common abbreviations and variations
    "W Boylston": "West Boylston",
    "E Brookfield": "East Brookfield", 
    "W Brookfield": "West Brookfield",
    "N Brookfield": "North Brookfield",
    "Fiskdale": "Sturbridge",  # Village of Sturbridge
    
    # Handle Key Three formatting variations
    "West Boylston": "West Boylston",
    "East Brookfield": "East Brookfield",
    "West Brookfield": "West Brookfield", 
    "North Brookfield": "North Brookfield",
}

def get_district_for_town(town_name: str) -> str:
    """
    Get district assignment for a town name
    
    Args:
        town_name: Name of the town (handles variations and aliases)
        
    Returns:
        District name ("Quinapoxet" or "Soaring Eagle") or "Unknown" if not found
    """
    if not town_name:
        return "Unknown"
    
    # Clean and normalize town name
    clean_town = town_name.strip()
    
    # Try direct lookup first
    if clean_town in TOWN_TO_DISTRICT:
        return TOWN_TO_DISTRICT[clean_town]
    
    # Try aliases
    if clean_town in TOWN_ALIASES:
        canonical_town = TOWN_ALIASES[clean_town]
        return TOWN_TO_DISTRICT.get(canonical_town, "Unknown")
    
    # Handle case variations
    for town, district in TOWN_TO_DISTRICT.items():
        if clean_town.lower() == town.lower():
            return district
    
    return "Unknown"

def get_all_towns_by_district() -> dict:
    """
    Get all towns organized by district
    
    Returns:
        Dictionary with district names as keys and list of towns as values
    """
    districts = {"Quinapoxet": [], "Soaring Eagle": []}
    
    for town, district in TOWN_TO_DISTRICT.items():
        if district in districts:
            districts[district].append(town)
    
    return districts

def validate_town_coverage() -> dict:
    """
    Validate town coverage and return statistics
    
    Returns:
        Dictionary with coverage statistics
    """
    districts = get_all_towns_by_district()
    
    return {
        "total_towns": len(TOWN_TO_DISTRICT),
        "quinapoxet_towns": len(districts["Quinapoxet"]),
        "soaring_eagle_towns": len(districts["Soaring Eagle"]),
        "aliases_supported": len(TOWN_ALIASES)
    }

if __name__ == "__main__":
    # Test the district mapping
    stats = validate_town_coverage()
    print("🗺️ HNE Council District Mapping")
    print(f"   Total towns: {stats['total_towns']}")
    print(f"   Quinapoxet District: {stats['quinapoxet_towns']} towns")
    print(f"   Soaring Eagle District: {stats['soaring_eagle_towns']} towns")
    print(f"   Town aliases supported: {stats['aliases_supported']}")
    
    # Test some example lookups
    test_towns = ["Acton", "Gardner", "E Brookfield", "Fiskdale", "Worcester"]
    print(f"\n📍 Example District Lookups:")
    for town in test_towns:
        district = get_district_for_town(town)
        print(f"   {town} → {district}")