# PRD: Inspections & Enforcement Workflow UI Consolidation — FoodCert NG

## 1. Document Purpose

This PRD defines a simpler and more intuitive structure for managing **Inspections, Enforcement Notices, Enforcement Cases, Corrective Actions, Escalations, and Enforcement Reports** on FoodCert NG.

The current issue is that the platform appears to treat the following as separate menu items or separate modules:

```txt
Inspections
Enforcement Notices
Cases
Enforcement
```

This creates confusion because these are not completely separate user journeys. They are different stages of one compliance workflow.

The improved product decision is:

> **Create one consolidated module called Inspections & Enforcement, where inspections, findings, notices, cases, corrective actions, escalations, and reports are handled in one connected workflow.**

---

# 2. Product Decision

## 2.1 One Parent Module

Use one parent module:

```txt
Inspections & Enforcement
```

Inside it, use a clean tab structure:

```txt
Inspections & Enforcement
├── Overview
├── Inspections
├── Cases
├── Notices
└── Reports
```

Do not show these as separate top-level menu items:

```txt
Inspections
Enforcement Notices
Cases
Enforcement
Corrective Actions
Escalations
```

Those should all live inside the single **Inspections & Enforcement** module.

---

# 3. Why This Change Is Needed

The user experience should follow the real-world compliance process:

```txt
Inspection is planned
→ Inspector visits employer/facility
→ Inspector completes inspection form/checklist
→ Findings are recorded
→ If violation exists, notice is issued
→ If follow-up is required, case is opened
→ Corrective action is tracked
→ Follow-up inspection may be scheduled
→ Case is closed or escalated
```

This is one connected workflow, not four unrelated modules.

A user should not have to jump from:

```txt
Inspections → Notices → Cases → Enforcement
```

to understand what happened. Everything should be visible from one consolidated module and from the relevant inspection/case detail page.

---

# 4. Core Product Principle

Use this principle across the UI:

> **An inspection can create findings. Findings can generate notices. Serious or unresolved notices can become cases. Enforcement is the overall process that manages the case until resolution.**

So the platform should not make users think that Inspections, Notices, Cases, and Enforcement are unrelated.

---

# 5. Recommended Navigation

## 5.1 State Ministry Navigation

Recommended State Ministry navigation:

```txt
Dashboard
Stakeholder Management
Medical Facilities
Employers / Directory
Forms Tool
Inspections & Enforcement
Certificate Registry
Reports
Revenue
Settings
```

Remove or avoid separate sidebar items such as:

```txt
Inspections
Enforcement Notices
Cases
Enforcement
Corrective Actions
Escalations
```

## 5.2 Inspector Navigation

Inspector navigation should be simpler:

```txt
Dashboard
My Inspections
Inspection History
Notices / Follow-ups
Reports
```

The inspector does not need a full enforcement backend. They need to see assignments, complete inspections, create findings, and follow up where assigned.

## 5.3 Employer / Food Business Navigation

Employers should not see the State enforcement backend. They should see only compliance actions that concern them.

Recommended employer placement:

```txt
Compliance
├── Inspection History
├── Notices
├── Corrective Actions
└── Case Status, if any
```

or:

```txt
Employer Portal
├── Dashboard
├── Food Handlers
├── Branches / Outlets
├── Compliance
├── Assigned Forms
├── Billing
└── Settings
```

Inside **Compliance**, they can respond to notices and upload corrective action evidence.

## 5.4 Medical Facility Navigation

Medical facilities should only see inspections, notices, or cases that relate to their facility accreditation or conduct.

Recommended placement:

```txt
Medical Facility Portal
├── Dashboard
├── Accreditation
├── Assessments
├── Compliance
│   ├── Inspections
│   ├── Notices
│   └── Corrective Actions
├── Settlements
└── Reports
```

---

# 6. Simplified Module Structure

## 6.1 Final Recommended Module

```txt
Inspections & Enforcement
├── Overview
├── Inspections
├── Cases
├── Notices
└── Reports
```

## 6.2 Why This Is Better

This structure is simple because:

- **Inspections** is where compliance checks start.
- **Cases** is where serious or unresolved issues are tracked.
- **Notices** is where official communications are listed.
- **Reports** is where performance and compliance summaries are generated.
- **Overview** gives users a quick dashboard of everything.

Corrective actions, escalations, follow-ups, and evidence should not be separate tabs. They should be inside the relevant **Case** or **Inspection Detail**.

---

# 7. Tab Definitions

## 7.1 Overview Tab

### Purpose

The Overview tab gives State Ministry users and authorized enforcement users a summary of inspection and enforcement activity.

### KPI Cards

Show cards such as:

```txt
Scheduled Inspections
Inspections In Progress
Completed Inspections
Failed Inspections
Open Cases
Notices Issued
Corrective Actions Due
Overdue Corrective Actions
Escalated Cases
Closed Cases
```

### Dashboard Widgets

Recommended widgets:

```txt
Recent Inspections
High-Risk Findings
Overdue Notices
Open Cases by Severity
Inspection Completion Rate
Top Non-Compliant Employers
Cases by Status
Upcoming Follow-up Inspections
```

### Quick Actions

Depending on permissions:

```txt
Create Inspection
Assign Inspector
View Open Cases
Issue Notice
Export Report
```

---

## 7.2 Inspections Tab

### Purpose

The Inspections tab is where users plan, assign, conduct, review, and complete inspections.

### Inspection Table Columns

```txt
Inspection Reference
Inspection Type
Target Type
Target Name
Branch / Facility
LGA
Assigned Inspector
Scheduled Date
Inspection Status
Risk Level
Findings Count
Actions
```

### Inspection Statuses

```txt
Draft
Scheduled
Assigned
In Progress
Submitted
Under Review
Completed
Requires Follow-up
Cancelled
```

### Filters

Use filters/status chips:

```txt
All
Draft
Scheduled
Assigned
In Progress
Submitted
Under Review
Completed
Requires Follow-up
Cancelled
```

### Inspection Types

```txt
Routine Inspection
Follow-up Inspection
Complaint-Based Inspection
High-Risk Inspection
Accreditation Inspection
Re-accreditation Inspection
Incident Investigation
```

### Inspection Target Types

```txt
Employer / Food Business
Branch / Outlet
Medical Facility
Accreditation Application
Incident
```

### Key Actions

```txt
Create Inspection
Assign Inspector
Assign Inspection Template
Reschedule
Start Inspection
Review Submission
Create Finding
Issue Notice
Open Case
Close Inspection
```

---

# 8. Inspection Detail View

## 8.1 Purpose

The Inspection Detail page should be the main workspace for everything related to a specific inspection.

When a user clicks an inspection, they should see:

```txt
Inspection Detail
├── Summary
├── Assigned Form / Checklist
├── Findings
├── Evidence
├── Notices
├── Linked Case
├── Follow-up
└── Audit Log
```

## 8.2 Summary Section

Shows:

```txt
Inspection Reference
Inspection Type
Target Employer / Facility
Branch / Outlet
Inspector
Scheduled Date
Submission Date
Inspection Status
Risk Level
Overall Score
Outcome
```

## 8.3 Assigned Form / Checklist

This should use the **Forms Tool**.

Flow:

```txt
State creates inspection
→ State assigns inspector
→ State selects inspection template from Forms Tool
→ Inspector opens inspection
→ Inspector completes assigned form/checklist
→ Response is saved under this inspection
```

## 8.4 Findings Section

Findings are issues discovered during inspection.

Examples:

```txt
Uncertified food handlers found working
Expired food handler certificates
Poor hygiene condition
No evidence of illness exclusion process
Unapproved medical facility conducting assessments
```

Finding severity:

```txt
Low
Medium
High
Critical
```

Finding actions:

```txt
Mark as Observation
Create Notice
Open Case
Require Corrective Action
Escalate
```

## 8.5 Evidence Section

Evidence can include:

```txt
Photos
Documents
Videos, optional
Inspector notes
GPS location
Signatures
Form attachments
```

## 8.6 Notices Section

Shows notices issued from this inspection.

The user should be able to:

```txt
Issue Notice
View Notice
Send Notice
Track Notice Status
Convert Notice to Case
```

## 8.7 Linked Case Section

If a case has been opened from the inspection, show:

```txt
Case Reference
Case Status
Case Severity
Assigned Officer
Corrective Actions
Due Dates
Escalations
Resolution Status
```

## 8.8 Follow-up Section

Allows users to schedule follow-up inspections.

```txt
Schedule Follow-up Inspection
Assign Inspector
Set Follow-up Date
Link to Original Case
```

---

# 9. Cases Tab

## 9.1 Purpose

The Cases tab is the main place to track unresolved, serious, repeated, or escalated compliance issues.

A case should be opened when:

```txt
A finding is serious
A notice requires follow-up
A party fails to comply with a notice
A violation is repeated
An inspector escalates an inspection
A medical facility or employer requires regulatory action
```

## 9.2 Case Table Columns

```txt
Case Reference
Case Title
Target Type
Target Name
Source
Severity
Assigned Officer
Status
Due Date
Last Updated
Actions
```

## 9.3 Case Sources

```txt
Inspection Finding
Enforcement Notice
Complaint
Incident Report
Accreditation Review
Certificate Violation
Illness / RTW Violation
Manual Case Creation
```

## 9.4 Case Statuses

```txt
Open
Under Review
Awaiting Response
Corrective Action Submitted
Evidence Under Review
Follow-up Required
Escalated
Resolved
Closed
Cancelled
```

## 9.5 Case Severity

```txt
Low
Medium
High
Critical
```

## 9.6 Case Detail View

When a user clicks a case, show:

```txt
Case Detail
├── Case Summary
├── Violation Details
├── Linked Inspection / Source
├── Notices
├── Corrective Actions
├── Evidence
├── Follow-up Inspections
├── Escalations
├── Resolution
└── Audit Log
```

## 9.7 Case Actions

```txt
Assign Officer
Issue Notice
Request Corrective Action
Review Evidence
Schedule Follow-up Inspection
Escalate Case
Mark Resolved
Close Case
Reopen Case
```

---

# 10. Notices Tab

## 10.1 Purpose

The Notices tab is a searchable register of all official notices issued by the State Ministry or authorized officers.

Notices are official communications, not full case files.

## 10.2 Notice Table Columns

```txt
Notice Reference
Notice Type
Target Type
Target Name
Related Inspection / Case
Issue Date
Due Date
Notice Status
Issued By
Actions
```

## 10.3 Notice Types

```txt
Warning Notice
Compliance Notice
Corrective Action Notice
Improvement Notice
Suspension Notice
Re-inspection Notice
Closure Recommendation
Information Request Notice
```

## 10.4 Notice Statuses

```txt
Draft
Issued
Acknowledged
Response Submitted
Under Review
Complied
Partially Complied
Overdue
Escalated
Closed
Withdrawn
```

## 10.5 Notice Actions

```txt
Create Notice
Issue Notice
Send Reminder
View Response
Return Response
Mark Complied
Convert to Case
Close Notice
```

## 10.6 Important Rule

A notice can exist without a case, especially for minor issues.

A case should be opened only when the issue needs tracking, follow-up, escalation, or formal resolution.

---

# 11. Reports Tab

## 11.1 Purpose

The Reports tab provides inspection and enforcement reports.

## 11.2 Report Types

```txt
Inspection Summary Report
Inspection Completion Report
Inspection Findings Report
Notices Issued Report
Open Cases Report
Closed Cases Report
Corrective Action Report
Overdue Notices Report
Escalated Cases Report
Employer Compliance Report
Medical Facility Compliance Report
Inspector Performance Report
LGA Compliance Report
High-Risk Violations Report
```

## 11.3 Report Filters

```txt
Date Range
State
LGA
Inspector
Inspection Type
Target Type
Employer
Medical Facility
Case Status
Notice Status
Severity
Risk Level
```

## 11.4 Export Formats

```txt
CSV
Excel
PDF
```

---

# 12. End-to-End Workflow

## 12.1 Routine Inspection Workflow

```txt
State creates inspection
→ Select target employer / branch / facility
→ Select inspection type
→ Assign inspector
→ Assign inspection form template
→ Inspector receives assignment
→ Inspector conducts inspection
→ Inspector submits checklist, evidence, and findings
→ State reviews submission
→ If no issue, inspection is completed
→ If issue exists, notice is issued or case is opened
```

## 12.2 Notice Workflow

```txt
Finding identified
→ Notice drafted
→ Notice issued to employer/facility
→ Target acknowledges notice
→ Target submits corrective action evidence
→ State reviews evidence
→ Notice marked complied, partially complied, overdue, or escalated
```

## 12.3 Case Workflow

```txt
Serious finding or unresolved notice
→ Case opened
→ Officer assigned
→ Case details reviewed
→ Notice or corrective action requested
→ Evidence submitted
→ Evidence reviewed
→ Follow-up inspection scheduled if needed
→ Case resolved
→ Case closed
```

## 12.4 Escalation Workflow

```txt
Notice overdue or violation critical
→ Case escalated
→ Senior officer reviews
→ Enforcement action selected
→ Additional notice, suspension, follow-up inspection, or closure recommendation issued
→ Case remains open until resolved
```

---

# 13. UI Consolidation Rules

## 13.1 One Module Rule

All inspection and enforcement-related activities should be reachable from:

```txt
Inspections & Enforcement
```

## 13.2 Do Not Use Separate Top-Level Modules

Do not create separate top-level modules for:

```txt
Enforcement Notices
Cases
Corrective Actions
Escalations
Enforcement
```

## 13.3 Detail Page Rule

Deep workflow items should appear inside detail pages.

For example:

```txt
Corrective Actions → inside Case Detail or Notice Detail
Escalations → inside Case Detail
Evidence → inside Inspection Detail or Case Detail
Follow-up → inside Inspection Detail or Case Detail
```

## 13.4 Notice vs Case Rule

Use this distinction:

```txt
Notice = official communication / instruction
Case = tracked compliance file
Enforcement = overall process
```

## 13.5 Inspection First Rule

Most enforcement should start from an inspection finding.

The UI should make it easy to move from:

```txt
Inspection → Finding → Notice → Case → Follow-up → Closure
```

---

# 14. Role-Based Experience

## 14.1 State Ministry Admin / Compliance Officer

Can:

```txt
Create inspections
Assign inspectors
Assign inspection templates
Review submissions
Issue notices
Open cases
Assign case officers
Escalate cases
Close cases
View reports
```

## 14.2 Inspector

Can:

```txt
View assigned inspections
Complete inspection forms
Upload evidence
Create findings
Recommend notice or case
Submit inspection
View follow-up assignments
```

## 14.3 Employer / Food Business

Can:

```txt
View notices issued to them
Acknowledge notices
Submit corrective action evidence
View case status related to them
View inspection history
Respond to information requests
```

Employer cannot see internal State enforcement notes.

## 14.4 Medical Facility

Can:

```txt
View notices issued to facility
Submit corrective action evidence
View inspection/accreditation compliance status
Respond to requests
```

## 14.5 Federal Ministry

Can:

```txt
View aggregate inspection and enforcement reports
Monitor state-level trends
View high-risk summaries
Export national oversight reports
```

Federal should not operationally manage state cases unless policy grants that power.

---

# 15. Data Model Requirements

## 15.1 Inspection

```txt
id
inspection_reference
inspection_type
target_type
target_id
branch_id
assigned_inspector_id
assigned_by
scheduled_date
due_date
status
risk_level
form_template_id
template_version_id
form_response_id
submitted_at
reviewed_by
reviewed_at
created_at
updated_at
```

## 15.2 InspectionFinding

```txt
id
inspection_id
finding_title
finding_description
severity
category
requires_notice
requires_case
critical_flag
status
created_by
created_at
updated_at
```

## 15.3 EnforcementNotice

```txt
id
notice_reference
notice_type
target_type
target_id
inspection_id
case_id
finding_id
issued_by
issued_at
due_date
status
summary
required_action
response_required
created_at
updated_at
```

## 15.4 EnforcementCase

```txt
id
case_reference
case_title
target_type
target_id
source_type
source_id
severity
status
assigned_officer_id
opened_by
opened_at
due_date
resolved_at
closed_at
resolution_summary
created_at
updated_at
```

## 15.5 CorrectiveAction

```txt
id
case_id
notice_id
description
assigned_to_type
assigned_to_id
due_date
status
submitted_by
submitted_at
reviewed_by
reviewed_at
review_comment
created_at
updated_at
```

## 15.6 EnforcementEvidence

```txt
id
inspection_id
case_id
notice_id
corrective_action_id
uploaded_by
file_url
file_type
caption
metadata_json
created_at
```

## 15.7 CaseEscalation

```txt
id
case_id
escalated_by
escalated_to
reason
severity_before
severity_after
escalated_at
resolution_note
created_at
updated_at
```

## 15.8 EnforcementAuditLog

```txt
id
actor_id
action
entity_type
entity_id
old_value_json
new_value_json
ip_address
user_agent
created_at
```

---

# 16. API Requirements

## 16.1 Inspection APIs

```txt
GET    /api/inspections
POST   /api/inspections
GET    /api/inspections/:id
PATCH  /api/inspections/:id
POST   /api/inspections/:id/assign-inspector
POST   /api/inspections/:id/assign-template
POST   /api/inspections/:id/submit
POST   /api/inspections/:id/review
POST   /api/inspections/:id/complete
POST   /api/inspections/:id/cancel
```

## 16.2 Finding APIs

```txt
GET    /api/inspections/:id/findings
POST   /api/inspections/:id/findings
PATCH  /api/findings/:id
POST   /api/findings/:id/create-notice
POST   /api/findings/:id/open-case
```

## 16.3 Notice APIs

```txt
GET    /api/enforcement/notices
POST   /api/enforcement/notices
GET    /api/enforcement/notices/:id
PATCH  /api/enforcement/notices/:id
POST   /api/enforcement/notices/:id/issue
POST   /api/enforcement/notices/:id/acknowledge
POST   /api/enforcement/notices/:id/respond
POST   /api/enforcement/notices/:id/review-response
POST   /api/enforcement/notices/:id/mark-complied
POST   /api/enforcement/notices/:id/escalate
POST   /api/enforcement/notices/:id/close
```

## 16.4 Case APIs

```txt
GET    /api/enforcement/cases
POST   /api/enforcement/cases
GET    /api/enforcement/cases/:id
PATCH  /api/enforcement/cases/:id
POST   /api/enforcement/cases/:id/assign-officer
POST   /api/enforcement/cases/:id/request-corrective-action
POST   /api/enforcement/cases/:id/review-evidence
POST   /api/enforcement/cases/:id/schedule-follow-up
POST   /api/enforcement/cases/:id/escalate
POST   /api/enforcement/cases/:id/resolve
POST   /api/enforcement/cases/:id/close
POST   /api/enforcement/cases/:id/reopen
```

## 16.5 Portal APIs for Employers / Facilities

```txt
GET  /api/employer/compliance/notices
GET  /api/employer/compliance/cases
POST /api/employer/compliance/notices/:id/acknowledge
POST /api/employer/compliance/notices/:id/respond
POST /api/employer/compliance/corrective-actions/:id/submit

GET  /api/facility/compliance/notices
GET  /api/facility/compliance/cases
POST /api/facility/compliance/notices/:id/acknowledge
POST /api/facility/compliance/notices/:id/respond
POST /api/facility/compliance/corrective-actions/:id/submit
```

---

# 17. Permissions

## 17.1 Inspection Permissions

```txt
inspection.view
inspection.create
inspection.update
inspection.assign_inspector
inspection.assign_template
inspection.submit
inspection.review
inspection.complete
inspection.cancel
```

## 17.2 Finding Permissions

```txt
inspection_finding.view
inspection_finding.create
inspection_finding.update
inspection_finding.create_notice
inspection_finding.open_case
```

## 17.3 Notice Permissions

```txt
enforcement_notice.view
enforcement_notice.create
enforcement_notice.issue
enforcement_notice.review_response
enforcement_notice.close
enforcement_notice.escalate
```

## 17.4 Case Permissions

```txt
enforcement_case.view
enforcement_case.create
enforcement_case.assign_officer
enforcement_case.update
enforcement_case.escalate
enforcement_case.resolve
enforcement_case.close
enforcement_case.reopen
```

## 17.5 External Party Permissions

```txt
compliance_notice.view_own
compliance_notice.acknowledge_own
compliance_notice.respond_own
corrective_action.submit_own
enforcement_case.view_own_status
```

---

# 18. Status Definitions

## 18.1 Inspection Status

```txt
Draft
Scheduled
Assigned
In Progress
Submitted
Under Review
Completed
Requires Follow-up
Cancelled
```

## 18.2 Notice Status

```txt
Draft
Issued
Acknowledged
Response Submitted
Under Review
Complied
Partially Complied
Overdue
Escalated
Closed
Withdrawn
```

## 18.3 Case Status

```txt
Open
Under Review
Awaiting Response
Corrective Action Submitted
Evidence Under Review
Follow-up Required
Escalated
Resolved
Closed
Cancelled
```

## 18.4 Corrective Action Status

```txt
Pending
In Progress
Submitted
Under Review
Accepted
Rejected
Overdue
Closed
```

---

# 19. Notifications

## 19.1 Inspector Notifications

Notify inspector when:

```txt
Inspection assigned
Inspection rescheduled
Inspection due soon
Inspection returned for correction
Follow-up inspection assigned
```

## 19.2 Employer / Facility Notifications

Notify target party when:

```txt
Inspection scheduled, if policy allows advance notice
Notice issued
Notice due soon
Notice overdue
Corrective action requested
Case opened
Case escalated
Case resolved or closed
```

## 19.3 State User Notifications

Notify State users when:

```txt
Inspection submitted
Critical finding reported
Notice response submitted
Corrective action evidence submitted
Notice overdue
Case escalated
Follow-up due
```

---

# 20. Reports and Analytics

## 20.1 Dashboard Metrics

```txt
Total inspections
Completed inspections
Pending inspections
Overdue inspections
Findings by severity
Notices issued
Open cases
Overdue corrective actions
Escalated cases
Closed cases
```

## 20.2 Performance Metrics

```txt
Inspection completion rate
Average time to close notice
Average time to resolve case
Inspector workload
Employer compliance rate
Medical facility compliance rate
Repeat violations
Critical violation trend
```

## 20.3 Export Requirements

Support:

```txt
CSV
Excel
PDF
```

Exports must be permission-controlled and audit logged.

---

# 21. Acceptance Criteria

## 21.1 UI Consolidation

- There is one parent module called **Inspections & Enforcement**.
- Inspections, Notices, Cases, and Reports are tabs inside the module.
- Enforcement is not a separate top-level menu item.
- Enforcement Notices are not a separate top-level menu item.
- Cases are not a separate top-level menu item.
- Corrective Actions are not a separate top-level menu item.
- Escalations are not a separate top-level menu item.

## 21.2 Inspection Workflow

- State can create inspection.
- State can assign inspector.
- State can assign inspection template from Forms Tool.
- Inspector can complete inspection form.
- Inspector can submit findings and evidence.
- State can review inspection.
- State can issue notice or open case from finding.

## 21.3 Notice Workflow

- Notice can be created from inspection finding or case.
- Notice can be issued to employer or facility.
- Target party can acknowledge notice.
- Target party can submit response/evidence.
- State can review response.
- Notice can be marked complied, overdue, escalated, or closed.

## 21.4 Case Workflow

- Case can be opened from serious finding, unresolved notice, complaint, or incident.
- Case has assigned officer.
- Case tracks corrective actions, evidence, follow-up, and escalation.
- Case can be resolved and closed.

## 21.5 Role-Based Access

- Inspectors see assigned inspections.
- Employers see only their own notices/cases.
- Medical facilities see only their own notices/cases.
- State sees state-scoped inspections and cases.
- Federal sees aggregate oversight unless granted deeper access.

---

# 22. Implementation Chunks for Codex

## Chunk 1: Navigation Consolidation

### Goal

Replace separate inspection/enforcement menus with one parent module.

### Tasks

- Add `Inspections & Enforcement` parent nav item.
- Create parent route.
- Add tabs: Overview, Inspections, Cases, Notices, Reports.
- Remove or redirect old top-level routes.

### Suggested Redirects

```txt
/state/inspections → /state/inspections-enforcement?tab=inspections
/state/enforcement-notices → /state/inspections-enforcement?tab=notices
/state/cases → /state/inspections-enforcement?tab=cases
/state/enforcement → /state/inspections-enforcement
/state/corrective-actions → /state/inspections-enforcement?tab=cases
```

### Acceptance Criteria

- One parent module is visible.
- Old routes redirect correctly.
- Tabs load correctly.
- No duplicate top-level enforcement menus remain.

---

## Chunk 2: Parent Page Shell

### Goal

Create the `Inspections & Enforcement` page shell.

### Tasks

- Create `InspectionsEnforcementPage`.
- Add page header.
- Add tab navigation.
- Add permission-based tab visibility.
- Add shared filters where useful.

### Acceptance Criteria

- Page renders with Overview, Inspections, Cases, Notices, Reports.
- Active tab is URL-controlled.
- Unauthorized tabs/actions are hidden.

---

## Chunk 3: Overview Tab

### Goal

Create a dashboard summary.

### Tasks

- Add KPI cards.
- Add recent inspections list.
- Add open cases list.
- Add overdue notices list.
- Add high-risk findings widget.
- Add quick actions.

### Acceptance Criteria

- Dashboard gives a clear summary of inspections and enforcement.
- Cards link to filtered tabs.
- Empty/loading/error states work.

---

## Chunk 4: Inspections Tab

### Goal

Implement inspection planning and review queue.

### Tasks

- Create inspections table.
- Add filters/status chips.
- Add create inspection flow.
- Add assign inspector action.
- Add assign form template action.
- Link to inspection detail.

### Acceptance Criteria

- State can create inspection.
- Inspector can be assigned.
- Form template can be assigned.
- Inspections are searchable/filterable.

---

## Chunk 5: Inspection Detail Workflow

### Goal

Create a connected inspection workspace.

### Tasks

- Create inspection detail page/drawer.
- Add sections: Summary, Assigned Form, Findings, Evidence, Notices, Linked Case, Follow-up, Audit Log.
- Integrate Forms Tool response renderer.
- Allow findings from submitted inspection forms.
- Allow issue notice/open case from finding.

### Acceptance Criteria

- Inspection detail contains the full inspection workflow.
- Findings can create notices or cases.
- Evidence is linked to inspection.
- Form response is linked to inspection.

---

## Chunk 6: Notices Tab

### Goal

Create the official notices register.

### Tasks

- Create notices table.
- Add notice creation flow.
- Add issue notice action.
- Add notice detail page/drawer.
- Add response/evidence review.
- Add convert/escalate to case.

### Acceptance Criteria

- Notices can be issued and tracked.
- Target party can respond.
- State can review response.
- Notice can be closed or escalated.

---

## Chunk 7: Cases Tab

### Goal

Create case management workflow.

### Tasks

- Create cases table.
- Add case detail page.
- Add case assignment.
- Add corrective action tracking.
- Add evidence review.
- Add follow-up inspection scheduling.
- Add escalation and closure actions.

### Acceptance Criteria

- Cases track full violation lifecycle.
- Corrective actions are inside case detail.
- Escalations are inside case detail.
- Follow-up inspections can be linked.

---

## Chunk 8: Employer and Facility Compliance Views

### Goal

Allow external regulated parties to respond to notices and corrective actions.

### Tasks

- Add Employer Compliance view.
- Add Facility Compliance view.
- Show only own notices/cases.
- Allow acknowledgement.
- Allow corrective evidence upload.
- Show status and due dates.

### Acceptance Criteria

- Employers/facilities can respond to notices.
- They see only their own records.
- They cannot see internal State notes.

---

## Chunk 9: Reports Tab

### Goal

Add inspection and enforcement reporting.

### Tasks

- Add report list/cards.
- Add filters.
- Add export actions.
- Add report summaries.

### Acceptance Criteria

- Users can view inspection/enforcement reports.
- Exports are permission-controlled.
- Reports are state-scoped.

---

## Chunk 10: Permissions, Scope, and Audit

### Goal

Secure the consolidated module.

### Tasks

- Implement permissions.
- Enforce state scope.
- Enforce target-party scope.
- Audit major actions.
- Hide unauthorized actions.

### Acceptance Criteria

- Users only see allowed records.
- Sensitive/internal notes are protected.
- All major actions are audit logged.

---

## Chunk 11: Notifications

### Goal

Add workflow notifications.

### Tasks

- Notify inspectors of assignments.
- Notify employers/facilities of notices.
- Notify State users of submissions and critical findings.
- Notify users of due/overdue actions.

### Acceptance Criteria

- Notifications are sent at key workflow events.
- Notification links open the correct record.

---

## Chunk 12: Final UI QA

### Goal

Confirm the workflow is simple and intuitive.

### QA Checklist

- One module: Inspections & Enforcement.
- No separate top-level Enforcement, Notices, or Cases menus.
- Inspections tab handles inspection planning.
- Inspection detail links findings, notices, and cases.
- Cases tab handles unresolved/serious issues.
- Notices tab acts as official notice register.
- Corrective actions are inside cases/notices.
- Escalations are inside cases.
- Employer/facility views are limited and simple.
- Reports work.
- Permissions work.
- Mobile/responsive layout works.

---

# 23. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Update the FoodCert NG inspection and enforcement UX.

Current problem:
Inspections, Enforcement Notices, Cases, and Enforcement are appearing as separate modules/menu items, which makes the workflow confusing.

Required product change:
Create one consolidated parent module called Inspections & Enforcement.

Use this tab structure:
- Overview
- Inspections
- Cases
- Notices
- Reports

Do not keep separate top-level menu items for:
- Inspections
- Enforcement Notices
- Cases
- Enforcement
- Corrective Actions
- Escalations

Workflow rule:
Inspection creates findings.
Findings can generate notices.
Serious or unresolved findings/notices can open cases.
Cases track corrective actions, evidence, follow-up inspections, escalations, resolution, and closure.
Enforcement is the overall process, not a separate menu.

Inspection Detail should include:
- Summary
- Assigned Form / Checklist from Forms Tool
- Findings
- Evidence
- Notices
- Linked Case
- Follow-up
- Audit Log

Case Detail should include:
- Case Summary
- Violation Details
- Linked Inspection / Source
- Notices
- Corrective Actions
- Evidence
- Follow-up Inspections
- Escalations
- Resolution
- Audit Log

Notice Detail should include:
- Notice summary
- Required action
- Due date
- Target party
- Related inspection/case
- Response/evidence
- Review status

Employer and Medical Facility portals should only show their own compliance notices, corrective actions, and case status. They should not see internal State enforcement notes.

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions and scoping remain the source of truth.
```

---

# 24. MVP Build Order

1. Navigation consolidation
2. Parent page shell
3. Overview tab
4. Inspections tab
5. Inspection detail workflow
6. Notices tab
7. Cases tab
8. Employer/facility compliance views
9. Reports tab
10. Permissions, scope, and audit
11. Notifications
12. Final UI QA
