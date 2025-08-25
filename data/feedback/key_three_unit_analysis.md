# Key Three - Unit Analysis
1. The "beascout/data/input/Key 3 08-22-2025.xlsx" spreadsheet is the definitive source of units in the HNE Council.
2. The unitcommorgname column in "beascout/data/input/Key 3 08-22-2025.xlsx" identifies the unit type, unit number, town, and chartered organization, though not in a consistent format. (Explained further below.)
   - Some chartered organization names may contain the town name (e.g. "Acton-Group of Citizens").
3. The unitcommorgname columne contains 169 unique string values.
   - There are 169 units in the HNE Council.
4. The citystate column is part of the address of the Key Three member; it is not the source for the unit town.
5. The unitcommorgname column contains the town of the unit, though not in a consistent format:
   -  "Worcester - Heart of New England Council" - unit town is clearly Worcester
   -  "Pepperell-Fire Firefighters Association" - unit town is clearly Pepperell; note no spaces before or after separating '-'
   -  "Clinton Heart of New England Council" - unit town is Clinton; note absence of separating '-'
   -  "Acton-Group Of Citizens, Inc" - Chartered organization contains unit town in its name: Acton
   -  "Acton-Boxborough Rotary Club" - Chartered organization contains two towns in its name. Acton and Boxborough are both towns in HNE Council. Fallback to the Key Three members' addresses to select the actual unit town. The correct answer is Acton.
   -  "E Brookfield - Howe Lumber Co Inc" - Sometimes North, South, East, West are abbreviated as N, S, E, W. Full unit town name is "East Brookfield"
   -  "Oxford First Congregational Church of Oxford" - The separating '-' is missing. Town name is Oxford.
   -  "Veterans Of Foreign Wars Westminster Post" - Town name is near end of chartered organization name: Westminister
   -  "Fiskdale-American Legion Post 109" - Fiskdale is a village of Sturbridge. Its unit town is Sturbridge.
6. Some units may not be present in fully successfully scraped beascout or joinexploring data.
7. "beascout/data/input/Key 3 08-22-2025.xlsx" was manually saved as a tab delimited file named beascout/data/input/Key_3_08-22-2025_original_cleaned.txt; the header lines including column headers was manually removed to leave only data.
8. The following analysis of Key_3_08-22-2025_original_cleaned.txt identified 169 units in HNE Council:
   -  awk -F '\t' '{print $10}' Key_3_08-22-2025_original_cleaned.txt | sed -e 's/\"//g' | sort -u  | wc -l
9. New versions of the Key Three spreadsheet will be provided by the Council Office as its the Key Three members change.
10. The full scraping to report pipeline should re-parse the input Key Three spreadsheet.
11. Re-examine logic for extracting unit town in "beascout/data/input/Key 3 08-22-2025.xlsx".
    - I think it may have to be modified.
12. Re-examine logic for extracting unit town from scraped beascout and joinexploring data.
    - I think it will still be valid.
13. Once the unit identifier values (<unit type><unit number><town>>) have be re-verified, we can accurately determine the unit counts in the Key Three spreadsheet and the scraped beascout and joinexploring data.
14. From there, we can determine what units, if any, are listed in the Key Three spreadsheet but are not present in beascout nor joinexploring data. Missing units must be clearly identified in the reports.
15. Additional items
    - At what part of the processing is the unit's district saved. Would it be best to first associate a town with a district in extra_hne_towns.py? This data will only change during redistricting, which is a rare occurrence. This processing would permit the district field to be readily populated when generating parsing the scraped beascout and joinexploring data.
    - Add a date and time stamps to the file names of the scraped beascout and join scouting data. This will enable application user to check if/when a zip code was scrape to verify information updated by Key Three
