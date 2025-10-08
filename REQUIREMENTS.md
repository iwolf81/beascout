# BeAScout System - Business Requirements and Acceptance Criteria

## Executive Summary

**System Purpose**: Automated data quality monitoring platform for Heart of New England Council that processes Scout unit information from beascout.scouting.org and joinexploring.org to generate quality reports and improvement recommendations.

**Business Goals**: 
- Achieve 100% coverage of all 71 HNE Council zip codes
- Ensure comprehensive unit presence correlation between Council Office's authoritative unit registry and web platforms to identify missing web presence and potentially defunct units
- Provide actionable quality improvement guidance to unit leaders
- Generate professional reports for district commissioners

**Current Performance**: Complete unit correlation analysis (165 of 169 Key Three units matched), processing all HNE units across 71 zip codes with 60.2% average quality score

---

## 1. Data Collection Requirements

### REQ-001: Multi-Source Data Acquisition
**Business Need**: Comprehensive unit data collection from primary Scout registration platforms
**Functional Requirements**:
- Process all 71 HNE Council zip codes from `data/zipcodes/hne_council_zipcodes.json`
- Collect data from BeAScout.org (10-mile radius per zip code)
- Collect data from JoinExploring.org (20-mile radius per zip code)
- Support all unit types: Packs, Troops, Crews, Ships, Posts, Clubs

**Performance Requirements**:
- Complete 71-zip processing within 75 minutes
- Implement 8-12 second delays between requests with randomization
- Maximum 8 requests per browser session to prevent blocking
- Handle network failures with exponential backoff retry (3 attempts max)

**Acceptance Criteria**: AC-001 through AC-008

### REQ-002: Data Integrity and Validation
**Business Need**: Ensure scraped data quality and completeness
**Functional Requirements**:
- Validate HTML structure and parseability
- Create timestamped data directories: `data/scraped/YYYYMMDD_HHMMSS/`
- Detect and handle corrupted or invalid HTML files
- Maintain audit trail of all scraping activities

**Acceptance Criteria**: AC-009 through AC-012

---

## 2. Territory Processing Requirements

### REQ-003: HNE Territory Identification
**Business Need**: Accurate identification of Heart of New England Council units only
**Functional Requirements**:
- Extract unit towns using position-first algorithm (handles hyphenated towns correctly)
- Apply four-source precedence: unit_address → unit_name → unit_description → chartered_org  
- Recognize all 65 HNE towns from `TOWN_TO_DISTRICT` mapping
- Handle town aliases and village processing (Fiskdale, Whitinsville, Jefferson)
- Filter out non-HNE units using state pattern recognition

**Data Quality Requirements**:
- Achieve ~165 unique HNE units from ~2,034 raw scraped units (92% filtering accuracy)
- Correctly assign units to Quinapoxet (29 towns) or Soaring Eagle (36 towns) districts
- Handle edge cases: "Acton-Boxborough" → "Acton", directional towns, village names

**Acceptance Criteria**: AC-013 through AC-020

### REQ-004: Data Consolidation and Deduplication  
**Business Need**: Eliminate duplicate units across multiple zip codes
**Functional Requirements**:
- Use unit_key format for cross-zip deduplication: `<unit_type> <unit_number> <town>`
- Retain best-quality unit when duplicates found
- Maintain unit identifier consistency (4-digit internal, display format for reports)
- Preserve data integrity during consolidation process

**Acceptance Criteria**: AC-021 through AC-025

---

## 3. Quality Assessment Requirements

### REQ-005: Business Rule Quality Scoring
**Business Need**: Standardized quality measurement aligned with Scouting best practices  
**Functional Requirements**:
- Required fields (100% of score): meeting_location, meeting_day, meeting_time, contact_email
- Specialized scoring: Crews include specialty field (5 fields × 20% each)
- Standard scoring: Other units (4 fields × 25% each) 
- Grade scale: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- Quality penalties: Half credit for PO Box locations, personal emails

**Business Intelligence Requirements**:
- Track informational fields without scoring impact: contact_person, phone_number, website, description
- Generate 10 human-readable recommendation categories
- Distinguish unit-appropriate vs personal contact emails

**Acceptance Criteria**: AC-026 through AC-036

### REQ-006: Email Classification System
**Business Need**: Identify unit continuity risks from personal email usage
**Functional Requirements**:
- Classify emails as unit-specific vs personal using multi-pass analysis
- Recognize unit numbers and role indicators in email addresses  
- Flag personal identifier patterns (names, initials)
- Handle complex edge cases per 5-pass manual review validation

**Examples**:
- Unit-specific: "sudburypack62@gmail.com", "scoutmaster130@gmail.com" → GOOD
- Personal: "john.smith@gmail.com", "smbrunker.troop1acton@gmail.com" → QUALITY_PERSONAL_EMAIL

**Acceptance Criteria**: AC-037 through AC-042

---

## 4. Data Validation Requirements

### REQ-007: Unit Presence Correlation and Gap Analysis
**Business Need**: Ensure comprehensive correlation between Council Office's authoritative unit registry and web platforms to identify missing web presence and potentially defunct units
**Functional Requirements**:
- Load Key Three database (169 units with member contact information) as authoritative unit registry
- Cross-reference with scraped web data using normalized unit_key matching
- Achieve complete correlation processing (165/169 units matched with web data, identifying gaps)
- Identify missing web presence units with actionable contact information for outreach
- Detect potentially defunct units appearing on web platforms but not in Key Three registry

**Gap Analysis Requirements**:
- Generate specific unit lists for Council Office action:
  - Missing Web Presence Units: Known active units (Key Three) lacking beascout.org/joinexploring.org visibility
  - Potentially Defunct Units: Web-listed units not in current Key Three registry requiring removal verification
- Preserve Key Three member details (up to 3 per unit) for direct unit contact
- Use town-to-district mapping instead of Key Three district data
- Maintain format consistency throughout processing pipeline

**Current Status**: ✅ IMPLEMENTED - Complete three-way validation system with unit presence correlation and gap analysis

**Acceptance Criteria**: AC-043 through AC-054

---

## 5. Report Generation Requirements

### REQ-008: Commissioner Quality Reports
**Business Need**: Professional Excel reports for district leadership decision-making
**Functional Requirements**:
- Generate timestamped reports: `BeAScout_Quality_Report_YYYYMMDD_HHMMSS.xlsx` and weekly reports: `BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.xlsx`
- Create separate sheets for Quinapoxet and Soaring Eagle districts
- Include professional formatting: borders, frozen panes, optimal column widths
- Display quality scores numerically with letter grades
- Integrate Key Three contact information (up to 3 members per unit)
- Populate zip code data based on unit town mapping
- Translate recommendation tags to human-readable improvement suggestions

**Current Status**: ✅ IMPLEMENTED - Professional Excel reports with district sheets, quality grades, Key Three contacts, and zip code integration

**Acceptance Criteria**: AC-055 through AC-062

### REQ-009: Unit Improvement Email System
**Business Need**: Personalized communication to unit leaders with specific improvement guidance
**Functional Requirements**:
- Generate individual markdown emails for units with identified improvement opportunities
- Include unit-specific recommendations with actionable steps
- Integrate accurate Key Three contact information
- Support both real and anonymized data for development safety
- Format emails ready for sending with proper structure
- Output filename pattern: `{UnitType}_{UnitNumber}_{UnitTown}_beascout_improvements.md`

**Current Status**: ✅ IMPLEMENTED - 169 personalized markdown emails generated with actual Key Three contact information

**Acceptance Criteria**: AC-063 through AC-069

### REQ-019: Professional PDF Unit Communications
**Business Need**: Printable, professionally-branded unit improvement handouts for in-person distribution
**Functional Requirements**:
- Convert markdown unit emails to PDF documents with professional formatting
- Include Heart of New England Council branding header with Scouting America identity
- Display unit identification in header: "{Unit Type} {Unit Number} {Unit Town}"
- Apply consistent visual styling: 14pt headers, Scouting America brand colors (#003f87 blue, #ce1126 red)
- Strip email metadata (TO:/FROM:/SUBJECT:) from PDF while preserving in markdown
- Remove emoji symbols to prevent Adobe font embedding errors
- Support council contacts display in two-column table format from `email_distribution.json`
- Generate matching PDF for each markdown file: `{UnitType}_{UnitNumber}_{UnitTown}_beascout_improvements.pdf`

**PDF Header Format**:
```
Heart of New England Council, Scouting America
Be A Scout Improvements
{Unit Type} {Unit Number} {Unit Town}
─────────────────────────────── [red separator]
```

**Technical Requirements**:
- Professional typography with readable 10pt body font
- Standard letter size (8.5" × 11") with 0.5in top/bottom, 0.75in left/right margins
- Compact spacing for efficient content presentation
- WeasyPrint-based HTML/CSS to PDF conversion

**Current Status**: ✅ IMPLEMENTED - Professional PDF generation with council branding

**Acceptance Criteria**: AC-136 through AC-145

---

## 6. System Architecture Requirements

### REQ-010: Pipeline Integration and Reliability
**Business Need**: Robust, maintainable system architecture supporting operational use
**Functional Requirements**:
- Execute complete pipeline: scraping → processing → analysis → reports without manual intervention
- Maintain comprehensive debug logging with audit trails and source identification
- Implement error handling preventing data corruption from pipeline failures
- Organize code in clean operational structure: `src/pipeline/` vs `src/dev/`
- Maintain single source of truth for all configuration mappings
- Support execution from different contexts with stable import paths

**Acceptance Criteria**: AC-070 through AC-076

### REQ-011: Performance and Scalability
**Business Need**: Efficient processing of full HNE Council dataset
**Performance Requirements**:
- Complete 71-zip processing within 75 minutes (conservative scraping pace)
- Maintain stable memory usage during large dataset processing  
- Keep debug log files manageable (<100MB per processing run)
- Handle JSON file I/O without timeouts or corruption
- Implement proper browser automation cleanup preventing resource leaks
- Support concurrent file access safely during report generation

**Acceptance Criteria**: AC-077 through AC-082

---

## 7. Security and Privacy Requirements

### REQ-012: Data Protection and Development Safety
**Business Need**: Responsible handling of personal information with secure development practices
**Functional Requirements**:
- Provide anonymized test data maintaining structural compatibility with real data
- Ensure email generation works identically with real and anonymized data
- Prevent real contact information from appearing in committed code
- Default development workflow to test data usage
- Require explicit flags/parameters for production mode real data access
- Complete two-step anonymization workflow (Excel anonymization → JSON conversion)

**Current Status**: ✅ IMPLEMENTED - Complete anonymization framework with dedicated workflow documentation (see KEY_THREE_ANONYMIZATION_WORKFLOW.md)

**Privacy Requirements**:
- Limit real Key Three data processing to local environment only
- Include only authorized council member information in generated reports
- Validate email addresses as unit-appropriate before inclusion
- Exclude personal information from debug files and audit trails
- Follow established council data retention policies

**Acceptance Criteria**: AC-083 through AC-093

---

## 8. Quality Assurance Requirements

### REQ-013: Regression Prevention and Reference Testing
**Business Need**: Maintain system reliability and prevent functionality degradation
**Functional Requirements**:
- Implement reference file comparison showing zero regressions in HNE unit identification
- Validate unit extraction changes against known good results
- Provide debug log comparison tools detecting processing changes accurately
- Maintain reference testing catching format changes in unit identifiers
- Validate quality scoring changes against manual review baselines
- Test town extraction modifications against edge case library

**Data Isolation Requirements**:
- Regression tests use separate output directories to prevent contaminating production data
- Validation output: `data/output/regression/enhanced_three_way_validation_results.json` (vs production: `data/output/enhanced_three_way_validation_results.json`)
- Report output: `data/output/regression/reports/*.xlsx` (vs production: `data/output/reports/*.xlsx`)
- Email output: `data/output/regression/unit_emails/*.md` (vs production: `data/output/unit_emails/*.md`)
- All regression test scripts support `--output` and `--output-dir` flags for path isolation
- Production data remains unchanged during regression test execution

**Automated Testing Requirements**:
- Complete regression test suite: `python tests/run_regression_tests.py`
- Six automated test steps: process dataset, unit processing regression, three-way validation, validation regression, commissioner report, Excel regression
- Support unit-only testing for faster development cycles: `--unit-only` flag
- Detailed logging with session correlation: `--log` flag
- Clear PASS/FAIL reporting with comprehensive file tracking

**Issue Tracking Requirements**:
- Systematic development planning through GitHub issues management system
- Production-ready v1.0.0 milestone achieved with complete core functionality
- Handle known edge cases consistently (e.g., Pack 148 East Brookfield website validation)
- Ensure personal email detection improvements don't introduce false positives
- Maintain existing accuracy in website validation enhancements
- Track discard regression for non-HNE unit processing changes

**Current Status**: ✅ IMPLEMENTED - Complete regression testing framework with data isolation and automated test runner

**Acceptance Criteria**: AC-094 through AC-104, AC-146 through AC-152

---

## 9. User Experience Requirements

### REQ-014: Commissioner Workflow Support
**Business Need**: Clear, actionable information enabling effective council leadership
**Functional Requirements**:
- Generate Excel reports opening cleanly in Microsoft Excel with proper formatting
- Enable district commissioners to identify priority units for follow-up
- Provide clear quality performance indicators using A-F grade scale
- Translate improvement recommendations to specific action items
- Clearly identify missing units with contact information for outreach
- Include zip code links enabling direct BeAScout/JoinExploring searches

**Acceptance Criteria**: AC-105 through AC-110

### REQ-015: Key Three Communication Excellence
**Business Need**: Effective unit leader communication driving quality improvements
**Functional Requirements**:
- Focus email recommendations on highest-impact improvements first
- Provide specific, actionable improvement steps in clear language
- Include contact information enabling direct follow-up by commissioners
- Demonstrate system understanding of individual unit needs through unit-specific content
- Avoid technical jargon in all user-facing communications

**Acceptance Criteria**: AC-111 through AC-115

### REQ-018: Weekly Automated Reporting Pipeline
**Business Need**: Streamlined weekly report generation for Council leadership distribution
**Functional Requirements**:
- Execute complete end-to-end pipeline: scraping → processing → validation → reporting → analytics → email drafts
- Generate weekly Excel reports with consistent naming: `BeAScout_Weekly_Quality_Report_YYYYMMDD_HHMMSS.xlsx`
- Create week-over-week analytics comparing quality metrics and unit improvements
- Generate copy/paste email drafts with recipient lists, subject lines, and formatted statistics
- Support stage-based execution with error recovery and resume capabilities
- Maintain accurate data timestamps throughout pipeline stages

**Current Status**: ✅ IMPLEMENTED - Complete automated weekly pipeline with analytics and email generation (see WEEKLY_REPORT_WORKFLOW.md)

**Acceptance Criteria**: AC-128 through AC-135

---

## 10. Production Deployment Requirements

### REQ-016: Production Environment Readiness
**Business Need**: Reliable production deployment and operational management
**Functional Requirements**:
- Support clean directory structure for container deployment (`src/pipeline/` only)
- Provide configuration management supporting different environment settings
- Ensure consistent package versions through dependency management
- Generate adequate production troubleshooting information through error logging
- Implement resource cleanup preventing memory/disk space leaks in long-running deployments
- Maintain backup and recovery procedures preserving data integrity
- Support rollback to previous stable states through version control

**Acceptance Criteria**: AC-116 through AC-122

### REQ-017: Operational Monitoring and Visibility
**Business Need**: System health visibility and operational intelligence
**Functional Requirements**:
- Report clear success/failure metrics after each processing run
- Provide processing statistics enabling capacity planning and optimization
- Log error conditions with sufficient detail for troubleshooting
- Generate data quality metrics enabling trend analysis over time
- Provide system performance metrics supporting optimization decisions

**Acceptance Criteria**: AC-123 through AC-135 (expanded to include weekly automation requirements)

---

## Success Metrics

### Quantitative Targets - ACHIEVED
- **Data Coverage**: ✅ 100% of 71 HNE Council zip codes processed successfully
- **Validation Accuracy**: ✅ Complete cross-validation with comprehensive gap analysis (165/169 units matched)
- **Processing Efficiency**: ✅ Complete full dataset processing within 90-120 minutes
- **Quality Assessment**: ✅ Generate quality scores for 100% of web-active units (60.2% average)
- **Territory Accuracy**: ✅ Correctly identify and filter HNE units (165 units from 2,034 raw)

### Qualitative Targets - ACHIEVED
- **Commissioner Satisfaction**: ✅ Professional Excel reports with district organization and Key Three integration
- **Unit Leader Engagement**: ✅ 169 personalized improvement emails generated with specific recommendations
- **System Reliability**: ✅ Complete pipeline integration with comprehensive error handling
- **Operational Maintainability**: ✅ Clean `src/pipeline/` architecture with single source of truth mappings
- **Development Safety**: ✅ Complete anonymization framework with safe test data
- **Weekly Automation**: ✅ Automated weekly reporting pipeline with analytics and email draft generation

---

## Risk Assessment

### High-Risk Areas
1. **Website Structure Changes**: BeAScout/JoinExploring HTML format modifications
2. **Rate Limiting**: Excessive request frequency causing IP blocking
3. **Data Corruption**: Processing errors affecting data integrity
4. **Personal Information Exposure**: Accidental inclusion of real contact data in development

### Mitigation Strategies - IMPLEMENTED
1. **Conservative Scraping**: ✅ 8-12 second delays, session limits, retry logic with fallback mechanisms
2. **Reference Testing**: ✅ Complete regression framework with reference data pipeline (REGRESSION_TEST_PIPELINE.md)
3. **Backup Procedures**: ✅ Data preservation, version control, and rollback capabilities
4. **Anonymization Framework**: ✅ Complete two-step anonymization with dedicated workflow documentation
5. **Weekly Automation**: ✅ Error recovery, stage-based execution, and resume capabilities

---

## Compliance and Governance

### Data Handling Standards
- Heart of New England Council data governance policies
- Scouting America privacy guidelines
- Local development environment security requirements
- Version control and backup retention standards

### Quality Standards
- >95% acceptance test pass rate for production deployment
- Zero critical defects in production release
- Comprehensive documentation for all business rules and processes
- Full audit trail for all data processing activities

---

## Acceptance Criteria Appendix

### REQ-019: Professional PDF Unit Communications (AC-136 through AC-145)

**AC-136**: System generates PDF file for each markdown unit email with matching base filename
**AC-137**: PDF includes Heart of New England Council branding header with three-line format
**AC-138**: Header displays unit identification: "{Unit Type} {Unit Number} {Unit Town}"
**AC-139**: PDF applies Scouting America brand colors: #003f87 (blue), #ce1126 (red)
**AC-140**: Email metadata (TO:/FROM:/SUBJECT:) stripped from PDF content
**AC-141**: Emoji symbols removed from PDF to prevent Adobe font errors
**AC-142**: Professional typography with 14pt headers and 10pt body text
**AC-143**: Council contacts from `email_distribution.json` displayed in two-column table
**AC-144**: PDF uses standard letter size with 0.5in/0.75in margins
**AC-145**: Generated PDFs open correctly in Adobe Reader and Apple Preview

### REQ-013: Regression Testing Enhancement (AC-146 through AC-152)

**AC-146**: Regression tests write to `data/output/regression/` directories, not production paths
**AC-147**: `three_way_validator.py` supports `--output` flag for custom validation output path
**AC-148**: `generate_commissioner_report.py` supports `--output-dir` flag for custom report directory
**AC-149**: `generate_unit_emails.py` supports `--output-dir` flag for custom email directory
**AC-150**: Automated test runner (`tests/run_regression_tests.py`) executes all 6 test steps successfully
**AC-151**: Regression test suite reports clear PASS/FAIL status for each step
**AC-152**: Production data files remain unchanged after regression test execution

---

This requirements document provides the foundation for systematic acceptance testing, ensuring all business needs are met while maintaining operational reliability and data security.