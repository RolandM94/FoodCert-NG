# PRD: Inspection Settings — Defaults, Templates, Severity Levels, Corrective Action Deadlines & Workflow Rules — FoodCert NG

## 1. Document Purpose

This PRD defines the **Inspection Settings** area for the FoodCert NG platform.

The Inspection Settings area should live inside the State Ministry account configuration, not as a separate operational module.

The key product decision is:

> **Inspection Settings is where the State Ministry configures inspection rules, defaults, templates, severity levels, corrective action timelines, reminder rules, escalation rules, and inspection workflow behaviour. The Inspections & Enforcement module uses these settings to run inspections.**

This PRD should guide Codex implementation for:

```txt
State Ministry
└── Account Settings
    └── Inspection Settings
```

Inspection Settings should support:

```txt
Default Inspection Templates
Inspection Types
Inspection Scheduling Rules
Inspector Assignment Defaults
Severity Levels
Corrective Action Deadlines
Notice Defaults
Case Opening Rules
Follow-up Inspection Rules
Reminder Rules
Escalation Rules
Evidence Requirements
Scoring and Risk Rating Rules
Inspection Closure Rules
Reports and Audit Logs
```

---

# 2. Product Decision

## 2.1 Inspection Settings Should Be in Account Settings

Inspection configuration should not be scattered across the Inspections module, Forms Tool, Enforcement module, or Reports.

The correct placement is:

```txt
State Ministry
└── Account Settings
    └── Inspection Settings
```

The operational inspection workflow should remain in:

```txt
State Ministry
└── Inspections & Enforcement
```

## 2.2 Separation of Configuration and Operations

Use this rule across the platform:

```txt
Account Settings = Configure rules and defaults
Forms Tool = Build inspection form/checklist templates
Inspections & Enforcement = Run inspections and enforcement workflow
Reports = Monitor inspection performance and outcomes
```

## 2.3 Inspection Templates Come from the Forms Tool

Inspection Settings should not contain a full form builder.

The State should create inspection checklist templates in the **Forms Tool**.

Then, inside Inspection Settings, the State selects which published templates are used as default templates for different inspection purposes.

Example:

```txt
Forms Tool
→ Create “Food Business Routine Inspection Checklist v1”
→ Publish Template

Account Settings
→ Inspection Settings
→ Default Inspection Templates
→ Routine Food Business Inspection = Food Business Routine Inspection Checklist v1
```

---

# 3. Core Product Principle

Inspection Settings defines:

```txt
What template is used
What severity levels exist
How quickly issues must be corrected
When reminders are sent
When cases escalate
When follow-up inspections are required
What evidence is mandatory
How inspection risk is calculated
```

The Inspections & Enforcement module uses these settings when creating, assigning, conducting, reviewing, and closing inspections.

---

# 4. Recommended Navigation

## 4.1 State Ministry Sidebar

Use this clean State Ministry navigation:

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

## 4.2 Account Settings Structure

Inside Account Settings:

```txt
Account Settings
├── State Profile
├── Fees & Payments
├── Certificate Settings
├── Medical Facility Settings
├── Inspection Settings
├── Forms Settings
├── Notification Settings
├── Security & Access
└── Audit Logs
```

## 4.3 Inspection Settings Internal Sections

Inside Inspection Settings:

```txt
Inspection Settings
├── Inspection Templates
├── Inspection Types
├── Severity Levels
├── Corrective Action Deadlines
├── Notices & Case Rules
├── Follow-up & Escalation Rules
├── Evidence & Submission Rules
├── Scoring & Risk Rules
├── Reminders & Notifications
└── Audit Logs
```

For a simpler UI, this can be presented as grouped settings cards on one page, with editable drawers/modals for each group.

---

# 5. Relationship with Forms Tool

## 5.1 Forms Tool Responsibility

The Forms Tool is responsible for:

```txt
Creating inspection checklist templates
Adding questions
Adding sections
Adding required fields
Adding skip logic
Adding repeat groups
Adding media upload questions
Adding scoring rules, where applicable
Publishing template versions
Archiving templates
```

## 5.2 Inspection Settings Responsibility

Inspection Settings is responsible for:

```txt
Selecting active default inspection templates
Mapping templates to inspection types
Configuring severity levels
Configuring corrective action deadlines
Configuring enforcement notice rules
Configuring case opening rules
Configuring follow-up inspection rules
Configuring reminders and escalation
```

## 5.3 Inspections & Enforcement Responsibility

Inspections & Enforcement is responsible for:

```txt
Creating inspection assignments
Assigning inspectors
Assigning selected inspection templates
Capturing inspection responses
Generating findings
Issuing notices
Opening cases
Tracking corrective actions
Scheduling follow-up inspections
Closing inspections and cases
```

---

# 6. Inspection Settings Overview Page

The Inspection Settings page should open with an overview of the active inspection configuration.

## 6.1 Overview Cards

Display cards such as:

```txt
Default Routine Inspection Template
Default Complaint Inspection Template
Default Follow-up Inspection Template
Severity Levels Configured
Corrective Action SLA Rules
Auto Case Opening Rules
Reminder Rules Active
Last Updated
```

## 6.2 Quick Actions

```txt
Edit Default Templates
Edit Severity Levels
Edit Corrective Deadlines
Edit Escalation Rules
Preview Inspection Workflow
View Audit Logs
```

## 6.3 State Scope

All inspection settings are state-scoped.

Example:

```txt
Lagos State may use different inspection templates and deadlines from Kano State.
```

Federal Ministry may define national recommended defaults or minimum standards, but State Ministry should manage operational state-specific settings where policy allows.

---

# 7. Default Inspection Templates

## 7.1 Purpose

Default Inspection Templates determine which Forms Tool template is automatically selected when a State user creates an inspection of a particular type.

## 7.2 Template Source

Only published templates from the Forms Tool should be selectable.

Template filter:

```txt
purpose = Inspection Checklist
status = Published
owner = State or Federal/System template available to State
```

## 7.3 Recommended Default Template Mappings

```txt
Routine Food Business Inspection
Complaint-Based Inspection
Follow-up Inspection
Re-inspection
High-Risk Employer Inspection
Branch / Outlet Inspection
Medical Facility Inspection, if applicable
Incident-Triggered Inspection
Training / Awareness Visit Checklist, optional
```

## 7.4 Example Configuration

```txt
Routine Food Business Inspection = Food Business Routine Inspection Checklist v1
Complaint-Based Inspection = Food Business Complaint Inspection Checklist v1
Follow-up Inspection = Follow-up Corrective Action Verification Checklist v1
High-Risk Inspection = High-Risk Food Employer Inspection Checklist v1
```

## 7.5 Rules

- Default templates can be overridden during inspection creation if the user has permission.
- If no default template exists, the user must manually select a published inspection template.
- A template used in previous inspections should not be deleted.
- If a template version is archived, existing inspections remain linked to the old version.
- New inspections should use the currently active configured version.

---

# 8. Inspection Types

## 8.1 Purpose

Inspection Types categorize inspections and determine default templates, priority, SLA, and workflow behaviour.

## 8.2 Recommended Inspection Types

```txt
Routine
Complaint-Based
Follow-up
Re-inspection
High-Risk
Incident-Triggered
Random Spot Check
Accreditation-Related
Certificate Verification Sweep
```

## 8.3 Inspection Type Configuration Fields

```txt
inspection_type_name
description
default_template_id
default_template_version_id
default_priority
requires_scheduled_date
allows_unannounced_visit
requires_employer_notice
requires_branch_selection
requires_gps_capture
requires_photo_evidence
requires_signature
default_due_days
active
```

## 8.4 Example

```txt
Inspection Type: Complaint-Based
Default Template: Complaint Inspection Checklist v1
Priority: High
Requires Scheduled Date: Yes
Allows Unannounced Visit: Yes
Requires Employer Notice: No
Default Due Days: 3 working days
```

---

# 9. Severity Levels

## 9.1 Purpose

Severity levels classify findings and violations discovered during inspections.

They help determine:

```txt
Corrective action deadline
Notice type
Case opening rule
Escalation requirement
Follow-up inspection requirement
Risk rating
```

## 9.2 Recommended Severity Levels

Use a simple and intuitive structure:

```txt
Low
Medium
High
Critical
```

## 9.3 Severity Level Definitions

### Low

Minor non-compliance with limited public health risk.

Example:

```txt
Minor documentation gap
Non-critical hygiene improvement required
Incomplete display of compliance notice
```

### Medium

Moderate non-compliance that requires correction but does not create immediate severe risk.

Example:

```txt
Some food handlers have certificates expiring soon
Incomplete branch record
Minor facility hygiene issue
```

### High

Significant non-compliance with potential health or regulatory risk.

Example:

```txt
Several food handlers without valid certificates
Repeated failure to submit requested compliance information
Poor food handling practice observed
```

### Critical

Severe non-compliance requiring immediate action or escalation.

Example:

```txt
Food handler marked excluded from food handling is found working
Evidence of contamination risk
Employer refuses inspection
Medical facility operating while suspended
```

## 9.4 Severity Configuration Fields

```txt
severity_name
description
default_corrective_action_deadline
deadline_unit
requires_notice
default_notice_type
requires_case
requires_follow_up_inspection
requires_escalation
requires_immediate_action
risk_score_value
active
```

## 9.5 Example Severity Configuration

| Severity | Deadline | Notice Required | Case Required | Follow-up Required | Escalation |
|---|---:|---|---|---|---|
| Low | 30 days | Optional | No | No | No |
| Medium | 14 days | Yes | Optional | Optional | No |
| High | 7 days | Yes | Yes | Yes | Optional |
| Critical | Immediate / 24 hours | Yes | Yes | Yes | Yes |

---

# 10. Corrective Action Deadlines

## 10.1 Purpose

Corrective Action Deadlines define how long a regulated party has to correct an inspection finding.

Corrective action deadlines should be based on:

```txt
Finding severity
Inspection type
Violation category
State policy
Public health risk
```

## 10.2 Default Deadline Rules

Recommended defaults:

```txt
Low = 30 calendar days
Medium = 14 calendar days
High = 7 calendar days
Critical = Immediate or 24 hours
```

State should be able to customize these.

## 10.3 Deadline Units

Support:

```txt
Hours
Calendar Days
Working Days
Immediate
```

## 10.4 Corrective Action Deadline Logic

When an inspector records a finding:

```txt
Finding severity selected
→ System checks severity deadline rule
→ Corrective action due date is calculated
→ Notice includes due date
→ Employer/facility is notified
→ System schedules reminders
```

Example:

```txt
Finding Severity: High
Configured Deadline: 7 calendar days
Finding Date: 1 July 2026
Corrective Action Due Date: 8 July 2026
```

## 10.5 Custom Override

Authorized State users may override a deadline if permitted.

Override should require:

```txt
New deadline
Reason for override
Approver, if required
Audit log
```

---

# 11. Notices and Case Rules

## 11.1 Notice Rules

The platform should be able to determine whether a notice should be issued automatically or manually after inspection findings are submitted.

Recommended Notice Types:

```txt
Warning Notice
Corrective Action Notice
Improvement Notice
Compliance Notice
Suspension Notice
Closure Recommendation
Re-inspection Notice
```

## 11.2 Notice Generation Logic

Possible configuration:

```txt
Low severity → No automatic notice; optional warning
Medium severity → Corrective Action Notice
High severity → Corrective Action Notice + Case
Critical severity → Immediate Compliance Notice + Case + Escalation
```

## 11.3 Case Opening Rules

Cases should not be opened for every minor finding.

Recommended logic:

```txt
Low → No case by default
Medium → Case optional if repeated or unresolved
High → Open case by default
Critical → Open case automatically
```

## 11.4 Case Auto-Open Triggers

```txt
Critical finding recorded
High severity finding recorded
Corrective action overdue
Repeated violation by same employer/branch
Inspector escalates finding
Employer fails to submit corrective evidence
Facility operating while expired/suspended
Food handler excluded but found working
```

## 11.5 Case Linking

A case may link to:

```txt
Inspection
Employer
Branch / Outlet
Food Handler, if applicable
Medical Facility, if applicable
Notice
Corrective Actions
Evidence
Follow-up Inspection
```

---

# 12. Follow-up Inspection Rules

## 12.1 Purpose

Follow-up inspection rules determine when a new follow-up inspection should be required.

## 12.2 Recommended Rules

```txt
Low severity → No follow-up by default
Medium severity → Follow-up optional
High severity → Follow-up required
Critical severity → Follow-up required
Overdue corrective action → Follow-up required
Repeated violation → Follow-up required
```

## 12.3 Follow-up Scheduling Logic

```txt
Inspection submitted
→ Findings reviewed
→ System checks severity and case rules
→ If follow-up required, follow-up inspection recommendation is created
→ State officer schedules follow-up inspection
→ Inspector is assigned
→ Follow-up template is selected
```

## 12.4 Default Follow-up Template

The State should select:

```txt
Default Follow-up Inspection Template
```

from published Forms Tool templates.

---

# 13. Evidence and Submission Rules

## 13.1 Evidence Requirements

Inspection Settings should define whether certain evidence is required.

Recommended settings:

```txt
Require GPS capture
Require inspector signature
Require employer/branch representative signature
Require photo evidence for High findings
Require photo evidence for Critical findings
Require evidence for corrective action closure
Require timestamp on media
Allow offline evidence capture
```

## 13.2 Evidence Rules by Severity

Example:

| Severity | Photo Evidence | GPS | Signature | Corrective Evidence |
|---|---|---|---|---|
| Low | Optional | Optional | Optional | Optional |
| Medium | Optional | Optional | Optional | Required if notice issued |
| High | Required | Required | Optional | Required |
| Critical | Required | Required | Required where feasible | Required |

## 13.3 Offline Inspection Rule

The State can allow or disallow offline inspection completion.

Recommended default:

```txt
Allow Offline Inspection Forms = Yes
```

Important for inspectors working in locations with poor connectivity.

---

# 14. Scoring and Risk Rules

## 14.1 Purpose

Inspection scoring helps determine overall inspection outcome and risk rating.

## 14.2 Scoring Source

Question-level scoring may be configured in the Forms Tool.

Inspection Settings should define how scores are interpreted.

## 14.3 Recommended Inspection Outcomes

```txt
Passed
Passed with Observations
Corrective Action Required
Failed
Critical Failure
```

## 14.4 Risk Ratings

```txt
Low Risk
Medium Risk
High Risk
Critical Risk
```

## 14.5 Score Threshold Example

```txt
90–100 = Passed
75–89 = Passed with Observations
60–74 = Corrective Action Required
Below 60 = Failed
Any Critical Finding = Critical Failure
```

## 14.6 Critical Override Rule

If any critical finding is recorded:

```txt
Inspection Outcome = Critical Failure
Case Required = Yes
Escalation Required = Yes
Follow-up Required = Yes
```

even if the numeric score is high.

---

# 15. Reminders and Notifications

## 15.1 Inspection Assignment Reminders

Notify inspectors when:

```txt
Inspection assigned
Inspection due soon
Inspection overdue
Inspection reassigned
Inspection cancelled
```

## 15.2 Corrective Action Reminders

Notify employer/facility when:

```txt
Notice issued
Corrective action due soon
Corrective action overdue
Correction returned for more information
Correction accepted
```

## 15.3 State Officer Reminders

Notify State reviewers when:

```txt
Inspection response submitted
High/Critical finding submitted
Corrective action overdue
Follow-up required
Case escalation required
```

## 15.4 Reminder Schedule

Recommended configurable rules:

```txt
Inspection due soon reminder: 2 days before due date
Inspection overdue reminder: on due date + 1 day
Corrective action due soon: 3 days before deadline
Corrective action overdue: on deadline + 1 day
Escalate overdue corrective action: 3 days after overdue
```

---

# 16. Escalation Rules

## 16.1 Purpose

Escalation rules define when a matter should be sent to a supervisor, enforcement officer, or higher authority.

## 16.2 Escalation Triggers

```txt
Critical finding recorded
High finding unresolved after deadline
Corrective action overdue
Repeated violation
Employer refuses inspection
Medical facility operates while suspended
Excluded food handler found working
Inspector flags immediate public health risk
```

## 16.3 Escalation Recipients

```txt
State Inspection Supervisor
State Enforcement Officer
State Ministry Admin
Federal Oversight User, aggregate or exceptional cases only
```

## 16.4 Escalation Action

Possible escalation actions:

```txt
Create enforcement case
Notify supervisor
Require follow-up inspection
Issue stronger notice
Suspend facility/employer privilege, if policy allows
Flag in dashboard
```

---

# 17. Inspection Closure Rules

## 17.1 Inspection Statuses

Recommended statuses:

```txt
Draft
Scheduled
Assigned
In Progress
Submitted
Under Review
Returned for Correction
Reviewed
Closed
Cancelled
Overdue
```

## 17.2 Closure Conditions

An inspection can be closed when:

```txt
Inspection form submitted
Required evidence uploaded
Reviewer has reviewed submission
Required notices generated
Required cases opened
Corrective actions created where needed
```

## 17.3 Auto-Close Rule

State may configure auto-close for clean inspections.

Example:

```txt
If no findings and inspection outcome = Passed
→ Auto-close after review
```

Do not auto-close inspections with High or Critical findings until required enforcement workflow is created.

---

# 18. Data Model Requirements

## 18.1 InspectionSettingsPolicy

Suggested fields:

```txt
id
state_id
allow_offline_inspections
default_routine_template_id
default_routine_template_version_id
default_complaint_template_id
default_complaint_template_version_id
default_followup_template_id
default_followup_template_version_id
default_reinspection_template_id
default_reinspection_template_version_id
requires_gps_by_default
requires_inspector_signature
requires_employer_signature
auto_open_case_for_high
auto_open_case_for_critical
auto_require_followup_for_high
auto_require_followup_for_critical
score_thresholds_json
reminder_rules_json
escalation_rules_json
created_by
updated_by
created_at
updated_at
```

## 18.2 InspectionTypeSetting

```txt
id
policy_id
name
description
default_template_id
default_template_version_id
default_priority
requires_scheduled_date
allows_unannounced_visit
requires_employer_notice
requires_branch_selection
requires_gps_capture
requires_photo_evidence
requires_signature
default_due_days
active
created_at
updated_at
```

## 18.3 SeverityLevelSetting

```txt
id
policy_id
name
description
rank
default_deadline_value
default_deadline_unit
requires_notice
default_notice_type
requires_case
requires_follow_up
requires_escalation
requires_immediate_action
risk_score_value
active
created_at
updated_at
```

## 18.4 CorrectiveActionDeadlineRule

```txt
id
policy_id
severity_level_id
inspection_type_id
violation_category
deadline_value
deadline_unit
allow_override
requires_override_reason
active
created_at
updated_at
```

## 18.5 NoticeRuleSetting

```txt
id
policy_id
severity_level_id
notice_type
auto_generate
requires_review_before_send
default_message_template
active
created_at
updated_at
```

## 18.6 EscalationRuleSetting

```txt
id
policy_id
trigger_type
severity_level_id
days_after_due
recipient_role
action_type
active
created_at
updated_at
```

---

# 19. API Requirements

## 19.1 Inspection Settings APIs

```txt
GET    /api/state/account-settings/inspection-settings
PATCH  /api/state/account-settings/inspection-settings
GET    /api/state/account-settings/inspection-settings/templates
PATCH  /api/state/account-settings/inspection-settings/templates
GET    /api/state/account-settings/inspection-settings/audit-logs
```

## 19.2 Inspection Type APIs

```txt
GET    /api/state/account-settings/inspection-settings/types
POST   /api/state/account-settings/inspection-settings/types
PATCH  /api/state/account-settings/inspection-settings/types/:id
DELETE /api/state/account-settings/inspection-settings/types/:id
```

## 19.3 Severity Level APIs

```txt
GET    /api/state/account-settings/inspection-settings/severity-levels
POST   /api/state/account-settings/inspection-settings/severity-levels
PATCH  /api/state/account-settings/inspection-settings/severity-levels/:id
DELETE /api/state/account-settings/inspection-settings/severity-levels/:id
```

## 19.4 Corrective Deadline APIs

```txt
GET   /api/state/account-settings/inspection-settings/corrective-deadlines
POST  /api/state/account-settings/inspection-settings/corrective-deadlines
PATCH /api/state/account-settings/inspection-settings/corrective-deadlines/:id
```

## 19.5 Rule Resolution API

The Inspections & Enforcement module should be able to resolve settings dynamically.

```txt
POST /api/inspections/settings/resolve
```

Example request:

```json
{
  "inspection_type": "routine",
  "severity": "high",
  "violation_category": "certificate_non_compliance",
  "state_id": "state-id"
}
```

Example response:

```json
{
  "default_template_id": "template-id",
  "template_version_id": "version-id",
  "corrective_action_deadline": {
    "value": 7,
    "unit": "calendar_days"
  },
  "requires_notice": true,
  "notice_type": "Corrective Action Notice",
  "requires_case": true,
  "requires_follow_up": true,
  "requires_escalation": false
}
```

---

# 20. Permissions

## 20.1 Inspection Settings Permissions

```txt
inspection_settings.view
inspection_settings.update
inspection_settings.manage_templates
inspection_settings.manage_types
inspection_settings.manage_severity
inspection_settings.manage_deadlines
inspection_settings.manage_notices
inspection_settings.manage_escalations
inspection_settings.view_audit_logs
```

## 20.2 Operational Permissions

```txt
inspection.create
inspection.assign_inspector
inspection.assign_template
inspection.submit
inspection.review
inspection.close

enforcement.notice.create
enforcement.case.create
enforcement.corrective_action.review
```

## 20.3 Permission Rules

- Only authorized State users can update inspection settings.
- Inspectors cannot update inspection settings.
- Employers cannot update inspection settings.
- Medical facilities cannot update inspection settings.
- Federal users may view settings for oversight where permitted, but cannot update state settings unless explicitly authorized.
- Backend remains the source of truth.

---

# 21. UI Requirements

## 21.1 Inspection Settings Page Header

```txt
Inspection Settings
Configure inspection templates, severity levels, corrective action timelines, evidence rules, reminders, and escalation rules for your state.
```

Actions:

```txt
Save Changes
Preview Workflow
View Audit Logs
```

## 21.2 Recommended UI Layout

Use a settings page with grouped cards:

```txt
Inspection Templates
Inspection Types
Severity Levels
Corrective Action Deadlines
Notices & Cases
Follow-up & Escalation
Evidence & Submission Rules
Scoring & Risk Rules
Reminders & Notifications
Audit Logs
```

Each card opens an edit drawer or modal.

## 21.3 Inspection Templates UI

Fields:

```txt
Routine Inspection Template
Complaint Inspection Template
Follow-up Inspection Template
High-Risk Inspection Template
Re-inspection Template
```

Each field should:

```txt
Show selected template name and version
Allow preview
Allow change
Only list published inspection templates from Forms Tool
```

## 21.4 Severity Levels UI

Show table:

```txt
Severity
Description
Default Deadline
Notice Required
Case Required
Follow-up Required
Escalation Required
Actions
```

## 21.5 Corrective Deadlines UI

Show deadline rules by severity and inspection type.

Example:

```txt
Severity: High
Inspection Type: Routine
Deadline: 7 calendar days
Override Allowed: Yes
```

## 21.6 Notices & Cases UI

Allow State to configure:

```txt
Notice type by severity
Auto-generate notice
Requires review before sending
Auto-open case
Case opening triggers
```

## 21.7 Follow-up & Escalation UI

Allow State to configure:

```txt
Follow-up required by severity
Escalation trigger
Escalation recipient role
Escalation timing
```

## 21.8 Evidence & Submission Rules UI

Allow State to configure:

```txt
Require GPS
Require photo evidence
Require inspector signature
Require employer/branch representative signature
Allow offline inspection forms
Require evidence before closure
```

## 21.9 Scoring & Risk UI

Allow State to configure:

```txt
Score thresholds
Risk ratings
Critical override rule
Auto-generate findings from critical answers
```

## 21.10 Reminders UI

Allow State to configure:

```txt
Inspection due soon reminder
Inspection overdue reminder
Corrective action due soon reminder
Corrective action overdue reminder
Escalation timing
```

---

# 22. UI Consolidation Rules

## 22.1 Do Not Scatter Inspection Configuration

Do not place inspection configuration in:

```txt
Inspections & Enforcement
Forms Tool
Reports
Directory
Medical Facilities
```

except where it is used or previewed.

## 22.2 Forms Tool Builds Templates Only

Forms Tool should build inspection forms/checklists, but should not own:

```txt
Corrective deadlines
Severity levels
Notice rules
Case rules
Escalation rules
Inspection closure rules
```

## 22.3 Inspections & Enforcement Runs Workflow

Inspections & Enforcement should consume settings and show operational results.

Example:

```txt
Create Inspection
→ Select Inspection Type
→ System auto-loads default template
→ Assign Inspector
→ Inspector submits form
→ Findings generated
→ Severity determines deadlines/notices/cases/follow-up
```

## 22.4 Account Settings Owns Rules

Inspection Settings is the only place for State users to configure inspection defaults and policy behaviour.

---

# 23. End-to-End Inspection Settings Flow

## 23.1 Setup Flow

```txt
1. State creates inspection template in Forms Tool.
2. State publishes template.
3. State goes to Account Settings → Inspection Settings.
4. State maps published template to inspection type.
5. State configures severity levels.
6. State configures corrective action deadlines.
7. State configures notice and case rules.
8. State configures reminders and escalation.
9. State saves settings.
```

## 23.2 Operational Flow

```txt
1. State creates inspection in Inspections & Enforcement.
2. State selects inspection type.
3. System loads default template from Inspection Settings.
4. State assigns inspector.
5. Inspector receives assignment.
6. Inspector completes inspection form.
7. System calculates score/risk/finding severity.
8. Corrective action deadline is calculated.
9. Notice is generated where required.
10. Case is opened where required.
11. Follow-up inspection is recommended where required.
12. Reminders and escalations are scheduled.
```

---

# 24. Acceptance Criteria

## 24.1 Account Settings

- Inspection Settings appears under State Account Settings.
- Inspection Settings is not a standalone top-level module.
- Only authorized users can edit Inspection Settings.

## 24.2 Template Integration

- State can select default inspection templates from published Forms Tool templates.
- Only templates with purpose `Inspection Checklist` are selectable.
- Selected template version is stored.
- Inspections use selected default template.

## 24.3 Severity Levels

- State can configure severity levels.
- Severity levels include deadlines and workflow rules.
- Findings can reference severity levels.
- Severity determines corrective deadline and enforcement actions.

## 24.4 Corrective Action Deadlines

- Deadline is calculated based on severity and configured rules.
- Deadline can be overridden only by authorized users.
- Override reason is required when configured.
- Deadline is shown on notice and case records.

## 24.5 Notices and Cases

- Notice rules can be configured by severity.
- Case opening rules can be configured by severity and triggers.
- High/Critical cases can auto-open where configured.
- Notices and cases link to inspection findings.

## 24.6 Follow-up and Escalation

- Follow-up inspection is recommended where configured.
- Escalation triggers work.
- Escalation notifications are sent.
- Overdue corrective actions trigger reminders/escalations.

## 24.7 Evidence and Submission

- Evidence rules can be configured.
- Required evidence blocks closure/submission where configured.
- Offline inspections are allowed if enabled.

## 24.8 Audit

- Changes to Inspection Settings are audit logged.
- Template changes, severity changes, deadline changes, and escalation changes are logged.

---

# 25. Implementation Chunks for Codex

## Chunk 1: Inspection Settings Page Shell

### Goal

Create the Inspection Settings page under State Account Settings.

### Tasks

- Add `Inspection Settings` section under Account Settings.
- Create page header and description.
- Add grouped settings cards.
- Add permission-based access.
- Add loading, empty, and error states.

### Acceptance Criteria

- Inspection Settings appears inside Account Settings.
- Page displays grouped configuration cards.
- Unauthorized users cannot access or edit settings.

---

## Chunk 2: Inspection Settings Data Models and APIs

### Goal

Implement backend foundation for inspection settings.

### Tasks

- Create `InspectionSettingsPolicy`.
- Create `InspectionTypeSetting`.
- Create `SeverityLevelSetting`.
- Create `CorrectiveActionDeadlineRule`.
- Create `NoticeRuleSetting`.
- Create `EscalationRuleSetting`.
- Implement CRUD APIs.
- Implement state scoping.
- Add audit logging.

### Acceptance Criteria

- State can store inspection settings.
- Settings are state-scoped.
- Changes are audit logged.
- APIs return active policy.

---

## Chunk 3: Default Inspection Templates Integration

### Goal

Allow State to select default templates from Forms Tool.

### Tasks

- Fetch published templates where purpose is `Inspection Checklist`.
- Add template selection UI.
- Store selected template and version.
- Add template preview.
- Use selected template in inspection creation.

### Acceptance Criteria

- Only published inspection templates are selectable.
- Selected template version is stored.
- Inspection creation auto-loads default template by inspection type.
- User can override template only with permission.

---

## Chunk 4: Inspection Types Configuration

### Goal

Allow State to configure inspection types.

### Tasks

- Add inspection types table.
- Add create/edit inspection type drawer.
- Link inspection type to default template.
- Configure priority and default due days.
- Configure GPS/photo/signature defaults.

### Acceptance Criteria

- State can manage inspection types.
- Inspection types drive default template and settings.
- Inactive inspection types cannot be used for new inspections.

---

## Chunk 5: Severity Levels Configuration

### Goal

Allow State to configure severity levels and their workflow impact.

### Tasks

- Add severity levels table.
- Add create/edit severity drawer.
- Configure deadline, notice, case, follow-up, escalation, and immediate action rules.
- Add severity badges.

### Acceptance Criteria

- Severity levels are configurable.
- Severity determines deadline and enforcement defaults.
- Critical severity can force case/escalation/follow-up.

---

## Chunk 6: Corrective Action Deadlines

### Goal

Implement corrective deadline rules.

### Tasks

- Add deadline rules table.
- Configure deadline by severity, inspection type, and violation category.
- Support hours, working days, calendar days, and immediate.
- Support override permission and override reason.
- Calculate due date from finding date.

### Acceptance Criteria

- Corrective action due date is calculated automatically.
- Rules can vary by severity/type/category.
- Override is controlled and audit logged.

---

## Chunk 7: Notices and Case Rules

### Goal

Implement notice generation and case opening configuration.

### Tasks

- Add notice rules UI.
- Add case rules UI.
- Configure notice type by severity.
- Configure auto-generate and review-before-send.
- Configure auto-open case triggers.
- Link rules to inspection findings.

### Acceptance Criteria

- Notices can be generated from inspection findings.
- Cases can auto-open based on configured rules.
- Notice/case logic follows severity and trigger settings.

---

## Chunk 8: Follow-up, Escalation, and Reminders

### Goal

Implement follow-up, escalation, and reminder rules.

### Tasks

- Add follow-up rules UI.
- Add escalation rules UI.
- Add reminder schedule UI.
- Trigger reminders for inspection due dates and corrective deadlines.
- Trigger escalation for overdue or critical cases.

### Acceptance Criteria

- Follow-up inspection recommendations are generated.
- Reminders are scheduled.
- Escalations notify configured roles.
- Overdue corrective actions escalate where configured.

---

## Chunk 9: Evidence, Offline, and Submission Rules

### Goal

Implement evidence and submission settings.

### Tasks

- Add evidence rules settings.
- Configure GPS/photo/signature requirements.
- Configure offline inspection allowed.
- Enforce evidence requirements during inspection submission/review/closure.

### Acceptance Criteria

- Required evidence rules are enforced.
- Offline inspection availability follows setting.
- Inspection cannot close if required evidence is missing.

---

## Chunk 10: Scoring and Risk Rules

### Goal

Interpret Forms Tool scores using Inspection Settings.

### Tasks

- Add score threshold settings.
- Add risk rating mapping.
- Add critical override rule.
- Apply scoring rules to inspection response.
- Generate inspection outcome.

### Acceptance Criteria

- Inspection outcome is calculated.
- Risk rating is assigned.
- Critical findings override score where configured.

---

## Chunk 11: Inspections & Enforcement Workflow Integration

### Goal

Ensure operational module consumes Inspection Settings.

### Tasks

- Update inspection creation flow to use inspection types and default templates.
- Update finding creation to use severity rules.
- Update corrective actions to use deadline rules.
- Update notice/case creation to use configured rules.
- Update follow-up and escalation recommendations.
- Update closure rules.

### Acceptance Criteria

- Inspection workflow uses state settings.
- Settings are applied consistently across inspection lifecycle.
- Operational users do not configure settings from workflow screens.

---

## Chunk 12: Permissions, Audit, and QA

### Goal

Secure and validate Inspection Settings.

### Tasks

- Implement permissions.
- Add audit log for all changes.
- Add tests for state scoping.
- Add tests for template selection.
- Add tests for severity/deadline resolution.
- Add tests for notice/case triggers.
- Add final UI QA.

### Acceptance Criteria

- Only authorized users can edit settings.
- State users cannot edit other states' settings.
- Settings changes are audit logged.
- Workflow rules pass tests.
- UI is responsive and follows FoodCert NG design system.

---

# 26. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Implement Inspection Settings for FoodCert NG under State Account Settings.

Do not create Inspection Settings as a standalone operational module. It must live under:
State Ministry → Account Settings → Inspection Settings.

Inspection Settings should configure:
- Default Inspection Templates
- Inspection Types
- Severity Levels
- Corrective Action Deadlines
- Notice Rules
- Case Opening Rules
- Follow-up Inspection Rules
- Escalation Rules
- Evidence Requirements
- Offline Inspection Rules
- Scoring and Risk Rules
- Reminder Rules
- Audit Logs

Forms Tool integration:
- Inspection checklist templates are created and published in Forms Tool.
- Inspection Settings only selects published templates where purpose = Inspection Checklist.
- Store selected template and version.
- Inspections & Enforcement consumes selected defaults when creating inspections.

Operational flow:
- State creates inspection.
- User selects inspection type.
- System loads default inspection template.
- State assigns inspector.
- Inspector completes inspection form.
- Findings use severity levels.
- Severity determines corrective deadline, notice, case, follow-up, and escalation rules.

Implement models:
- InspectionSettingsPolicy
- InspectionTypeSetting
- SeverityLevelSetting
- CorrectiveActionDeadlineRule
- NoticeRuleSetting
- EscalationRuleSetting

Implement APIs under:
/api/state/account-settings/inspection-settings

Implement permissions:
- inspection_settings.view
- inspection_settings.update
- inspection_settings.manage_templates
- inspection_settings.manage_types
- inspection_settings.manage_severity
- inspection_settings.manage_deadlines
- inspection_settings.manage_notices
- inspection_settings.manage_escalations
- inspection_settings.view_audit_logs

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions and state scoping remain the source of truth.
```

---

# 27. MVP Build Order

1. Inspection Settings page shell
2. Data models and APIs
3. Default inspection templates integration
4. Inspection types configuration
5. Severity levels configuration
6. Corrective action deadline rules
7. Notice and case rules
8. Follow-up, escalation, and reminders
9. Evidence, offline, and submission rules
10. Scoring and risk rules
11. Inspections & Enforcement workflow integration
12. Permissions, audit, and QA
