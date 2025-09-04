# Feedback 01Sep2025

## Pass 1
1. No regressions for identifying the 165 HNE units
2. There are still multiple discarded logs, this time three:
-rw-r--r--  1 iwolf  staff    5111 Sep  1 11:56 discarded_unit_identifier_debug_scraped_20250901_115602.log
-rw-r--r--  1 iwolf  staff    7744 Sep  1 11:56 discarded_unit_identifier_debug_scraped_20250901_115603.log
-rw-r--r--  1 iwolf  staff   84403 Sep  1 11:56 discarded_unit_identifier_debug_scraped_20250901_115604.log
3. There as still a few parsing town errors in the discard logs
  unit_type: 'Pack',   unit_number: '0001',   unit_town: 'We meet Mondays from 6',   chartered_org: 'Burrillville Prevention Action Coalition',   reason: 'Non-HNE unit filtered out (town: we meet mondays from 6)'
  unit_type: 'Pack',   unit_number: '0033',   unit_town: 'We are an active Pack accepting children in Grades K',   chartered_org: 'John Humiston Post 11 American Legion',   reason: 'Non-HNE u
  nit filtered out (town: we are an active pack accepting children in grades k)'
  unit_type: 'Troop',   unit_number: '0001',   unit_town: 'American Legion Post 355',   chartered_org: 'American Legion Post 355 - Roger L Wood',   reason: 'Non-HNE unit filtered out (town: american legion post 355)'
  unit_type: 'Troop',   unit_number: '0001',   unit_town: 'Troop 1 Pascoag was the first established Boy Scout Troop in Burrillville. We meet Mondays from 7',   chartered_org: 'Burrillville Prevention Action Coalition',   reason: 'Non-HNE unit filtered out (town: troop 1 pascoag was the first established boy scout troop in burrillville. we meet mondays from 7)'
  unit_type: 'Troop',   unit_number: '0019',   unit_town: 'Daniel Webster Council',   chartered_org: 'Daniel Webster Council',   reason: 'Non-HNE unit (outside council territory)'
  unit_type: 'Troop',   unit_number: '0252',   unit_town: 'Contact:Christopher FunkPhone:(603) 960',   chartered_org: 'StKathryns Roman Catholic Church',   reason: 'Non-HNE unit filtered out (town: contact:christopher funkphone:(603) 960)'
  unit_type: 'Troop',   unit_number: '0308',   unit_town: 'Dedicated to the vision of Lord Baden',   chartered_org: 'Mens Club Of First Congregational Church',   reason: 'Non-HNE unit filtered out (town: dedicated to the vision of lord baden)'
  unit_type: 'Troop',   unit_number: '0773',   unit_town: 'Troop 773 is a boy',   chartered_org: 'St. Christopher Parish',   reason: 'Non-HNE unit filtered out (town: troop 773 is a boy)'
4. With improved discard logging, some HNE-units appear to be incorrectly filtered out:
  unit_type: 'Troop',   unit_number: '0118',   unit_town: 'W Brookfield',   chartered_org: 'W Brookfield - Our Lady of The Sacred Heart',   reason: 'Non-HNE unit filtered out (town: w brookfield)'
  unit_type: 'Pack',   unit_number: '0148',   unit_town: 'E Brookfield',   chartered_org: 'E Brookfield - Baptist Church',   reason: 'Non-HNE unit filtered out (town: e brookfield)'
  unit_type: 'Troop',   unit_number: '0118',   unit_town: 'W Brookfield',   chartered_org: 'W Brookfield - Our Lady of The Sacred Heart',   reason: 'Non-HNE unit filtered out (town: w brookfield)'
  unit_type: 'Troop',   unit_number: '0151',   unit_town: 'W Boylston',   chartered_org: 'W Boylston - Masonic Charityand Education Assoc. Inc',   reason: 'Non-HNE unit filtered out (town: w boylston)'

## Pass 2

1. There is now correctly one discard log.
2. Town names in discard log are now mostly legit, except for "Daniel Webster Council" and "American Legion Post 355".
3. There are 42 units in discard log without town names.
iwolf@Iras-MacBook-Pro debug % grep "unit_town: \'\'." discarded_unit_identifier_debug_scraped_20250901_121905_u.log | wc -l > discarded_unit_identifier_debug_scraped_20250901_121905_null_towns.log

## Pass 3 - Report Generation Feedback

1. These are likely personal emails (do NOT work too much on solving this; it's not worth effort)
Pack 158 Shrewsbury | CubMasterMaggie@gmail.com
Troop 1 Acton | smbrunker.troop1acton@gmail.com

2. This is a personal email
Troop 180 Holden | straightshooters@mail.com

3. Bad parsing of meeting times:
Troop 7338 Charlton | 73:38 AM (invalid)
Pack 37 Worcester | 10:52 PM (unlikely)
Troop 1 Princeton | 00:01 PM (unlikely)
Pack 16 Athol | 16:00 AM (Should this be 4PM?)
Troop 243 Sutton | 7:00 AM - 8:30 AM (This should be PM, not AM)
Troop 6 Gardner | 7:00 AM - 8:30 AM (This should be PM, not AM)
Pack 1455 Pepperell | 5:00 AM (This should be PM, not AM))
Troop 1 Acton | 1:00 AM (unlikely )
Troop 1 Boxborough | 7:00 AM - 8:30 AM (This should be PM, not AM))

4. Bad parsing of meeting location
Ship 1935 Webster | 4 Bates Point Road in Webster. Our off season meetings are at the 200 Sportsmans Club also in Webster. We meet weekly on Tuesday nights starting at 6:30 PM. We also get together on weekends for all kinds of fun activities Apply Now More Information

5. Column Enumerations
Are columns enumerated such that they can be moved around by simply changing their position value in one location in code? This is, column values in code are not hard coded but reference an enumerated value

6. Links to beascout.scouting.org and joinexploring.org
Can the value under Zip Code column be links to the correct beascout.scouting.org or joinexploring.org search page for the unit type and zip code?
Think about how to do this, but don't implement changes in code.

### Review of Time Fixes

     📝 MEETING TIME CHANGES:
     ================================================================================
     UNIT IDENTIFIER                          OLD TIME             NEW TIME Status/Description
     ================================================================================
     Pack 123 Leicester                       6:00 PM              (6pm- 7pmx) <p>Meeting Wednesday nights from 6pm - 7pm during the school year.</p>
     Pack 1455 Pepperell                      5:00 AM              (none) ok
     Pack 16 Athol                            16:00 AM             (none) ok
     Pack 37 Worcester                        10:52 PM             (none) ok
     Pack 62 Shrewsbury                       8:00 PM              (7-8pm) <p>Pack meetings - 7-8pm at Ray Stone Post
Full agenda: <a href="https://docs.google.com/document/d/1FJG-Fclr3L2olU9wD5c7zRPzzpxYVCDa/edit">https://docs.google.com/document/d/1FJG-Fclr3L2olU9wD5c7zRPzzpxYVCDa/edit</a></p>
     Troop 1 Acton                            1:00 AM              (none) ok
     Troop 1 Princeton                        00:01 PM             (none) ok
     Troop 281 Ware                           6:00 PM              (6PM) <p>We are a youth-led program with a very active outdoor program. Meet on Tuesdays 6PM at the American Legion Hall in Ware. </p>
     Troop 7054 Worcester                     8:00 PM              (6:30-8 pm) <p>The Troop meets on Tuesdays from 6:30-8 pm.</p>
     Troop 7163 Fiskdale                      6:00 PM              (4-6 pm) <p>Scouts BSA Troop 163 is a premier Scout Troop for girls.  We meet on Sundays from 4-6 pm, and have monthly camping trips or day activities.  We're a fun and inclusive group, come check us out, we'd love to have you!</p>
     Troop 7338 Charlton                      73:38 AM             (none) ok
     ================================================================================
