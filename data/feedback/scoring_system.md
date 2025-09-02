# Quality Scoring System

1. Each unit starts off with 100 points.
2. Points are deducted when required information is not present or it does not meet quality standards.
3. There are four REQUIRED_xxx tags for Packs, Troops, Club, Posts as defined in quality_scorer.py:
        Unit Field:         Corresponding Tag:
        meeting_location    'REQUIRED_MISSING_LOCATION': "Add meeting location with street address.",
        meeting_day         'REQUIRED_MISSING_DAY': "Add meeting day(s) to description.",
        meeting_time         REQUIRED_MISSING_TIME': "Add meeting time(s) to description.",
        contact_email       'REQUIRED_MISSING_EMAIL': "Add contact email address.",
4. Crews have a fifth REQUIRED_xxx tag:
        specialty           'REQUIRED_MISSING_SPECIALTY': "Add specialty information for Venturing Crew.",
5. The REQUIRED_xxx tags have equal value totaling 100 points for each unit type (e.g. REQUIRED_MISSING_DAY is worth 25 points for a Troop and 20 points for a Crew)
6. The value of the REQUIRED_xxx tag for a unit type, when assigned to a unit, is deducted from that unit's score.
7. There are three QUALITY_xxx tags for all unit types:
        Unit Field:         Corresponding Tag:
        meeting_location    'QUALITY_POBOX_LOCATION': "Replace PO Box with physical meeting location.",
            - Derived meeting location has an PO BOX but not a street/town address
        contact_email       'QUALITY_PERSONAL_EMAIL': "Use unit-specific email instead of personal email.",
            - Derived contact email is not unit-specific (e.g., irawolf81@gmail.com vs troop12acton@gmail.com)
        meeting_location    'QUALITY_UNIT_ADDRESS': "Meeting location should be in address field, not description.",
            - The scraped unit-address field is empty; meeting_location derived from description
8. Each QUALITY_xxx deducts 50% of the value of their corresponding field (e.g., QUALITY_UNIT_ADDRESS is worth 12.5 points for a Pack and 10 points for a Crew)
9. There are three RECOMMENDED_xxx tags for all unit types:
        Unit Field:         Corresponding Tag:
        contact_person.     'RECOMMENDED_MISSING_CONTACT': "Add contact person name.",
        contact_phone.      'RECOMMENDED_MISSING_PHONE': "Add contact phone number.",
        website             'RECOMMENDED_MISSING_WEBSITE': "Add unit-specific website.",
10. The RECOMMENDED_xxx tags do not affect the quality score for a unit. They informational and are presented in quality reports and emails.
11. quality_scorer.py appears to have implemented these rules, but verification is required.