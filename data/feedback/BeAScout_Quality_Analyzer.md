# BeAScout Quality Analyzer

## Use Case Scenarios

1. Complete scraping of beascout.org and joinexploring.org for all Heart of New England (HNE) zip codes.
2. Complete scraping of beascout.org and joinexploring.org for specific HNE zip codes.
   1. Need to retrieve on-demand updated information for unit(s) in specific zip code(s).
3. Complete parsing of Key Three spreadsheet from HNE Council Office.
   1. The Key Three are intermittently updated.
   2. The HNE Council office can generate Key Three spreadsheet upon request.
4. Generate BeAScout Quality Report periodically and on-demand.
   1. Include debug logging of unique unit information from scraped beascout.org and joinexploring.org data and parsed Key Three spreadsheet.
   2. This debug information can help identify parsing issues when these data sources are modified in an unexpected manner.

## Reporting

### HNE Council Commissioner's Report

1. Report generated in MS Excel spreadsheet format (.xlsx).
   1. May need to also generate report in Google Sheets format.
2. Executive Summary sheet
   1. @claude - Make proposal
3. Create separate sheets for each District in Council.
4. Include the following information in the header for each District sheet
   1. Title - BeAScout Quality Report
   2. Council Name
   3. District Name
   4. Generation date/time
   5. Data Sources: BeAScout.org (10-mile radius) + JoinExploring.org (20-mile)
   6. Last Complete Data Retrieval: <date/time>
   7. <n> Units across <n> towns
   8. Legend describing means of all the quality tags
5. List the following information for each unit on District sheet:
   1. Unit identifier: <unit type> <unit number> <unit town>
   2. Chartered organization
   3. Town
      1. This permits sorting by town
   4. Quality Score
   5. Quality Grade
   6. Missing Information
      1. REQUIRED_xxx tags
   7. Quality Issues
      1. QUALITY_xxx tags
   8. Recommended Improvements
      1. RECOMMENDED_xxx tags
   9. Meeting Location
      1. [facilty], <street address>, <town/state/zip code>
   10. Meeting Day
   11. Meeting Time
   12. Contact Email
   13. Contact Person
   14. Contact Phone Number
   15. Unit Website
   16. Key Three - first person
       1.  Position, Name, Address, Email, Phone (same cell)
       2.  "None" if non-existent
   17. Key Three - second person
       1.  Position, Name, Address, Email, Phone (same cell)
       2.  "None" if non-existent
   18. Key Three - third person
       1.  Position, Name, Address, Email, Phone (same cell)
       2.  "None" if non-existent

## Feedback
1. District Report sheets
   1. Key Three contact cells: Key Three - [First|Second|Third] Person:
      1. Remove labels and write position, name, address, email, and phone one separate lines in same cell.
   2. Contact information
      1. Order columns by Contact Person, Contact Email, Contact Phone
   3. Missing Information,	Quality Issues,	Recommended Improvements columns
      1. List each issue on separate lines within the same cell.
   4. Meeting Location
      1. List facility, street address, city/state/zip on separate lines within the same cell
   5. Units not present in BeAScout
      1. Include entries for these units
      2. Quality score 0, grade "N/A", grade fill color Red
      3. Leave quality, meeting info, and contact cells empty
   6. Sort by quality score then unit identifier.
   7. Header
      1. Add source Key Three spreadsheet filename as it contains its generation date in filename.
      2. Include units not present in BeAScout in count for "<n> Units across <n> towns" line
2. Executive Summary sheet
   1. Add Key Three spreadsheet name to Data Sources
   2. Change "Last Complete Data Retrieval" to "Last Complete BeAScout Data Retrieval"
   3. QUALITY section
      1. Include units missing from BeAScout in "Total Units Analyzed: <n>" counts
      2. Insert line below it with "Units missing from BeAScout: <n>"
   4. UNITS BY DISTRICT section
      1. Include units missing from BeAScout in district unit counts
   5. Replace "QUALITY TAG LEGEND" section, including TITLE, with QUALITY ISSUE LEGEND
      1. Create separate sub-sections for Required Information, Needs Improvement, Recommended Information
      2. For each subsection, move the contents of Column B, which contains the error messages in the District sheets, and repopulation Column B with the explanation of each error that is present in the documentation.

## Feedback 2

1. Executive Summary sheet
   1. I removed extra blank rows in BeAScout_Quality_Report_20250830_223614.xlsx
   2. Duplicate this format in the output
2. District sheets
   1. Sort by Quality Grade, Quality Score, then Unit Identifier
      1. N/A is worse than F
   2. Key Three contact cells
      1. Why is N/A in each cell; it's not helpful
   3. Missing BeAScout units need Quality Score of 0; these cells are currently empty
   4. Meeting Location column
      1. Town name was two words such as "North Grafton", "West Boylston", and "E. Templeton" are incorrectly written on separate lines in cell
3.  Possible parsing issue
    1.  Troop 134 Douglas (Soaring Eagle) has a Meeting Location of:
            22 Church STREETPO BOX 898
            Douglas MA 01516
        Note the concatenation of the street and po box; however, they are separated in the source:
            beascout_01590.html:3410:          22 Church STREET<br>PO BOX 898<br>Douglas MA 01516        </div>
    2. Similarly, the Meeting Location for Troop 1004 Shrewsbury (Quinapoxet) has its address munged together:
            2 School St.Raymond Stone American Legion Post PO Box 302
            Shrewsbury MA 01545
        However, they are separated in the source:
            beascout_01610.html:4625:           2 School St.<br>Raymond Stone American Legion Post  PO Box 302<br>Shrewsbury MA 01545        </div>

## Feedback 3

1. Write Quality Score values as numbers to avoid MS Excel warnings
   1. Format as <n>.<n>
2. Fix extra blank rows in Executive Summary page
3. Note the formatting changes to Quinapoxet District sheet in BeAScout_Quality_Report_20250830_231940.xlsx
   1. Borders for table cells
   2. Fill colors for columns
   3. Columns A and B frozen
   4. Apply these formatting changes to both district sheets

## Feedback 4

1. Fix Meeting Location values where <facilty><address><town/state/zip> are concatenated on one line
   1. Root cause may be with parsing of scaped HTML unit files
   2. Examples
      1. Troop 123 Leicester -> St. Pius X Church 759 Main ST, Leicester MA 01524
      2. Troop 182 Holden -> First Baptist Church1216 Main STHolden MA 1520
         1. Note truncated zip code; likely 01520. DO NOT CORRECT IN CODE; KEY THREE MUST FIX IT
      3. Pack 31 Shirley -> Lancaster RD, Shirley MA 01464
      4. Troop 7123 Shirley -> Kittridge Rd, Shirley MA 01464
   3. Possible root causes
      1. Is capitalized "ST" affecting parsing?
2. Add fill color to different columns to create visible categories
   1. Quality Columns F-H
      1. Fill with very light yellow
   2. BeAScout Information Columns I-O
      1. Fill with very light blue
   3. Key Three Contacts Columns P-R
      1. Fill with very light green2

## Feedback 5

In html_extractor.py, does the following address pattern cover all cases? In some meeting_locations, the address line separation is not fully working. Also, should <br> be replaced with ", " instead of " "? I am asking, not suggesting.

              address_patterns = [
                    r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd)[^,]*',
                    r'[A-Za-z\s]+\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd)[^,]*'
                ]

Troop 12 Leicester -> St. Pius X Church 759 Main ST, Leicester MA 01524
   street and town/state/zip are on same line  

Also, "E. Templeton" is now being printed as "E., Templeton"

   "25 Lake Ave
   E., Templeton MA 01438"

## Feedback 6

1. The meet_location formatting issues are still present.
   1. Let's table them for later. We've spent too many tokens on nit issue.
2. New QUALITY_UNIT_ADDRESS tag
   1. Consider adding QUALITY_UNIT_ADDRESS tag to indicate the <div class="unit-address"> is empty/missing for a unit though its meeting address was found elsewhere, likely in <div class="unit-description">.
   2. Logic could be:
         Process HTML input for a unit
            If <div class="unit-address"> empty/missing
               Set REQUIRED_MISSING_LOCATION
            If meeting_location is NOT empty at end of HTML processing for a unit
               Replace REQUIRED_MISSING_LOCATION tag with QUALITY_UNIT_ADDRESS tag
3. Consider revised grading system
   1. REQUIRED_xxx tags comprise 100% of score
      1. Each REQUIRED_xxx tag for a unit type has equal value
         1. Recall that only Crews have a required specialty field
   2. QUALITY_xxx tags deduct 50% of point for corresponding REQUIRED_xxx field
      1. QUALITY_UNIT_ADDRESS -> REQUIRED_MISSING_LOCATION
      2. QUALITY_PO_BOX -> REQUIRED_MISSING_LOCATION
      3. QUALITY_PERSONAL_EMAIL -> REQUIRED_MISSING_EMAIL

THINK HARD about Feedback 6, items 2 and 3. Propose plan but do not implement yet.

## Feedback 7

Reorder the follow columns in District sheets:
   Meeting Location, Meeting Day, Meeting Time, Contact Person, Contact Email, Contact Phone Number, Unit Website
as
   Meeting Location, Meeting Day, Meeting Time, Contact Email, Contact Person, Contact Phone Number, Unit Website
This new order follows the order of the error/quality/recommended messages, which helps with visual verification of quality score.

## Feedback 8

### Clickable Email Address
1. Make email addresses shows in Key Three contact values (columns Q,R,S) clickable links

### Add Zip Code
1. Insert new "Zip Code" column for unit after column C (Town).
1. This modification will permit report reader to readily look up unit in beascout.org, which accepts only zip code for search criteria.

### Quality Scoring Issues
#### Quinapoxet District
1. Troop 7012 Leominster - BSA.TROOP12.leominster@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
1. Pack 12 Groton - karl@grindleyfamily.com is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. Pack 1455 Pepperell - Meeting time of 5AM is incorrect - Was "grades K-5" in unit-description incorrectly parsed as 5AM?
1. Troop 12 Leominster - BSA.TROOP12.leominster@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
1. Troop 1728 Lunenburg - carlsuzannerose@prodigy.net is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. Troop 41 Fitchburg - billh@boutwellowens.com is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. Crew 204 Boylston - jason@micro-monkey.com is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. Pack 37 Worcester - where did meeting time of "10:52 PM" come from??? - This is not correct
1. Troop 1004 Shrewsbury - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 175 Holden - Adam@currier.us is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. Pack 123 Leicester - pack123den.leader@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
#### Soaring Eagle District
1. Pack 134 Douglas - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Pack 26 Barre - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 134 Douglas - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 7006 Gardner -  <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 7006 Gardner - smtroop6.girls@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
1. Troop 7338 Charlton - where did meeting time of "73:38 AM" come from??? - This is not correct
1. Ship 1935 Webster - The meeting_location value is the entire unit-description string - meeting_locate has parsing issue
Troop 165 Charlton - troop165.charlton@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect - Did the substring 'charlton', which is the unit_town, be improperly identified as a person? Should the unit_town be ruled out as an indicator for a personal email?  
1. Troop 6 Gardner - GardnerScouting6@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect - Should the unit_number be ruled out as an indicator for a personal email?

## Feedback 9

### Zip code, links, and columns feedback
1. The zip code values are NOT populated in the Zip Code column
2. The entire multi-line string in the Key Three (1), Key Three (2), and Key Three (3) values are links. Only the email substring in each multi-line string should be an email link.
3. Freeze columns A (Unit Identifier) through D (Zip Code) instead of current columns A and B (Chartered Org)

### Quality tag adjustments feedback
#### Quinapoxet
@claude were the fixes actually implemented?? I did not verify Soar Eagle be nothing was fixed for Quinapoxet
1. FAIL - Troop 7012 Leominster - BSA.TROOP12.leominster@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect 
1. FAIL - Pack 12 Groton - karl@grindleyfamily.com is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. FAIL - Pack 1455 Pepperell - Meeting time of 5AM is incorrect - Was "grades K-5" in unit-description incorrectly parsed as 5AM?
1. FAIL - Troop 12 Leominster - BSA.TROOP12.leominster@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
1. FAIL - Troop 1728 Lunenburg - carlsuzannerose@prodigy.net is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. FAIL - Troop 41 Fitchburg - billh@boutwellowens.com is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. FAIL - Crew 204 Boylston - jason@micro-monkey.com is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. FAIL - Pack 37 Worcester - where did meeting time of "10:52 PM" come from??? - This is not correct
1. FAIL - Troop 1004 Shrewsbury - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. FAIL - Troop 175 Holden - Adam@currier.us is not a unit-specific address - QUALITY_PERSONAL_EMAIL tag is missing
1. FAIL - Pack 123 Leicester - pack123den.leader@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
#### Soaring Eagle District
1. Pack 134 Douglas - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Pack 26 Barre - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 134 Douglas - <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 7006 Gardner -  <div class="unit-address"> has street address and PO Box - The QUALITY_POBOX_LOCATION is incorrect
1. Troop 7006 Gardner - smtroop6.girls@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect
1. Troop 7338 Charlton - where did meeting time of "73:38 AM" come from??? - This is not correct
1. Ship 1935 Webster - The meeting_location value is the entire unit-description string - meeting_locate has parsing issue
Troop 165 Charlton - troop165.charlton@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect - Did the substring 'charlton', which is the unit_town, be improperly identified as a person? Should the unit_town be ruled out as an indicator for a personal email?  
1. Troop 6 Gardner - GardnerScouting6@gmail.com is a unit-specific address - QUALITY_PERSONAL_EMAIL tag is incorrect - Should the unit_number be ruled out as an indicator for a personal email?
