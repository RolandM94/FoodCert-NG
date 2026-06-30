# FoodCert NG Flexible AI Dashboard Module PRD

## Update Note: Indicators Added

This updated version explicitly adds **Indicators** as a first-class data source for the dashboard engine, including indicator definitions, targets, measurements/results, performance status, account-specific visibility, indicator widgets, AI prompts, and a dedicated implementation chunk.


## 1. Document Purpose

This PRD redesigns the earlier Federal Dashboard concept into a **platform-wide flexible dashboard module** for FoodCert NG.

The dashboard module should support multiple account types:

```txt
Federal Ministry
State Ministry
Employer / Food Business
Medical Facility
Platform Admin
```

The dashboard should not be a fixed hardcoded page for only one account type. It should be a **customisable analytics and dashboard system** that allows each account type to explore approved datasets, build reusable analytical logic, create widgets, arrange widgets on a dashboard canvas, apply filters, use AI to generate insights, publish dashboard views, and export dashboards/reports.

This PRD adapts the core analytics/dashboard concepts from the uploaded analytics dashboard document into the FoodCert NG application architecture and workflows.

---

# 2. Product Vision

FoodCert NG should have a flexible, AI-assisted dashboard system that gives each account type the right level of visibility and control.

The system should combine:

```txt
Data exploration
Reusable analytics logic
Visual widgets
Drag-and-drop dashboards
AI-assisted insight generation
Role-based visibility
Export and sharing
```

The goal is to allow FoodCert NG users to move beyond fixed dashboards and create dashboard views that answer operational, compliance, regulatory, revenue, accreditation, inspection, and performance questions.

---

# 3. Core Product Decision

The FoodCert NG dashboard module should use a layered architecture:

```txt
Dataset
→ Worksheet
→ Widget
→ Dashboard Canvas
→ Published Dashboard View
```

## 3.1 Dataset Layer

The source data available for analysis.

Examples:

```txt
Food Handlers
Certificates
Employers / Food Businesses
Employer Branches / Outlets
Medical Facilities
Facility Accreditation Applications
Medical Assessments
Inspections
Enforcement Cases
Corrective Actions
Forms Responses
Indicators
Indicator Results / Measurements
Indicator Targets
Indicator Performance
Payments
Settlements
Notifications
Audit Logs
State Reports
Federal Reports
```

## 3.2 Worksheet Layer

The reusable analytical logic layer.

A worksheet defines:

```txt
Dataset
Metrics
Dimensions
Filters
Aggregations
Derived fields
Query rules
Chart recommendation
Preview output
```

Example:

```txt
Worksheet Name: Certificate Coverage by LGA
Dataset: Certificates + Food Handlers
Metric: Certified Food Handlers Count
Dimension: LGA
Filter: Certificate Status = Active
Visualization: Bar Chart
```

## 3.3 Widget Layer

The visual component layer.

A widget references a worksheet and displays the result as:

```txt
KPI Card
Bar Chart
Line Chart
Pie / Donut Chart
Table
Map
Progress Card
Queue Card
Trend Card
Risk Card
AI Insight Card
```

## 3.4 Dashboard Canvas Layer

The editable workspace where users arrange widgets.

A canvas can contain:

```txt
Widgets
Text blocks
Filter blocks
AI insight blocks
Narrative blocks
Data preview blocks
Quick action blocks
```

## 3.5 Published Dashboard View

A published, read-only dashboard derived from a canvas.

It is used for executives, supervisors, reporting, sharing, presentation, and cross-account oversight.

---

# 4. Account-Type Dashboard Logic

The same flexible dashboard system should serve all account types, but each account type must have different datasets, permissions, templates, AI capabilities, and default dashboards.

---

## 4.1 Federal Ministry Dashboard

### Purpose

Federal users need national oversight, cross-state comparison, policy monitoring, national M&E, guideline implementation tracking, and aggregate performance monitoring.

### Federal Dashboard Focus

```txt
National compliance overview
State-by-state performance
Certificate coverage across states
Medical facility accreditation performance by state
Inspection and enforcement trends
Forms/reporting response rate by state
Policy adoption and implementation status
Revenue summary, if permitted
National risk signals
```

### Federal Datasets

```txt
States
State Ministry Profiles
State-level Food Handler Aggregates
State-level Certificate Aggregates
State-level Employer Aggregates
State-level Medical Facility Aggregates
State-level Inspection Aggregates
Federal Forms Responses
Indicators
Indicator Results / Measurements
Indicator Targets
Indicator Performance
State Reports
National Templates Adoption
Cross-State Compliance Indicators
```

### Federal Default Dashboards

```txt
National Overview Dashboard
State Performance Comparison Dashboard
Guideline Implementation Dashboard
National Facility Accreditation Dashboard
National Certificate Coverage Dashboard
Inspection & Enforcement Trend Dashboard
Federal Forms Reporting Dashboard
```

### Federal Restrictions

Federal dashboards should default to aggregate and cross-state views.

Federal users should not see sensitive medical details or private individual-level records unless explicitly permitted.

---

## 4.2 State Ministry Dashboard

### Purpose

State users need operational management, compliance monitoring, accreditation review, certificate validation, inspection management, enforcement tracking, revenue monitoring, and state-level reporting.

### State Dashboard Focus

```txt
Food handler compliance
Employer compliance
Medical facility readiness
Certificate validation queue
Facility accreditation queue
Inspection and enforcement workload
Illness/return-to-work oversight signals
Revenue and settlements
Forms response tracking
Operational priority actions
```

### State Datasets

```txt
Food Handlers
Certificates
Employers
Branches / Outlets
Medical Facilities
Accreditation Applications
Medical Assessments
Inspections
Enforcement Cases
Corrective Actions
Forms Responses
Indicators
Indicator Results / Measurements
Indicator Targets
Indicator Performance
Payments
Settlements
State Audit Logs
```

### State Default Dashboards

```txt
State Executive Dashboard
Food Handler Compliance Dashboard
Medical Facility Readiness Dashboard
Inspections & Enforcement Dashboard
Certificate Validation Dashboard
Payments & Revenue Dashboard
Forms Response Monitoring Dashboard
```

---

## 4.3 Employer / Food Business Dashboard

### Purpose

Employers need to monitor their own compliance, branches, food handlers, certificates, illness exclusions, RTW status, assigned forms, inspections, notices, and subscriptions.

### Employer Dashboard Focus

```txt
Food handler certification coverage
Branch/outlet compliance
Expiring certificates
Pending assessments
Illness exclusions
Return-to-work pending cases
Inspection outcomes
Corrective actions
Enforcement notices
Assigned forms
Subscription/payment status
```

### Employer Datasets

```txt
Employer Profile
Branches / Outlets
Linked Food Handlers
Certificates
Assessment Requests
Illness Reports
Return-to-Work Cases
Employer Inspections
Enforcement Notices
Corrective Actions
Assigned Forms
Employer Compliance Indicators
Branch Compliance Indicators
Subscription Payments
```

### Employer Default Dashboards

```txt
Employer Compliance Dashboard
Branch Compliance Dashboard
Food Handler Certification Dashboard
Inspection & Corrective Actions Dashboard
Assigned Forms Dashboard
```

### Employer Restrictions

Employers must not see private medical details such as:

```txt
Diagnosis
Lab results
Doctor notes
Health declaration answers
Treatment notes
Private medical reports
```

Employer dashboards should show only operational statuses.

---

## 4.4 Medical Facility Dashboard

### Purpose

Medical facilities need to monitor accreditation status, assessment workload, doctor/lab queues, submitted results, certificate decisions, return-to-work cases, assigned forms, settlements, and performance.

### Medical Facility Dashboard Focus

```txt
Accreditation status
Accreditation expiry
Assessment appointments
Doctor review queue
Lab review queue
Certificate submissions
Rejected/pending cases
Return-to-work clearance queue
Assigned forms
Settlement and payment status
Facility performance
```

### Medical Facility Datasets

```txt
Facility Profile
Accreditation Applications
Facility Staff
Assessment Appointments
Medical Assessments
Lab Requests
Doctor Decisions
Certificate Submissions
Return-to-Work Cases
Assigned Forms
Facility Performance Indicators
Assessment Turnaround Indicators
Payments / Settlements
Facility Audit Logs
```

### Medical Facility Default Dashboards

```txt
Facility Operations Dashboard
Assessment Workflow Dashboard
Doctor/Lab Queue Dashboard
Certificate Submission Dashboard
Settlement Dashboard
Accreditation Status Dashboard
```

### Medical Facility Restrictions

Medical facilities can see medical details only for records assigned to or performed by that facility and only by authorized users.

---

## 4.5 Platform Admin Dashboard

### Purpose

Platform Admin users need system-level monitoring, adoption, account health, usage, performance, errors, payments, support, and audit visibility.

### Platform Admin Dashboard Focus

```txt
Platform usage
Account onboarding
Module adoption
System health
Failed jobs
Payment gateway health
Notification delivery
API performance
Security events
Audit events
AI usage
Storage usage
```

---

# 5. Core Features

## 5.1 Dashboard Home

Each account type should have a Dashboard Home.

The Dashboard Home should show:

```txt
Default dashboard for the account
Recently used dashboards
Saved dashboards
Shared dashboards
Dashboard templates
Create New Dashboard action
AI dashboard prompt
```

### Dashboard Home Actions

```txt
Create Dashboard
Create Worksheet
Use Template
Ask AI
Open Existing Dashboard
Publish Dashboard
Export Dashboard
```

---

## 5.2 Dataset Catalogue

The dashboard module should expose a role-based dataset catalogue.

### Dataset Catalogue Requirements

Each dataset must define:

```txt
Dataset name
Description
Module source
Allowed account types
Allowed roles
Available fields
Field labels
Field types
Sensitive fields
Default filters
Joinable datasets
Aggregation rules
```

### Dataset Examples

```txt
Food Handlers
Certificates
Employers
Facilities
Inspections
Forms Responses
Indicators
Indicator Results / Measurements
Indicator Targets
Indicator Performance
Payments
State Aggregates
Federal Aggregates
```

### Dataset Access Rules

Datasets must be scoped by:

```txt
Account type
Organization
State
LGA
Role
Permission
Unit/branch restriction
Privacy classification
```

## 5.2.1 Indicators as a First-Class Dashboard Data Source

Indicators must be treated as a core analytics dataset, not only as a Federal aggregate reference.

The dashboard engine must support indicators across Federal, State, Employer, and Medical Facility dashboards, with account-specific scoping.

### Indicator Dataset Purpose

Indicators allow FoodCert NG to track measurable performance, compliance, operational effectiveness, and policy implementation outcomes.

Examples:

```txt
Certificate coverage rate
Food handler compliance rate
Employer compliance rate
Branch compliance rate
Inspection completion rate
Inspection overdue rate
Accreditation approval rate
Facility accreditation coverage
Assessment turnaround time
Certificate issuance turnaround time
Return-to-work clearance turnaround time
Corrective action closure rate
Forms response rate
State reporting compliance rate
Revenue collection performance
Settlement turnaround time
Guideline implementation score
```

### Indicator Dataset Entities

The dataset catalogue should expose the following indicator-related datasets where available:

```txt
Indicators
Indicator Definitions
Indicator Targets
Indicator Results / Measurements
Indicator Periods
Indicator Owners
Indicator Performance
Indicator Data Sources
Indicator Exceptions / Flags
```

### Indicator Field Examples

```txt
indicator_code
indicator_name
indicator_category
indicator_description
account_type_scope
owner_organization
state
lga
period_type
period_start
period_end
baseline_value
target_value
actual_value
achievement_percentage
performance_status
data_source_module
calculation_method
last_calculated_at
```

### Indicator Performance Statuses

```txt
On Track
At Risk
Off Track
Exceeded Target
No Data
Pending Validation
```

### Indicator Dashboard Use Cases by Account Type

Federal users can use indicators for:

```txt
National policy implementation tracking
State-by-state compliance comparison
Guideline implementation scorecards
Federal M&E dashboards
Cross-state performance ranking
National reporting to leadership
```

State users can use indicators for:

```txt
State compliance performance
LGA-by-LGA performance
Inspection completion tracking
Certificate coverage monitoring
Accreditation backlog monitoring
Operational SLA tracking
```

Employer users can use indicators for:

```txt
Branch compliance score
Food handler certification coverage
Certificate renewal performance
Corrective action closure rate
Assigned form completion rate
```

Medical Facility users can use indicators for:

```txt
Assessment turnaround time
Doctor review turnaround time
Lab completion turnaround time
Certificate submission rate
Rejected assessment rate
Settlement turnaround time
```

### Indicator Calculation Rules

Indicators may be:

```txt
Manual
Auto-calculated from module activity
Imported from forms
Derived from multiple datasets
Validated by an authorized officer
```

Examples:

```txt
Certificate Coverage Rate = Active Certified Food Handlers / Total Linked Food Handlers * 100
Inspection Completion Rate = Completed Inspections / Scheduled Inspections * 100
Corrective Action Closure Rate = Closed Corrective Actions / Total Corrective Actions * 100
Forms Response Rate = Submitted Responses / Assigned Recipients * 100
```

### Indicator Widget Examples

```txt
KPI: Certificate Coverage Rate
Progress Card: State Guideline Implementation Score
Bar Chart: Indicator Performance by State
Line Chart: Compliance Rate Over Time
Table: Indicators Off Track
Map: State Performance Heatmap
AI Insight: Explain why an indicator is off track
```

### Indicator AI Requirements

The AI assistant must understand indicator definitions and calculation methods.

Example prompts:

```txt
Show certificate coverage rate by state.
Which states are off track on facility accreditation?
Explain why inspection completion declined this quarter.
Create a dashboard for guideline implementation indicators.
Show employers below 70% certification coverage.
```

AI must not invent indicator values. It must use approved indicator definitions, calculation methods, and accessible underlying datasets.

---

## 5.3 Worksheet Builder

### Purpose

The Worksheet Builder is the logic layer. It lets users define analytics before creating widgets.

### Worksheet Builder Flow

```txt
Analytics / Dashboard
→ New Worksheet
→ Select Dataset
→ Select Metrics
→ Select Dimensions
→ Add Filters
→ Choose Aggregation
→ Preview Result
→ Save Worksheet
→ Add to Dashboard
```

### Worksheet Builder UI

Recommended layout:

```txt
Left Panel: Dataset fields
Center Panel: Live preview
Right Panel: Configuration
```

### Worksheet Configuration

```txt
Metric
Dimension
Group by
Filter
Sort
Limit
Aggregation
Derived fields
Visualization suggestion
```

### Supported Aggregations

```txt
COUNT
COUNT DISTINCT
SUM
AVG
MIN
MAX
PERCENTAGE
RATE
RATIO
MEDIAN, future
PERCENTILE, future
```

### Example Worksheets

```txt
Certificate Coverage by LGA
Pending Accreditation by Facility Type
Inspection Findings by Severity
Employer Compliance by Branch
Revenue by Payment Type
Forms Response Rate by State
```

---

## 5.4 Widget System

### Widget Types

```txt
KPI Card
Grouped KPI Card
Progress / Coverage Card
Bar Chart
Grouped Bar Chart
Stacked Bar Chart
Line Chart
Area Chart
Donut Chart
Pie Chart
Table
Pivot Table, future
Map
Heatmap, future
Queue Card
Priority Action Card
Trend Card
AI Insight Card
Text / Narrative Block
```

### Widget Requirements

Each widget should have:

```txt
Widget title
Worksheet reference
Visualization type
Visual config
Filter behaviour
Refresh behaviour
Permission rules
Export options
```

### Widget Actions

```txt
Edit Widget
Duplicate Widget
Resize
Move
Delete
Export PNG
Export CSV/Excel, for tabular widgets
Add to Another Dashboard
Ask AI About This Widget
```

---

## 5.5 Dashboard Canvas Builder

### Purpose

The Dashboard Canvas is the workspace where users build dashboards using widgets and blocks.

### Canvas Block Types

```txt
Widget Block
Text Block
Filter Block
AI Insight Block
Dataset Preview Block
Quick Action Block
Divider / Section Header
```

### Canvas Features

```txt
Drag-and-drop layout
Resizable blocks
Multi-column grid
Section grouping
Responsive layout
Global filters
Save draft
Preview mode
Publish mode
Version snapshots
```

### Canvas User Flow

```txt
Create New Dashboard
→ Add Widget
→ Add Filter
→ Add Text / Narrative
→ Arrange Layout
→ Save
→ Preview
→ Publish / Share
```

---

## 5.6 Published Dashboard View

Published dashboards are read-only or limited-interaction views.

### Published View Features

```txt
Read-only layout
Interactive filters
Refresh data
Export
Share link
Role-based visibility
Version snapshot
```

### Publishing Options

```txt
Private
Organization
Role-based
Selected Users
Federal-only
State-only
Public link, optional and restricted
```

### Public Link Rule

Public links should be disabled by default for FoodCert NG because the platform contains sensitive compliance and health-adjacent information.

If enabled, public links must only expose approved aggregate data.

---

## 5.7 Global Filters

### Filter Types

```txt
Dropdown
Multi-select
Date range
Number range
Text search
Status filter
LGA filter
State filter
Employer category filter
Facility status filter
Certificate status filter
Inspection severity filter
```

### Filter Behaviour

A global filter applies only to widgets where the field exists.

Example:

```txt
Global Filter: LGA
Applies to: Food Handlers, Employers, Facilities, Inspections
Ignored by: Federal Template Adoption if no LGA field exists
```

### Filter Indicator

If a filter applies to only some widgets, show:

```txt
LGA filter applies to 8 of 10 widgets
```

---

## 5.8 AI Integration

### Purpose

AI should help users create worksheets, build widgets, generate dashboards, explain data, and identify risks.

### AI Capabilities

```txt
Generate worksheet from prompt
Generate widget from prompt
Build dashboard from prompt
Explain dashboard
Summarize trends
Detect anomalies
Suggest priority actions
Recommend filters
Generate executive summary
Explain why a metric changed
Generate report narrative
```

### Example Prompts

Federal:

```txt
Create a national dashboard showing certificate coverage by state and pending reports.
Compare inspection performance across states.
Show states with low facility accreditation readiness.
```

State:

```txt
Show food handler certification coverage by LGA.
Create a dashboard for pending accreditation applications and overdue inspections.
Explain why enforcement cases increased this month.
```

Employer:

```txt
Show branches with expiring certificates.
Which food handlers need renewal this month?
Summarize my corrective actions due this week.
```

Medical Facility:

```txt
Show pending doctor review cases.
Create a dashboard for assessment volume and certificate submissions.
Summarize rejected certificate requests and reasons.
```

### AI Guardrails

AI must respect:

```txt
Permissions
Account scope
State scope
Branch scope
Medical privacy
Dataset sensitivity
Field-level privacy
```

AI must not expose data the user cannot access.

### AI Output Types

```txt
Worksheet configuration
Widget configuration
Dashboard layout proposal
Narrative summary
Insight card
Suggested filters
Suggested action list
```

### AI Review Mode

When AI creates a worksheet/dashboard, show a review screen before saving:

```txt
Dataset selected
Metrics selected
Dimensions selected
Filters selected
Widgets proposed
Privacy warnings
Save / Edit / Cancel
```

---

# 6. Dashboard Templates

The system should support prebuilt templates by account type.

## 6.1 Federal Templates

```txt
National Overview
State Performance Comparison
Guideline Implementation Monitoring
Federal Forms Response Monitoring
National Inspection Trends
Facility Accreditation Coverage
```

## 6.2 State Templates

```txt
State Executive Overview
Food Handler Compliance
Medical Facility Readiness
Inspection & Enforcement Workload
Certificate Validation Queue
Revenue Summary
Forms Response Monitoring
```

## 6.3 Employer Templates

```txt
Employer Compliance Overview
Branch Compliance Overview
Food Handler Certificate Renewal
Inspection Corrective Actions
Assigned Forms Overview
```

## 6.4 Medical Facility Templates

```txt
Facility Operations Overview
Assessment Workflow
Doctor Review Queue
Lab Review Queue
Certificate Submission Tracking
Settlement Overview
```

## 6.5 Template Behaviour

Users should be able to:

```txt
Use template
Clone template
Customize template
Save as new dashboard
Publish customized dashboard
```

---

# 7. Dashboard Permissions

## 7.1 Roles

Recommended generic dashboard roles:

```txt
Dashboard Viewer
Dashboard Analyst
Dashboard Builder
Dashboard Publisher
Dashboard Admin
```

## 7.2 Permissions

```txt
dashboard.view
dashboard.create
dashboard.update
dashboard.delete
dashboard.publish
dashboard.share
dashboard.export
dashboard.manage_templates

worksheet.view
worksheet.create
worksheet.update
worksheet.delete
worksheet.ai_generate

widget.view
widget.create
widget.update
widget.delete

dashboard.ai.use
dashboard.ai.generate_insights
dashboard.ai.generate_dashboard
```

## 7.3 Account-Specific Permission Examples

Federal:

```txt
dashboard.view_national
dashboard.view_cross_state
dashboard.create_federal
dashboard.publish_federal
dashboard.ai_cross_state
```

State:

```txt
dashboard.view_state
dashboard.create_state
dashboard.publish_state
dashboard.view_state_revenue
```

Employer:

```txt
dashboard.view_employer
dashboard.create_employer
dashboard.view_branch_compliance
```

Medical Facility:

```txt
dashboard.view_facility
dashboard.create_facility
dashboard.view_assessment_metrics
```

---

# 8. Privacy and Data Protection

## 8.1 Sensitive Data Rules

The dashboard system must classify fields as:

```txt
Public
Internal
Confidential
PII
Medical
Financial
Security
```

## 8.2 Field-Level Restrictions

Sensitive fields should have:

```txt
Role-based visibility
Aggregation-only mode
Masking rules
Export restrictions
AI access restrictions
Audit-on-view where needed
```

## 8.3 Medical Privacy

Dashboards should not expose medical details to employers, federal users, inspectors, or unauthorized state users.

Allowed for employer dashboards:

```txt
Fit to Work
Certificate Status
RTW Pending
Excluded from Food Handling
Cleared to Return
```

Not allowed for employer dashboards:

```txt
Diagnosis
Lab Result
Doctor Note
Medical Declaration Details
Treatment Details
```

## 8.4 AI Privacy

AI must only summarize and analyze fields the user can access.

The AI should not infer or reveal restricted medical details.

---

# 9. Data and Query Engine

## 9.1 Query Engine Requirements

```txt
PostgreSQL-backed queries
Predefined safe dataset views
Aggregation support
Filtering support
Join support where allowed
Query caching
Pagination
Permission-aware query execution
Query timeout protection
```

## 9.2 Performance Targets

```txt
Dashboard load: less than 3 seconds for cached dashboards
Widget query: less than 2 seconds where possible
Large export: background job
Support 100k+ records per dataset
Support concurrent users
```

## 9.3 Caching

Use caching for:

```txt
Dashboard summary queries
Common widgets
Federal aggregate dashboards
State dashboard summary cards
Chart datasets
```

Cache invalidation should occur on relevant workflow changes.

---

# 10. Dashboard Export and Sharing

## 10.1 Export Options

```txt
PDF dashboard export
PNG widget export
CSV widget data export
Excel table export
Dashboard snapshot export
```

## 10.2 Sharing Options

```txt
Private
Organization
Role-based
Selected users
Selected states, for Federal dashboards
Public aggregate link, optional and restricted
```

## 10.3 Export Rules

Exports must respect:

```txt
Permissions
Scope
Sensitive fields
Medical privacy
Revenue permissions
Audit logging
```

---

# 11. Notifications and Alerts

Dashboards should support optional alert rules.

## 11.1 Alert Examples

```txt
Certificate coverage drops below 70%
Overdue inspections exceed 20
Facility accreditation backlog exceeds threshold
Corrective actions overdue for more than 7 days
State reporting response rate below 60%
Payment reconciliation failures exceed threshold
```

## 11.2 Alert Channels

```txt
In-app
Email
Dashboard alert banner
Reports notification
```

## 11.3 Alert Ownership

Users can create alerts only if they have permission.

Alerts must respect scope and privacy.

---

# 12. Recommended UI Structure

## 12.1 Dashboard Home

```txt
Dashboard
├── Default Dashboard
├── My Dashboards
├── Shared With Me
├── Templates
├── Worksheets
├── Recent Activity
└── Ask AI
```

## 12.2 Dashboard Builder

```txt
Dashboard Builder
├── Header: Dashboard name, save, preview, publish
├── Left Panel: Datasets, worksheets, widgets, blocks
├── Center: Drag-and-drop canvas
├── Right Panel: Selected block settings
└── AI Assistant Drawer
```

## 12.3 Worksheet Builder

```txt
Worksheet Builder
├── Dataset selector
├── Field list
├── Metrics and dimensions
├── Filters
├── Chart recommendation
├── Preview
└── Save / Add to Dashboard
```

## 12.4 AI Assistant Drawer

```txt
AI Assistant
├── Prompt input
├── Suggested questions
├── Generated analysis
├── Proposed widgets
├── Privacy notice
└── Add to dashboard
```

---

# 13. API Requirements

## 13.1 Dashboard APIs

```txt
GET    /api/dashboards
POST   /api/dashboards
GET    /api/dashboards/:id
PATCH  /api/dashboards/:id
DELETE /api/dashboards/:id
POST   /api/dashboards/:id/publish
POST   /api/dashboards/:id/share
GET    /api/dashboards/:id/view
POST   /api/dashboards/:id/export
```

## 13.2 Worksheet APIs

```txt
GET    /api/analytics/worksheets
POST   /api/analytics/worksheets
GET    /api/analytics/worksheets/:id
PATCH  /api/analytics/worksheets/:id
DELETE /api/analytics/worksheets/:id
POST   /api/analytics/worksheets/:id/preview
POST   /api/analytics/worksheets/:id/query
```

## 13.3 Widget APIs

```txt
GET    /api/analytics/widgets
POST   /api/analytics/widgets
GET    /api/analytics/widgets/:id
PATCH  /api/analytics/widgets/:id
DELETE /api/analytics/widgets/:id
POST   /api/analytics/widgets/:id/query
POST   /api/analytics/widgets/:id/export
```

## 13.4 Dataset APIs

```txt
GET /api/analytics/datasets
GET /api/analytics/datasets/:id
GET /api/analytics/datasets/:id/fields
GET /api/analytics/datasets/:id/sample
```

## 13.5 AI APIs

```txt
POST /api/analytics/ai/generate-worksheet
POST /api/analytics/ai/generate-widget
POST /api/analytics/ai/generate-dashboard
POST /api/analytics/ai/explain-widget
POST /api/analytics/ai/explain-dashboard
POST /api/analytics/ai/suggest-insights
POST /api/analytics/ai/generate-summary
```

## 13.6 Template APIs

```txt
GET  /api/analytics/dashboard-templates
POST /api/analytics/dashboard-templates/:id/use
POST /api/analytics/dashboard-templates/:id/clone
```

---

# 14. Data Model Requirements

## 14.1 AnalyticsDataset

```txt
id
name
description
module_source
account_type_scope
permission_key
schema_json
sensitive_fields_json
join_rules_json
default_filters_json
is_active
created_at
updated_at
```

## 14.2 AnalyticsWorksheet

```txt
id
name
description
dataset_id
owner_user_id
owner_organization_id
account_type
scope_type
metrics_json
dimensions_json
filters_json
aggregation_json
derived_fields_json
visualization_suggestion
created_by
updated_by
created_at
updated_at
```

## 14.3 AnalyticsWidget

```txt
id
name
worksheet_id
widget_type
visual_config_json
filter_config_json
refresh_config_json
created_by
updated_by
created_at
updated_at
```

## 14.4 DashboardCanvas

```txt
id
name
description
owner_user_id
owner_organization_id
account_type
scope_type
layout_json
global_filters_json
status
version
created_by
updated_by
created_at
updated_at
```

## 14.5 DashboardBlock

```txt
id
canvas_id
block_type
widget_id
content_json
position_json
size_json
settings_json
created_at
updated_at
```

## 14.6 PublishedDashboard

```txt
id
canvas_id
published_version
title
description
visibility
share_rules_json
snapshot_json
published_by
published_at
is_active
```

## 14.7 DashboardTemplate

```txt
id
name
description
account_type
template_category
layout_json
default_widgets_json
required_datasets_json
is_system_template
created_by
created_at
updated_at
```


## 14.8 AnalyticsIndicatorDataset Support

Indicators may already exist in a separate Indicator/KPI module. The dashboard module should not duplicate that module unnecessarily. Instead, it should expose indicator data through the analytics dataset registry.

If an analytics-specific representation is required, use this structure:

```txt
id
indicator_id
indicator_code
indicator_name
indicator_category
account_type_scope
owner_organization_id
state_id
lga_id
period_type
period_start
period_end
baseline_value
target_value
actual_value
achievement_percentage
performance_status
data_source_module
calculation_method
last_calculated_at
validation_status
created_at
updated_at
```

Indicator data must be available to worksheets as:

```txt
Dataset: Indicators
Dataset: Indicator Results / Measurements
Dataset: Indicator Targets
Dataset: Indicator Performance
```

## 14.9 DashboardAIInsight

```txt
id
dashboard_id
widget_id
prompt
response
insight_type
created_by
created_at
```

---

# 15. Implementation Chunks for Codex

## Chunk 1: Dashboard Architecture Foundation

### Goal

Implement the core dashboard architecture.

### Tasks

- Create analytics dataset registry.
- Create worksheet model.
- Create widget model.
- Create dashboard canvas model.
- Create dashboard block model.
- Create published dashboard model.
- Create dashboard template model.
- Add account type and scope fields.
- Add permission and privacy metadata.

### Acceptance Criteria

- System supports datasets, worksheets, widgets, canvas, and published dashboards.
- Records are scoped by account type and organization.
- Dataset access can be permission-controlled.
- Published dashboards reference canvases.

---

## Chunk 2: Dataset Catalogue

### Goal

Expose role-based datasets for dashboard building.

### Tasks

- Implement dataset registry API.
- Add FoodCert datasets, including Indicators, Indicator Targets, Indicator Results / Measurements, and Indicator Performance.
- Add account-type visibility rules.
- Add field metadata.
- Add sensitive field metadata.
- Add dataset sample endpoint.
- Add join rules where allowed.

### Acceptance Criteria

- Federal sees federal/cross-state datasets, including cross-state indicator performance.
- State sees state-scoped datasets, including state and LGA indicator performance.
- Employer sees employer-scoped datasets, including employer and branch compliance indicators.
- Medical Facility sees facility-scoped datasets, including facility workflow/performance indicators.
- Sensitive fields are marked and protected.

---

## Chunk 2A: Indicator Dataset Integration

### Goal

Make Indicators a first-class analytics data source across all dashboard account types.

### Tasks

- Register Indicators in the analytics dataset catalogue.
- Register Indicator Targets.
- Register Indicator Results / Measurements.
- Register Indicator Performance.
- Add field metadata for indicator code, name, category, period, baseline, target, actual, achievement percentage, status, owner, state, LGA, and source module.
- Add indicator calculation metadata.
- Add account-specific indicator visibility rules.
- Add indicator worksheet examples/templates.
- Add AI prompt support for indicator-based analysis.

### Acceptance Criteria

- Federal users can build worksheets from cross-state indicators.
- State users can build worksheets from state and LGA indicators.
- Employer users can view only employer/branch indicators assigned to their organization.
- Medical Facility users can view only facility performance indicators for their facility.
- AI can generate indicator widgets without inventing values.
- Indicator values respect permissions, scope, validation status, and privacy rules.

---

## Chunk 3: Worksheet Builder

### Goal

Build reusable analytics logic layer.

### Tasks

- Create worksheet builder UI.
- Add dataset selector.
- Add fields panel.
- Add metrics builder.
- Add dimensions builder.
- Add filter builder.
- Add aggregation options.
- Add live preview.
- Add save worksheet.
- Add “Add to Dashboard” CTA.

### Acceptance Criteria

- User can create worksheet from accessible dataset.
- User can preview results.
- User can save worksheet.
- Worksheet can be reused by widgets.
- Unauthorized fields cannot be selected.

---

## Chunk 4: Widget System

### Goal

Create visual widget system.

### Tasks

- Implement widget creation.
- Support KPI, grouped KPI, charts, tables, maps, queue cards, and AI insight cards.
- Add widget configuration UI.
- Add widget preview.
- Add export options.
- Link widgets to worksheets.

### Acceptance Criteria

- Widgets render from worksheet results.
- Widgets can be configured and saved.
- Widgets can be added to dashboards.
- Widget export respects permissions.

---

## Chunk 5: Dashboard Canvas Builder

### Goal

Create flexible dashboard builder.

### Tasks

- Build canvas page.
- Add drag-and-drop layout.
- Add resizable blocks.
- Add widget block.
- Add text block.
- Add filter block.
- Add AI insight block.
- Add block settings panel.
- Add save and preview.

### Acceptance Criteria

- User can create a dashboard canvas.
- User can add and arrange widgets.
- User can add filters and text.
- Dashboard layout saves correctly.
- Canvas is responsive.

---

## Chunk 6: Published Dashboard View

### Goal

Allow users to publish dashboard canvases.

### Tasks

- Add publish flow.
- Add visibility settings.
- Add role/user/organization sharing.
- Add read-only dashboard view.
- Add dashboard version snapshot.
- Add export/share buttons.

### Acceptance Criteria

- Canvas can be published.
- Published dashboard is read-only.
- Filters remain interactive.
- Sharing respects permissions.
- Snapshot/version is preserved.

---

## Chunk 7: Global Filters

### Goal

Implement dashboard-wide filters.

### Tasks

- Add filter block.
- Add filter selector from worksheets.
- Apply filters to compatible widgets.
- Ignore non-compatible widgets.
- Show filter applicability indicator.
- Persist filter settings.

### Acceptance Criteria

- Filters apply across compatible widgets.
- Users know which widgets a filter affects.
- Filters work in published dashboard view.
- Filter state can be shared/bookmarked.

---

## Chunk 8: AI Dashboard Assistant

### Goal

Add AI-powered dashboard creation and insights.

### Tasks

- Implement AI prompt drawer.
- Add generate worksheet endpoint.
- Add generate widget endpoint.
- Add generate dashboard endpoint.
- Add explain widget/dashboard endpoint.
- Add insight generation.
- Add review-before-save UI.
- Enforce permission-aware dataset access.

### Acceptance Criteria

- AI can generate worksheet configs.
- AI can generate widget configs.
- AI can propose dashboard layouts.
- AI respects user permissions and data scope.
- AI output can be reviewed before saving.

---

## Chunk 9: Account-Type Default Templates

### Goal

Provide prebuilt dashboard templates for each account type.

### Tasks

- Create Federal templates.
- Create State templates.
- Create Employer templates.
- Create Medical Facility templates.
- Add template gallery.
- Add use/clone template actions.

### Acceptance Criteria

- Users see templates relevant to their account type.
- Users can create dashboards from templates.
- Templates are customisable after cloning.
- Templates use accessible datasets only.

---

## Chunk 10: Export and Sharing

### Goal

Support dashboard and widget export/sharing.

### Tasks

- Add PDF dashboard export.
- Add PNG widget export.
- Add CSV/Excel export for table widgets.
- Add share permissions.
- Add audit logs for exports/shares.

### Acceptance Criteria

- Exports work where permitted.
- Sensitive fields are masked/omitted.
- Sharing respects account and role scope.
- Export/share events are audit logged.

---

## Chunk 11: Alerts and Notifications

### Goal

Allow users to create alert rules from dashboard metrics.

### Tasks

- Add alert rule model.
- Add alert creation UI.
- Add threshold conditions.
- Add notification channels.
- Add alert history.
- Add account-scope enforcement.

### Acceptance Criteria

- Users can create alerts from widgets.
- Alerts trigger when thresholds are met.
- Notifications are sent.
- Alerts respect permissions and scope.

---

## Chunk 12: Permissions, Privacy, and Audit

### Goal

Secure dashboard system.

### Tasks

- Implement dashboard permissions.
- Enforce dataset access rules.
- Enforce sensitive field restrictions.
- Add AI privacy enforcement.
- Add audit logs for view, create, edit, publish, share, export, AI use.
- Add tests.

### Acceptance Criteria

- Users cannot access unauthorized datasets.
- Users cannot export restricted fields.
- AI cannot expose restricted data.
- Dashboard actions are audit logged.
- Tests pass.

---

## Chunk 13: Performance and Caching

### Goal

Ensure dashboards load quickly.

### Tasks

- Add query caching.
- Add widget-level refresh.
- Add pagination for table widgets.
- Add background exports.
- Add query timeout protection.
- Add indexes for common filters.

### Acceptance Criteria

- Cached dashboards load under 3 seconds where possible.
- Widget queries return under 2 seconds where possible.
- Large exports run as background jobs.
- Slow queries fail gracefully.

---

## Chunk 14: Embedded Module Analytics Integration

### Goal

Reuse dashboard engine inside operational modules.

### Tasks

- Allow modules to use worksheet/widget system for embedded analytics.
- Add “Add to Dashboard” from module analytics.
- Add “Open in Dashboard Builder” from module dashboards.
- Ensure embedded widgets use the same engine.

### Acceptance Criteria

- Forms, Inspections, Certificates, Medical Facilities, and Employers can reuse widgets.
- No duplicate analytics engine is created per module.
- Module widgets can be added to dashboards.

---

## Chunk 15: Final UI QA

### Goal

Validate full dashboard module.

### QA Checklist

- Federal dashboard works.
- State dashboard works.
- Employer dashboard works.
- Medical Facility dashboard works.
- Worksheet builder works.
- Widget builder works.
- Canvas builder works.
- AI assistant works.
- Publishing works.
- Exports work.
- Templates work.
- Permissions work.
- Mobile responsive layout works.

---

# 16. Codex Master Implementation Prompt

```txt
Build a flexible AI-powered Dashboard Module for FoodCert NG that works across Federal, State, Employer, Medical Facility, and Platform Admin accounts.

Use this architecture:
Dataset → Worksheet → Widget → Dashboard Canvas → Published Dashboard View

The system should support:
- Role-based dataset catalogue, including Indicators as a first-class data source
- Worksheet builder
- Widget builder
- Drag-and-drop dashboard canvas
- Published read-only dashboards
- Global filters
- Dashboard templates
- AI-generated worksheets, widgets, dashboards, and insights
- Export and sharing
- Alerts and notifications
- Embedded module analytics
- Permission-aware and privacy-aware querying

Account-specific dashboard behaviour:
Federal:
- National overview, cross-state comparison, guideline implementation, federal forms reporting, aggregate compliance, state performance.

State:
- Food handler compliance, employer compliance, medical facility readiness, inspections/enforcement, certificates, forms, revenue, operational queues.

Employer:
- Food handler certificate compliance, branch compliance, illness/RTW statuses, assigned forms, inspections, corrective actions, subscriptions.

Medical Facility:
- Accreditation status, assessment queues, doctor/lab workflow, certificate submissions, RTW clearance, assigned forms, settlements.

Do not hardcode only one Federal dashboard. Build a reusable dashboard engine with account-specific templates and dataset scoping.

AI requirements:
- AI can generate worksheets, widgets, dashboards, summaries, and insights from prompts.
- AI must respect permissions, account scope, state scope, organization scope, field sensitivity, and medical privacy.
- AI output must be reviewed before saving.

Use existing FoodCert NG stack:
Next.js + React + TypeScript + Tailwind CSS.
Backend permissions and scoping remain the source of truth.
```

---

# 17. MVP Build Order

1. Dashboard architecture foundation
2. Dataset catalogue
3. Indicator dataset integration
4. Worksheet builder
5. Widget system
6. Dashboard canvas builder
7. Published dashboard view
8. Global filters
9. AI dashboard assistant
10. Account-type templates
11. Export and sharing
12. Alerts and notifications
13. Permissions, privacy, and audit
14. Performance and caching
15. Embedded module analytics integration
16. Final UI QA
