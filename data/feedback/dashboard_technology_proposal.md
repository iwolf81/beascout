# BeAScout Dashboard Technology Proposal
**Heart of New England Council - Technology Committee Review**

**Date:** August 25, 2025  
**Prepared by:** HNE Council Executive Board  
**Purpose:** Technology architecture proposal for automated unit information quality monitoring system

---

## Executive Summary

The BeAScout Unit Information Quality Dashboard will provide automated monitoring and improvement recommendations for all ~200 HNE Council units across 72 zip codes. This system will help unit leaders maintain complete, accurate information for prospective Scout families while reducing manual oversight burden on council staff.

**Current Status:** Core scraping and analysis system is operational and validated with 24 units from test zip codes.

---

## Business Requirements

### Primary Users
- **Council Commissioner & Staff** - Council-wide quality oversight and unit improvement tracking  
- **District Executives** - District-specific unit performance and Key Three outreach coordination
- **Executive Board Members** - Strategic unit development and territory coverage analysis

### Core Functionality
- **Automated Data Collection** - Periodic scraping from beascout.scouting.org and joinexploring.org
- **Quality Analysis** - A-F grading system with specific improvement recommendations
- **Key Three Integration** - Automated personalized emails to unit leadership with improvement guidance
- **District Reporting** - Excel reports for Quinapoxet and Soaring Eagle Districts
- **Historical Tracking** - Improvement trends and data freshness monitoring

### Security Requirements
- **Authorized Access Only** - Board member authentication with session management
- **Data Protection** - HNE Key Three contact information requires encryption and access controls
- **Usage Restrictions** - System limited to authorized Scouting America purposes per BSA data policies

---

## Technical Architecture Options

### Option 1: Flask + SQLite + DigitalOcean Droplet (Recommended)
**Technology Stack:**
- Backend: Python Flask web framework
- Database: SQLite (suitable for ~200 units, simple backup/restore)
- Frontend: Server-side rendered HTML with Chart.js for visualizations
- Deployment: Docker container on DigitalOcean Droplet

**Advantages:**
- **Simple Integration** - Leverages existing Python scraping pipeline without modification
- **Cost Effective** - Estimated $10-15/month for suitable droplet size
- **Full Control** - SSH access for maintenance, custom Python environment, complete data sovereignty
- **Rapid Development** - Minimal complexity, faster time-to-production
- **Easy Backup** - SQLite database files easily archived and restored

**Considerations:**
- Single-server architecture (suitable for council staff user count)
- Manual SSL certificate management (can be automated with Let's Encrypt)

### Option 2: Managed Service Integration
**Technology Stack:**
- Explore integration with existing hnescouting.org hosting provider
- Potentially leverage existing WordPress/CMS infrastructure
- Database integration with current council systems

**Advantages:**
- **Existing Infrastructure** - Leverage current hosting relationship and support
- **Unified Management** - Single point of contact for all web services
- **Established Security** - Existing SSL, backup, and maintenance procedures

**Information Needed:**
- Current hosting provider and technology stack for hnescouting.org
- Available database and application hosting options
- Integration capabilities with Python applications
- Pricing for additional services or resource allocation

### Option 3: Cloud-Native Solution
**Technology Stack:**
- Frontend: React/Vue.js single-page application
- Backend: FastAPI with PostgreSQL database  
- Deployment: DigitalOcean App Platform or similar managed service

**Advantages:**
- **Modern Architecture** - Rich user interface with real-time updates
- **Automatic Scaling** - Managed deployment with built-in SSL and monitoring
- **Professional Appearance** - Modern dashboard interface

**Considerations:**
- **Higher Complexity** - More moving parts, longer development time
- **Higher Cost** - Estimated $25-40/month for managed services
- **Build Pipeline** - Requires JavaScript build process and deployment automation

---

## Deployment Considerations

### Data Volume and Performance
- **~200 Scout units** across 72 HNE Council zip codes
- **Periodic scraping** - monthly or quarterly data refresh cycles
- **Historical data** - 2-3 years of improvement tracking recommended
- **Concurrent users** - Designed for 5-10 council staff simultaneous access

### Integration with Existing Systems
- **Independence** - Dashboard operates independently, no impact on existing hnescouting.org
- **Data Export** - Excel reports compatible with existing council reporting workflows  
- **Email Integration** - Key Three outreach emails can integrate with existing council email systems
- **Backup Coordination** - Can align with existing council backup procedures

### Maintenance and Support
- **Automated Operation** - System designed for minimal ongoing maintenance
- **Update Requirements** - Quarterly updates for scraping logic as BSA websites change
- **Monitoring** - Built-in failure detection and progress reporting
- **Documentation** - Comprehensive admin documentation and user guides provided

---

## Security and Compliance

### Data Protection
- **Encryption at Rest** - All databases encrypted with strong keys
- **HTTPS Everywhere** - All communications encrypted in transit
- **Access Logging** - Complete audit trail of data access and modifications
- **Data Retention** - Configurable retention policies for historical data

### Scouting America Compliance  
- **Authorized Use Only** - System restricted to legitimate council business purposes
- **Data Scope Limitation** - Only public unit information and authorized Key Three contacts
- **Usage Monitoring** - Access controls prevent unauthorized data export or sharing
- **BSA Policy Alignment** - Designed to support official unit development initiatives

### Authentication and Authorization
- **Board Member Access** - Individual accounts for authorized council leadership
- **Role-Based Permissions** - District-level access controls where appropriate
- **Session Management** - Automatic timeouts and secure session handling
- **Password Requirements** - Strong password policies with periodic rotation

---

## Implementation Timeline

### Phase 1: Infrastructure Setup (Weeks 1-2)
- Technology committee review and hosting decision
- Development environment setup and deployment pipeline
- Database design and security implementation
- Basic authentication and access control

### Phase 2: Core Dashboard Development (Weeks 3-4)
- Executive overview dashboard with district comparison
- Unit drill-down interface with improvement recommendations
- Integration with existing scraping and analysis pipeline
- Key Three contact integration and email generation

### Phase 3: Advanced Features (Weeks 5-6)
- Historical trend analysis and improvement tracking
- Manual scraping triggers and progress monitoring
- Excel report generation and download functionality
- Administrative interface for user management

### Phase 4: Testing and Deployment (Weeks 7-8)
- User acceptance testing with council staff
- Security review and penetration testing
- Production deployment and backup procedures
- Training documentation and user guides

---

## Cost Analysis

### Option 1: DigitalOcean Droplet (Recommended)
- **Monthly Hosting:** $12-15 (4GB RAM, 2 vCPU, 80GB storage)
- **Domain/SSL:** $15/year (if separate domain needed)
- **Development:** One-time setup and customization
- **Annual Total:** ~$150-200 (excluding development)

### Option 2: Existing Hosting Integration
- **Cost:** To be determined based on current provider capabilities
- **Advantages:** Potential cost savings through existing relationship
- **Considerations:** May require provider capability assessment

### Option 3: Managed Cloud Service
- **Monthly Hosting:** $30-50 (App Platform with database)
- **Domain/SSL:** Included in managed service
- **Development:** Higher complexity, longer timeline
- **Annual Total:** ~$350-600

---

## Technology Committee Questions

1. **Current Infrastructure:** What hosting provider and technology stack currently supports hnescouting.org? Are additional Python applications supported?

2. **Integration Preferences:** Should this dashboard integrate with existing council systems, or operate as a standalone tool?

3. **Budget Considerations:** What hosting budget range is appropriate for this tool's ongoing operation?

4. **Support Preferences:** Is there a preference for managed services (higher cost, less maintenance) vs. self-hosted solutions (lower cost, more control)?

5. **Timeline Requirements:** Is there a target date for dashboard availability, or flexibility for technology evaluation?

6. **Data Policies:** Are there existing council data retention and access policies that should guide database design?

---

## Recommendation

Based on technical simplicity, cost effectiveness, and integration with existing Python pipeline, **Option 1 (Flask + SQLite + DigitalOcean Droplet)** provides the optimal balance of functionality, control, and cost for HNE Council's needs.

However, **Option 2 (Existing Hosting Integration)** may offer advantages if current infrastructure can support Python applications cost-effectively.

The technology committee's input on current hosting capabilities and preferences will inform the final implementation approach.

---

**Contact:** [Board Member] for technical questions and implementation coordination.