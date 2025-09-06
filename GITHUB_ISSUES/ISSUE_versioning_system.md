# Enhancement: Versioning and Labeling System

**Title**: Implement systematic versioning for reports and releases

**Labels**: enhancement, infrastructure, maintenance, medium-priority

**Component**: core (infrastructure)

## Enhancement Description
Implement a systematic versioning and labeling mechanism for BeAScout quality reports and system releases to improve tracking, deployment, and rollback capabilities.

## Problem/Opportunity
Reports are currently generated with timestamps (e.g., `BeAScout_Quality_Report_20250904_084334.xlsx`) but lack semantic versioning or release labeling, making it difficult to:
- Track which system version produced which reports
- Manage rollbacks to previous working versions
- Reference specific versions in feedback and issues
- Maintain systematic release processes for production deployments

## Proposed Solution
Implement comprehensive versioning system with:

1. **Semantic Versioning System**:
   - Format: `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
   - MAJOR: Breaking changes or significant architectural updates
   - MINOR: New features or enhancements (backwards compatible)  
   - PATCH: Bug fixes and minor improvements

2. **Release Labeling**:
   - Development Labels: `DEV`, `STAGING`, `PROD`
   - Feature Labels: `QUALITY_SCORING`, `REPORT_GEN`, `EMAIL_GEN`
   - Milestone Labels: `ALPHA`, `BETA`, `RC`, `STABLE`

3. **Git Tag Integration**:
   - Automatic tagging for each release
   - Tag format: `v1.2.3-report-20250904`
   - Auto-generated release notes from commits

4. **Report Versioning**:
   - Include version in report filenames: `BeAScout_Quality_Report_v1.2.3_20250904.xlsx`
   - Add version metadata to Excel report properties
   - Track changes between report versions

## User Story
As a **system administrator**, I want **systematic versioning for all reports and releases** so that **I can track deployments, manage rollbacks, and clearly reference specific versions in communications**.

## Acceptance Criteria
- [ ] Semantic versioning system implemented (MAJOR.MINOR.PATCH)
- [ ] All reports include version information in filename and metadata
- [ ] Git tags created automatically for releases with release notes
- [ ] Version management utilities created for increment/update workflows
- [ ] Release pipeline automation for quality checks and versioning
- [ ] Easy rollback capability to previous versions

## Implementation Notes

**Phase 1: Version Management Script**
```bash
# scripts/version.py
- Read current version from VERSION file
- Increment version based on change type
- Update version in all relevant files
- Create git tag with release notes
```

**Phase 2: Automated Release Pipeline**
```bash
# scripts/release.py  
- Run quality checks and tests
- Generate reports with version labels
- Create git tag and release notes
- Archive previous versions
```

**Phase 3: Version Integration**
- Update report generators to include version metadata
- Add version display to Excel reports
- Include version in email signatures

## Files to Create/Modify
- `VERSION` - Store current version number
- `scripts/version.py` - Version management utilities
- `scripts/release.py` - Release pipeline automation
- `src/pipeline/analysis/generate_commissioner_report.py` - Add version to reports
- `src/pipeline/analysis/generate_unit_emails.py` - Add version to emails

## Benefits
- **User Impact**: Clear version references improve communication and feedback
- **System Impact**: Systematic release process and easy rollback capabilities
- **Business Impact**: Professional versioning increases confidence and maintainability

## Success Criteria
- All reports include version information in filename and metadata
- Git tags created automatically for releases with descriptive release notes
- Version increments follow semantic versioning rules consistently
- Easy rollback to previous versions when deployment issues occur

## Priority: Medium
This infrastructure enhancement supports systematic deployment and maintenance workflows.