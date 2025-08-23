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

# PASS 3

This is NOT a personal email. The search results included units from towns outside of Heart of New England Council, thus Sudbury is not present in town_zipcodes[]. 01720 is on boarder of HNE council. I am unsure how to best solve this.
28      sudburypack62@gmail.com                  QUALITY_PERSONAL_EMAIL   Pack 0062 St Elizabeth's Episcopal Church

These are not personal emails:
32      westfordpack100@gmail.com                QUALITY_PERSONAL_EMAIL   Pack 0100 Westford Rotary Club Inc
33      harvardcubpack10@gmail.com               QUALITY_PERSONAL_EMAIL   Pack 0010 Harvard-Boy Scouts Inc
44      cubscoutchelmsfordpack81@gmail.com       QUALITY_PERSONAL_EMAIL   Pack 0081 Chelmsford Land Conservation Trust Inc
50      ayerscouts@gmail.com                     QUALITY_PERSONAL_EMAIL   Pack 0032 Ayer-St Andrews Church

# PASS 4

This are personal emails. Recall that a personal reference in an email address overrides an otherwise unit-specific email thus it should be tagged as QUALITY_PERSONAL_EMAIL
4       smbrunker.troop1acton@gmail.com          GOOD                     Troop 0001 Acton-Group Of Citizens, Inc
21      anthony.nardone.scouts@gmail.com         GOOD                     Crew 1923 Troop One Stow Alumni Inc Specialty:  CA...

# PASS 5

These are not personal emails. Not that '130' in the email is the unit number. Should you search email for unit number, with and without leading zeros, to identify the found string as unit-specific and not personal? Note that the unit number could appear anywhere in the email address.
8       130scoutmaster@gmail.com                 QUALITY_PERSONAL_EMAIL   Troop 0130 Maynard Rod and Gun Club Inc.
39      troop195scoutmaster+beascout@gmail.com   QUALITY_PERSONAL_EMAIL   Troop 0195 Friends of Westford Scouting Inc