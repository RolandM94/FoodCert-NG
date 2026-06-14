# PRD: State Dashboard Redesign & KPI Consolidation — FoodCert NG

## 1. Document Purpose

This PRD defines the improved **State Ministry Dashboard** for FoodCert NG.

The current dashboard shows many separate metric widgets, which makes the screen feel busy and repetitive. Some metrics are related and should be combined into higher-value summary cards.

For example:

```txt
Food Handlers
Certified Food Handlers
Pending Certificate Validation
Expired Certificates
```

should not be shown as four disconnected cards. They should be combined into a single insight card:

```txt
Food Handler Compliance
├── Total Food Handlers
├── Certified Food Handlers
├── Certification Coverage %
├── Pending Validation
├── Expired Certificates
└── Expiring Soon
```

The goal of the redesigned dashboard is to help State Ministry users quickly answer:

```txt
What is the compliance position of the state?
What requires attention today?
What queues need action?
Where are the risks?
What operational work is delayed?
What trends should leadership monitor?
```

---

# 2. Product Decision

The State Dashboard should move from **many raw metric cards** to **fewer, smarter grouped summary cards**.

## 2.1 Current Problem

The current dashboard separates related metrics into individual cards, such as:

```txt
Food Handlers
Certified Handlers
Pending Certificate Validation
Expired Certificates
Food Businesses
Active Illness Exclusions
RTW Pending
Enforcement Notices
Inspections
Open Enforcement Cases
Approved Facilities
Pending Accreditation
Due for Re-accreditation
```

This creates a dashboard with too many equally weighted widgets.

## 2.2 New Direction

Use grouped cards that summarize related operational areas:

```txt
State Dashboard
├── Filters
├── Executive Summary Cards
├── Priority Actions
├── Operational Queues
├── Recent Activity
├── Analytics / Charts
└── Quick Actions
```

## 2.3 Recommended Executive Summary Cards

Use five main summary cards:

```txt
Food Handler Compliance
Employer Compliance
Medical Facility Readiness
Inspections & Enforcement
Revenue Summary
```

Each card should contain multiple related metrics and a clear action link.

---

# 3. Dashboard Design Principle

The State Dashboard should not be a database dump. It should be a **decision dashboard**.

Each section should help the user decide what to do next.

Use this hierarchy:

```txt
1. Summary: What is the state of compliance?
2. Priority: What needs urgent action?
3. Queues: What work needs processing?
4. Activity: What recently happened?
5. Analytics: What patterns are emerging?
```

---

# 4. State Dashboard Navigation Context

The State Dashboard is the landing page for State Ministry users.

Recommended sidebar structure:

```txt
Dashboard
Stakeholder Management
Medical Facilities
Directory & Registry
Forms Tool
Inspections & Enforcement
Certificates
Payments & Revenue
Reports
Account Settings
```

The Dashboard should not duplicate full module functionality. It should provide summary information and quick access into the relevant modules.

---

# 5. Dashboard Page Structure

## 5.1 Recommended Page Layout

```txt
State Dashboard
├── Header
├── Filter Toolbar
├── Executive Summary Cards
├── Priority Actions
├── Operational Queues
├── Recent Activity
├── Analytics / Charts
└── Quick Actions
```

## 5.2 Header

Header content:

```txt
Eyebrow: STATE MINISTRY ADMIN
Title: State Dashboard
Subtitle: Monitor FoodCert NG compliance, facilities, certificates, inspections, and operational risks across your state.
```

## 5.3 Filter Toolbar

Filters should sit below the header.

Recommended filters:

```txt
LGA
Date Range
Employer Category
Certificate Status
Facility Status
Inspection Status
```

For MVP, use:

```txt
LGA
From Date
To Date
Employer Category
Certificate Status
Apply Filters
Reset
```

## 5.4 Filter Behaviour

Filters should update all dashboard cards, tables, and charts.

Examples:

```txt
LGA = Ikeja
→ Dashboard shows Ikeja-only food handlers, businesses, facilities, certificates, inspections, and enforcement records.

Certificate Status = Expired
→ Food Handler Compliance and Certificate charts update to expired certificate records only where applicable.
```

---

# 6. Executive Summary Cards

The top summary should use fewer grouped cards.

Recommended cards:

```txt
Food Handler Compliance
Employer Compliance
Medical Facility Readiness
Inspections & Enforcement
Revenue Summary
```

## 6.1 Food Handler Compliance Card

### Purpose

Shows whether food handlers in the state are properly certified and whether certificate workflows need attention.

### Combines Former Widgets

```txt
Food Handlers
Certified Handlers
Pending Certificate Validation
Expired Certificates
Certificates Expiring Soon
```

### Card Fields

```txt
Total Food Handlers
Certified Handlers
Certification Coverage %
Pending Certificate Validation
Expired Certificates
Expiring in 30 Days
```

### Example Display

```txt
Food Handler Compliance

4,382 Total Handlers
2,915 Certified
66.5% Coverage

Needs Attention
37 Pending Validation
312 Expired
23 Expiring Soon

[View Food Handlers]
```

### Action Link

```txt
View Food Handlers
```

Route:

```txt
/state/directory?tab=food-handlers
```

or:

```txt
/state/certificates?status=pending_validation
```

depending on clicked metric.

---

## 6.2 Employer Compliance Card

### Purpose

Shows compliance signals for food businesses/employers.

### Combines Former Widgets

```txt
Food Businesses
Active Illness Exclusions
RTW Pending
Open Enforcement Cases
Employer Non-Compliance Signals
```

### Card Fields

```txt
Total Food Businesses
Compliant Employers
Compliance Coverage %
Active Illness Exclusions
RTW Pending
Open Enforcement Cases
High-Risk Employers
```

### Example Display

```txt
Employer Compliance

1,246 Food Businesses
1,012 Compliant
81.2% Compliance Coverage

Risk Signals
6 Active Illness Exclusions
11 RTW Pending
9 Open Enforcement Cases

[View Employers]
```

### Action Link

```txt
View Employers
```

Route:

```txt
/state/directory?tab=employers
```

---

## 6.3 Medical Facility Readiness Card

### Purpose

Shows whether the state has enough approved medical facilities and whether accreditation work needs attention.

### Combines Former Widgets

```txt
Approved Facilities
Pending Accreditation
Due for Re-accreditation
Expired Facility Accreditation
Suspended Facilities
```

### Card Fields

```txt
Approved Facilities
Pending Accreditation Applications
Due for Re-accreditation
Expired Accreditation
Suspended Facilities
Assessment Capacity Status
```

### Example Display

```txt
Medical Facility Readiness

876 Approved Facilities
14 Pending Accreditation
18 Due for Re-accreditation

Risks
3 Expired Accreditation
1 Suspended Facility

[View Facilities]
```

### Action Link

```txt
View Facilities
```

Route:

```txt
/state/medical-facilities
```

---

## 6.4 Inspections & Enforcement Card

### Purpose

Shows inspection workload, enforcement pressure, and unresolved corrective actions.

### Combines Former Widgets

```txt
Inspections
Enforcement Notices
Open Enforcement Cases
Corrective Actions Overdue
Overdue Inspections
```

### Card Fields

```txt
Open Inspections
Completed Inspections
Overdue Inspections
Open Enforcement Cases
Corrective Actions Overdue
High/Critical Findings
```

### Example Display

```txt
Inspections & Enforcement

28 Open Inspections
114 Completed This Period
12 Overdue

Enforcement
9 Open Cases
5 Corrective Actions Overdue
3 Critical Findings

[Open Inspections]
```

### Action Link

```txt
Open Inspections
```

Route:

```txt
/state/inspections-enforcement
```

---

## 6.5 Revenue Summary Card

### Purpose

Shows state collections and settlement position.

### Combines Former Widgets

```txt
State Revenue
Assessment Fees Collected
Certificate Fees
Facility Accreditation Fees
Settlement Pending
```

### Card Fields

```txt
Total Revenue
Assessment Fee Revenue
Certificate Fee Revenue
Facility Accreditation Fee Revenue
Settlements Pending
Refunds / Failed Payments, if relevant
```

### Example Display

```txt
Revenue Summary

₦12.45M Collected
₦8.20M Assessment Fees
₦2.10M Certificate Fees
₦2.15M Facility Fees

₦1.40M Pending Settlement

[View Revenue]
```

### Action Link

```txt
View Revenue
```

Route:

```txt
/state/payments-revenue
```

---

# 7. Priority Actions Section

## 7.1 Purpose

The Priority Actions section should show what needs urgent attention.

This section should be above detailed queues/tables.

## 7.2 Recommended Priority Action Cards

```txt
High-risk facilities pending review
Overdue inspections
Certificates expiring soon
Corrective actions overdue
Pending certificate validation
Applications awaiting accreditation review
```

## 7.3 Example Display

```txt
Priority Actions

High-risk facilities pending review    7     [View facilities]
Overdue inspections                    12    [View inspections]
Certificates expiring in 30 days       23    [View certificates]
Corrective actions overdue             5     [View enforcement]
Pending certificate validation          37    [Review certificates]
```

## 7.4 Priority Severity

Each item should have a visual severity:

```txt
Critical
High
Medium
Low
```

Color guidance:

```txt
Critical = red
High = orange
Medium = amber
Low = neutral/green
```

## 7.5 Action Links

Each priority item should deep-link to the relevant module with filters applied.

Examples:

```txt
/state/medical-facilities?filter=high_risk_pending_review
/state/inspections-enforcement?status=overdue
/state/certificates?expiry=30_days
/state/inspections-enforcement?tab=corrective-actions&status=overdue
```

---

# 8. Operational Queues Section

## 8.1 Purpose

Operational Queues show work that State users need to process.

## 8.2 Recommended Queues

```txt
Facility Accreditation
Certificate Validation
Inspection Review
Enforcement Follow-up
Re-accreditation
Form Responses Review
Payment Reconciliation
```

## 8.3 Queue Table Columns

```txt
Queue
Count
Oldest Pending
Priority
Status
Action
```

## 8.4 Example

```txt
Queue                     Count    Oldest Pending    Status
Facility Accreditation    14       6 days            Pending
Certificate Validation    37       2 days            Pending
Inspection Review         28       3 days            In Progress
Enforcement Follow-up     9        8 days            Pending
Re-accreditation          18       12 days           Pending
```

## 8.5 Queue Action Routes

```txt
Facility Accreditation → /state/medical-facilities?tab=accreditation
Certificate Validation → /state/certificates?status=pending_validation
Inspection Review → /state/inspections-enforcement?tab=inspections&status=submitted
Enforcement Follow-up → /state/inspections-enforcement?tab=cases&status=open
Re-accreditation → /state/medical-facilities?tab=facilities&filter=reaccreditation_due
Form Responses Review → /state/forms?tab=responses&status=submitted
Payment Reconciliation → /state/payments-revenue?tab=reconciliation
```

---

# 9. Recent Activity Section

## 9.1 Purpose

Shows recently completed or submitted activities.

## 9.2 Recommended Recent Activity Panels

```txt
Recent Inspections
Recent Certificate Requests
Recent Facility Applications
Recent Enforcement Actions
Recent Form Submissions
```

## 9.3 Recent Inspections Table

Columns:

```txt
Employer
LGA
Inspection Type
Status
Severity
Date
Action
```

## 9.4 Recent Certificate Requests Table

Columns:

```txt
Food Handler / Employer
Request Type
Submitted Date
Status
Action
```

## 9.5 Recent Facility Applications Table

Columns:

```txt
Facility
Application Type
Submitted Date
Status
Reviewer
Action
```

## 9.6 Display Rule

Do not show too many tables at once.

Recommended layout:

```txt
Recent Activity
├── Tabs: Inspections | Certificates | Facilities | Enforcement | Forms
└── One table shown at a time
```

This reduces visual clutter.

---

# 10. Analytics and Charts

## 10.1 Purpose

Charts should show trends and distribution, not repeat raw cards.

## 10.2 Recommended Charts

```txt
Certificate Status Distribution
Compliance by LGA
Inspection Outcomes by Severity
Facility Accreditation Status
Revenue Trend
Response Rate by Form Assignment
```

## 10.3 MVP Charts

For MVP:

```txt
Certificate Status Distribution
Compliance by LGA
Inspection Outcomes by Severity
Revenue Trend
```

## 10.4 Chart Placement

Charts should be placed below summary and priority sections.

They should not take priority over urgent operational queues.

---

# 11. Quick Actions

## 11.1 Purpose

Quick Actions help users start common workflows.

## 11.2 Recommended Quick Actions

```txt
Create Inspection
Review Certificates
View Facilities
Open Reports
Create Form Assignment
Review Accreditation Applications
```

## 11.3 Placement

Place Quick Actions near Priority Actions or as a right-side panel on desktop.

On mobile, show Quick Actions as a horizontal scroll list or collapsed action menu.

---

# 12. Dashboard Metrics Dictionary

This section defines key metrics for implementation.

## 12.1 Food Handler Compliance

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

## 12.2 Employer Compliance

```txt
total_employers
compliant_employers
employer_compliance_coverage_percentage
active_illness_exclusions_count
return_to_work_pending_count
open_enforcement_cases_count
high_risk_employers_count
```

Calculation:

```txt
employer_compliance_coverage_percentage =
(compliant_employers / total_employers) * 100
```

## 12.3 Medical Facility Readiness

```txt
approved_facilities_count
pending_accreditation_count
due_for_reaccreditation_count
expired_facility_accreditation_count
suspended_facilities_count
facility_capacity_status
```

## 12.4 Inspections & Enforcement

```txt
open_inspections_count
completed_inspections_count
overdue_inspections_count
open_enforcement_cases_count
corrective_actions_overdue_count
critical_findings_count
high_findings_count
```

## 12.5 Revenue Summary

```txt
total_revenue_collected
assessment_fee_revenue
certificate_fee_revenue
facility_accreditation_fee_revenue
pending_settlements
failed_payments_count
refunds_count
```

---

# 13. Dashboard API Requirements

## 13.1 Main Dashboard Summary API

```txt
GET /api/state/dashboard/summary
```

Query params:

```txt
state_id
lga
date_from
date_to
employer_category
certificate_status
facility_status
inspection_status
```

Response structure:

```json
{
  "filters": {
    "state": "Lagos",
    "lga": "All LGAs",
    "date_from": "2026-06-01",
    "date_to": "2026-06-30"
  },
  "food_handler_compliance": {
    "total_food_handlers": 4382,
    "certified_food_handlers": 2915,
    "certification_coverage_percentage": 66.5,
    "pending_certificate_validation_count": 37,
    "expired_certificates_count": 312,
    "certificates_expiring_soon_count": 23
  },
  "employer_compliance": {
    "total_employers": 1246,
    "compliant_employers": 1012,
    "employer_compliance_coverage_percentage": 81.2,
    "active_illness_exclusions_count": 6,
    "return_to_work_pending_count": 11,
    "open_enforcement_cases_count": 9,
    "high_risk_employers_count": 7
  },
  "medical_facility_readiness": {
    "approved_facilities_count": 876,
    "pending_accreditation_count": 14,
    "due_for_reaccreditation_count": 18,
    "expired_facility_accreditation_count": 3,
    "suspended_facilities_count": 1
  },
  "inspections_enforcement": {
    "open_inspections_count": 28,
    "completed_inspections_count": 114,
    "overdue_inspections_count": 12,
    "open_enforcement_cases_count": 9,
    "corrective_actions_overdue_count": 5,
    "critical_findings_count": 3
  },
  "revenue_summary": {
    "total_revenue_collected": 12450000,
    "assessment_fee_revenue": 8200000,
    "certificate_fee_revenue": 2100000,
    "facility_accreditation_fee_revenue": 2150000,
    "pending_settlements": 1400000
  }
}
```

## 13.2 Priority Actions API

```txt
GET /api/state/dashboard/priority-actions
```

Response:

```json
{
  "items": [
    {
      "key": "high_risk_facilities_pending_review",
      "label": "High-risk facilities pending review",
      "count": 7,
      "severity": "critical",
      "route": "/state/medical-facilities?filter=high_risk_pending_review"
    },
    {
      "key": "overdue_inspections",
      "label": "Overdue inspections",
      "count": 12,
      "severity": "high",
      "route": "/state/inspections-enforcement?status=overdue"
    }
  ]
}
```

## 13.3 Operational Queues API

```txt
GET /api/state/dashboard/operational-queues
```

## 13.4 Recent Activity API

```txt
GET /api/state/dashboard/recent-activity
```

## 13.5 Analytics API

```txt
GET /api/state/dashboard/analytics
```

---

# 14. Frontend Components

## 14.1 Page-Level Components

```txt
StateDashboardPage
StateDashboardHeader
StateDashboardFilters
ExecutiveSummaryGrid
PriorityActionsPanel
OperationalQueuesPanel
RecentActivityPanel
DashboardAnalyticsSection
QuickActionsPanel
```

## 14.2 Summary Card Components

```txt
FoodHandlerComplianceCard
EmployerComplianceCard
MedicalFacilityReadinessCard
InspectionsEnforcementCard
RevenueSummaryCard
```

## 14.3 Shared Components

```txt
MetricLine
MetricGroup
CoverageProgressBar
TrendIndicator
StatusBadge
PriorityBadge
DashboardCard
DashboardSection
EmptyState
LoadingSkeleton
```

## 14.4 Chart Components

```txt
CertificateStatusDonut
ComplianceByLgaBarChart
InspectionSeverityChart
RevenueTrendChart
```

---

# 15. UI Consolidation Rules

## 15.1 Combine Related Metrics

Do not render these as separate independent KPI cards:

```txt
Food Handlers
Certified Handlers
Pending Certificate Validation
Expired Certificates
```

They belong under:

```txt
Food Handler Compliance
```

Do not render these as separate independent KPI cards:

```txt
Food Businesses
Active Illness Exclusions
RTW Pending
Open Enforcement Cases
```

They belong under:

```txt
Employer Compliance
```

Do not render these as separate independent KPI cards:

```txt
Approved Facilities
Pending Accreditation
Due for Re-accreditation
```

They belong under:

```txt
Medical Facility Readiness
```

Do not render these as separate independent KPI cards:

```txt
Inspections
Enforcement Notices
Open Enforcement Cases
Corrective Actions Overdue
```

They belong under:

```txt
Inspections & Enforcement
```

## 15.2 Avoid Widget Duplication

If a metric appears inside an executive summary card, it should not also appear as a separate top-level card unless it is in a detailed table/chart context.

## 15.3 Action-Oriented Cards

Every summary card should have:

```txt
Primary metric
Coverage/ratio where useful
Needs attention subsection
Action link
```

## 15.4 State Dashboard Is Not a Module Replacement

The dashboard should link into modules, not replace them.

Example:

```txt
Pending Accreditation count
→ Links to Medical Facilities → Accreditation filter
```

## 15.5 Illness/RTW as Oversight Signals

Active Illness Exclusions and RTW Pending should remain under Employer Compliance or Priority Actions, not as standalone State workflow cards.

---

# 16. Responsive Design Rules

## 16.1 Desktop

Desktop layout:

```txt
Header
Filters
5 summary cards in responsive grid
Priority Actions + Quick Actions
Operational Queues + Recent Activity
Analytics Charts
```

## 16.2 Tablet

Tablet layout:

```txt
2-column summary cards
Priority Actions full width
Tables stacked
Charts stacked
```

## 16.3 Mobile

Mobile layout:

```txt
Header
Collapsed filters
Horizontal summary cards or stacked cards
Priority actions
Queues
Recent activity
Charts
```

## 16.4 Mobile Summary Cards

On mobile, each summary card should be compact:

```txt
Title
Primary number
Coverage/status
Needs attention count
CTA
```

---

# 17. Permissions and Scope

## 17.1 Permissions

Recommended permissions:

```txt
state_dashboard.view
state_dashboard.view_revenue
state_dashboard.view_enforcement_summary
state_dashboard.view_health_signals
state_dashboard.export
```

## 17.2 Scope Rules

- State users see only their state.
- LGA filter limits records to selected LGA.
- Users without revenue permission should not see revenue values.
- Users without enforcement permission should see only limited enforcement summary or no enforcement card.
- Users without illness/RTW visibility should not see those signals.

## 17.3 Revenue Card Permission

If user lacks revenue permission:

```txt
Revenue Summary card should be hidden
```

or show:

```txt
Restricted
You do not have permission to view revenue data.
```

Recommended: hide the card for cleaner UI.

---

# 18. Empty, Loading, and Error States

## 18.1 Loading

Use skeleton cards for:

```txt
Summary Cards
Priority Actions
Operational Queues
Recent Activity
Charts
```

## 18.2 Empty State

If no data exists:

```txt
No dashboard data available for the selected filters.
Try adjusting your filters or date range.
```

## 18.3 Error State

If API fails:

```txt
Unable to load dashboard data.
Retry
```

Show partial data where possible.

---

# 19. Acceptance Criteria

## 19.1 Dashboard Structure

- Dashboard has header, filters, executive summary cards, priority actions, queues, recent activity, charts, and quick actions.
- Summary metrics are grouped into decision-making cards.
- Related raw metrics are not shown as separate top-level cards.

## 19.2 Executive Summary Cards

- Food Handler Compliance combines total handlers, certified handlers, coverage, pending validation, expired, and expiring soon.
- Employer Compliance combines food businesses, compliance coverage, illness exclusions, RTW pending, enforcement cases, and high-risk employers.
- Medical Facility Readiness combines approved facilities, pending accreditation, due for reaccreditation, expired, and suspended.
- Inspections & Enforcement combines open inspections, completed inspections, overdue inspections, enforcement cases, corrective actions, and critical findings.
- Revenue Summary combines all revenue-related metrics.

## 19.3 Priority Actions

- Priority Actions show urgent items.
- Each item has severity, count, and action link.
- Links route to the correct module with filters.

## 19.4 Operational Queues

- Queues show pending work by module.
- Queues deep-link to relevant workflow.
- Counts match filters.

## 19.5 Recent Activity

- Recent activity is grouped and does not overcrowd the dashboard.
- Recent activity supports tabs or compact panels.

## 19.6 Charts

- Charts show distribution/trends.
- Charts do not duplicate summary card information unnecessarily.
- Charts respect selected filters.

## 19.7 Permissions

- Dashboard data is state-scoped.
- Revenue card is permission-controlled.
- Enforcement and illness/RTW signals are permission-controlled where required.

## 19.8 UI Quality

- Dashboard is cleaner than the current many-widget design.
- Cards are readable and scannable.
- Layout is responsive.
- Empty/loading/error states are implemented.

---

# 20. Implementation Chunks for Codex

## Chunk 1: Dashboard Data Model and API Aggregation

### Goal

Create backend aggregation endpoints for the redesigned dashboard.

### Tasks

- Implement `/api/state/dashboard/summary`.
- Implement `/api/state/dashboard/priority-actions`.
- Implement `/api/state/dashboard/operational-queues`.
- Implement `/api/state/dashboard/recent-activity`.
- Implement `/api/state/dashboard/analytics`.
- Add filter support.
- Add state scoping.
- Add permission-based response shaping.

### Acceptance Criteria

- APIs return grouped metrics.
- Filters affect all returned data.
- State scoping is enforced.
- Restricted metrics are hidden or omitted based on permission.

---

## Chunk 2: Dashboard Page Shell

### Goal

Build the redesigned dashboard page structure.

### Tasks

- Create or update `StateDashboardPage`.
- Add page header.
- Add filter toolbar.
- Add section layout:
  - Executive Summary
  - Priority Actions
  - Operational Queues
  - Recent Activity
  - Analytics
  - Quick Actions
- Add loading and error states.

### Acceptance Criteria

- Page renders redesigned structure.
- Filters are visible and usable.
- Sections are clearly grouped.
- Layout follows FoodCert NG design system.

---

## Chunk 3: Executive Summary Cards

### Goal

Replace many raw widgets with grouped insight cards.

### Tasks

- Create:
  - `FoodHandlerComplianceCard`
  - `EmployerComplianceCard`
  - `MedicalFacilityReadinessCard`
  - `InspectionsEnforcementCard`
  - `RevenueSummaryCard`
- Add primary metrics, sub-metrics, coverage percentages, needs-attention areas, and CTA links.
- Remove old individual metric cards where replaced.

### Acceptance Criteria

- Food handler and certified handler metrics are combined.
- Employer-related compliance metrics are combined.
- Facility readiness metrics are combined.
- Inspection/enforcement metrics are combined.
- Revenue metrics are combined.
- Cards link to correct modules.

---

## Chunk 4: Priority Actions Panel

### Goal

Create action-driven urgent work section.

### Tasks

- Build `PriorityActionsPanel`.
- Render priority cards/list from API.
- Add severity badges.
- Add count and CTA.
- Deep-link to relevant filtered module route.

### Acceptance Criteria

- Priority actions are visible above queues.
- Critical/high items are visually prominent.
- CTA links work.

---

## Chunk 5: Operational Queues Panel

### Goal

Show pending work queues across modules.

### Tasks

- Build `OperationalQueuesPanel`.
- Show queues table/cards.
- Add count, oldest pending, priority, and status.
- Add route links.

### Acceptance Criteria

- Queues display current workload.
- Queue actions route to correct module.
- Counts respect filters.

---

## Chunk 6: Recent Activity Consolidation

### Goal

Reduce dashboard clutter from multiple separate activity tables.

### Tasks

- Build `RecentActivityPanel`.
- Use tabs or segmented controls:
  - Inspections
  - Certificates
  - Facilities
  - Enforcement
  - Forms
- Render one compact table at a time.
- Add View All links.

### Acceptance Criteria

- Recent activity does not overcrowd dashboard.
- Users can switch activity type.
- Links route to detailed module pages.

---

## Chunk 7: Analytics and Charts

### Goal

Add useful charts without duplicating raw metrics.

### Tasks

- Build chart components:
  - CertificateStatusDonut
  - ComplianceByLgaBarChart
  - InspectionSeverityChart
  - RevenueTrendChart
- Add filters.
- Add empty states.
- Add permission control for revenue chart.

### Acceptance Criteria

- Charts render correctly.
- Charts respect filters.
- Charts provide trend/distribution insights.
- Revenue chart is permission-controlled.

---

## Chunk 8: Filter Toolbar

### Goal

Implement dashboard-wide filters.

### Tasks

- Add filters:
  - LGA
  - From Date
  - To Date
  - Employer Category
  - Certificate Status
  - Facility Status, optional
  - Inspection Status, optional
- Add Apply and Reset.
- Sync filters to URL query params.
- Refetch dashboard APIs on apply.

### Acceptance Criteria

- Filters update dashboard data.
- URL query state works.
- Reset restores default dashboard.

---

## Chunk 9: Permission and Scope Handling

### Goal

Ensure dashboard data is secure.

### Tasks

- Implement permission checks.
- Hide Revenue Summary for unauthorized users.
- Hide restricted enforcement/illness signals where required.
- Enforce state and LGA scope.
- Add tests.

### Acceptance Criteria

- Users see only authorized data.
- State scoping works.
- Revenue data is protected.
- Dashboard does not leak restricted information.

---

## Chunk 10: Responsive UI and Final QA

### Goal

Ensure dashboard works well across devices.

### Tasks

- Implement responsive grid.
- Stack cards on mobile.
- Collapse filters on mobile.
- Add skeleton states.
- Add empty states.
- Add error states.
- Test deep links.
- Remove old unused dashboard widgets/components.

### Acceptance Criteria

- Desktop, tablet, and mobile layouts work.
- Old raw widget layout is removed.
- Dashboard is cleaner and easier to scan.
- All sections meet acceptance criteria.

---

# 21. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Redesign the FoodCert NG State Ministry Dashboard.

The current dashboard has too many separate KPI widgets. Combine related metrics into smarter grouped summary cards.

Use this dashboard structure:
- Header
- Filter Toolbar
- Executive Summary Cards
- Priority Actions
- Operational Queues
- Recent Activity
- Analytics / Charts
- Quick Actions

Replace separate raw cards with grouped cards:
1. Food Handler Compliance
   - Total Food Handlers
   - Certified Handlers
   - Certification Coverage %
   - Pending Certificate Validation
   - Expired Certificates
   - Expiring Soon

2. Employer Compliance
   - Food Businesses
   - Compliant Employers
   - Compliance Coverage %
   - Active Illness Exclusions
   - RTW Pending
   - Open Enforcement Cases
   - High-Risk Employers

3. Medical Facility Readiness
   - Approved Facilities
   - Pending Accreditation
   - Due for Re-accreditation
   - Expired Accreditation
   - Suspended Facilities

4. Inspections & Enforcement
   - Open Inspections
   - Completed Inspections
   - Overdue Inspections
   - Open Enforcement Cases
   - Corrective Actions Overdue
   - Critical Findings

5. Revenue Summary
   - Total Revenue
   - Assessment Fee Revenue
   - Certificate Fee Revenue
   - Facility Accreditation Fee Revenue
   - Pending Settlements

Add Priority Actions:
- High-risk facilities pending review
- Overdue inspections
- Certificates expiring soon
- Corrective actions overdue
- Pending certificate validation
- Applications awaiting accreditation review

Add Operational Queues:
- Facility Accreditation
- Certificate Validation
- Inspection Review
- Enforcement Follow-up
- Re-accreditation
- Form Responses Review
- Payment Reconciliation

Add Recent Activity as a consolidated tabbed panel, not many separate tables.

Add charts:
- Certificate Status Distribution
- Compliance by LGA
- Inspection Outcomes by Severity
- Revenue Trend, permission-controlled

Implement APIs:
- GET /api/state/dashboard/summary
- GET /api/state/dashboard/priority-actions
- GET /api/state/dashboard/operational-queues
- GET /api/state/dashboard/recent-activity
- GET /api/state/dashboard/analytics

Filters:
- LGA
- From Date
- To Date
- Employer Category
- Certificate Status
- Facility Status, optional
- Inspection Status, optional

Permissions:
- state_dashboard.view
- state_dashboard.view_revenue
- state_dashboard.view_enforcement_summary
- state_dashboard.view_health_signals
- state_dashboard.export

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system.

Do not render Food Handlers and Certified Handlers as separate top-level cards. They must be combined under Food Handler Compliance.

Do not render Approved Facilities, Pending Accreditation, and Due for Re-accreditation as separate top-level cards. They must be combined under Medical Facility Readiness.

Do not render Illness Exclusions and RTW Pending as standalone State workflow cards. They should appear as oversight signals under Employer Compliance or Priority Actions.
```

---

# 22. MVP Build Order

1. Dashboard API aggregation
2. Dashboard page shell
3. Executive summary cards
4. Priority actions panel
5. Operational queues panel
6. Recent activity consolidation
7. Analytics/charts
8. Filter toolbar
9. Permissions and scope handling
10. Responsive UI and final QA
