# Data Restructuring Feedback

1. The Excel report is good, with few minor issues itemized below.
- It is ready to provide to Council Commissioner for feedback.
- Commit and push current code with label BEASCOUT_20250904_REPORT_01.
- A versioning and labeling mechanism will be added in the near future.
  - Add this maintenance feature as an enhancement request.
2. There are no regressions in unit_identifier_debug_scraped_20250904_084416_u.log.
3. There still are in discarded_unit_identifier_debug_scraped_20250904_084416_u.log but those will be fixed later.
- Upon careful review of scraped HTML data, there is only one HNE-units with unit-address containing a PO BOX address but no street address: Post 4879 Groton.
- This unit is tagged REQUIRED_MISSING_LOCATION but not QUALITY_POBOX_LOCATION.
- I wonder if the presence of the town 'Groton' in "<div class="unit-address"> PO Box 314<br>Groton MA 01450 </div>" is preventing QUALITY_POBOX_LOCATION from being set.
- Regardless, this affects only one unit and the Key Three will be triggered to enter a real street address.
- Write this QUALITY_POBOX_LOCATION issue as a minor defect.
4. Troop 180 Holden (Quinapoxet) has contact email "straightshooters@mail.com", but not the QUALITY_PERSONAL_EMAIL tag.
- Write this up as a minor defect to fix later.
- It is not worth risking introducing regressions at this time.
5. Pack 148 East Brookfield (Soaring Eagle) has an invalid website in its scraped HTML data: http://n/A
- Write up an enhancement request to confirm websites exist and confirm secure https is specified, and not unsecure http. 
6. Write new code from scratch to generate unit emails.
- With all the architectural changes, fixing existing code will problematic.
- See sample_troop_email.md and sample_pack_email.md for guiding desired output.