# Rethinking Processing
1. The Key Three excel input ("Key 3 08-22-2025.xlsx") is source of truth for number of units.
2. Parsing the Key Three excel input should result with list of units identified by <unit type> <unit number> <unit town>.
   1. key_three_unit_analysis.md lists the edge case issues with extracting the <unit town> from the unitcommorgname field.
3. Parsing the scraped beascout and joinexploring data must also determine the town for each unit by parsing the address, if the field is present, or the description, which has its own issues.
4. The unit identifiers should be normalized consistently when parsing the Key Three excel spreadsheet and the scraped beascout and joinexploring data. This will simplify joining the two types of data sources.
5. Should there be a unit_key field that contains the normalized unit identifer string (e.g., Pack 3 Leominster)?
6. Parsing the HNE_council_map.png image should clearly identify the district for each town. Obtain the town's district from this source instead of the Key Three excel input file because some Crew units are in the "Special 04" district, which does not exist.

# Notes
1. A manual scan of the Key Three excel input shows that the following units do NOT have three Key Three contacts, but rather only two. These should be the only units with incomplete contact info in the excel report.
   1. Pack 3 Leominster
   2. Pack 7 Clinton 
   3. Post 2012 Holden 
   4. Post 4879 Groton
   5. Ship 375 Groton
   6. Troop 131 Sutton
   7. Troop 151 Leominster
   8. Troop 7001 Harvard
   9. Troop 7027 Templeton
   10. Troop 7165 Charlton