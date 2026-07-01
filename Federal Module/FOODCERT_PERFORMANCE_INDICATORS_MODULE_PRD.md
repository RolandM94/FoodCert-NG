# FoodCert NG PRD: Performance Indicators / KPI Definition & Calculation Engine

## 1. Document Purpose

This PRD defines the **Performance Indicators** feature for FoodCert NG.

The feature is not intended to be a heavy manual data-entry system. Instead, it is a **KPI / Indicator Definition and Calculation Engine** that converts activities already executed on the FoodCert NG platform into standardised, measurable, target-based performance indicators.

The feature must fit into the latest FoodCert NG platform flow for:

```txt
Federal Ministry Account
State Ministry Account
Employer / Food Business Account
Medical Facility Account
Dashboard / Analytics Module
Forms Tool
Reports Module
Account Settings
```

The system should allow FoodCert NG to answer:

```txt
What are we measuring?
How is it calculated?
What is the target?
Who owns the indicator?
Which account type can view it?
What data source powers it?
How often is it calculated?
What performance band does the result fall into?
How is it displayed on dashboards and reports?
What trend or risk does AI detect?
```

---

# 2. Product Decision

FoodCert NG should build a **Performance Indicators** module.

Recommended module name:

```txt
Performance Indicators
```

This module should contain:

```txt
Performance Indicators
├── Overview
├── Indicator Library
├── Definitions
├── Targets & Thresholds
├── Calculation Rules
├── Results
├── Reports
└── Settings
```

However, the visible menu structure should vary by account type.

---

# 3. Core Principle

Most FoodCert indicators should be automatically calculated from activities already performed on the platform.

FoodCert workflows already generate data from:

```txt
Food handler registration
NIN verification
Health declaration submission
Medical assessment submission
Doctor review
Lab test completion
Certificate validation
Certificate issuance
Certificate expiry
Employer onboarding
Branch/outlet management
Medical facility accreditation
Facility re-accreditation
Inspection creation
Inspection completion
Enforcement notices
Corrective actions
Return-to-work clearance
Forms submissions
Payments
Settlements
State reports
Federal template adoption
```

The indicator engine should turn these activities into structured KPIs.

```txt
Platform activity generates data.
Indicator engine defines meaning.
Dashboard displays performance.
AI explains trends, risks, and actions.
```

---

# 4. What This Feature Is and Is Not

## 4.1 This Feature Is

```txt
A KPI definition engine
A calculation rule engine
A target and threshold engine
A performance measurement engine
An indicator result history engine
A dashboard/reporting data source
A Federal-to-State standardisation tool
An AI-ready performance interpretation layer
```

## 4.2 This Feature Is Not

```txt
A replacement for the Forms Tool
A replacement for the Dashboard Builder
A replacement for operational modules
A primary manual KPI entry system
A generic project M&E tool outside FoodCert workflows
```

Manual entry should exist only for special indicators that are not generated automatically from platform activity.

---

# 5. Relationship With Other FoodCert Modules

## 5.1 Dashboard / Analytics Module

The Dashboard module visualises indicators.

The Indicator engine defines:

```txt
Formula
Target
Threshold
Scope
Frequency
Result values
```

The Dashboard module displays:

```txt
KPI cards
Trend charts
Comparative charts
State performance tables
Employer compliance cards
Facility performance cards
AI insight cards
```

The Dashboard module should treat indicators as a first-class dataset:

```txt
Indicators
Indicator Definitions
Indicator Results
Indicator Targets
Indicator Thresholds
Indicator Performance History
```

## 5.2 Forms Tool

The Forms Tool collects structured data.

The Indicator engine can consume Forms Tool data when an indicator needs form responses as a data source.

Examples:

```txt
State quarterly reporting response rate
Guideline implementation survey score
Facility self-reporting compliance
Employer compliance declaration completion rate
Training/sensitisation completion evidence
```

The Forms Tool does not define KPIs. It only collects data that can be used by KPI formulas.

## 5.3 Account Settings

Account Settings should configure default settings and permissions for indicator management.

Relevant account settings:

```txt
Default indicator calculation frequency
Default performance bands
Notification rules for poor indicator performance
Approval rules for state-created indicators
Data visibility and privacy rules
```

Federal and State account settings should not duplicate the full Indicator Library.

## 5.4 Reports Module

Reports should consume indicator results.

Examples:

```txt
State Performance Report
National Compliance Report
Guideline Implementation Report
Facility Accreditation Report
Inspection Performance Report
Employer Compliance Report
```

## 5.5 Notifications and Alerts

Indicators should trigger alerts.

Examples:

```txt
Certificate coverage below target
Inspection completion rate below threshold
Corrective action closure rate critical
Facility re-accreditation backlog high
State reporting compliance below target
```

## 5.6 AI Integration

AI should use indicator definitions and results to:

```txt
Explain performance changes
Generate executive summaries
Identify risks
Recommend actions
Compare states/LGAs/branches/facilities
Suggest new indicators
Detect anomalies
Explain indicator formulas in plain English
```

---

# 6. Account-Type Fit and Flow

---

## 6.1 Federal Ministry Account

### Federal Role

Federal Ministry should own national performance standards.

Federal should be able to:

```txt
Create national indicator definitions
Publish national indicators
Define national formulas
Set national default targets
Set national threshold bands
Share indicators with all states
Share indicators with selected states
Monitor cross-state performance
Compare states
Track national guideline implementation
View aggregate indicator results
Generate national reports
Use AI to explain state performance trends
```

### Federal Menu Placement

Recommended Federal navigation:

```txt
Federal Ministry
├── Dashboard
├── States Overview
├── Directory & Registry
├── Forms Tool
├── Performance Indicators
├── Reports & Analytics
└── Account Settings
```

### Federal Performance Indicators Tabs

```txt
Performance Indicators
├── Overview
├── National Indicator Library
├── Definitions
├── Targets & Thresholds
├── State Adoption
├── Results
├── Reports
└── Settings
```

### Federal Indicator Use Cases

```txt
Certificate Coverage Rate by State
Accredited Facility Coverage Rate by State
Inspection Completion Rate by State
Corrective Action Closure Rate by State
Certificate Issuance Turnaround Time by State
Assessment Completion Rate by State
State Reporting Compliance Rate
Guideline Implementation Score
Federal Standard Template Adoption Rate
Food Handler Compliance Rate
Employer Compliance Coverage Rate
```

### Federal Restrictions

Federal should generally see:

```txt
Aggregated national data
Aggregated state-level data
Cross-state performance data
Indicator results
Trend data
Compliance bands
```

Federal should not automatically see:

```txt
Private medical details
Individual food handler lab results
Doctor notes
Medical declaration details
Employer-only private operational details
Facility-only internal notes
```

Federal access to sensitive details must be permission-controlled and audit-logged.

---

## 6.2 State Ministry Account

### State Role

State Ministry should implement national indicators, monitor state operations, and create state-level operational indicators where permitted.

State should be able to:

```txt
View national indicators assigned/shared by Federal
Adopt national indicators
Use national formulas as-is
Set state-specific targets where allowed
Create state-owned indicators for internal monitoring
Monitor LGA, employer, facility, and inspection performance
Track operational queues using indicators
Generate state performance reports
Use AI to explain state trends and risks
```

### State Menu Placement

Recommended State navigation:

```txt
State Ministry
├── Dashboard
├── Stakeholder Management
├── Medical Facilities
├── Directory & Registry
├── Forms Tool
├── Inspections & Enforcement
├── Certificates
├── Payments & Revenue
├── Performance Indicators
├── Reports
└── Account Settings
```

### State Performance Indicators Tabs

```txt
Performance Indicators
├── Overview
├── Indicator Library
├── Adopted National Indicators
├── State Indicators
├── Targets & Thresholds
├── Results
├── Reports
└── Settings
```

### State Indicator Use Cases

```txt
Food Handler Certificate Coverage by LGA
Pending Certificate Validation Rate
Certificate Expiry Risk Rate
Approved Medical Facility Coverage
Facility Accreditation Backlog
Inspection Completion Rate
Overdue Inspection Rate
Corrective Action Closure Rate
Employer Compliance Rate
Illness Exclusion Resolution Rate
Return-to-Work Clearance Turnaround Time
Assessment-to-Certificate Issuance Time
State Forms Response Rate
State Revenue Collection Performance
```

### State Restrictions

State should only see its own state-level data, except where Federal has explicitly shared aggregate comparative information.

State-created indicators should not override Federal national indicators unless allowed.

---

## 6.3 Employer / Food Business Account

### Employer Role

Employers should mostly consume indicators, not create complex national/state KPI definitions.

Employer users should be able to:

```txt
View employer compliance indicators
View branch/outlet indicators
Track food handler certification coverage
Track expiring certificates
Track corrective action closure
Track inspection performance
Track assigned form completion
Use indicators in employer dashboards
```

### Employer Performance Indicators Placement

Recommended:

```txt
Employer Account
├── Dashboard
├── Food Handlers
├── Branches / Outlets
├── Inspections & Notices
├── Forms
├── Payments / Subscription
├── Reports
└── Account Settings
```

For MVP, Performance Indicators does not need to be a separate employer sidebar module.

Instead, employer indicators should appear inside:

```txt
Dashboard
Reports
Branch details
Food Handler compliance views
```

### Employer Indicator Use Cases

```txt
Certification Coverage Rate
Branch Compliance Score
Certificate Renewal Risk
Assigned Forms Completion Rate
Corrective Action Closure Rate
Inspection Pass Rate
RTW Pending Count
Active Exclusion Count
Subscription Payment Status
```

### Employer Restrictions

Employers must not see medical details.

Allowed:

```txt
Fit to Handle Food
Certificate Active
Certificate Expired
RTW Pending
Excluded
Cleared to Return
```

Not allowed:

```txt
Diagnosis
Lab Result
Doctor Note
Health Declaration Answers
Treatment Details
```

---

## 6.4 Medical Facility Account

### Medical Facility Role

Medical facilities should mostly consume facility performance indicators and may use them operationally.

Medical facility users should be able to:

```txt
Track assessment workload
Track lab completion turnaround
Track doctor review turnaround
Track certificate submission rate
Track rejected submissions
Track return-to-work clearance processing
Track accreditation status
Track settlement performance
```

### Medical Facility Performance Indicators Placement

For MVP, Performance Indicators does not need to be a separate medical facility sidebar module.

Indicators should appear inside:

```txt
Dashboard
Reports
Assessment workflow
Accreditation status
Settlement dashboard
```

### Medical Facility Indicator Use Cases

```txt
Assessment Completion Rate
Doctor Review Turnaround Time
Lab Result Completion Time
Certificate Submission Rate
Certificate Rejection Rate
RTW Clearance Turnaround Time
Assessment Volume Trend
Settlement Completion Rate
Accreditation Expiry Risk
```

### Medical Facility Restrictions

Medical facilities can see medical data only for assessments handled by the facility and only based on staff role permissions.

---

# 7. Indicator Ownership and Visibility

## 7.1 Ownership Types

```txt
Federal-Owned Indicator
State-Owned Indicator
System Indicator
Employer-Scoped Indicator
Facility-Scoped Indicator
```

## 7.2 Visibility Types

```txt
system_default
federal_private
federal_standard
federal_shared
state_owned
state_private
organization_scoped
role_scoped
```

## 7.3 Indicator Lifecycle

```txt
Draft
Under Review
Published
Active
Paused
Deprecated
Archived
```

## 7.4 Federal-to-State Flow

```txt
Federal creates national indicator
→ Federal defines formula, target, threshold, scope, and frequency
→ Federal publishes as Federal Standard Indicator
→ States see it under Adopted/National Indicators
→ States can adopt as-is
→ States may set state-specific target if allowed
→ Platform auto-calculates results by state
→ Federal monitors cross-state performance
→ State monitors internal performance by LGA/employer/facility
```

## 7.5 State-Owned Indicator Flow

```txt
State creates internal indicator
→ State selects dataset and formula
→ State sets target and threshold
→ Indicator is calculated from state data
→ State displays indicator on dashboards/reports
→ Federal cannot edit state-owned indicator
→ Federal may view aggregate if shared/allowed
```

---

# 8. Indicator Types

## 8.1 System-Generated Indicators

Automatically calculated from system activity.

Examples:

```txt
Certificate Coverage Rate
Inspection Completion Rate
Corrective Action Closure Rate
Facility Accreditation Approval Rate
Assessment Turnaround Time
Certificate Issuance Turnaround Time
Payment Collection Rate
Forms Response Rate
```

## 8.2 Formula-Based Indicators

Defined using metrics, dimensions, filters, and calculations.

Example:

```txt
Certified Food Handlers / Total Registered Food Handlers × 100
```

## 8.3 Composite Indicators

Made up of multiple indicators with weights.

Example:

```txt
State Compliance Index
├── Certificate Coverage Rate: 30%
├── Facility Readiness Rate: 20%
├── Inspection Completion Rate: 20%
├── Corrective Action Closure Rate: 15%
└── State Reporting Compliance Rate: 15%
```

## 8.4 Manual Indicators

Used only where platform activity does not generate data automatically.

Examples:

```txt
Public awareness campaign completed
Stakeholder workshop conducted
Policy adoption milestone completed
Training programme completed
```

Manual indicators should require:

```txt
Evidence upload
Submission comment
Reviewer approval
Audit log
```

## 8.5 Forms-Based Indicators

Calculated from Forms Tool submissions.

Examples:

```txt
Guideline Implementation Survey Score
State Reporting Response Rate
Facility Monthly Report Submission Rate
Employer Self-Assessment Completion Rate
```

---

# 9. Indicator Definition Requirements

Each indicator definition should include:

```txt
Indicator Name
Indicator Code
Description
Purpose
Owner
Account Type Scope
Data Source
Formula Type
Formula
Numerator
Denominator
Aggregation Method
Dimensions
Filters
Calculation Frequency
Reporting Period
Target
Threshold Bands
Direction of Good Performance
Unit of Measure
Privacy Classification
Responsible Role
Approval Requirement
Dashboard Availability
Report Availability
AI Availability
Status
Version
```

## 9.1 Direction of Good Performance

Each indicator must define whether higher or lower is better.

Examples:

```txt
Higher is better:
Certificate Coverage Rate
Inspection Completion Rate
Corrective Action Closure Rate

Lower is better:
Certificate Issuance Turnaround Time
Overdue Inspection Rate
Certificate Rejection Rate
Accreditation Backlog
```

## 9.2 Unit of Measure

```txt
Count
Percentage
Rate
Days
Hours
Currency
Score
Index
Ratio
```

## 9.3 Calculation Frequency

```txt
Real-time
Hourly
Daily
Weekly
Monthly
Quarterly
On demand
```

MVP recommendation:

```txt
Daily
Weekly
Monthly
On demand
```

---

# 10. Formula Builder

## 10.1 Purpose

The formula builder allows authorised users to define how an indicator is calculated from platform datasets.

## 10.2 Formula Builder Inputs

```txt
Dataset
Metric
Aggregation
Dimension
Filters
Numerator
Denominator
Time period
Scope
Derived calculation
```

## 10.3 Supported Formula Types

```txt
Count
Percentage
Rate
Ratio
Average Duration
Sum
Composite Score
Manual Value
Forms Score
```

## 10.4 Example Formula

```txt
Indicator:
Certificate Coverage Rate

Formula Type:
Percentage

Numerator:
COUNT(food_handlers where certificate_status = active)

Denominator:
COUNT(registered_food_handlers)

Calculation:
Numerator / Denominator × 100

Scope:
State, LGA, Employer, Branch

Frequency:
Daily
```

## 10.5 Formula Validation Rules

The system must validate:

```txt
Dataset exists
User has permission to dataset
Numerator and denominator are compatible
Denominator cannot be zero
Fields exist
Fields are not restricted
Aggregation is allowed
Formula syntax is valid
Scope is allowed
```

---

# 11. Targets and Thresholds

## 11.1 Target Types

```txt
National Target
State Target
LGA Target
Employer Target
Facility Target
Branch Target
Custom Target
```

## 11.2 Threshold Bands

Each indicator should support configurable performance bands.

Example:

```txt
Green: >= 90%
Amber: 70% - 89%
Red: < 70%
```

For indicators where lower is better:

```txt
Green: <= 2 days
Amber: > 2 and <= 5 days
Red: > 5 days
```

## 11.3 Threshold Fields

```txt
Band Name
Color
Minimum Value
Maximum Value
Label
Severity
Action Recommendation
```

## 11.4 Target Inheritance

Federal can define national target defaults.

States may either:

```txt
Use Federal target
Set state-specific target, if allowed
Set LGA target, if allowed
```

Employers and facilities may have organisation-level targets where relevant.

---

# 12. Indicator Results

## 12.1 Result Generation

Indicator results should be generated:

```txt
On schedule
On demand
On relevant workflow events, future
```

## 12.2 Result Dimensions

Results should support dimensions such as:

```txt
Federal
State
LGA
Employer
Branch / Outlet
Medical Facility
Facility Type
Inspector
Doctor
Lab Technician
Certificate Status
Inspection Severity
Time Period
```

## 12.3 Result Storage

Results should be stored over time to support:

```txt
Trends
Comparisons
Performance history
Reports
AI explanations
Auditability
```

## 12.4 Result Fields

```txt
Indicator
Period Start
Period End
Scope Type
Scope ID
Calculated Value
Numerator Value
Denominator Value
Target Value
Performance Band
Variance from Target
Calculation Status
Calculation Timestamp
Calculation Version
```

---

# 13. AI Integration

## 13.1 AI Capabilities

AI should support:

```txt
Suggest indicators
Generate formulas
Explain indicator performance
Explain variance from target
Identify deteriorating indicators
Generate executive summary
Recommend actions
Compare states/LGAs/facilities/employers
Detect anomalies
Suggest dashboard widgets
```

## 13.2 AI Prompts

Federal:

```txt
Which states are below target for certificate coverage?
Explain why inspection completion rate declined nationally.
Create a national indicator for guideline implementation score.
Compare Lagos, Kano, and Rivers on facility accreditation readiness.
```

State:

```txt
Which LGAs have low food handler certification coverage?
Explain the increase in overdue inspections this month.
Suggest indicators for medical facility readiness.
Create a dashboard from my high-risk indicators.
```

Employer:

```txt
Which branches have the worst certificate renewal risk?
Explain my corrective action closure performance.
```

Medical Facility:

```txt
Why is doctor review turnaround time increasing?
Which assessment stages are causing delays?
```

## 13.3 AI Guardrails

AI must respect:

```txt
User permissions
Account type
Organization scope
State scope
Branch scope
Facility scope
Sensitive field rules
Medical privacy
Aggregation-only restrictions
```

AI should not create indicators using fields the user cannot access.

---

# 14. Dashboard Integration

Indicators should be available as a dashboard dataset.

## 14.1 Dashboard Widget Examples

```txt
Indicator KPI Card
Indicator Trend Chart
Indicator Comparison Table
Indicator Performance Band Card
Indicator Target vs Actual Chart
Composite Score Card
State Ranking Table
LGA Performance Map
```

## 14.2 Dashboard Filters

Indicators should support filters such as:

```txt
Indicator Category
State
LGA
Employer
Facility
Period
Performance Band
Target Status
Owner
```

## 14.3 Dashboard Actions

```txt
View Indicator Detail
Explain with AI
Add to Report
Export
Create Alert
View Underlying Data, if permitted
```

---

# 15. Reports Integration

Reports should be able to include:

```txt
Indicator summary
Target vs actual
Trend
Performance band
Variance analysis
AI narrative
Recommended actions
```

Report examples:

```txt
National FoodCert Performance Report
State Food Handler Compliance Report
Medical Facility Readiness Report
Inspection Performance Report
Employer Compliance Report
Guideline Implementation Report
```

---

# 16. Notifications and Alerts

## 16.1 Alert Triggers

```txt
Indicator below target
Indicator above critical risk threshold
Indicator result missing
Indicator calculation failed
State failed to meet reporting indicator
Facility performance deteriorated
Employer branch compliance below threshold
```

## 16.2 Alert Recipients

```txt
Federal programme officers
State admins
State M&E officers
State directors
Employer compliance officers
Facility admins
Assigned reviewers
```

## 16.3 Alert Channels

```txt
In-app
Email
Dashboard alert banner
Reports notification
```

---

# 17. UI / UX Requirements

## 17.1 Federal UI

```txt
Performance Indicators
├── Overview
├── National Indicator Library
├── Definitions
├── Targets & Thresholds
├── State Adoption
├── Results
├── Reports
└── Settings
```

## 17.2 State UI

```txt
Performance Indicators
├── Overview
├── Indicator Library
├── Adopted National Indicators
├── State Indicators
├── Targets & Thresholds
├── Results
├── Reports
└── Settings
```

## 17.3 Overview Page

Show:

```txt
Total Active Indicators
Indicators Below Target
Indicators at Risk
Indicators Meeting Target
Recent Calculations
Failed Calculations
Top Improving Indicators
Top Declining Indicators
```

## 17.4 Indicator Library

Columns:

```txt
Indicator Name
Code
Owner
Category
Formula Type
Data Source
Frequency
Status
Visibility
Last Calculated
Actions
```

Actions:

```txt
View
Edit
Clone
Adopt
Publish
Archive
Calculate Now
Add to Dashboard
Explain with AI
```

## 17.5 Indicator Detail Page

Sections:

```txt
Summary
Formula
Targets & Thresholds
Results
Trend
Breakdowns
Dashboards Using This Indicator
Reports Using This Indicator
Audit Trail
```

## 17.6 Indicator Creation Flow

```txt
Step 1: Basic Information
Step 2: Data Source
Step 3: Formula Builder
Step 4: Scope and Dimensions
Step 5: Targets and Thresholds
Step 6: Calculation Schedule
Step 7: Privacy and Visibility
Step 8: Review and Publish
```

## 17.7 State Adoption Flow

```txt
Open Adopted National Indicators
→ Preview Federal Indicator
→ Review formula and target
→ Adopt as-is or clone
→ Set state-specific target if allowed
→ Activate
```

---

# 18. Permissions

## 18.1 Federal Permissions

```txt
indicators.view_federal
indicators.create_federal
indicators.update_federal
indicators.publish_federal
indicators.share_to_states
indicators.set_national_targets
indicators.manage_thresholds
indicators.view_cross_state_results
indicators.export_federal_results
indicators.ai_use_federal
```

## 18.2 State Permissions

```txt
indicators.view_state
indicators.create_state
indicators.update_state
indicators.adopt_federal
indicators.clone_federal
indicators.set_state_targets
indicators.manage_state_thresholds
indicators.view_state_results
indicators.export_state_results
indicators.ai_use_state
```

## 18.3 Employer Permissions

```txt
indicators.view_employer
indicators.view_branch_indicators
indicators.export_employer_indicators
indicators.ai_use_employer
```

## 18.4 Medical Facility Permissions

```txt
indicators.view_facility
indicators.view_assessment_indicators
indicators.export_facility_indicators
indicators.ai_use_facility
```

## 18.5 Admin Permissions

```txt
indicators.manage_system_defaults
indicators.manage_dataset_registry
indicators.manage_formula_engine
indicators.view_all_audit_logs
```

---

# 19. Data Model Requirements

## 19.1 IndicatorDefinition

```txt
id
name
code
description
purpose
category
owner_type
owner_organization_id
visibility
account_type_scope
status
version
formula_type
data_source_id
formula_json
dimensions_json
filters_json
unit_of_measure
direction_of_good_performance
calculation_frequency
reporting_period
privacy_classification
allow_state_target_override
allow_state_clone
dashboard_enabled
report_enabled
ai_enabled
created_by
updated_by
published_by
created_at
updated_at
published_at
```

## 19.2 IndicatorTarget

```txt
id
indicator_definition_id
scope_type
scope_id
target_value
target_unit
effective_start_date
effective_end_date
set_by
source
is_active
created_at
updated_at
```

## 19.3 IndicatorThreshold

```txt
id
indicator_definition_id
scope_type
scope_id
band_name
severity
min_value
max_value
color
label
action_recommendation
created_at
updated_at
```

## 19.4 IndicatorResult

```txt
id
indicator_definition_id
period_start
period_end
scope_type
scope_id
dimension_values_json
calculated_value
numerator_value
denominator_value
target_value
variance_from_target
performance_band
calculation_status
calculation_version
calculated_at
metadata_json
```

## 19.5 IndicatorCalculationRun

```txt
id
indicator_definition_id
run_type
status
started_at
completed_at
triggered_by
records_processed
error_message
metadata_json
```

## 19.6 IndicatorAdoption

```txt
id
federal_indicator_id
state_id
adoption_status
adopted_version
state_target_override_enabled
adopted_by
adopted_at
last_synced_at
```

## 19.7 IndicatorManualEntry

```txt
id
indicator_definition_id
scope_type
scope_id
period_start
period_end
value
evidence_file_url
comment
submitted_by
reviewed_by
review_status
review_comment
created_at
updated_at
```

---

# 20. API Requirements

## 20.1 Federal APIs

```txt
GET    /api/federal/indicators
POST   /api/federal/indicators
GET    /api/federal/indicators/:id
PATCH  /api/federal/indicators/:id
POST   /api/federal/indicators/:id/publish
POST   /api/federal/indicators/:id/share-to-states
POST   /api/federal/indicators/:id/calculate
GET    /api/federal/indicators/:id/results
GET    /api/federal/indicators/:id/state-adoption
GET    /api/federal/indicators/results
GET    /api/federal/indicators/reports
```

## 20.2 State APIs

```txt
GET    /api/state/indicators
POST   /api/state/indicators
GET    /api/state/indicators/:id
PATCH  /api/state/indicators/:id
GET    /api/state/indicators/federal-library
POST   /api/state/indicators/federal-library/:id/adopt
POST   /api/state/indicators/federal-library/:id/clone
POST   /api/state/indicators/:id/calculate
GET    /api/state/indicators/:id/results
GET    /api/state/indicators/results
GET    /api/state/indicators/reports
```

## 20.3 Shared APIs

```txt
GET    /api/indicators/datasets
GET    /api/indicators/formula-fields
POST   /api/indicators/formula/validate
POST   /api/indicators/formula/preview
POST   /api/indicators/ai/suggest
POST   /api/indicators/ai/explain-result
POST   /api/indicators/ai/generate-formula
```

## 20.4 Employer APIs

```txt
GET /api/employer/indicators
GET /api/employer/indicators/results
GET /api/employer/indicators/:id
```

## 20.5 Medical Facility APIs

```txt
GET /api/facility/indicators
GET /api/facility/indicators/results
GET /api/facility/indicators/:id
```

---

# 21. Default FoodCert Indicator Library

## 21.1 Federal / National Indicators

```txt
National Certificate Coverage Rate
State Certificate Coverage Rate
Accredited Facility Coverage Rate
Inspection Completion Rate
Corrective Action Closure Rate
State Reporting Compliance Rate
Federal Template Adoption Rate
Guideline Implementation Score
Average Certificate Issuance Turnaround Time
Average Assessment Completion Time
Employer Compliance Coverage Rate
```

## 21.2 State Indicators

```txt
Food Handler Certificate Coverage by LGA
Pending Certificate Validation Rate
Expired Certificate Rate
Certificate Renewal Risk Rate
Medical Facility Accreditation Approval Rate
Facility Re-accreditation Compliance Rate
Inspection Completion Rate
Overdue Inspection Rate
Critical Finding Rate
Corrective Action Closure Rate
RTW Clearance Turnaround Time
Employer Compliance Rate
Forms Response Rate
Revenue Collection Rate
```

## 21.3 Employer Indicators

```txt
Employer Certificate Coverage Rate
Branch Certificate Coverage Rate
Expiring Certificate Risk
Assigned Forms Completion Rate
Corrective Action Closure Rate
Inspection Pass Rate
Active Exclusion Count
RTW Pending Count
```

## 21.4 Medical Facility Indicators

```txt
Assessment Completion Rate
Doctor Review Turnaround Time
Lab Result Completion Time
Certificate Submission Rate
Certificate Rejection Rate
RTW Clearance Turnaround Time
Settlement Completion Rate
Accreditation Expiry Risk
```

---

# 22. Acceptance Criteria

## 22.1 General

```txt
Performance Indicators module exists for Federal and State accounts.
Indicators appear as datasets in Dashboard / Analytics module.
Most indicators can be auto-calculated from platform activity.
Manual indicators are supported only where required.
Indicator results are stored historically.
Indicators support targets and thresholds.
Indicators support AI explanation.
```

## 22.2 Federal

```txt
Federal can create and publish national indicators.
Federal can set national targets and thresholds.
Federal can share indicators with states.
Federal can view cross-state results.
Federal can monitor state adoption.
Federal cannot access sensitive details without permission.
```

## 22.3 State

```txt
State can adopt national indicators.
State can clone Federal indicators where allowed.
State can create state-owned indicators.
State can set state-specific targets where allowed.
State can view state, LGA, employer, and facility breakdowns.
State cannot edit Federal-owned indicators directly.
```

## 22.4 Employer

```txt
Employer can view employer-scoped indicators.
Employer can view branch indicators.
Employer cannot see private medical data.
Employer indicators can be used in dashboards and reports.
```

## 22.5 Medical Facility

```txt
Facility can view facility-scoped indicators.
Facility can monitor assessment and workflow performance.
Facility can see medical details only for authorised facility records.
Facility indicators can be used in dashboards and reports.
```

---

# 23. Implementation Chunks for Codex

## Chunk 1: Indicator Module Foundation

### Goal

Create the Performance Indicators module foundation.

### Tasks

```txt
Create indicator data models.
Add Federal and State routes.
Add permission keys.
Add navigation items.
Add module shell.
Add tabs for Federal and State.
```

### Acceptance Criteria

```txt
Federal sees Performance Indicators in sidebar.
State sees Performance Indicators in sidebar.
Employer and Medical Facility do not need separate sidebar module in MVP.
Core models exist.
Permissions are registered.
```

---

## Chunk 2: Indicator Dataset Registry

### Goal

Make FoodCert datasets available to the indicator engine.

### Tasks

```txt
Create indicator dataset registry.
Expose datasets from certificates, food handlers, employers, facilities, inspections, enforcement, forms, payments, and settlements.
Add field metadata.
Mark sensitive fields.
Add account-type scope rules.
Add dataset preview endpoint.
```

### Acceptance Criteria

```txt
Federal sees aggregate/cross-state datasets.
State sees state-scoped datasets.
Employer sees employer-scoped datasets.
Facility sees facility-scoped datasets.
Sensitive fields are protected.
```

---

## Chunk 3: Indicator Definition Builder

### Goal

Build UI and backend for creating indicator definitions.

### Tasks

```txt
Create definition form.
Add basic information step.
Add data source step.
Add formula builder step.
Add scope and dimensions step.
Add targets and thresholds step.
Add calculation schedule step.
Add privacy and visibility step.
Add review/publish step.
```

### Acceptance Criteria

```txt
Authorised Federal users can create national indicators.
Authorised State users can create state indicators.
Definitions can be saved as draft.
Definitions can be published.
Validation prevents invalid formulas.
```

---

## Chunk 4: Formula Builder and Validation

### Goal

Implement formula logic.

### Tasks

```txt
Support count, percentage, rate, ratio, average duration, sum, composite score, manual value, and forms score.
Add numerator/denominator builder.
Add aggregation selector.
Add filters.
Add dimensions.
Add preview calculation.
Validate permissions and restricted fields.
```

### Acceptance Criteria

```txt
Users can build formulas without writing code.
Preview works.
Invalid formulas are rejected.
Restricted fields cannot be used.
Denominator zero is handled.
```

---

## Chunk 5: Targets and Thresholds

### Goal

Implement target and threshold configuration.

### Tasks

```txt
Create target model and UI.
Create threshold model and UI.
Support national, state, LGA, employer, facility, and branch targets.
Support higher-is-better and lower-is-better indicators.
Support inherited Federal targets.
Support state target override where allowed.
```

### Acceptance Criteria

```txt
Targets can be configured.
Threshold bands can be configured.
State can override target only when allowed.
Indicator results can be assigned performance band.
```

---

## Chunk 6: Calculation Engine

### Goal

Calculate indicator results automatically.

### Tasks

```txt
Create calculation service.
Support scheduled calculation.
Support on-demand calculation.
Store results historically.
Track calculation runs.
Handle errors and failed calculations.
Add calculation logs.
```

### Acceptance Criteria

```txt
Indicators can be calculated.
Results are stored by period and scope.
Failed calculations are logged.
Users can manually trigger calculation if permitted.
```

---

## Chunk 7: Federal-to-State Adoption Flow

### Goal

Allow Federal indicators to be adopted by states.

### Tasks

```txt
Federal can publish indicator as standard.
Federal can share with all or selected states.
State can view Federal library.
State can adopt indicator as-is.
State can clone indicator where allowed.
State cannot edit Federal indicator directly.
Track adoption status.
```

### Acceptance Criteria

```txt
Federal indicators are visible to states based on sharing rules.
State adoption works.
State cloning works.
Federal can monitor adoption.
All actions are audit logged.
```

---

## Chunk 8: Indicator Results and Reports

### Goal

Create result views and reports.

### Tasks

```txt
Build results table.
Add filters.
Add trend chart.
Add target vs actual chart.
Add breakdown by scope.
Add reports tab.
Add export.
```

### Acceptance Criteria

```txt
Users can view indicator results.
Users can filter by period and scope.
Users can compare target vs actual.
Reports can export permitted results.
```

---

## Chunk 9: Dashboard Integration

### Goal

Integrate indicators into the flexible AI dashboard module.

### Tasks

```txt
Register indicators as dashboard datasets.
Add indicator widgets.
Add Add to Dashboard action.
Support indicator KPI cards, trend charts, comparison tables, maps, and score cards.
Allow AI to create dashboards from indicators.
```

### Acceptance Criteria

```txt
Indicators appear in dataset catalogue.
Indicator widgets can be created.
Indicator widgets respect permissions.
Indicator results can be used in dashboards.
```

---

## Chunk 10: AI Integration

### Goal

Add AI support for indicators.

### Tasks

```txt
Add AI suggest indicator endpoint.
Add AI generate formula endpoint.
Add AI explain result endpoint.
Add AI compare performance endpoint.
Add AI executive summary endpoint.
Add privacy guardrails.
```

### Acceptance Criteria

```txt
AI can suggest indicators.
AI can explain trends.
AI can generate formulas for review.
AI cannot access restricted fields.
AI output requires review before saving definitions.
```

---

## Chunk 11: Manual and Forms-Based Indicators

### Goal

Support non-automatic indicators.

### Tasks

```txt
Add manual entry model.
Add evidence upload.
Add review/approval workflow.
Add forms-based score calculation.
Connect Forms Tool responses to indicator formula engine.
```

### Acceptance Criteria

```txt
Manual indicators can be submitted with evidence.
Manual entries require review where configured.
Forms-based indicators calculate from form responses.
All submissions are audit logged.
```

---

## Chunk 12: Notifications and Alerts

### Goal

Trigger alerts from indicator performance.

### Tasks

```txt
Add indicator alert rules.
Add below-target trigger.
Add critical-band trigger.
Add missing-result trigger.
Add calculation-failed trigger.
Connect to notification settings.
```

### Acceptance Criteria

```txt
Alerts trigger based on indicator results.
Recipients receive notifications.
Alerts respect scope and permissions.
Alert events are audit logged.
```

---

## Chunk 13: Permissions, Privacy, and Audit

### Goal

Secure the feature.

### Tasks

```txt
Enforce Federal, State, Employer, and Facility permissions.
Enforce scope rules.
Enforce field-level restrictions.
Audit create, update, publish, adopt, clone, calculate, export, AI use, and sensitive views.
Add tests.
```

### Acceptance Criteria

```txt
Users cannot view unauthorized indicators.
Users cannot use restricted fields.
Sensitive views are protected.
Audit logs are created.
Tests pass.
```

---

## Chunk 14: Default Indicator Seeding

### Goal

Seed useful FoodCert indicators.

### Tasks

```txt
Seed national indicators.
Seed state indicators.
Seed employer indicators.
Seed medical facility indicators.
Add default targets and thresholds.
Add default dashboard-ready metadata.
```

### Acceptance Criteria

```txt
Default indicator library is available.
Federal and State users can start without creating all indicators manually.
Dashboard can immediately use default indicators.
```

---

## Chunk 15: Final UI QA

### Goal

Validate full feature.

### Tasks

```txt
Test Federal flow.
Test State flow.
Test Employer dashboard visibility.
Test Facility dashboard visibility.
Test indicator creation.
Test formula preview.
Test calculation.
Test results.
Test dashboards.
Test AI.
Test reports.
Test permissions.
```

### Acceptance Criteria

```txt
Feature fits into latest Federal and State account flows.
No duplicate dashboard or forms logic is created.
Indicators work as a reusable platform layer.
```

---

# 24. Codex Master Prompt

```txt
Build the FoodCert NG Performance Indicators module as a KPI / Indicator Definition and Calculation Engine.

This is not primarily a manual data-entry KPI system. Most indicator values should be automatically calculated from activities already executed on the FoodCert NG platform, including certificates, assessments, inspections, accreditation, enforcement, corrective actions, forms, payments, settlements, and reporting.

Create the Performance Indicators module for Federal and State accounts.

Federal account:
- Can create national indicators.
- Can define formulas, targets, thresholds, calculation frequency, and visibility.
- Can publish indicators as Federal Standard Indicators.
- Can share indicators with all or selected states.
- Can monitor cross-state results and state adoption.
- Can view aggregate performance, not restricted medical details unless permitted.

State account:
- Can view and adopt Federal indicators.
- Can clone Federal indicators where allowed.
- Can create state-owned indicators.
- Can set state-specific targets where allowed.
- Can monitor state, LGA, employer, facility, certificate, inspection, enforcement, forms, and revenue performance.

Employer and Medical Facility accounts:
- Do not need a separate Performance Indicators module in MVP.
- They should consume employer/facility scoped indicators inside their dashboards and reports.
- Employer must not see medical details.
- Facility can see medical details only for authorised facility records.

Integrate indicators with:
- Flexible AI Dashboard Module
- Forms Tool
- Reports
- Notifications
- Account Settings
- Audit Logs

Architecture:
Activity Data → Indicator Definition → Calculation Engine → Indicator Results → Dashboards / Reports / AI Insights

Implement:
- IndicatorDefinition
- IndicatorTarget
- IndicatorThreshold
- IndicatorResult
- IndicatorCalculationRun
- IndicatorAdoption
- IndicatorManualEntry

Support:
- Count
- Percentage
- Rate
- Ratio
- Average Duration
- Sum
- Composite Score
- Manual Value
- Forms Score

AI:
- Suggest indicators
- Generate formulas for review
- Explain results
- Compare performance
- Generate executive summaries
- Respect all permissions, scopes, and privacy rules

Use Next.js + React + TypeScript + Tailwind CSS for frontend.
Backend permissions and scoping remain the source of truth.
Do not duplicate the Forms Tool or Dashboard Builder.
```

---

# 25. MVP Build Order

```txt
1. Indicator Module Foundation
2. Indicator Dataset Registry
3. Indicator Definition Builder
4. Formula Builder and Validation
5. Targets and Thresholds
6. Calculation Engine
7. Federal-to-State Adoption Flow
8. Indicator Results and Reports
9. Dashboard Integration
10. AI Integration
11. Manual and Forms-Based Indicators
12. Notifications and Alerts
13. Permissions, Privacy, and Audit
14. Default Indicator Seeding
15. Final UI QA
```
