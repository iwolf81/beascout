#!/usr/bin/env python3
"""
Extract Heart of New England Council towns and zip codes
"""
import json

def get_hne_towns_and_zipcodes():
    """
    Extract towns from both HNE Council districts and their zip codes
    Based on data/input/HNE_council_map.png showing district boundaries
    """
    
    # QUINAPOXET District (blue on map) - Northern and central Massachusetts
    # Import from authoritative source instead of duplicating
    from src.mapping.district_mapping import TOWN_TO_DISTRICT
    quinapoxet_towns = [town for town, district in TOWN_TO_DISTRICT.items() if district == "Quinapoxet"]
    
    # SOARING EAGLE District (red on map) - Southern and western Massachusetts  
    # Import from authoritative source instead of duplicating
    soaring_eagle_towns = [town for town, district in TOWN_TO_DISTRICT.items() if district == "Soaring Eagle"]
    
    # Complete HNE Council territory (both districts)
    hne_towns = quinapoxet_towns + soaring_eagle_towns
    
    # Massachusetts zip codes for these towns (major ones)
    # Note: Many towns have multiple zip codes
    town_zipcodes = {
        # QUINAPOXET District towns
        "Acton": ["01720"],
        "Ashby": ["01431"],
        "Auburn": ["01501"],  
        "Ayer": ["01432"],
        "Berlin": ["01503"],
        "Bolton": ["01740"],
        "Boxborough": ["01719"],
        "Boylston": ["01505"],
        "Clinton": ["01510"],
        "Fitchburg": ["01420", "01421"],
        "Groton": ["01450"],
        "Harvard": ["01451"],
        "Holden": ["01520"],
        "Lancaster": ["01523"],
        "Leicester": ["01524"],
        "Leominster": ["01453"],
        "Littleton": ["01460"],
        "Lunenburg": ["01462"],
        "Millbury": ["01527"],
        "Paxton": ["01612"],
        "Pepperell": ["01463"],
        "Princeton": ["01541"],
        "Rutland": ["01543"],
        "Shirley": ["01464"],
        "Shrewsbury": ["01545"],
        "Sterling": ["01564"],
        "Townsend": ["01469"],
        "West Boylston": ["01583"],
        "Worcester": ["01601", "01602", "01603", "01604", "01605", "01606", "01607", "01608", "01609", "01610"],
        
        # SOARING EAGLE District towns
        "Ashburnham": ["01430"],
        "Athol": ["01331"],
        "Barre": ["01005"],
        "Brookfield": ["01506"],
        "Charlton": ["01507"],
        "Douglas": ["01516"], 
        "Dudley": ["01571"],
        "East Brookfield": ["01515"],
        "Gardner": ["01440"],
        "Grafton": ["01519"],
        "Hardwick": ["01037"],
        "Hubbardston": ["01452"],
        "New Braintree": ["01531"],
        "North Brookfield": ["01535"],
        "Northbridge": ["01534"],
        "Oakham": ["01068"],
        "Orange": ["01364"],
        "Oxford": ["01540"],
        "Petersham": ["01366"],
        "Phillipston": ["01331"],
        "Royalston": ["01368"],
        "Southbridge": ["01550"],
        "Spencer": ["01562"],
        "Sturbridge": ["01566"],
        
        # Villages with separate ZIP codes
        "Fiskdale": ["01518"],  # Village within Sturbridge
        "Jefferson": ["01522"],  # Village within Holden
        "Whitinsville": ["01588"],  # Village within Northbridge
        "Sutton": ["01590"],
        "Templeton": ["01468"],
        "Upton": ["01568"],
        "Ware": ["01082"],
        "Warren": ["01083"],
        "Webster": ["01570"],
        "West Brookfield": ["01585"],
        "Westminster": ["01473"],
        "Winchendon": ["01475"]
    }
    
    return hne_towns, town_zipcodes

def calculate_extraction_scope():
    """Calculate the total scope of data extraction"""
    hne_towns, town_zipcodes = get_hne_towns_and_zipcodes()
    
    total_towns = len(hne_towns)
    total_zipcodes = sum(len(zips) for zips in town_zipcodes.values())
    
    # Realistic unit estimates based on typical town sizes
    estimated_units_low = total_towns * 2   # Conservative: 2 units per town average
    estimated_units_high = total_towns * 4  # Optimistic: 4 units per town average
    
    print("=== HEART OF NEW ENGLAND COUNCIL EXTRACTION SCOPE ===\n")
    print(f"Total towns in HNE Council: {total_towns}")
    print(f"Total zip codes to process: {total_zipcodes}")
    print(f"Estimated total units: {estimated_units_low}-{estimated_units_high} units")
    print(f"  (Range based on 2-4 units per town average)")
    
    print(f"\n=== TOWNS AND ZIP CODES ===")
    for town in sorted(hne_towns):
        zips = town_zipcodes.get(town, ["ZIP_NEEDED"])
        zip_str = ", ".join(zips)
        print(f"{town:15} : {zip_str}")
    
    # Save to JSON file
    output_data = {
        "council": "Heart of New England",
        "total_towns": total_towns,
        "total_zipcodes": total_zipcodes, 
        "estimated_units_range": f"{estimated_units_low}-{estimated_units_high}",
        "estimation_method": "2-4 units per town average",
        "towns": hne_towns,
        "town_zipcodes": town_zipcodes,
        "all_zipcodes": [zip_code for zips in town_zipcodes.values() for zip_code in zips]
    }
    
    with open('data/zipcodes/hne_council_zipcodes.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Saved to: data/zipcodes/hne_council_zipcodes.json")
    
    return output_data

if __name__ == "__main__":
    calculate_extraction_scope()