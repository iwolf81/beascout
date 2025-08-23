# BeAScout Unit Information System - Design Document

**Version:** 1.1 | **Last Updated:** 2025-08-22 | **Status:** Recommendation-First Strategy

## Document Control
- **Author:** Claude Code + Board Member
- **Reviewers:** Heart of New England Council Board Member
- **Approval Status:** Draft - Awaiting Review
- **Next Review Date:** TBD

---

## 1. Executive Summary

The BeAScout Unit Information System is designed to improve the quality and completeness of Scouting America unit information published on beascout.scouting.org and joinexploring.org for the Heart of New England Council (Massachusetts). The system will automate data collection, analysis, and monitoring to help prospective Scout families find complete and accurate unit information.

### Key Objectives
- **Immediate Value**: Build recommendation system using current 62 validated units
- **Quality Improvement**: Generate actionable improvement reports for Key Three members
- **Business Validation**: Prove concept effectiveness before scaling to full 72 zip codes
- **100% Coverage**: Process all 72 zip codes after recommendation system validation

### System Benefits
- **Immediate Impact**: Actionable recommendations for 62 units ready within days
- **Validation-First**: Prove business value before large-scale infrastructure investment
- **Key Three Engagement**: Direct unit leader communication with specific improvement guidance
- **Scalable Foundation**: Validated recommendation engine ready for full council expansion

---

## 2. System Architecture

### 2.1 Data Collection Pipeline

**Input Sources:**
- beascout.scouting.org (10-mile radius searches)
- joinexploring.org (20-mile radius searches)
- 72 zip codes across HNE Council territory

**Collection Strategy:**
- Conservative scraping approach to avoid blocking
- Respectful implementation honoring robots.txt and ToS
- Board member authority for legitimate data access
- Automated monitoring with manual backup procedures

### 2.2 Processing Components

**Data Extraction:**
- HTML parsing using BeautifulSoup
- Regex-based meeting information extraction (day/time/location)
- Field validation and quality scoring
- Duplicate detection across zip codes and platforms

**Data Storage:**
- JSON files for raw scraped data
- SQLite database for processed unit information
- Version control for tracking changes over time
- Backup and recovery procedures

**Analysis Engine:**
- Field completeness scoring by unit
- Geographic and temporal trend analysis
- Quality improvement tracking
- Anomaly detection for unusual changes

### 2.3 Monitoring & Reporting

**Automated Monitoring:**
- Periodic re-scraping of all zip codes
- Change detection and validation
- Alert system for significant updates
- Dashboard generation for Council office

---

## 3. Technical Requirements

### 3.1 Scraping Strategy

**Rate Limiting & Respect:**
- 8-12 second delays between requests (randomized)
- Maximum 8 requests per browser session
- 10-15 zip codes per day maximum
- Business hours only, avoid weekends
- Honor robots.txt and terms of service

**Detection Avoidance:**
- Real browser automation (Playwright)
- Randomized user agents and headers
- Human-like navigation patterns
- Session management and cookie handling

**Failure Recovery:**
- Exponential backoff on errors
- Session reset after failures
- 24-hour cooling periods for blocked requests
- Manual intervention protocols

### 3.2 Data Quality Standards

**Required Fields (Must Have):**
- Unit primary identifier (type, number, organization)
- Meeting location (not PO Box)
- Meeting day and time
- Contact email (unit-specific preferred)
- Unit composition (Boys/Girls/Coed)
- Specialty (Venturing Crews only)

**Recommended Fields (Should Have):**
- Contact person name
- Phone number
- Unit website
- Informative description

**Completeness Scoring (IMPLEMENTED):**
- **Required fields: 70% weight**
  - Non-Crew units (Packs, Troops, Ships): 17.5% each (location, day, time, email)
  - Crew units: 14% each (location, day, time, email, specialty)
- **Recommended fields: 30% weight**
  - 7.5% each (contact person, phone, website, description)
- **Quality Penalties**: Half credit for PO Box locations and personal emails
- **Grade scale**: A (90%+), B (80-89%), C (70-79%), D (60-69%), F (<60%)
- **Baseline Results (62 units)**: 56.3% average, 62.9% F grades

**Recommendation Identifier System:**
- Human-readable codes: `REQUIRED_MISSING_DAY`, `QUALITY_PERSONAL_EMAIL`, etc.
- Stored persistently with unit data for tracking over time
- Mapped to actionable improvement descriptions for Key Three emails

### 3.3 Deduplication Logic

**Primary Matching:**
- Exact primary identifier string comparison
- Format: "{Unit Type} {Number} {Chartered Organization}"

**Fallback Matching:**
- Unit type and number when organization names vary
- Geographic proximity validation
- Manual review for edge cases

**Conflict Resolution:**
- Flag units with inconsistent data across sources
- Prefer more complete information
- Document resolution decisions

---

## 4. Operational Workflows

### 4.1 Initial Data Collection (Weeks 1-6)

**Phase 1: Testing & Validation (Week 1)**
- Test scraping approach with 3 representative zip codes
- Validate extraction accuracy and completeness
- Adjust parameters based on initial results

**Phase 2: Primary Collection (Weeks 2-4)**
- Process 15-20 zip codes per week
- Daily monitoring of success rates and blocking indicators
- Generate interim reports for progress tracking

**Phase 3: Completion & Cleanup (Weeks 5-6)**
- Process remaining zip codes
- Retry any failed attempts with enhanced recovery
- Complete deduplication and data validation
- Generate baseline report for Council

### 4.2 Ongoing Monitoring System

**Re-scraping Schedule:**
- **Biweekly**: Complete re-scraping of all 72 zip codes
- **Monthly**: Deep analysis and strategic reporting
- **Quarterly**: Comprehensive system review and updates

**Change Detection:**
- Field-level comparison against baseline
- Quality score calculations and trending
- Duplicate detection across time periods
- Alert generation for significant changes

**Reporting Cadence:**
- **Weekly**: High-level status updates
- **Biweekly**: Detailed unit completeness reports
- **Monthly**: Strategic analysis and recommendations
- **Quarterly**: Executive summary and system metrics

### 4.3 Council Integration & Key Three Outreach

**Report Distribution:**
- Automated delivery to Council office
- Dashboard access for real-time monitoring
- Custom reports for district/unit levels

**"Carrot and Stick" Implementation:**
- **Recognition**: Highlight units with complete information
- **Accountability**: Scoreboard and charter review integration
- **Support**: Training and resources for improvement
- **Escalation**: Intensive intervention for persistent gaps

---

## 5. Success Metrics & KPIs

### 5.1 Primary Objectives (Non-negotiable)

**Coverage Requirements:**
- 100% zip code processing success rate
- 95%+ unit discovery rate (no missing active units)
- Zero blocking incidents or service disruptions

**Data Quality Targets:**
- 50%+ units with complete meeting information (day/time/location)
- 80%+ units with valid contact email addresses
- 90%+ reduction in duplicate unit entries

### 5.2 Operational Excellence

**System Performance:**
- 99%+ uptime for monitoring system
- <5% false positive rate on change detection
- 48-hour maximum delay from change to report update

**Council Impact:**
- 70%+ response rate from Key Three outreach
- +50% units reaching "complete" status within 6 months
- Positive feedback on report utility from Council office

### 5.3 Long-term Sustainability

**Maintenance Requirements:**
- Automated processing requiring <2 hours/week oversight
- Annual system review and parameter tuning
- Documentation updates and knowledge transfer

---

## 6. Implementation Timeline (Revised: Recommendation-First Strategy)

### Phase 1: Recommendation System (Days 1-3) ✅ COMPLETED
- [x] Complete data extraction system (62 units from ZIP 01720)
- [x] Build quality scoring algorithm with A-F grading
- [x] Implement recommendation identifier system with human-readable codes
- [x] Create enhanced personal email detection across all domains
- [x] Fix time parsing for 3-4 digit formats (330PM → 3:30PM)
- [ ] Design Key Three email templates and communication workflow

### Phase 2: Business Validation (Days 4-7)
- [ ] Generate prototype recommendation reports for 5-10 units
- [ ] Review business logic and scoring accuracy with Board member
- [ ] Refine recommendation templates based on feedback
- [ ] Validate Key Three communication approach

### Phase 3: Full Council Scaling (Weeks 2-4)
- [ ] Build conservative multi-zip scraping system
- [ ] Execute complete data collection across all 72 zip codes
- [ ] Apply validated recommendation system to complete dataset
- [ ] Generate comprehensive Council-wide quality analysis

### Phase 4: Council Deployment (Week 5)
- [ ] Deploy recommendation system to production workflow
- [ ] Launch Key Three outreach program with validated reports
- [ ] Train Council staff on system outputs and follow-up procedures
- [ ] Establish success metrics and tracking

### Phase 5: Operations (Ongoing)
- [ ] Monthly automated re-scraping and recommendation updates
- [ ] Quarterly system optimization and business logic refinement
- [ ] Biannual comprehensive Council quality analysis
- [ ] Annual comprehensive review

---

## 7. Risk Management

### 7.1 Technical Risks

**Website Blocking:**
- **Mitigation**: Conservative approach, respectful implementation
- **Recovery**: Board authority contact, manual collection backup
- **Monitoring**: Real-time detection of blocking indicators

**Data Quality Issues:**
- **Mitigation**: Multi-tier extraction approach (regex + manual review)
- **Recovery**: Volunteer verification network
- **Prevention**: Continuous validation and anomaly detection

**System Failures:**
- **Mitigation**: Robust error handling, checkpoint system
- **Recovery**: Resume capability from last successful state
- **Backup**: Manual processes for critical deadlines

### 7.2 Operational Risks

**Timeline Delays:**
- **Mitigation**: Conservative planning, early testing
- **Recovery**: Parallel manual collection processes
- **Communication**: Regular stakeholder updates

**User Adoption:**
- **Mitigation**: Council staff training, intuitive reports
- **Recovery**: Enhanced documentation and support
- **Success factors**: Clear value demonstration

### 7.3 Legal/Ethical Considerations

**Terms of Service Compliance:**
- **Authority**: Board member status for legitimate use
- **Documentation**: Written justification and permission requests
- **Limits**: HNE Council territory only, biannual collection

---

## 8. Decisions & Rationale

### 8.1 Technology Choices

**Playwright vs Requests Library:**
- **Decision**: Playwright for JavaScript-heavy sites
- **Rationale**: BeAScout uses dynamic loading, requests insufficient

**Regex vs LLM Extraction:**
- **Decision**: Tiered approach (regex primary, LLM fallback)
- **Rationale**: Cost and speed for 3K+ units, accuracy where needed

**JSON vs Database Storage:**
- **Decision**: JSON for raw data, SQLite for processed
- **Rationale**: Simplicity for development, structure for analysis

### 8.2 Process Decisions

**Conservative vs Aggressive Scraping:**
- **Decision**: Conservative approach (8-12s delays)
- **Rationale**: Sustainability over speed, 100% coverage requirement

**Biweekly vs Monthly Monitoring:**
- **Decision**: Biweekly re-scraping, monthly deep analysis
- **Rationale**: Balance responsiveness with resource efficiency

---

## 9. Open Questions & Action Items

### 9.1 Pending Decisions
- [ ] **Report Format**: Dashboard vs PDF vs Email preferences?
- [ ] **Alert Thresholds**: What changes warrant immediate notification?
- [ ] **Volunteer Integration**: How to coordinate manual collection backup?
- [ ] **Data Retention**: How long to maintain historical change data?

### 9.2 Research Required
- [ ] **BSA Contact Protocol**: Best approach for official permission request
- [ ] **Council Systems**: Integration with existing databases/workflows
- [ ] **Key Three Communication**: Preferred channels and messaging

### 9.3 Technical Validation
- [ ] **Extraction Accuracy**: Validate regex patterns against larger dataset
- [ ] **Performance Testing**: Confirm system can handle full 72-zip processing
- [ ] **Error Handling**: Test recovery procedures under various failure modes

---

## Appendices

### Appendix A: HNE Council Zip Codes
**Total:** 72 zip codes across 62 towns
**Estimated Units:** ~3,000 units council-wide

**Major Population Centers:**
- Worcester: 01601-01610 (10 zip codes)
- Fitchburg: 01420, 01421
- Leominster: 01453
- Acton: 01720 (baseline test case)

### Appendix B: Data Schema
```json
{
  "unit": {
    "primary_identifier": "Pack 0070 Acton-Congregational Church",
    "unit_type": "Pack",
    "unit_number": "0070", 
    "chartered_organization": "Acton-Congregational Church",
    "meeting_location": "12 Concord Rd",
    "meeting_day": "Friday",
    "meeting_time": "6:30 PM",
    "contact_email": "unit@example.com",
    "contact_person": "John Smith",
    "phone_number": "(555) 123-4567",
    "website": "https://unit.example.com",
    "description": "Unit description text...",
    "unit_composition": "Boys and Girls",
    "specialty": "High Adventure",
    "source_website": "beascout.scouting.org",
    "zipcode_found": "01720",
    "distance": "0.5 miles",
    "last_updated": "2024-12-22T10:30:00Z",
    "completeness_score": 85.5,
    "completeness_grade": "B+"
  }
}
```

### Appendix C: Report Template Examples
- Executive Dashboard Template
- Unit Scorecard Template  
- Change Detection Report Template
- Key Three Outreach Template

---

**End of Document**

*This document is maintained under version control. All changes should be tracked with clear commit messages describing the modifications and rationale.*