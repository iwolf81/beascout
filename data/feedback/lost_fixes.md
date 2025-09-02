The prior fixes for Post 1872 Douglas/Franklin and Troop 7102 Acton/Boxborough are no longer working.

iwolf@Iras-MacBook-Pro debug % diff unit_identifier_debug_scraped_20250828_085755_u.log unit_identifier_debug_scraped_20250828_110829_u.log 
56a57
>   unit_type: 'Post',   unit_number: '1872',   unit_town: 'Douglas',   chartered_org: 'Franklin Fire Department'
140c141
<   unit_type: 'Troop',   unit_number: '7012',   unit_town: 'Acton',   chartered_org: 'Acton-Group Of Citizens, Inc'
---
>   unit_type: 'Troop',   unit_number: '7012',   unit_town: 'Boxborough',   chartered_org: 'Acton-Group Of Citizens, Inc'
iwolf@Iras-MacBook-Pro debug % 