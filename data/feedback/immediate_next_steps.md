# Immediate Next Steps

1. Modify email generation.
   1. Include town name in unit_identifier to units missing in beascout.org/joinexploring.org.
   2. Remove JSON files as an key_three_file input option for generate_all_unit_emails.py.
      1. This is unneeded legacy functionality.
   3. Rename <Unit type>_<Unit number>_URGENT_setup_email.md to <Unit type>_<Unit number>_<Unit town>_setup_email.md
2. Clean up code base in preparation for developing unit tests.
   1. Identify duplication of data and processing.
      1. Create restructuring plans but do not yet execute them.
   2. Remove _vN suffixes from file names and function names.
   3. Archive or remove code no longer used by pipeline.
   4. Archive source files not used by pipeline.
   5. Archive test scripts associated with code that is no longer current.
3. Update all documentation.
4. Export defect reports to beascout project in github.
5. Create Key Three test data (Excel spreadsheet) that replaces only names, emails, and phone numbers with random information
   1. Goal is to remove identifiable person information while preserving all other unit information.
   2. Format phone numbers with Massachusetts area codes and 555 exchange (e.g., 617-555-1234, 978-555-6789).
   3. Create reference file for BeAScout_Quality_Report spreadsheet with Key Three test data.
      1. This will be used for all development
6. Improve reference data and tests.
   1. Identify what reference data is and is not used.
   2. Identify what reference tool is and is not used.
   3. Create reference test for BeAScout_Quality_Report spreadsheet with Key Three test data.
7. Create automated regression testing.
   1. Integrate udiff2 alias to automatically test for HTML parsing regressions with any parsing code change.
      1. dudiff2 alias must await fix to discard town names.
   2. Create regression test for BeAScout_Quality_Report spreadsheet.
8.  