# Exception for Troop 0132 Upton

## beascout_01590.html contains Troop 0132 Upton with a unit-address of Mendon:
- Mendon and Upton are adjacent towns.
- Upton is an HNE town while Mendon is not
- Troop 0132 Upton likely had to move their meeting location to nearby Mendon
- Troop 0132 Upton remained an HNE troop

<div class="unit-name">
          <h5>Troop 0132 Upton - St. Gabriel the Archangel Parish<br>
<div class="unit-address">
          Miscoe Hill Middle School<br>148 North Ave<br>Mendon MA 01756        </div>            

## unit_town parsing exception
- The current precedence parsing for Troop 0132 Upton would identify the town being Mendon.
  - With Mendon being a non-HNE town, the troop is filtered out
- An exception must be made for Troop 0132 Upton to have a unit_town of Upton and not be filtered out.
