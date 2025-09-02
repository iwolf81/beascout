Two two of the  units missing from scraped HTML data are being discarded because their town were determined to be "North Grafton", which is currently not an HNE town nor village. "North Grafton was correctly parsed from their unit-address value:

(venv) iwolf@Iras-MacBook-Pro debug % grep -E "(1924.*Rutland|2254.*Rutland|0003.*Leominster|0106.*Grafton|0161.*Fiskdale)"  discarded_unit_identifier_debug_scraped_20250829_212854_u.log
  unit_type: 'Pack',   unit_number: '0106',   unit_town: 'North Grafton',   chartered_org: 'Grafton - Our Lady of Hope Parish Grafton @ St. Mary',   reason: 'Invalid town: North Grafton not in HNE territory'
  unit_type: 'Troop',   unit_number: '0106',   unit_town: 'North Grafton',   chartered_org: 'Grafton - Our Lady of Hope Parish Grafton @ St. Mary',   reason: 'Invalid town: North Grafton not in HNE territory'
(venv) iwolf@Iras-MacBook-Pro debug % 

In the key three data, these two units are identified as "Troop 0106 Grafton" and "Pack 0106 Grafton" in their unitcommorgname values.

I think the solution is to map the parsed town name of "North Grafton" to the unit_town name of "Grafton", similarly as "N Brookfield" is mapped to "North Brookfield". This would permit the joining of scraped HTML unit data with parsed Key Three unit data to correctly match on unit type, unit number, and unit town.
