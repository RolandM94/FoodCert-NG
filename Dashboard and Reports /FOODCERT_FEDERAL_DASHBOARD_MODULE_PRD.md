# PRD: Federal Dashboard Module — FoodCert NG

## 1. Document Purpose

This PRD defines the **Federal Dashboard Module** for FoodCert NG.

The Federal Dashboard is the landing workspace for Federal Ministry users. It should provide national oversight across states, medical facilities, certificates, food handlers, employers, inspections, enforcement, payments, forms, and implementation performance.

The Federal Dashboard should not behave like a State operational dashboard. The Federal account is not expected to run day-to-day state workflows such as approving individual certificates, assigning state inspectors, or reviewing every state facility application unless a special national intervention or escalation permission exists.

The Federal Dashboard should focus on:

```txt
National oversight
Cross-state performance comparison
Policy implementation monitoring
Aggregate compliance indicators
State response and reporting performance
National risk signals
Federal M&E visibility
Executive reporting
```

---

# 2. Product Decision

## 2.1 Federal Dashboard Is an Oversight Dashboard

The Federal Dashboard should provide national-level visibility across all states and the FCT.

It should answer:

```txt
How is FoodCert NG performing nationally?
Which states are compliant or lagging?
Where are the public health/compliance risks?
Which states have pending work or overdue workflows?
How many food handlers, employers, and medical facilities are active nationally?
How are certificates, inspections, accreditation, forms, and revenue performing across states?
```

## 2.2 Federal Dashboard Should Not Duplicate State Dashboard

The State Dashboard focuses on operational queues and state-level action.

The Federal Dashboard focuses on national monitoring and state comparison.

Example:

```txt
State Dashboard:
Review pending certificates for Lagos State.

Federal Dashboard:
Compare certificate validation performance across all states.
```

## 2.3 Federal Dashboard Should Link to Oversight Views

Federal Dashboard cards and tables should deep-link into:

```txt
States Overview
Directory & Registry
Forms Tool
Reports & Analytics
Certificates Oversight
Medical Facilities Oversight
Inspections & Enforcement Oversight
Account Settings
```

---

# 3. Federal Account Navigation Context

Recommended Federal Ministry sidebar:

```txt
Dashboard
States Overview
Directory & Registry
Forms Tool
Reports & Analytics
Account Settings
```

Optional, if the product requires more direct oversight modules:

```txt
Dashboard
States Overview
Medical Facilities Oversight
Certificates Oversight
Inspections & Enforcement Oversight
Directory & Registry
Forms Tool
Reports & Analytics
Account Settings
```

Recommended MVP: keep the navigation simpler and use the Dashboard + Reports & Analytics + States Overview to access deeper views.

---

# 4. Federal Dashboard Design Principle

The Federal Dashboard should follow this hierarchy:

```txt
1. National Summary: What is the national compliance position?
2. State Performance: Which states are doing well or lagging?
3. Priority Risks: What requires Federal attention?
4. Federal M&E / Forms: What reporting exercises are pending?
5. Trends and Analytics: What patterns are emerging nationally?
6. Recent Escalations: What has been escalated to Federal level?
```

Do not overload the page with too many isolated widgets. Use grouped insight cards, state comparison tables, and aggregate charts.

---

# 5. Federal Dashboard Page Structure

Recommended layout:

```txt
Federal Dashboard
├── Header
├── National Filter Toolbar
├── Executive Summary Cards
├── Priority Federal Attention
├── State Performance Overview
├── National Operational Indicators
├── Forms / M&E Reporting Monitor
├── Recent Escalations
├── Analytics & Trends
└── Quick Actions
```

---

# 6. Header

## 6.1 Header Text

```txt
Eyebrow: FEDERAL MINISTRY OVERSIGHT
Title: Federal Dashboard
Subtitle: Monitor FoodCert NG implementation, compliance performance, state reporting, and national risk signals across Nigeria.
```

## 6.2 Header Actions

Recommended actions:

```txt
Export National Summary
Open Reports
Create Federal Form Assignment
View State Performance
```

Actions should be permission-based.

---

# 7. National Filter Toolbar

## 7.1 Purpose

Federal users need to filter national data by geography, time, status, and programme category.

## 7.2 Filters

Recommended filters:

```txt
Geopolitical Zone
State
Date Range
Employer Category
Certificate Status
Facility Accreditation Status
Inspection Status
Form Assignment / M&E Exercise
```

MVP filters:

```txt
Zone
State
From Date
To Date
Certificate Status
Facility Status
Apply Filters
Reset
```

## 7.3 Filter Behaviour

Filters should update all dashboard cards, state tables, charts, and reports.

Example:

```txt
Zone = South West
→ Dashboard shows only South West states.

State = Lagos
→ Dashboard shows Lagos values in Federal oversight context.
```

---

# 8. Executive Summary Cards

The Federal Dashboard should use grouped national cards, not too many raw KPI widgets.

Recommended cards:

```txt
National Certification Coverage
State Implementation Performance
Medical Facility Readiness
Inspection & Enforcement Oversight
Federal Forms & Reporting
```

Optional permission-based card:

```txt
National Revenue Summary
```

---

## 8.1 National Certification Coverage Card

### Purpose

Shows national food handler certification status.

### Combines Metrics

```txt
Total Food Handlers
Certified Food Handlers
Certification Coverage %
Pending Certificate Validation
Expired Certificates
Certificates Expiring Soon
```

### Example

```txt
National Certification Coverage

142,850 Total Food Handlers
91,420 Certified
64.0% National Coverage

Needs Attention
4,920 Pending Validation
8,410 Expired Certificates
3,200 Expiring in 30 Days

[View Certificate Oversight]
```

### Route

```txt
/federal/directory?tab=food-handlers
/federal/reports?category=certificate_coverage
```

---

## 8.2 State Implementation Performance Card

### Purpose

Shows how states are performing in implementation, reporting, and platform usage.

### Metrics

```txt
Active States
States Reporting This Period
States with Overdue Reports
Average State Compliance Score
Top Performing State
Lowest Performing State
```

### Example

```txt
State Implementation Performance

37 States/FCT Onboarded
29 Reporting This Period
8 States Overdue
72% Average State Compliance Score

Top: Lagos
Needs Support: State X

[View States Overview]
```

---

## 8.3 Medical Facility Readiness Card

### Purpose

Shows national accreditation/readiness of medical facilities.

### Metrics

```txt
Approved Medical Facilities
Pending Accreditation Applications
Facilities Due for Re-accreditation
Expired Facility Accreditation
Suspended Facilities
State Facility Coverage Gap
```

### Example

```txt
Medical Facility Readiness

3,420 Approved Facilities
218 Pending Accreditation
126 Due for Re-accreditation
42 Expired
11 Suspended

[View Facility Oversight]
```

---

## 8.4 Inspection & Enforcement Oversight Card

### Purpose

Shows national inspection and enforcement risk signals.

### Metrics

```txt
Inspections Conducted
Open Inspections
Overdue Inspections
High/Critical Findings
Open Enforcement Cases
Corrective Actions Overdue
```

### Example

```txt
Inspection & Enforcement Oversight

8,450 Inspections Conducted
620 Open Inspections
132 Overdue
76 High/Critical Findings
210 Open Enforcement Cases

[View Enforcement Reports]
```

---

## 8.5 Federal Forms & Reporting Card

### Purpose

Shows Federal M&E forms, state reporting assignments, and submission performance.

### Metrics

```txt
Active Federal Form Assignments
State Reporting Response Rate
Pending State Submissions
Overdue State Submissions
Federal Standard Templates Published
States Adopted Federal Templates
```

### Example

```txt
Federal Forms & Reporting

12 Active Federal Assignments
78% State Response Rate
9 Pending State Submissions
4 Overdue States
16 Federal Standard Templates

[Open Forms Tool]
```

---

## 8.6 National Revenue Summary Card

### Purpose

Shows national collections and payment performance where Federal users have permission.

### Metrics

```txt
Total National Revenue
Assessment Fee Revenue
Certificate Fee Revenue
Facility Accreditation Fee Revenue
Pending Settlements
Failed Payments / Reconciliation Exceptions
```

### Permission Rule

Only users with:

```txt
federal_dashboard.view_revenue
```

should see this card.

---

# 9. Priority Federal Attention

## 9.1 Purpose

This section shows urgent matters requiring Federal oversight or intervention.

## 9.2 Recommended Priority Items

```txt
States with overdue reporting
States with low certification coverage
States with high pending certificate validation
States with accreditation backlog
States with high critical inspection findings
States with overdue enforcement cases
States not adopting Federal templates
States with inactive platform usage
```

## 9.3 Example UI

```txt
Priority Federal Attention

8 States overdue on monthly reporting                  [View]
5 States below 40% certification coverage              [View]
4 States have facility accreditation backlog            [View]
3 States have high critical inspection findings         [View]
9 States have not adopted latest Federal templates      [View]
```

## 9.4 Severity Levels

```txt
Critical
High
Medium
Low
```

## 9.5 Deep Links

Each item should link into the relevant filtered view.

Examples:

```txt
/federal/states-overview?filter=overdue_reporting
/federal/reports?category=low_certification_coverage
/federal/forms?tab=responses&status=overdue
/federal/reports?category=inspection_risk
```

---

# 10. State Performance Overview

## 10.1 Purpose

This is one of the most important Federal Dashboard sections.

It should let Federal users compare state performance quickly.

## 10.2 State Performance Table Columns

```txt
State
Zone
Certification Coverage
Approved Facilities
Pending Accreditation
Inspections Conducted
Open Enforcement Cases
Federal Reporting Status
Overall Status
Action
```

## 10.3 Example Table

```txt
State        Zone       Coverage   Facilities   Pending Accred.   Inspections   Reporting   Status
Lagos        SW         82%        876          14                420           Submitted   Good
Kano         NW         61%        420          22                310           Pending     Watch
Rivers       SS         74%        390          9                 260           Submitted   Good
State X      NE         34%        70           41                25            Overdue     Critical
```

## 10.4 Overall Status Logic

The overall status can be calculated using multiple signals:

```txt
Certification coverage
Facility readiness
Pending certificate validation
Inspection activity
Open enforcement risks
Federal form/reporting response status
Platform activity
```

Possible statuses:

```txt
Good
Watch
Needs Support
Critical
Inactive
```

## 10.5 State Detail Link

Clicking a state row should open:

```txt
/federal/states-overview/[stateId]
```

or filtered state detail dashboard.

---

# 11. National Operational Indicators

## 11.1 Purpose

Show national operational queues without turning Federal Dashboard into a state-level work queue.

## 11.2 Recommended Indicators

```txt
Pending Certificate Validation by State
Pending Facility Accreditation by State
Overdue Inspections by State
Open Enforcement Cases by State
Forms Pending by State
Re-accreditation Due by State
```

## 11.3 Display Format

Use compact cards or a table:

```txt
Indicator                         Count      Highest State      Action
Pending Certificate Validation     4,920      Kano               View
Pending Facility Accreditation     218        State X            View
Overdue Inspections                132        Lagos              View
Open Enforcement Cases             210        Rivers             View
Forms Pending                      9 States   Multiple           View
```

---

# 12. Forms / M&E Reporting Monitor

## 12.1 Purpose

The Federal account uses the Forms Tool for national templates, state reporting, Federal M&E data collection, guideline implementation monitoring, and cross-state surveys.

This section should show active Federal form assignments and response performance.

## 12.2 Metrics

```txt
Active Federal Assignments
Total States Assigned
Submitted States
Pending States
Overdue States
Response Rate
Returned Responses
```

## 12.3 Table Columns

```txt
Assignment
Purpose
Assigned States
Submitted
Pending
Overdue
Response Rate
Due Date
Action
```

## 12.4 Example

```txt
Assignment                         Purpose                  Response Rate   Overdue
Q2 State Compliance Report          State Reporting          78%             4 States
Guideline Implementation Survey     Policy Monitoring        62%             8 States
Facility Accreditation Summary      M&E Data Collection      84%             2 States
```

## 12.5 Routes

```txt
/federal/forms?tab=assignments
/federal/forms?tab=responses
/federal/forms?tab=reports
```

---

# 13. Recent Escalations

## 13.1 Purpose

Federal users should see serious matters escalated from states.

## 13.2 Escalation Types

```txt
Critical inspection finding
Repeated state reporting failure
Facility operating while suspended
High accreditation backlog
Enforcement case escalated
Public health incident
Certificate fraud anomaly
QR verification anomaly
```

## 13.3 Recent Escalations Table Columns

```txt
Date
State
Escalation Type
Entity
Severity
Status
Assigned Federal Officer
Action
```

## 13.4 Statuses

```txt
New
Under Review
Action Required
Resolved
Closed
```

---

# 14. Analytics & Trends

## 14.1 Purpose

Charts should provide national trend and distribution insights.

## 14.2 Recommended Charts

```txt
Certification Coverage by State
Certification Coverage by Zone
Facility Accreditation Status by State
Inspection Outcomes by Severity
Federal Reporting Response Rate by State
Certificate Status Distribution
Revenue Trend, permission-based
Forms Response Trend
```

## 14.3 MVP Charts

Recommended MVP:

```txt
Certification Coverage by State
State Reporting Response Rate
Facility Accreditation Status
Inspection Severity Distribution
```

---

# 15. Quick Actions

## 15.1 Purpose

Federal users need quick access to common oversight tasks.

## 15.2 Recommended Actions

```txt
Create Federal Form Assignment
View State Performance
Open National Reports
View Federal Standard Templates
Export National Summary
View Overdue State Reports
```

Actions should be permission-based.

---

# 16. Federal Dashboard Metrics Dictionary

## 16.1 National Certification Coverage

```txt
total_food_handlers
certified_food_handlers
certification_coverage_percentage
pending_certificate_validation_count
expired_certificates_count
certificates_expiring_soon_count
```

Calculation:

```txt
certification_coverage_percentage =
(certified_food_handlers / total_food_handlers) * 100
```

## 16.2 State Implementation Performance

```txt
total_states
active_states
states_reporting_this_period
states_overdue_reporting
average_state_compliance_score
top_performing_state
lowest_performing_state
```

## 16.3 Medical Facility Readiness

```txt
approved_facilities_count
pending_accreditation_count
reaccreditation_due_count
expired_facility_accreditation_count
suspended_facilities_count
facility_coverage_gap_count
```

## 16.4 Inspection & Enforcement Oversight

```txt
inspections_conducted_count
open_inspections_count
overdue_inspections_count
high_findings_count
critical_findings_count
open_enforcement_cases_count
corrective_actions_overdue_count
```

## 16.5 Federal Forms & Reporting

```txt
active_federal_assignments_count
states_assigned_count
states_submitted_count
states_pending_count
states_overdue_count
federal_reporting_response_rate
federal_standard_templates_count
states_adopted_templates_count
```

## 16.6 National Revenue Summary

```txt
total_revenue_collected
assessment_fee_revenue
certificate_fee_revenue
facility_accreditation_fee_revenue
pending_settlements
failed_payments_count
reconciliation_exceptions_count
```

---

# 17. Federal Dashboard API Requirements

## 17.1 Main Summary API

```txt
GET /api/federal/dashboard/summary
```

Query params:

```txt
zone
state
date_from
date_to
certificate_status
facility_status
inspection_status
form_assignment_id
```

Response shape:

```json
{
  "filters": {
    "zone": "All Zones",
    "state": "All States",
    "date_from": "2026-06-01",
    "date_to": "2026-06-30"
  },
  "national_certification_coverage": {
    "total_food_handlers": 142850,
    "certified_food_handlers": 91420,
    "certification_coverage_percentage": 64.0,
    "pending_certificate_validation_count": 4920,
    "expired_certificates_count": 8410,
    "certificates_expiring_soon_count": 3200
  },
  "state_implementation_performance": {
    "total_states": 37,
    "active_states": 37,
    "states_reporting_this_period": 29,
    "states_overdue_reporting": 8,
    "average_state_compliance_score": 72
  },
  "medical_facility_readiness": {
    "approved_facilities_count": 3420,
    "pending_accreditation_count": 218,
    "reaccreditation_due_count": 126,
    "expired_facility_accreditation_count": 42,
    "suspended_facilities_count": 11
  },
  "inspection_enforcement_oversight": {
    "inspections_conducted_count": 8450,
    "open_inspections_count": 620,
    "overdue_inspections_count": 132,
    "high_findings_count": 52,
    "critical_findings_count": 24,
    "open_enforcement_cases_count": 210,
    "corrective_actions_overdue_count": 84
  },
  "federal_forms_reporting": {
    "active_federal_assignments_count": 12,
    "states_assigned_count": 37,
    "states_submitted_count": 29,
    "states_pending_count": 8,
    "states_overdue_count": 4,
    "federal_reporting_response_rate": 78
  }
}
```

## 17.2 Priority Federal Attention API

```txt
GET /api/federal/dashboard/priority-attention
```

## 17.3 State Performance API

```txt
GET /api/federal/dashboard/state-performance
```

## 17.4 Operational Indicators API

```txt
GET /api/federal/dashboard/operational-indicators
```

## 17.5 Forms / M&E Monitor API

```txt
GET /api/federal/dashboard/forms-reporting-monitor
```

## 17.6 Recent Escalations API

```txt
GET /api/federal/dashboard/recent-escalations
```

## 17.7 Analytics API

```txt
GET /api/federal/dashboard/analytics
```

---

# 18. Frontend Components

## 18.1 Page-Level Components

```txt
FederalDashboardPage
FederalDashboardHeader
FederalDashboardFilters
FederalExecutiveSummaryGrid
FederalPriorityAttentionPanel
StatePerformanceOverviewTable
NationalOperationalIndicatorsPanel
FederalFormsReportingMonitor
RecentEscalationsPanel
FederalAnalyticsSection
FederalQuickActionsPanel
```

## 18.2 Summary Card Components

```txt
NationalCertificationCoverageCard
StateImplementationPerformanceCard
MedicalFacilityReadinessFederalCard
InspectionEnforcementOversightCard
FederalFormsReportingCard
NationalRevenueSummaryCard
```

## 18.3 Shared Components

```txt
DashboardCard
MetricLine
MetricGroup
CoverageProgressBar
PriorityBadge
StateStatusBadge
TrendIndicator
EmptyState
LoadingSkeleton
```

## 18.4 Chart Components

```txt
CertificationCoverageByStateChart
CertificationCoverageByZoneChart
FacilityAccreditationStatusChart
InspectionSeverityDistributionChart
StateReportingResponseRateChart
FormsResponseTrendChart
NationalRevenueTrendChart
```

---

# 19. UI Consolidation Rules

## 19.1 Do Not Duplicate State Dashboard

Federal Dashboard should not show state operational work queues as if Federal users are processing them directly.

Use aggregate oversight views.

## 19.2 Combine Related Metrics

Do not show these as separate independent top-level cards:

```txt
Total Food Handlers
Certified Food Handlers
Pending Certificate Validation
Expired Certificates
```

They belong under:

```txt
National Certification Coverage
```

Do not show these as separate independent top-level cards:

```txt
Approved Facilities
Pending Accreditation
Due for Re-accreditation
Expired Facility Accreditation
```

They belong under:

```txt
Medical Facility Readiness
```

Do not show these as separate independent top-level cards:

```txt
Federal Form Assignments
Pending State Submissions
Overdue State Forms
```

They belong under:

```txt
Federal Forms & Reporting
```

## 19.3 State Performance Is Central

The Federal Dashboard must include a state comparison section. This is the key difference from the State Dashboard.

## 19.4 Forms Tool Integration

Federal Forms & Reporting should integrate with the Federal Forms Tool.

Do not create a separate Federal M&E form dashboard outside Forms Tool.

## 19.5 Revenue Permission

Revenue should be optional and permission-based.

---

# 20. Permissions and Scope

## 20.1 Dashboard Permissions

Recommended permissions:

```txt
federal_dashboard.view
federal_dashboard.view_state_performance
federal_dashboard.view_certification_summary
federal_dashboard.view_facility_summary
federal_dashboard.view_inspection_enforcement_summary
federal_dashboard.view_forms_reporting
federal_dashboard.view_revenue
federal_dashboard.export
```

## 20.2 Scope Rules

- Federal users can see national aggregate data.
- Federal users can filter by state and zone.
- Federal users should not access private medical details unless explicitly permitted.
- Federal users should see aggregate or state-level summaries by default.
- Revenue data is hidden unless user has revenue permission.
- State operational details are available only through appropriate oversight permissions.

## 20.3 Sensitive Data Rules

Federal Dashboard should not expose:

```txt
Individual diagnosis
Lab results
Doctor notes
Private medical assessment details
Full health declaration responses
```

Federal Dashboard can expose aggregate operational indicators such as:

```txt
Number of temporarily unfit food handlers
Active illness exclusions by state
Return-to-work pending count by state
```

only if permission allows.

---

# 21. Empty, Loading, and Error States

## 21.1 Loading

Use skeleton loading for:

```txt
Summary cards
Priority attention
State performance table
Forms reporting monitor
Charts
Recent escalations
```

## 21.2 Empty State

```txt
No Federal dashboard data is available for the selected filters.
Try adjusting your filters or date range.
```

## 21.3 Error State

```txt
Unable to load Federal dashboard data.
Retry
```

Show partial data where possible.

---

# 22. Acceptance Criteria

## 22.1 Dashboard Structure

- Federal Dashboard contains header, filters, executive summary cards, priority attention, state performance overview, operational indicators, Federal Forms/M&E monitor, recent escalations, analytics, and quick actions.
- Dashboard is national and cross-state focused.
- Dashboard does not duplicate State Dashboard operational workflow.

## 22.2 Executive Summary Cards

- National Certification Coverage combines national food handler certification metrics.
- State Implementation Performance combines state reporting and implementation metrics.
- Medical Facility Readiness combines national facility accreditation metrics.
- Inspection & Enforcement Oversight combines national inspection/enforcement risk metrics.
- Federal Forms & Reporting combines Federal forms and M&E reporting metrics.
- National Revenue Summary is permission-controlled.

## 22.3 State Performance

- Federal users can compare states.
- Table shows certification coverage, facility readiness, inspection activity, enforcement cases, and reporting status.
- State rows deep-link to state detail views.

## 22.4 Priority Federal Attention

- Priority issues are shown with severity, count, and action link.
- Items deep-link to filtered views.

## 22.5 Forms / M&E Reporting

- Federal Forms Tool assignments appear in dashboard summary.
- Federal users can see pending, submitted, and overdue state submissions.
- Forms dashboard links to Federal Forms Tool.

## 22.6 Permissions

- Federal Dashboard is permission-controlled.
- Revenue is hidden from unauthorized users.
- Sensitive health details are not exposed.
- Federal users only see data they are permitted to view.

## 22.7 UI Quality

- Dashboard is clean, executive-level, and scannable.
- Related metrics are grouped.
- Tables and charts are not overcrowded.
- Layout is responsive.
- Empty/loading/error states work.

---

# 23. Implementation Chunks for Codex

## Chunk 1: Federal Dashboard API Aggregation

### Goal

Create backend aggregation endpoints for the Federal Dashboard.

### Tasks

- Implement `/api/federal/dashboard/summary`.
- Implement `/api/federal/dashboard/priority-attention`.
- Implement `/api/federal/dashboard/state-performance`.
- Implement `/api/federal/dashboard/operational-indicators`.
- Implement `/api/federal/dashboard/forms-reporting-monitor`.
- Implement `/api/federal/dashboard/recent-escalations`.
- Implement `/api/federal/dashboard/analytics`.
- Add filters for zone, state, date range, certificate status, facility status, inspection status, and form assignment.
- Enforce permissions and sensitive data protections.

### Acceptance Criteria

- APIs return national aggregate metrics.
- APIs support filters.
- APIs enforce Federal permissions.
- Revenue and sensitive fields are omitted when unauthorized.

---

## Chunk 2: Federal Dashboard Page Shell

### Goal

Build the Federal Dashboard route and page structure.

### Tasks

- Add Federal Dashboard route.
- Create `FederalDashboardPage`.
- Add header and subtitle.
- Add filter toolbar.
- Add page sections:
  - Executive Summary
  - Priority Federal Attention
  - State Performance Overview
  - National Operational Indicators
  - Forms / M&E Reporting Monitor
  - Recent Escalations
  - Analytics
  - Quick Actions
- Add loading, empty, and error states.

### Acceptance Criteria

- Federal Dashboard page renders successfully.
- Layout follows FoodCert NG design system.
- Sections render in correct order.
- State Dashboard remains unchanged.

---

## Chunk 3: Executive Summary Cards

### Goal

Implement grouped Federal summary cards.

### Tasks

Create:

```txt
NationalCertificationCoverageCard
StateImplementationPerformanceCard
MedicalFacilityReadinessFederalCard
InspectionEnforcementOversightCard
FederalFormsReportingCard
NationalRevenueSummaryCard
```

- Add primary metrics, sub-metrics, needs-attention fields, and CTA links.
- Make Revenue card permission-controlled.

### Acceptance Criteria

- Related metrics are grouped.
- Cards display national aggregate data.
- Cards link to correct Federal oversight routes.
- Revenue card is hidden unless permitted.

---

## Chunk 4: Priority Federal Attention Panel

### Goal

Create urgent Federal oversight section.

### Tasks

- Build `FederalPriorityAttentionPanel`.
- Display priority items with severity, count, and action links.
- Support deep links into state performance, reports, forms, or oversight views.

### Acceptance Criteria

- Priority issues are visible.
- Severity badges work.
- Action links route correctly.

---

## Chunk 5: State Performance Overview

### Goal

Build the state comparison table.

### Tasks

- Build `StatePerformanceOverviewTable`.
- Add columns:
  - State
  - Zone
  - Certification Coverage
  - Approved Facilities
  - Pending Accreditation
  - Inspections Conducted
  - Open Enforcement Cases
  - Federal Reporting Status
  - Overall Status
  - Action
- Add sorting and filtering.
- Add row click to state detail page.

### Acceptance Criteria

- Federal users can compare states.
- Status badges display correctly.
- Rows link to state detail.
- Filters affect table data.

---

## Chunk 6: National Operational Indicators

### Goal

Display national operational indicators by state.

### Tasks

- Build `NationalOperationalIndicatorsPanel`.
- Show indicators such as pending certificate validation, pending facility accreditation, overdue inspections, open enforcement cases, pending forms, and reaccreditation due.
- Add highest state / highest risk state where useful.
- Add action routes.

### Acceptance Criteria

- Indicators summarize national backlog and risk.
- Actions link to filtered reports or oversight views.

---

## Chunk 7: Federal Forms / M&E Reporting Monitor

### Goal

Integrate Federal Forms Tool reporting into the dashboard.

### Tasks

- Build `FederalFormsReportingMonitor`.
- Show active Federal assignments.
- Show state response rate.
- Show pending and overdue states.
- Add assignment table.
- Link to Federal Forms Tool assignments, responses, and reports.

### Acceptance Criteria

- Federal form assignments appear on dashboard.
- Response rates display correctly.
- Overdue states are visible.
- Links open Federal Forms Tool.

---

## Chunk 8: Recent Escalations Panel

### Goal

Show serious escalated issues from states.

### Tasks

- Build `RecentEscalationsPanel`.
- Add escalation type, state, entity, severity, status, assigned officer, and action.
- Add filters or limit to recent 5–10 items.

### Acceptance Criteria

- Recent escalations are visible.
- Critical items are visually prominent.
- Actions link to details.

---

## Chunk 9: Analytics and Charts

### Goal

Add national trend and comparison charts.

### Tasks

Build charts:

```txt
CertificationCoverageByStateChart
StateReportingResponseRateChart
FacilityAccreditationStatusChart
InspectionSeverityDistributionChart
```

Optional:

```txt
NationalRevenueTrendChart
FormsResponseTrendChart
```

- Add empty states.
- Add permission controls.

### Acceptance Criteria

- Charts render cleanly.
- Charts respect filters.
- Revenue chart is permission-controlled.

---

## Chunk 10: Filters, Permissions, Responsive QA

### Goal

Complete dashboard functionality and polish.

### Tasks

- Implement dashboard-wide filters.
- Sync filters with URL query params.
- Add permission checks.
- Hide unauthorized cards/sections.
- Add responsive layout.
- Add skeletons, empty states, and error states.
- Add tests.

### Acceptance Criteria

- Filters update dashboard data.
- Permissions are enforced.
- Dashboard is responsive.
- Sensitive data is protected.
- Tests pass.

---

# 24. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Build the FoodCert NG Federal Dashboard Module.

The Federal Dashboard is the landing workspace for Federal Ministry users. It should provide national oversight, cross-state performance comparison, Federal M&E visibility, forms/reporting performance, national risk signals, and executive reporting.

Do not duplicate the State Dashboard operational workflow. The Federal Dashboard should focus on aggregate national and state-level oversight, not day-to-day state operations.

Federal Dashboard sections:
- Header
- National Filter Toolbar
- Executive Summary Cards
- Priority Federal Attention
- State Performance Overview
- National Operational Indicators
- Forms / M&E Reporting Monitor
- Recent Escalations
- Analytics & Trends
- Quick Actions

Executive Summary Cards:
1. National Certification Coverage
2. State Implementation Performance
3. Medical Facility Readiness
4. Inspection & Enforcement Oversight
5. Federal Forms & Reporting
6. National Revenue Summary, permission-controlled

Implement APIs:
- GET /api/federal/dashboard/summary
- GET /api/federal/dashboard/priority-attention
- GET /api/federal/dashboard/state-performance
- GET /api/federal/dashboard/operational-indicators
- GET /api/federal/dashboard/forms-reporting-monitor
- GET /api/federal/dashboard/recent-escalations
- GET /api/federal/dashboard/analytics

Filters:
- Zone
- State
- From Date
- To Date
- Certificate Status
- Facility Status
- Inspection Status
- Form Assignment

Permissions:
- federal_dashboard.view
- federal_dashboard.view_state_performance
- federal_dashboard.view_certification_summary
- federal_dashboard.view_facility_summary
- federal_dashboard.view_inspection_enforcement_summary
- federal_dashboard.view_forms_reporting
- federal_dashboard.view_revenue
- federal_dashboard.export

Privacy:
- Do not expose private medical details.
- Federal dashboard should default to aggregate and state-level summaries.
- Revenue is hidden unless permitted.

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system.
```

---

# 25. MVP Build Order

1. Federal Dashboard API aggregation
2. Federal Dashboard page shell
3. Executive summary cards
4. Priority Federal Attention panel
5. State Performance Overview table
6. National Operational Indicators panel
7. Federal Forms / M&E Reporting monitor
8. Recent Escalations panel
9. Analytics and charts
10. Filters, permissions, responsive QA
