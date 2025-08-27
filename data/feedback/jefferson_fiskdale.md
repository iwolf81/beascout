# Exception Processing for Fiskdale and Jefferson Units

## Fiskdale

1. Fiskdale is a village within Sturbridge MA, which is an HNE town in the Soaring Eagle district.
2. 1. In the Key Three spreadsheet, there are three units in Fiskdale MA according to unitcommorgname column values:
   1. Pack 0161 Fiskdale
   2. Troop 0161 Fiskdale
   3. Troop 7163 Fiskdale.
3. The scraped data contains data for Troop 0161 Fiskdale and Troop 7163 Fiskdale but not Pack 0161 Fiskdale.
   1. Pack 0161 Fiskdale is not present in beascout search results.
4. The <div class="unit-address"> in the scraped data for both Fiskdale Troops contains Sturbridge as their town.
5. With the Key Three spreadsheet identifying these three units as Fiskdale units, they can only be correlated with units in the scraped data if the unit_town derived from the scraped data is Fiskdale and not Sturbridge.
6. The parsing of the unit town must make an exception to enable Fiskdale to supersede Sturbridge when <div class="unit-name"> contains Fiskdale.
7. Fiskdale should be defined as an HNE town in the Soaring Eagle district with zip code 01518.

## Jefferson

1. Jefferson is a village of Holden, MA, which is an HNE town.
2. In the Key Three spreadsheet, there is unit in Jefferson MA according to unitcommorgname column values:
   1. Pack 0046 Jefferson
3. Fortunately, <div class="unit-address"> and div class="unit-name"> for Pack 0046 Jefferson in the scraped data also specify Jefferson as the town.
4. Jefferson should be defined as an HNE town in the Quinapoxet District with zip code 01522
