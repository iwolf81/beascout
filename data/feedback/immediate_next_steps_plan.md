  Execution Plan for Immediate Next Steps                                                                                                    
                                                                                                                                             
  PHASE 1: Email Generation Improvements (Items 1.2, 1.3)                                                                                    
                                                                                                                                             
  Status: Item 1.1 already completed ✅                                                                                                       
                                                                                                                                             
  1.2 Remove JSON support from Key Three input                                                                                               
                                                                                                                                             
  - File: src/pipeline/reporting/generate_unit_emails_v2.py                                                                                  
  - Action: Remove JSON file handling in load_key_three_data() method                                                                        
  - Scope: Lines ~82-86 and help text line ~562                                                                                              
  - Rationale: Eliminate legacy functionality, force Excel input to prevent stale data                                                       
                                                                                                                                             
  1.3 Update missing unit email filenames                                                                                                    
                                                                                                                                             
  - File: src/scripts/generate_all_unit_emails.py                                                                                            
  - Current: Pack_0161_URGENT_setup_email.md                                                                                                 
  - Target: Pack_161_Fiskdale_setup_email.md                                                                                                 
  - Action: Modify filename generation logic to include town and remove "URGENT"                                                             
                                                                                                                                             
  PHASE 2: Codebase Cleanup (Item 2)                                                                                                         
                                                                                                                                             
  2.1 Data Duplication Analysis                                                                                                              
                                                                                                                                             
  - Create analysis document identifying:                                                                                                    
    - Duplicate processing between src/legacy/ and src/pipeline/  @claude - src/legacy should be unused. I'm concerned about duplicate processing within src/pipeline code.                                                                           
    - Redundant data structures across modules @claude - again, examine active pipeline code only. Should legacy be moved to archive directory?
    - Overlapping functionality in unit matching/filtering                                                                                   
  - Document restructuring plan without executing                                                                                            
                                                                                                                                             
  2.2 Remove _vN Suffixes                                                                                                                    
                                                                                                                                             
  Files to rename:                                                                                                                           
  - generate_unit_emails_v2.py → generate_unit_emails.py                                                                                     
  - process_full_dataset_v2.py → process_full_dataset.py                                                                                     
  - Update all imports and references                                                                                                        
  - Remove old pycache files                                                                                                                 
                                                                                                                                             
  2.3 Archive Unused Code                                                                                                                    
                                                                                                                                             
  Target directories:                                                                                                                        
  - Review src/legacy/ and src/archive/ for completeness @claude - see prior comments on src/legacy
  - Move unused pipeline scripts to appropriate archive locations                                                                            
  - Clean up test scripts from discontinued approaches                                                                                       
                                                                                                                                             
  PHASE 3: Documentation Update (Item 3)                                                                                                     
                                                                                                                                             
  - Update README.md with current pipeline architecture                                                                                      
  - Document new email generation system in SYSTEM_DESIGN.md                                                                                 
  - Update CLAUDE.md with new file structure                                                                                                 
  - Refresh code examples in documentation 
  - @claude - we need to examine all beascout/*.md file and update where needed, especially file hierarchy and pipeline execution commands
                                                                                                                                             
  PHASE 4: Test Data Creation (Item 5)                                                                                                       
                                                                                                                                             
  Key Three Test Spreadsheet                                                                                                                 
                                                                                                                                             
  - Input: data/input/Key 3 08-22-2025.xlsx                                                                                                  
  - Output: data/test/Key_Three_test_data.xlsx                                                                                               
  - Anonymization:                                                                                                                           
    - Replace names with realistic fake names                                                                                                
    - Generate MA area codes: 617-555-xxxx, 978-555-xxxx, 508-555-xxxx                                                                       
    - Replace emails with pattern: firstname.lastname@email.test                                                                             
    - Preserve all unit/organization data                                                                                                    
                                                                                                                                             
  PHASE 5: GitHub Issue Export (Item 4)                                                                                                      
                                                                                                                                             
  - Review current defect tracking                                                                                                           
  - Export issues from local tracking to GitHub Issues                                                                                       
  - Tag with appropriate labels (defect, enhancement, etc.)                                                                                  
                                                                                                                                             
  PHASE 6: Testing Infrastructure (Items 6, 7)                                                                                               
                                                                                                                                             
  Reference Data Audit                                                                                                                       
                                                                                                                                             
  - Identify used vs unused reference files in data/reference/                                                                               
  - Document current test coverage gaps                                                                                                      
  - Create regression test suite for BeAScout Quality Reports                                                                                
                                                                                                                                             
  Automated Testing                                                                                                                          
                                                                                                                                             
  - Implement udiff2 alias integration for HTML parsing regression detection                                                                 
  - Create automated test for email generation consistency                                                                                   
  - Set up CI/CD pipeline validation                                                                                                         
                                                                                                                                             
  Execution Priority:                                                                                                                        
                                                                                                                                             
  1. Phase 1 (immediate email improvements) - ~1 hour                                                                                        
  2. Phase 2 (code cleanup) - ~2-3 hours                                                                                                     
  3. Phase 4 (test data) - ~1 hour                                                                                                           
  4. Phase 3 (documentation) - ~1 hour                                                                                                       
  5. Phases 5-6 (issues/testing) - ~2 hours                                                                                                  
                                                                                                                                             
  Total Estimated Time: 7-8 hours across multiple sessions      