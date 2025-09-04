# Enhancement Request: Versioning and Labeling System

**Date**: 2025-09-04  
**Priority**: Maintenance  
**Type**: Infrastructure Enhancement

## Request Description
Implement a systematic versioning and labeling mechanism for BeAScout quality reports and system releases to improve tracking, deployment, and rollback capabilities.

## Current State
Reports are currently generated with timestamps (e.g., `BeAScout_Quality_Report_20250904_084334.xlsx`) but lack semantic versioning or release labeling.

## Proposed Enhancements

### 1. Semantic Versioning System
- **Format**: `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- **MAJOR**: Breaking changes or significant architectural updates
- **MINOR**: New features or enhancements (backwards compatible)  
- **PATCH**: Bug fixes and minor improvements
- **Example**: `BEASCOUT_v1.2.3_REPORT_20250904`

### 2. Release Labeling
- **Development Labels**: `DEV`, `STAGING`, `PROD`
- **Feature Labels**: `QUALITY_SCORING`, `REPORT_GEN`, `EMAIL_GEN`
- **Milestone Labels**: `ALPHA`, `BETA`, `RC` (Release Candidate), `STABLE`
- **Example**: `BEASCOUT_v1.2.3_RC1_QUALITY_SCORING`

### 3. Git Tag Integration
- **Automatic Tagging**: Create git tags for each release
- **Tag Format**: `v1.2.3-report-20250904`
- **Release Notes**: Auto-generate from commit messages and enhancement/defect files

### 4. Report Versioning
- **File Naming**: Include version in report filenames
- **Metadata**: Add version info to Excel report properties
- **Change Log**: Track what changed between report versions
- **Example**: `BeAScout_Quality_Report_v1.2.3_20250904.xlsx`

## Implementation Strategy

### Phase 1: Version Management Script
```bash
# scripts/version.py
- Read current version from VERSION file
- Increment version based on change type
- Update version in all relevant files
- Create git tag with release notes
```

### Phase 2: Automated Release Pipeline  
```bash
# scripts/release.py
- Run quality checks and tests
- Generate reports with version labels
- Create git tag and release notes
- Archive previous versions
```

### Phase 3: Version Integration
- Update report generators to include version metadata
- Add version display to Excel reports
- Include version in email signatures

## Files to Create/Modify
- `VERSION`: Store current version number
- `scripts/version.py`: Version management utilities
- `scripts/release.py`: Release pipeline automation
- `src/pipeline/reporting/generate_commissioner_report.py`: Add version to reports
- `src/pipeline/reporting/generate_key_three_emails.py`: Add version to emails

## Benefits
- **Tracking**: Clear identification of which version produced which reports
- **Rollback**: Easy to revert to previous working versions
- **Communication**: Clear version references in feedback and issues
- **Deployment**: Systematic release process for production deployments

## Success Criteria
- All reports include version information
- Git tags created automatically for releases
- Version increments follow semantic versioning rules
- Easy rollback to previous versions when needed