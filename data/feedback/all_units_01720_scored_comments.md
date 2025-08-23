# PASS 1

Index 14 has meeting time as "7 - 8:30" in description but not in "meeting_time"

Index 13 meeting_location does not have ", " separator between address and town - "St. Anne's Church basement, 75 King StreetLittleton MA 01460". Same issue for Index 16. This is aesthetic improvement for JSON reader only.

Index 17 email is NOT personal as tagged with QUALITY_PERSONAL_EMAIL - cubmaster.concord133@gmail.com

Index 21 does specify location in description as "The first meeting is in-person at Camp Resolute"; however, its address is incomplete, so keep the REQUIRED_MISSING_LOCATION tag.

Index 28 email is NOT personal as tagged with QUALITY_PERSONAL_EMAIL - sudburypack62@gmail.com

Index 32 email is NOT personal as tagged with QUALITY_PERSONAL_EMAIL - westfordpack100@gmail.com

Index 33 email is NOT personal as tagged with QUALITY_PERSONAL_EMAIL - harvardcubpack10@gmail.com

# PASS 2

Index 4 - meeting_location is missing ", " separator between street and building name ": "435 Central StreetSt. Matthew's Church, Acton MA 01720". There are two common address formats in raw data: <street>|<building name>|<town/state/zip> and <building name>|<street>|<town/state/zip> 

Index 33 email is NOT personal as tagged with QUALITY_PERSONAL_EMAIL - harvardcubpack10@gmail.com

Index 52 - incorrectly parsed meeting time (00:00 AM - 8:30 PM) from Description (7:00 - 8:30).

Index 54 - mail is NOT personal as tagged with QUALITY_PERSONAL_EMAIL - secretarypack37@gmail.com . Suggest adding 'secretary', 'info', and 'admin' to unit_role_patterns[] in quality_scorer.py

unit_patterns[] in quality_scorer.py includes some town name. Suggest removing the following from unit_patterns[] and do pattern matching on town names in town_zipcodes[] in extract_hne_towns.py to better determine QUALITY_PERSONAL_EMAIL result - town names are NOT personal.
            r'sudbury',
            r'westford',
            r'harvard',
            r'concord'