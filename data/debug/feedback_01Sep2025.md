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
