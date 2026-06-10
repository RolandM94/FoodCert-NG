# PRD Update: Illness Exclusions & Return-to-Work Clearance UI Consolidation — FoodCert NG

## 1. Document Purpose

This PRD update defines how **Illness Exclusions** and **Return-to-Work Clearance** should be positioned across the FoodCert NG application.

The key product decision is:

> **Illness Exclusions and Return-to-Work Clearance should not be a standalone State Ministry menu/module.**

They are primarily operational workflows for:

1. **Employers** — to report illness, exclude food handlers from food handling duties, monitor clearance, and comply with exclusion obligations.
2. **Medical Facilities / Doctors** — to medically review illness cases, determine clearance requirements, and issue return-to-work decisions.
3. **Food Handlers** — to view their own exclusion/clearance status and next steps.

For the **State Ministry**, illness exclusions and return-to-work clearance should be handled as:

- Dashboard indicators
- Report categories
- Directory status fields
- Inspection/enforcement flags
- Exception/high-risk oversight queues only where necessary

This update should be used by Codex to remove or avoid a separate State Ministry menu item such as:

```txt
Monitor Illness Exclusions
Return-to-Work Clearance
Illness & RTW Monitoring
```

and instead distribute the workflow correctly across Employer, Medical Facility, Inspector, Directory, Reports, and State dashboard views.

---

# 2. Product Decision

## 2.1 Do Not Make It a Standalone State Ministry Menu

The State Ministry should not have a full standalone operational menu for illness exclusions and return-to-work clearance.

Do not show this as a top-level State Ministry menu item:

```txt
Illness Exclusions
Return-to-Work Clearance
Monitor Illness Exclusions
Illness & RTW Monitoring
```

## 2.2 Correct Placement

Use this placement instead:

```txt
Employer Portal
├── Illness Reports
├── Exclusions
├── Return-to-Work Clearance
└── Compliance Dashboard

Medical Facility Portal
├── Assessments
├── Doctor Review
├── Return-to-Work Clearance
└── Medical Reports

State Ministry Portal
├── Dashboard indicators
├── Directory status fields
├── Inspection/compliance flags
├── Reports
└── High-risk exception monitoring only

Inspector Portal
├── Certificate Verification
├── Food Handler status flags
├── Inspection checklist
└── Enforcement findings
```

---

# 3. Why This Update Is Needed

Illness exclusion is a day-to-day operational responsibility of the employer. A food business must know which food handlers should not be handling food and when they are cleared to return.

Return-to-work clearance is a medical decision/workflow. Doctors and approved medical facilities are the users that should review symptoms, clearance tests, exclusion periods, and medical documentation.

The State Ministry has oversight and enforcement responsibility, but it should not be the main actor manually managing every ordinary illness exclusion or return-to-work case. If this becomes a full State Ministry menu, the platform will overburden state users and duplicate workflows that belong to employers and medical facilities.

The cleaner product model is:

```txt
Employer reports/manages operational exclusion
→ Medical facility/doctor reviews and clears medically
→ Inspector checks compliance during inspection
→ State Ministry monitors exceptions, dashboards, and reports
```

---

# 4. Core Product Principle

Use this principle across the application:

> **Illness Exclusions and Return-to-Work Clearance are operational and medical workflows. State Ministry sees them as oversight signals, not as a standalone operational module.**

---

# 5. Recommended Navigation Changes

## 5.1 State Ministry Navigation

Use this clean State Ministry navigation:

```txt
Dashboard
Stakeholder Management
Medical Facilities
Directory
Certificate Validation
Certificate Registry
Inspections
Reports
Revenue
Settings
```

Do not add:

```txt
Illness Exclusions
Return-to-Work Clearance
Monitor Illness Exclusions
```

as separate top-level State Ministry navigation items.

## 5.2 Employer Navigation

Employer portal may include illness and RTW as operational pages or as sub-sections under Food Handlers / Compliance.

Recommended Employer navigation:

```txt
Dashboard
Stakeholder Management
Food Handlers
Directory
Certificates
Vaccination Compliance
Illness Reports
Return-to-Work
Inspections
Billing
Reports
Settings
```

Alternative smoother grouping:

```txt
Employer
├── Food Handlers
│   ├── All Food Handlers
│   ├── Excluded Food Handlers
│   ├── Return-to-Work Pending
│   └── Cleared to Return
├── Illness Reports
└── Compliance Dashboard
```

## 5.3 Medical Facility Navigation

Medical facilities should handle RTW through clinical workflow queues.

Recommended Medical Facility navigation:

```txt
Dashboard
Stakeholder Management
Accreditation
Appointments
Assessments
Lab Requests
Return-to-Work Clearance
Certificates
Settlements
Reports
Settings
```

If the project needs fewer top-level items, RTW can sit under Assessments:

```txt
Assessments
├── Assessment Queue
├── Doctor Review
├── Lab Review
├── Return-to-Work Clearance
└── Completed Assessments
```

## 5.4 Inspector Navigation

Inspector portal should not manage RTW clinically, but should see compliance flags during inspections.

Recommended Inspector placement:

```txt
Assigned Inspections
Certificate Verification
Food Handler Verification
Inspection Checklist
Notices
Reports
```

Within inspection workflows, show flags:

```txt
Temporarily Not Fit
Excluded from Food Handling
Return-to-Work Pending
Cleared to Return
Excluded but Found Working
```

---

# 6. State Ministry UI Consolidation

## 6.1 State Dashboard

The State Ministry dashboard should show high-level cards:

```txt
Active Illness Exclusions
Return-to-Work Pending
High-Risk Exclusion Cases
Excluded Food Handlers Found Working
Overdue RTW Clearance
Employers with Active Exclusions
```

These cards should link to filtered views in:

- Directory
- Reports
- Inspections
- Exception monitoring view, if implemented

## 6.2 Directory Integration

In the State Directory, food handler records should show high-level operational statuses:

```txt
Fitness Status
Return-to-Work Status
Illness Exclusion Status
```

Example values:

```txt
Fit to Work
Temporarily Not Fit
Excluded from Food Handling
Return-to-Work Pending
Cleared to Return
Medical Review Required
```

The Directory should not expose sensitive medical details.

## 6.3 Reports Integration

Reports should include:

```txt
Illness Exclusion Report
Return-to-Work Clearance Report
Employer Compliance with Exclusion Report
High-Risk Illness Case Report
RTW Overdue Report
```

## 6.4 Inspection Integration

Inspectors and State Ministry inspection reviewers should see flags such as:

```txt
Excluded food handler present at work
Return-to-work clearance pending
Temporarily not fit but active in food handling
Employer failed to report illness
Employer failed to exclude sick handler
```

These should become inspection findings or enforcement triggers.

## 6.5 High-Risk Exception Monitoring

If the State Ministry needs visibility beyond reports, create a **filtered exception view**, not a top-level menu.

Possible placement:

```txt
State Dashboard → High-Risk Exclusion Cases
Reports → Illness & RTW Exceptions
Directory → Food Handlers filtered by RTW Pending / Excluded
Inspections → Exclusion Violations
```

This view should focus only on cases requiring regulatory attention.

Examples:

- Exclusion overdue
- Employer non-compliance
- Food handler found working while excluded
- Serious/public health disease flag
- RTW clearance repeatedly delayed
- Facility clearance disputed
- Inspector escalated case

---

# 7. Employer Workflow Requirements

## 7.1 Employer Responsibilities

Employer users should be able to:

- Report illness for a linked food handler.
- View active exclusions.
- View return-to-work pending cases.
- Confirm exclusion from food handling duties.
- Receive clearance notifications.
- View cleared-to-return status.
- Respond to inspector/state compliance issues.
- Keep operational records without seeing sensitive medical details.

## 7.2 Employer Illness Reports Page

The Employer portal should include an illness reporting workflow.

Recommended page:

```txt
/employer/illness-reports
```

Table columns:

```txt
Food Handler
Branch
Reported Symptoms Category
Reported Date
Exclusion Status
Return-to-Work Status
Medical Facility / Doctor Review Status
Clearance Due Date
Actions
```

Employer can see symptom category and operational instruction, but not private clinical notes.

## 7.3 Employer Exclusions View

Employer should have a filtered view of food handlers who are excluded.

This can be:

```txt
/employer/food-handlers?status=excluded
```

or:

```txt
/employer/illness-reports?filter=active_exclusions
```

Columns:

```txt
Food Handler
Branch
Exclusion Start Date
Exclusion Reason Category
Earliest Return Date
RTW Status
Actions
```

## 7.4 Employer Return-to-Work View

Employer should see:

```txt
Return-to-Work Pending
Cleared to Return
Clearance Rejected
Medical Review Required
```

Employer should not be allowed to clear a food handler medically. Employer only receives the clearance decision.

## 7.5 Employer Privacy Rules

Employer cannot see:

- Diagnosis
- Lab results
- Doctor notes
- Full health declaration
- Treatment notes
- Detailed medical report

Employer can see:

- Operational exclusion status
- Fitness status
- RTW status
- Earliest return date
- Clearance outcome
- Instruction such as “Do not assign to food handling duties”

---

# 8. Medical Facility / Doctor Workflow Requirements

## 8.1 Medical Facility Responsibilities

Medical facility users and doctors should be able to:

- Receive illness/RTW review requests.
- Review food handler illness case.
- Review symptoms and medical evidence.
- Request additional tests where needed.
- Apply exclusion rules.
- Determine earliest return date.
- Issue return-to-work clearance.
- Mark not cleared and request follow-up.
- Generate medical clearance report.
- Notify employer and food handler of operational outcome.

## 8.2 Medical Facility RTW Queue

Recommended placement:

```txt
/facility/assessments?queue=return-to-work
```

or:

```txt
/facility/return-to-work-clearance
```

Columns:

```txt
Food Handler
Employer
Branch
Case Type
Exclusion Start Date
Symptoms End Date
Required Clearance
Review Status
Assigned Doctor
Actions
```

## 8.3 Doctor Review Actions

Doctor can:

```txt
Review Case
Request Lab Test
Request More Information
Set Earliest Return Date
Mark Cleared to Return
Mark Not Cleared
Require Public Health Clearance
Generate Clearance Report
```

## 8.4 Medical Privacy

Medical facility and doctor views may include medical details, but only for authorized users and assigned cases.

Sensitive access must be audit logged.

---

# 9. Food Handler Workflow Requirements

Food handlers should be able to:

- View their own illness report status.
- View exclusion status.
- View return-to-work requirements.
- View appointment or follow-up instructions.
- View clearance outcome.
- Download clearance report where permitted.
- Receive notifications.

Food handler view should be simple:

```txt
You are temporarily excluded from food handling duties.
Next step: Visit approved medical facility for clearance.
Earliest possible return date: [date]
Status: Return-to-Work Pending
```

---

# 10. Inspector Workflow Requirements

Inspectors should see operational flags during inspections.

## 10.1 Food Handler Verification During Inspection

Inspector can see:

```txt
Certificate Status
Fitness Status
Illness Exclusion Status
Return-to-Work Status
```

Inspector cannot see medical details.

## 10.2 Inspection Findings

If the inspector finds a food handler working while excluded, create finding:

```txt
Excluded food handler found handling food
```

Severity:

```txt
Critical
```

Recommended enforcement action:

```txt
Immediate removal from food handling duties
Compliance notice
Follow-up inspection
State escalation if repeated or serious
```

---

# 11. Status Definitions

## 11.1 Illness Exclusion Status

Recommended values:

```txt
No Active Exclusion
Exclusion Reported
Excluded from Food Handling
Employer Confirmed Exclusion
Medical Review Pending
Public Health Clearance Required
Exclusion Ended
```

## 11.2 Return-to-Work Status

Recommended values:

```txt
Not Required
Pending Medical Review
Pending Lab Result
Pending Public Health Clearance
Cleared to Return
Not Cleared
Follow-Up Required
Overdue
```

## 11.3 Operational Fitness Status

Recommended values:

```txt
Fit to Work
Temporarily Not Fit
Excluded from Food Handling
Return-to-Work Pending
Cleared to Return
Medical Review Required
```

---

# 12. Data Model Clarification

This update does not require a State Ministry standalone model for illness monitoring.

Use or extend the existing planned models:

```txt
IllnessReport
ReturnToWorkCase
FoodHandlerProfile
Employer
OrganizationUnit as Branch
MedicalFacility
MedicalAssessment
Inspection
EnforcementNotice
AuditLog
Notification
```

## 12.1 IllnessReport

Suggested fields:

```txt
id
food_handler
employer
branch
reported_by
reported_by_type
symptom_category
reported_at
symptom_start_date
symptom_end_date
employer_action_taken
exclusion_status
notes_visible_to_employer
medical_notes_private
status
created_at
updated_at
```

## 12.2 ReturnToWorkCase

Suggested fields:

```txt
id
illness_report
food_handler
employer
branch
medical_facility
assigned_doctor
case_status
return_to_work_status
exclusion_start_date
earliest_return_date
clearance_date
clearance_decision
public_health_clearance_required
clearance_report_url
created_at
updated_at
```

## 12.3 Separation of Status

Do not confuse:

```txt
Illness Exclusion Status
Return-to-Work Status
Operational Fitness Status
Certificate Status
```

They are related but separate.

Example:

```txt
certificate_status = active
operational_fitness_status = excluded_from_food_handling
return_to_work_status = pending_medical_review
```

This means the food handler may still have an active certificate but is temporarily excluded due to illness.

---

# 13. API Requirements

## 13.1 Employer APIs

```txt
GET  /api/employer/illness-reports
POST /api/employer/illness-reports
GET  /api/employer/illness-reports/:id
GET  /api/employer/return-to-work-cases
GET  /api/employer/food-handlers?status=excluded
POST /api/employer/illness-reports/:id/confirm-exclusion
```

## 13.2 Medical Facility APIs

```txt
GET  /api/facility/return-to-work-cases
GET  /api/facility/return-to-work-cases/:id
POST /api/facility/return-to-work-cases/:id/request-lab-test
POST /api/facility/return-to-work-cases/:id/request-more-info
POST /api/facility/return-to-work-cases/:id/clear
POST /api/facility/return-to-work-cases/:id/not-clear
POST /api/facility/return-to-work-cases/:id/require-public-health-clearance
```

## 13.3 Food Handler APIs

```txt
GET /api/food-handler/illness-reports
GET /api/food-handler/return-to-work-cases
GET /api/food-handler/return-to-work-cases/:id
```

## 13.4 State Ministry APIs

State should consume filtered and aggregate APIs, not operationally own the workflow.

```txt
GET /api/state/dashboard/illness-rtw-summary
GET /api/state/reports/illness-exclusions
GET /api/state/reports/return-to-work
GET /api/state/directory/food-handlers?return_to_work_status=
GET /api/state/inspections/exclusion-violations
```

## 13.5 Inspector APIs

```txt
GET  /api/inspections/:id/food-handlers
POST /api/inspections/:id/findings/excluded-food-handler-working
```

---

# 14. Frontend Routes

## 14.1 Employer Routes

```txt
/employer/illness-reports
/employer/illness-reports/[id]
/employer/return-to-work
/employer/food-handlers?status=excluded
```

## 14.2 Medical Facility Routes

```txt
/facility/return-to-work-clearance
/facility/return-to-work-clearance/[caseId]
/facility/assessments?queue=return-to-work
```

## 14.3 Food Handler Routes

```txt
/food-handler/illness
/food-handler/return-to-work
/food-handler/return-to-work/[caseId]
```

## 14.4 State Ministry Routes

Do not create:

```txt
/state/illness-exclusions
/state/return-to-work-clearance
```

Use:

```txt
/state/dashboard
/state/directory/food-handlers?return_to_work_status=pending
/state/reports?category=illness_exclusion
/state/reports?category=return_to_work
/state/inspections?finding=excluded_food_handler_working
```

---

# 15. UI Consolidation Rules

## 15.1 State Ministry

Remove or avoid standalone menu:

```txt
Monitor Illness Exclusions
Return-to-Work Clearance
```

Replace with:

- Dashboard cards
- Directory filters
- Report categories
- Inspection flags
- High-risk exception filtered views

## 15.2 Employer

Illness and RTW can be visible because the employer is operationally responsible.

Recommended grouping:

```txt
Food Handlers
├── All Food Handlers
├── Excluded Food Handlers
├── Return-to-Work Pending
└── Cleared to Return

Illness Reports
Return-to-Work
```

The exact UX can be tabs, filters, or pages depending on the current portal design.

## 15.3 Medical Facility

RTW can be a queue under Assessments or a standalone clinical queue.

Recommended:

```txt
Assessments
├── Assessment Queue
├── Doctor Review
├── Lab Review
└── Return-to-Work Clearance
```

or:

```txt
Return-to-Work Clearance
```

if the facility dashboard has many clinical queues.

## 15.4 Inspector

RTW should be an inspection flag, not a clinical workflow.

## 15.5 Food Handler

RTW should appear in the user’s own health/certification journey.

---

# 16. Components to Build / Update

## 16.1 Employer Components

```txt
IllnessReportsPage
IllnessReportForm
IllnessReportsTable
ExclusionStatusBadge
ReturnToWorkStatusBadge
EmployerReturnToWorkPage
ConfirmExclusionButton
```

## 16.2 Medical Facility Components

```txt
ReturnToWorkQueue
ReturnToWorkCaseDetail
DoctorClearancePanel
ClearanceDecisionModal
PublicHealthClearancePanel
ClearanceReportCard
```

## 16.3 State Components

```txt
IllnessRtwDashboardCards
IllnessExclusionReport
ReturnToWorkReport
DirectoryRtwStatusFilter
InspectionExclusionViolationTable
```

## 16.4 Inspector Components

```txt
InspectionFoodHandlerStatusFlags
ExcludedFoodHandlerFindingForm
ReturnToWorkFlagBadge
```

## 16.5 Shared Components

```txt
IllnessExclusionStatusBadge
ReturnToWorkStatusBadge
OperationalFitnessStatusBadge
PrivacyNotice
```

---

# 17. Permissions

## 17.1 Employer Permissions

```txt
illness_report.view
illness_report.create
illness_report.confirm_exclusion
return_to_work.view
```

## 17.2 Medical Facility Permissions

```txt
return_to_work.view
return_to_work.review
return_to_work.request_lab
return_to_work.clear
return_to_work.not_clear
return_to_work.require_public_health_clearance
```

## 17.3 State Ministry Permissions

```txt
state_illness_summary.view
state_return_to_work_summary.view
state_illness_reports.view
state_return_to_work_reports.view
```

## 17.4 Inspector Permissions

```txt
inspection.view_food_handler_status
inspection.flag_exclusion_violation
```

## 17.5 Privacy Rule

State summary permissions do not automatically grant access to detailed medical notes.

---

# 18. Reports

## 18.1 Employer Reports

```txt
Active Exclusions Report
Return-to-Work Pending Report
Cleared to Return Report
Branch Exclusion Compliance Report
```

## 18.2 Medical Facility Reports

```txt
RTW Cases Reviewed
Clearance Decisions Report
Pending Medical Review Report
Public Health Clearance Required Report
```

## 18.3 State Reports

```txt
Illness Exclusion Summary Report
Return-to-Work Clearance Summary Report
Employer Exclusion Compliance Report
RTW Overdue Report
Exclusion Violation Report
```

## 18.4 Federal Reports

Federal reports should be aggregate only unless permission allows drilldown.

```txt
National Illness Exclusion Trend
State RTW Clearance Performance
High-Risk Exclusion Cases by State
```

---

# 19. Notifications

## 19.1 Employer Notifications

Notify employer when:

- Illness report submitted
- Food handler must be excluded
- RTW review is pending
- Clearance is issued
- Clearance is denied
- RTW case is overdue

## 19.2 Food Handler Notifications

Notify food handler when:

- Illness report is created
- Exclusion begins
- Medical review is required
- RTW clearance is issued
- RTW clearance is denied
- Follow-up is required

## 19.3 Medical Facility Notifications

Notify facility/doctor when:

- RTW case assigned
- Employer submits additional information
- Lab result is available
- Public health clearance is required

## 19.4 State Notifications

State should only receive notifications for:

- High-risk cases
- Overdue cases
- Employer non-compliance
- Inspector escalations
- Public health clearance exceptions

---

# 20. Acceptance Criteria

## 20.1 State Ministry UI

- No standalone State Ministry menu item for Illness Exclusions.
- No standalone State Ministry menu item for Return-to-Work Clearance.
- State dashboard shows summary indicators.
- State reports include illness/RTW reports.
- State Directory can filter by RTW/exclusion status.
- Inspection module can flag exclusion violations.

## 20.2 Employer UI

- Employer can create illness reports.
- Employer can view active exclusions.
- Employer can view return-to-work pending cases.
- Employer can confirm operational exclusion.
- Employer cannot medically clear a food handler.
- Employer cannot view private medical notes, diagnosis, or lab results.

## 20.3 Medical Facility UI

- Facility/doctor can review RTW cases.
- Doctor can clear or not clear food handler.
- Doctor can request lab tests or more information.
- Facility can generate clearance report.
- Medical access is permission-controlled and audit logged.

## 20.4 Inspector UI

- Inspector can see operational exclusion and RTW flags.
- Inspector cannot see medical details.
- Inspector can create finding if excluded food handler is working.

## 20.5 Privacy

- Employer and inspector views do not expose lab results, diagnosis, doctor notes, declaration answers, or treatment notes.
- State summary views are aggregate/status-based unless explicit permission allows more.
- Sensitive access is audit logged.

---

# 21. Implementation Chunks for Codex

## Chunk 1: State Menu Consolidation

### Goal

Remove or avoid standalone State Ministry illness/RTW menu items.

### Tasks

- Remove `Illness Exclusions`, `Return-to-Work Clearance`, or similar top-level State menu items if present.
- Add dashboard cards instead.
- Add links from cards to Directory filters, Reports, or Inspections.
- Add route redirects if old state routes exist.

### Suggested Redirects

```txt
/state/illness-exclusions → /state/reports?category=illness_exclusion
/state/return-to-work → /state/reports?category=return_to_work
/state/monitor-illness-exclusions → /state/dashboard
```

### Acceptance Criteria

- State Ministry sidebar does not show illness/RTW as standalone menu.
- Users can still access illness/RTW information through dashboard, reports, directory filters, and inspections.

---

## Chunk 2: Employer Illness Reports

### Goal

Implement employer operational illness reporting.

### Tasks

- Add illness report list.
- Add illness report creation form.
- Link report to food handler, employer, and branch.
- Add exclusion status.
- Add confirm exclusion action.
- Add privacy-safe fields.

### Acceptance Criteria

- Employer can report illness.
- Employer can view active illness reports.
- Employer can confirm exclusion from food handling.
- Employer cannot see private medical details.

---

## Chunk 3: Employer Return-to-Work View

### Goal

Implement employer RTW monitoring.

### Tasks

- Add employer RTW page or filtered view.
- Show RTW pending, cleared, not cleared, follow-up required.
- Link to food handler profile.
- Show operational next steps.
- Add notifications.

### Acceptance Criteria

- Employer can see RTW status for linked food handlers.
- Employer cannot clear medically.
- Employer sees clearance outcome only.

---

## Chunk 4: Medical Facility RTW Queue

### Goal

Implement clinical RTW review queue.

### Tasks

- Add facility RTW queue.
- Add case detail.
- Add doctor review panel.
- Add actions:
  - Request lab test
  - Request more information
  - Clear to return
  - Not clear
  - Require public health clearance
- Generate clearance report.

### Acceptance Criteria

- Facility/doctor can review assigned RTW cases.
- Doctor can issue clearance decision.
- Sensitive access is permission-controlled.

---

## Chunk 5: State Dashboard and Reports Integration

### Goal

Add State oversight without a standalone module.

### Tasks

- Add state dashboard summary cards.
- Add state reports:
  - Illness Exclusion Report
  - Return-to-Work Clearance Report
  - Employer Compliance with Exclusion Report
- Add report filters.
- Ensure state scoping.

### Acceptance Criteria

- State users can monitor illness/RTW at summary level.
- Reports are state-scoped.
- Reports do not expose private medical details by default.

---

## Chunk 6: Directory Integration

### Goal

Expose illness/RTW statuses through Directory filters and badges.

### Tasks

- Add status fields to Food Handler Directory rows:
  - illness_exclusion_status
  - return_to_work_status
  - operational_fitness_status
- Add filters for those statuses.
- Add badges.
- Ensure privacy-safe serializers.

### Acceptance Criteria

- State, employer, and inspector users can filter by RTW/exclusion status where permitted.
- Directory does not expose medical details.
- Filters respect scope.

---

## Chunk 7: Inspector Enforcement Integration

### Goal

Allow inspectors to flag exclusion violations.

### Tasks

- Show exclusion/RTW flags in inspection food handler list.
- Add finding action:
  - Excluded food handler found working
- Link finding to inspection, employer, branch, and food handler.
- Add severity and enforcement recommendation.

### Acceptance Criteria

- Inspector can identify excluded food handlers during inspection.
- Inspector can create enforcement finding.
- Inspector cannot view medical details.

---

## Chunk 8: Notifications

### Goal

Add workflow notifications.

### Tasks

- Notify employer, food handler, facility/doctor, and state exception users.
- Use existing notification system.
- Add event templates.

### Acceptance Criteria

- RTW/exclusion events trigger appropriate notifications.
- State gets only exception/high-risk notifications.

---

## Chunk 9: Permissions and Privacy Tests

### Goal

Ensure access control and privacy are correct.

### Tests

- Employer cannot see medical details.
- Inspector cannot see medical details.
- State cannot access private RTW medical notes by summary permission only.
- Medical facility users can see only assigned cases.
- Employer sees only linked food handlers.
- State sees only state-scoped summaries.
- Old state menu routes redirect.

### Acceptance Criteria

- All permission tests pass.
- All privacy tests pass.
- No unauthorized medical fields leak.

---

## Chunk 10: Final UI QA

### Goal

Confirm UX consolidation is correct.

### QA Checklist

- No standalone State menu for illness/RTW.
- Employer has illness/RTW operational workflow.
- Medical facility has RTW clinical queue.
- State dashboard has summary cards.
- State reports include illness/RTW categories.
- Directory has RTW/exclusion filters.
- Inspector can flag violations.
- UI is responsive and follows FoodCert NG design system.

---

# 22. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Update the Illness Exclusions and Return-to-Work Clearance UX across FoodCert NG.

Do not implement Illness Exclusions or Return-to-Work Clearance as a standalone State Ministry menu/module.

These workflows are primarily:
- Employer operational workflows
- Medical facility/doctor clinical clearance workflows
- Food handler personal status workflows
- Inspector enforcement flags
- State Ministry oversight/reporting indicators

State Ministry:
- Remove or avoid standalone top-level menu items for Illness Exclusions and Return-to-Work Clearance.
- Add dashboard cards, report categories, Directory filters, and inspection flags instead.
- State should monitor summaries, exceptions, overdue cases, and enforcement violations.

Employer:
- Implement illness reporting, active exclusions, and return-to-work monitoring.
- Employer can report illness and confirm operational exclusion.
- Employer cannot medically clear food handlers.
- Employer cannot see diagnosis, lab results, doctor notes, declaration answers, or treatment notes.

Medical Facility:
- Implement Return-to-Work clinical review queue.
- Doctor can review cases, request lab tests, request more information, clear to return, not clear, or require public health clearance.
- Medical access is permission-controlled and audit logged.

Inspector:
- Show operational exclusion and return-to-work flags during inspection.
- Allow finding for excluded food handler found working.
- Do not expose medical details.

Directory:
- Add illness_exclusion_status, return_to_work_status, and operational_fitness_status as privacy-safe status fields and filters.

Reports:
- Add Illness Exclusion Report, Return-to-Work Clearance Report, Employer Exclusion Compliance Report, RTW Overdue Report, and Exclusion Violation Report.

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions remain the source of truth.
```

---

# 23. MVP Build Order

1. State menu consolidation
2. Employer illness reports
3. Employer return-to-work view
4. Medical facility RTW queue
5. State dashboard and reports integration
6. Directory status/filter integration
7. Inspector enforcement integration
8. Notifications
9. Permissions and privacy tests
10. Final UI QA
