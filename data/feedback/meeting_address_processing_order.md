# meeting_address

## QUALITY_ADDRESS_EMPTY 

1. QUALITY_ADDRESS_EMPTY means meeting_address was found in scraped HTML data for unit, but not in scraped unit-address field where it should be.
2. QUALITY_ADDRESS_EMPTY was added to recommendation_map but not yet implemented.

## Update Processing Order:

1. Extract from <div class="unit-address"> HTML element.
2. If unit-address empty, set new QUALITY_ADDRESS_EMPTY flag and attempt to extract meeting_address from unit description text (comprehensive pattern matching)
3. If meet_address still not extracted, fallback to searching for address patterns in full unit text
4. If meet_address still not extracted, overwrite QUALITY_ADDRESS_EMPTY flag with REQUIRED_MISSING_LOCATION flag
