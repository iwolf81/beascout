# Missing Content

1. Change flag CONTENT_MISSING_DESCRIPTION to RECOMMENDED_MISSING_DESCRIPTION
   1. If the all the meeting info and contact info is present, a description may be nice but not necessary, hence it is RECOMMENDED.
   2. Do not apply a penalty if not presents.
2. The CONTENT_MISSING_DESCRIPTION flag is not being applied consistently.
   1. For example, in beascout_01612.html, the following units do not have a <div class="unit-description"> block within <div class="card-body> :
      1. Pack 0007 Clinton
      2. Troop 0141 Rutland 
   2. Units without <div class="unit-description"> should be tagged with RECOMMENDED_MISSING_DESCRIPTION (formerly CONTENT_MISSING_DESCRIPTION)
   