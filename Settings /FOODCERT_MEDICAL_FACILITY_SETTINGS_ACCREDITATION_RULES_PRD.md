# PRD: Medical Facility Settings — Accreditation Documents, Validity, Review Timelines & Reminders

## 1. Document Purpose

This PRD defines the **Medical Facility Settings** logic for FoodCert NG, specifically how State Ministries configure:

- Required accreditation documents
- Accreditation and re-accreditation templates
- Accreditation validity period
- Review timelines and service-level expectations
- Reminder and escalation rules
- Expiry, suspension, and renewal behaviour

This PRD also explains how **Medical Facility Settings** connects to the **Forms Tool** and the **Medical Facilities Module**.

The core product decision is:

> **The Forms Tool creates the accreditation data collection templates and required document fields. Medical Facility Settings selects which templates are active and defines the rules, timelines, validity periods, reminders, and expiry behaviour. The Medical Facilities Module consumes these settings during accreditation and re-accreditation workflows.**

---

# 2. Product Decision

## 2.1 Do Not Hardcode Required Accreditation Documents in the Medical Facilities Module

Required accreditation documents should not be hardcoded directly inside the Medical Facilities module.

Instead, the required documents should be configured through a published form template created in the **Forms Tool**.

Example:

```txt
Forms Tool
→ Create Template
→ Purpose: Medical Facility Accreditation
→ Add Required Document Upload Fields
→ Publish Template
```

Then the State Ministry links that template inside:

```txt
State Account Settings
→ Medical Facility Settings
→ Accreditation Templates
→ Active Accreditation Template
```

## 2.2 Medical Facility Settings Owns Rules, Not Form Design

Medical Facility Settings should configure:

```txt
Active Accreditation Template
Active Re-accreditation Template
Accreditation Validity Period
Review Timelines
More Information Correction Window
Re-accreditation Opening Window
Reminder Rules
Escalation Rules
Expiry Behaviour
Suspension Rules
```

The Forms Tool should configure:

```txt
Questions
Sections
Required Document Uploads
Validation Rules
Skip Logic
Repeat Groups
Declarations
Checklist Fields
Evidence Upload Rules
```

## 2.3 Medical Facilities Module Runs the Workflow

The Medical Facilities module should use the active settings to run the actual workflow.

Example:

```txt
Facility applies for accreditation
→ System loads active accreditation template from Medical Facility Settings
→ Facility completes form and uploads required documents
→ Application enters State review queue
→ State reviews application using configured review timelines
→ Approval creates validity period and expiry date
→ System triggers reminders and re-accreditation schedule
```

---

# 3. UI Consolidation Decision

Medical Facility Settings should be located inside the **State Account Settings** module, not as a standalone module.

Recommended State navigation:

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

Inside Medical Facility Settings:

```txt
Medical Facility Settings
├── Accreditation Templates
├── Accreditation Validity
├── Review Timelines
├── Reminder Rules
├── Re-accreditation Rules
├── Suspension & Expiry Rules
└── Audit History
```

Do not create separate top-level menus such as:

```txt
Accreditation Documents
Facility Validity Rules
Accreditation Reminder Settings
Review Timeline Settings
Re-accreditation Settings
```

These are all settings inside **Account Settings → Medical Facility Settings**.

---

# 4. Relationship Between Forms Tool, Medical Facility Settings, and Medical Facilities Module

## 4.1 Responsibilities

| Area | Responsibility |
|---|---|
| Forms Tool | Builds and publishes accreditation/re-accreditation templates |
| Medical Facility Settings | Selects active templates and configures rules/timelines/reminders |
| Medical Facilities Module | Runs accreditation/re-accreditation workflow using the active settings |
| Reports Module | Reports on applications, delays, expiry, renewals, approvals, and rejections |
| Notifications System | Sends reminders, alerts, due notices, and escalations |

## 4.2 System Relationship

```txt
Forms Tool
Creates published templates
        ↓
Account Settings → Medical Facility Settings
Selects active templates and sets policy rules
        ↓
Medical Facilities Module
Uses settings during accreditation/re-accreditation
        ↓
Notifications + Reports
Track reminders, SLA, expiry, and performance
```

---

# 5. Required Accreditation Documents Logic

## 5.1 Recommended Approach

Required documents should be implemented as **required file upload questions** inside a Forms Tool template.

Example template:

```txt
Medical Facility Accreditation Application Form v1
```

Template sections may include:

```txt
Facility Profile
Ownership Details
Operating License
Medical Personnel
Laboratory Capacity
Equipment Inventory
Quality Assurance
Waste Management
Emergency Readiness
Required Document Uploads
Facility Declaration
```

Required document upload fields may include:

```txt
Upload Facility Operating License
Upload CAC Certificate or Registration Evidence
Upload Medical Director License
Upload Laboratory Scientist License
Upload Equipment Inventory
Upload Waste Management Agreement
Upload Quality Assurance SOP
Upload Fire Safety Certificate
Upload Tax Clearance, if required by state policy
Upload Facility Layout, if required
Upload Staff List
Upload Laboratory Equipment Calibration Evidence
```

## 5.2 Document Field Rules

Each document upload question should support:

```txt
Required: Yes / No
Allowed File Types: PDF, JPG, PNG, DOCX, XLSX
Maximum File Size
Minimum Number of Files
Maximum Number of Files
Expiry Date Required: Yes / No
Document Number Required: Yes / No
Issuing Authority Required: Yes / No
Conditional Requirement
Reviewer Comment Enabled
Replacement Upload Enabled
```

## 5.3 Example Required Document Field

```txt
Question Label: Upload Facility Operating License
Question Type: File Upload
Required: Yes
Allowed File Types: PDF, JPG, PNG
Max File Size: 10MB
Expiry Date Required: Yes
Document Number Required: Yes
Visible To: Facility Applicant, State Reviewer
Reviewer Can Mark: Accepted / Rejected / More Information Required
```

## 5.4 Conditional Document Logic

Some documents should only be required under specific conditions.

Example:

```txt
If Facility Type = Laboratory
→ Require Laboratory License
→ Require Laboratory Scientist License
→ Require Equipment Calibration Records
```

Example:

```txt
If Ownership Type = Private
→ Require CAC Certificate
```

Example:

```txt
If Facility provides vaccination services
→ Require Cold Chain Equipment Evidence
```

This conditional logic should be configured in the Forms Tool, not hardcoded in Medical Facility Settings.

---

# 6. Accreditation Template Logic

## 6.1 Template Creation Flow

```txt
State user opens Forms Tool
→ Creates new template
→ Selects Purpose: Medical Facility Accreditation
→ Selects Target Respondent: Medical Facility
→ Selects Module Context: Medical Facilities / Accreditation
→ Adds sections, questions, required documents, skip logic, and declarations
→ Previews template
→ Publishes template
```

## 6.2 Linking Template to Medical Facility Settings

```txt
State user opens Account Settings
→ Opens Medical Facility Settings
→ Opens Accreditation Templates
→ Selects active published accreditation template
→ Selects active published re-accreditation template
→ Saves settings
```

## 6.3 Active Template Rules

- Only published templates can be selected.
- Draft templates cannot be used for live applications.
- Archived templates cannot be selected for new applications.
- Active template should store both template ID and template version ID.
- New applications should always use the active version at the time the application starts.
- Existing applications should remain linked to the version they started with.

Example:

```txt
Facility A starts application using Accreditation Template v1
State later publishes Accreditation Template v2
Facility A application remains on v1
New applications use v2
```

---

# 7. Accreditation Validity Period Logic

## 7.1 Purpose

The validity period determines how long a medical facility remains accredited after approval.

## 7.2 Recommended Setting Location

```txt
Account Settings
→ Medical Facility Settings
→ Accreditation Validity
```

## 7.3 Validity Options

The State Ministry should be able to configure:

```txt
6 months
12 months
24 months
Custom number of days/months/years
```

Recommended default:

```txt
12 months
```

## 7.4 Validity Calculation

```txt
Accreditation Start Date = Approval Date
Accreditation Expiry Date = Approval Date + Validity Period
```

Example:

```txt
Approval Date: 10 June 2026
Validity Period: 12 months
Expiry Date: 9 June 2027
```

## 7.5 Status Logic Based on Validity

| Condition | Facility Accreditation Status |
|---|---|
| Application not submitted | Not Accredited |
| Application submitted | Pending Accreditation |
| Application under review | Under Review |
| Application approved and not expired | Accredited |
| Within renewal reminder window | Re-accreditation Due |
| Past expiry date | Expired |
| Suspended by State | Suspended |
| Application rejected | Rejected / Not Accredited |

## 7.6 Facility Assessment Permission Logic

State should configure whether an expired or suspended facility can conduct assessments.

Recommended default:

```txt
Expired Facility Can Conduct Assessments: No
Suspended Facility Can Conduct Assessments: No
```

If accreditation expires:

```txt
Facility status = Expired
Facility assessment creation = Disabled
Facility appears in State expired facilities report
Facility receives expiry notification
State users see facility in Facilities tab with Expired status
```

---

# 8. Review Timeline Logic

## 8.1 Purpose

Review timelines define the expected SLA for State Ministry review of accreditation applications.

## 8.2 Recommended Setting Location

```txt
Account Settings
→ Medical Facility Settings
→ Review Timelines
```

## 8.3 Timeline Settings

Recommended settings:

```txt
Initial Review SLA
More Information Correction Window
Resubmission Review SLA
Final Decision SLA
Application Expiry Window
Escalation Threshold
```

Example default values:

```txt
Initial Review SLA: 14 working days
More Information Correction Window: 7 calendar days
Resubmission Review SLA: 7 working days
Final Decision SLA: 3 working days
Application Expiry Window: 30 calendar days after no response
Escalation Threshold: 2 days after SLA breach
```

## 8.4 Working Days vs Calendar Days

The State should be able to select:

```txt
Working Days
Calendar Days
```

For review SLAs, recommended default:

```txt
Working Days
```

For correction windows and expiry windows, recommended default:

```txt
Calendar Days
```

## 8.5 Review Timeline Flow

```txt
Facility submits application
→ Submitted date is recorded
→ Review due date is calculated using State SLA
→ Application appears in Accreditation queue
→ Reviewer is assigned
→ Reviewer starts review
→ Status changes to Under Review
→ Reviewer approves, rejects, or requests more information
```

If no action happens before review due date:

```txt
Application becomes Overdue
→ Reminder is sent to assigned reviewer
→ Escalation is sent to supervisor according to escalation rules
```

## 8.6 More Information Flow

```txt
Reviewer requests more information
→ Application status becomes More Information Required
→ Facility receives notification
→ Correction due date is calculated
→ Facility updates form/documents
→ Facility resubmits
→ Resubmission review SLA starts
```

If facility does not respond before correction due date:

```txt
Reminder is sent
→ Application becomes Correction Overdue
→ State reviewer may close, reject, or extend deadline
```

---

# 9. Reminder Rules Logic

## 9.1 Reminder Categories

Medical Facility Settings should support four reminder categories:

```txt
Application Review Reminders
Facility Correction Reminders
Accreditation Expiry Reminders
Re-accreditation Reminders
```

## 9.2 Application Review Reminders

These are sent to State reviewers and supervisors.

Recommended defaults:

```txt
Notify reviewer immediately when application is submitted
Reminder after 3 working days if not opened
Reminder 2 working days before review due date
Escalate to supervisor when review SLA is breached
Escalate again after 5 working days overdue
```

## 9.3 Facility Correction Reminders

These are sent to facilities when more information is requested.

Recommended defaults:

```txt
Notify facility immediately when more information is requested
Reminder 3 days before correction due date
Reminder on correction due date
Notify State reviewer when correction is overdue
```

## 9.4 Accreditation Expiry Reminders

These are sent to facilities and State users before accreditation expires.

Recommended defaults:

```txt
90 days before expiry
60 days before expiry
30 days before expiry
14 days before expiry
7 days before expiry
On expiry date
```

## 9.5 Re-accreditation Reminders

These reminders encourage facilities to start renewal before expiry.

Recommended defaults:

```txt
Open re-accreditation window 60 days before expiry
Notify facility when renewal window opens
Notify State when high-volume facilities are close to expiry
Reminder every 15 days until renewal is submitted or facility expires
```

## 9.6 Reminder Channels

Support channels:

```txt
In-app notification
Email
SMS, optional
WhatsApp, optional future phase
```

## 9.7 Reminder Configuration UI

The UI should allow State users to configure:

```txt
Reminder name
Trigger event
Offset before/after event
Recipient type
Notification channel
Escalation recipient
Enabled/Disabled
```

Example:

```txt
Reminder: Accreditation expiry warning
Trigger: Accreditation expiry date
Offset: 30 days before
Recipient: Facility Admin
Channel: Email + In-app
Status: Enabled
```

---

# 10. Re-accreditation Rules

## 10.1 Product Rule

Re-accreditation should not be a separate module. It is an application type under Accreditation.

## 10.2 Recommended Setting Location

```txt
Account Settings
→ Medical Facility Settings
→ Re-accreditation Rules
```

## 10.3 Re-accreditation Settings

State should configure:

```txt
Active Re-accreditation Template
Re-accreditation Opens X Days Before Expiry
Grace Period After Expiry
Allow Renewal After Expiry
Allow Suspended Facility to Apply for Renewal
Auto-disable Assessments on Expiry
Auto-change Facility Status to Expired
```

Recommended defaults:

```txt
Re-accreditation Opens: 60 days before expiry
Grace Period: 0 days
Allow Renewal After Expiry: Yes, but facility cannot conduct assessments while expired
Allow Suspended Facility to Apply: No, unless suspension lifted
Auto-disable Assessments on Expiry: Yes
Auto-change Facility Status to Expired: Yes
```

## 10.4 Re-accreditation Flow

```txt
Facility is accredited
→ System tracks expiry date
→ Renewal window opens based on setting
→ Facility receives reminder
→ Facility starts re-accreditation application
→ System loads active re-accreditation template
→ Facility submits updated documents/data
→ State reviews using configured review timelines
→ If approved, new validity period is applied
→ If rejected, current or expired status remains based on expiry date
```

---

# 11. Suspension & Expiry Rules

## 11.1 Purpose

This section controls what happens when a facility is suspended or accreditation expires.

## 11.2 Recommended Settings

```txt
Auto-expire facility on expiry date
Disable assessments when expired
Disable assessments when suspended
Allow facility to view past assessments while suspended
Allow facility to submit re-accreditation while expired
Allow facility to submit re-accreditation while suspended
Require State approval to reactivate
Require re-inspection before reactivation
```

## 11.3 Recommended Defaults

```txt
Auto-expire facility on expiry date: Yes
Disable assessments when expired: Yes
Disable assessments when suspended: Yes
Allow facility to view past assessments while suspended: Yes
Allow facility to submit re-accreditation while expired: Yes
Allow facility to submit re-accreditation while suspended: No
Require State approval to reactivate: Yes
Require re-inspection before reactivation: Configurable
```

---

# 12. Recommended UI Structure

## 12.1 Medical Facility Settings Page

```txt
Account Settings → Medical Facility Settings
```

Page header:

```txt
Medical Facility Settings
Configure accreditation templates, validity periods, review timelines, reminders, and expiry rules for medical facilities in your state.
```

Tabs or sections:

```txt
Accreditation Templates
Accreditation Validity
Review Timelines
Reminder Rules
Re-accreditation Rules
Suspension & Expiry Rules
Audit History
```

## 12.2 Accreditation Templates Section

Fields:

```txt
Active Accreditation Template
Active Accreditation Template Version
Active Re-accreditation Template
Active Re-accreditation Template Version
Preview Template
Change Template
```

Actions:

```txt
Select Template
Preview Template
Open in Forms Tool
Save Changes
```

Validation:

```txt
Only published templates can be selected
Template purpose must match Medical Facility Accreditation or Re-accreditation
Template target respondent must include Medical Facility
```

## 12.3 Accreditation Validity Section

Fields:

```txt
Validity Period Value
Validity Period Unit
Accreditation Start Date Rule
Expiry Behaviour
```

Options:

```txt
Validity Period Unit: Days / Months / Years
Start Date Rule: Approval Date / Custom Effective Date
```

## 12.4 Review Timelines Section

Fields:

```txt
Initial Review SLA
SLA Type: Working Days / Calendar Days
More Information Correction Window
Resubmission Review SLA
Final Decision SLA
Application Auto-close Window
Escalation Threshold
```

## 12.5 Reminder Rules Section

Display reminder rules in a table:

```txt
Reminder Name
Trigger
Offset
Recipient
Channel
Status
Actions
```

Actions:

```txt
Add Reminder Rule
Edit Rule
Disable Rule
Preview Notification
```

## 12.6 Re-accreditation Rules Section

Fields:

```txt
Re-accreditation Opens Days Before Expiry
Grace Period After Expiry
Allow Renewal After Expiry
Allow Suspended Facility to Apply
Auto-disable Assessments on Expiry
```

## 12.7 Suspension & Expiry Rules Section

Fields:

```txt
Auto-expire Facility
Disable Assessments When Expired
Disable Assessments When Suspended
Require State Approval to Reactivate
Require Re-inspection Before Reactivation
```

## 12.8 Audit History Section

Show:

```txt
Setting Changed
Changed By
Old Value
New Value
Date/Time
Reason, if provided
```

---

# 13. Data Model Requirements

## 13.1 MedicalFacilityAccreditationPolicy

Suggested fields:

```txt
id
state_id
active_accreditation_template_id
active_accreditation_template_version_id
active_reaccreditation_template_id
active_reaccreditation_template_version_id
validity_period_value
validity_period_unit
accreditation_start_date_rule
initial_review_sla_value
initial_review_sla_unit
initial_review_sla_type
more_info_correction_window_value
more_info_correction_window_unit
resubmission_review_sla_value
resubmission_review_sla_unit
final_decision_sla_value
final_decision_sla_unit
application_auto_close_window_value
application_auto_close_window_unit
reaccreditation_open_days_before_expiry
grace_period_days
auto_expire_facility
auto_disable_assessments_on_expiry
auto_disable_assessments_on_suspension
allow_renewal_after_expiry
allow_suspended_facility_reaccreditation
require_state_approval_to_reactivate
require_reinspection_before_reactivation
reminder_rules_json
escalation_rules_json
is_active
created_by
updated_by
created_at
updated_at
```

## 13.2 MedicalFacilityAccreditationApplication

Suggested fields impacted by this policy:

```txt
id
facility_id
state_id
application_type
form_template_id
form_template_version_id
form_response_id
status
submitted_at
review_due_at
correction_due_at
resubmission_review_due_at
assigned_reviewer_id
review_started_at
reviewed_at
decision
approval_date
expiry_date
policy_snapshot_json
created_at
updated_at
```

## 13.3 AccreditationReminderJob

Suggested fields:

```txt
id
state_id
facility_id
application_id
policy_id
reminder_type
trigger_date
recipient_type
recipient_id
channel
status
sent_at
error_message
created_at
updated_at
```

## 13.4 AccreditationPolicyAuditLog

Suggested fields:

```txt
id
policy_id
actor_id
action
field_name
old_value
new_value
reason
created_at
ip_address
user_agent
```

---

# 14. API Requirements

## 14.1 Medical Facility Settings APIs

```txt
GET    /api/state/settings/medical-facility
PATCH  /api/state/settings/medical-facility
GET    /api/state/settings/medical-facility/audit-logs
```

## 14.2 Template Selection APIs

```txt
GET /api/forms/templates?purpose=medical_facility_accreditation&status=published
GET /api/forms/templates?purpose=medical_facility_reaccreditation&status=published
GET /api/forms/templates/:id/preview
```

## 14.3 Application Workflow APIs

```txt
POST /api/facilities/accreditation/applications
GET  /api/facilities/accreditation/applications/:id
POST /api/facilities/accreditation/applications/:id/submit
POST /api/facilities/accreditation/applications/:id/request-more-info
POST /api/facilities/accreditation/applications/:id/resubmit
POST /api/facilities/accreditation/applications/:id/approve
POST /api/facilities/accreditation/applications/:id/reject
```

## 14.4 Reminder APIs

```txt
GET  /api/state/settings/medical-facility/reminder-rules
POST /api/state/settings/medical-facility/reminder-rules
PATCH /api/state/settings/medical-facility/reminder-rules/:id
POST /api/state/settings/medical-facility/reminder-rules/:id/test
```

---

# 15. Permissions

## 15.1 Settings Permissions

```txt
state.medical_facility_settings.view
state.medical_facility_settings.update
state.medical_facility_settings.audit.view
```

## 15.2 Template Permissions

```txt
forms.template.view
forms.template.create
forms.template.publish
```

## 15.3 Accreditation Workflow Permissions

```txt
medical_facility.accreditation.view
medical_facility.accreditation.apply
medical_facility.accreditation.review
medical_facility.accreditation.approve
medical_facility.accreditation.reject
medical_facility.accreditation.request_more_info
```

## 15.4 Access Rules

- Only authorized State users can update Medical Facility Settings.
- Medical facilities cannot change State accreditation rules.
- Medical facilities can only complete forms assigned to their facility/application.
- State reviewers can only review applications within their state.
- Federal users may view settings for oversight if permitted, but should not edit state settings unless granted special authority.
- All settings changes must be audit logged.

---

# 16. End-to-End Flow

## 16.1 State Setup Flow

```txt
1. State creates accreditation template in Forms Tool.
2. State publishes template.
3. State opens Account Settings → Medical Facility Settings.
4. State selects active accreditation template.
5. State selects active re-accreditation template.
6. State sets validity period.
7. State sets review timelines.
8. State sets reminder and escalation rules.
9. State saves settings.
10. Settings become active for new applications.
```

## 16.2 New Accreditation Flow

```txt
1. Medical facility starts accreditation application.
2. System loads active accreditation template from State settings.
3. Facility completes form and uploads required documents.
4. Required document validation runs.
5. Facility submits application.
6. System stores policy snapshot on the application.
7. System calculates review due date.
8. Reviewer receives notification.
9. Reviewer approves, rejects, or requests more information.
10. If approved, facility becomes accredited.
11. System calculates expiry date.
12. System schedules renewal and expiry reminders.
```

## 16.3 Re-accreditation Flow

```txt
1. Facility is accredited.
2. System monitors expiry date.
3. Re-accreditation window opens based on State settings.
4. Facility receives renewal reminder.
5. Facility starts re-accreditation application.
6. System loads active re-accreditation template.
7. Facility submits updated documents.
8. State reviews application.
9. If approved, new validity period is applied.
10. If not approved before expiry, facility becomes expired according to settings.
```

## 16.4 More Information Flow

```txt
1. Reviewer identifies incomplete or invalid document.
2. Reviewer selects Request More Information.
3. Reviewer adds comments against specific fields/documents.
4. Application status becomes More Information Required.
5. Facility receives notification.
6. Correction due date is calculated.
7. Facility updates form response/documents.
8. Facility resubmits.
9. Resubmission review SLA starts.
```

---

# 17. Acceptance Criteria

## 17.1 Medical Facility Settings

- State users can open Account Settings → Medical Facility Settings.
- State users can select active accreditation and re-accreditation templates.
- Only published and valid-purpose templates can be selected.
- State users can set validity period.
- State users can set review timelines.
- State users can set reminder rules.
- State users can set re-accreditation rules.
- State users can set suspension/expiry rules.
- All setting changes are audit logged.

## 17.2 Forms Tool Integration

- Accreditation documents are defined as required document upload fields in Forms Tool templates.
- Medical Facility Settings links to published templates.
- Medical Facilities Module loads the active template for new applications.
- Existing applications remain linked to the template version they started with.

## 17.3 Accreditation Workflow

- Facility application uses active template.
- Required document validation blocks incomplete submissions.
- Review due date is calculated from State settings.
- More Information correction due date is calculated from State settings.
- Approval calculates expiry date from validity settings.
- Renewal window opens according to re-accreditation settings.

## 17.4 Reminder Logic

- Application review reminders are sent.
- Facility correction reminders are sent.
- Expiry reminders are sent.
- Re-accreditation reminders are sent.
- Escalation notifications are sent when SLA is breached.

## 17.5 UI Consolidation

- Required documents are not a separate standalone module.
- Validity settings are not a separate standalone module.
- Reminder settings are not a separate standalone module.
- All are consolidated under Account Settings → Medical Facility Settings.
- Accreditation workflow remains inside Medical Facilities module.
- Template creation remains inside Forms Tool.

---

# 18. Implementation Chunks for Codex

## Chunk 1: Account Settings Navigation Update

### Goal

Add Medical Facility Settings under State Account Settings.

### Tasks

- Add Account Settings parent module if not already present.
- Add Medical Facility Settings section.
- Add tabs/sections:
  - Accreditation Templates
  - Accreditation Validity
  - Review Timelines
  - Reminder Rules
  - Re-accreditation Rules
  - Suspension & Expiry Rules
  - Audit History
- Add permission-based access.

### Acceptance Criteria

- State users can access Medical Facility Settings from Account Settings.
- Medical Facility Settings is not a standalone sidebar module.
- Unauthorized users cannot access settings.

---

## Chunk 2: MedicalFacilityAccreditationPolicy Model and API

### Goal

Create backend policy model for state-level facility accreditation rules.

### Tasks

- Implement `MedicalFacilityAccreditationPolicy`.
- Add fields for active templates, validity, review SLAs, reminders, re-accreditation, suspension, and expiry rules.
- Add GET/PATCH APIs.
- Add policy validation.
- Add audit logging.

### Acceptance Criteria

- State policy can be created and updated.
- Only one active policy per state exists.
- Policy updates are audited.
- API enforces permissions.

---

## Chunk 3: Accreditation Template Selection

### Goal

Allow State users to select active templates from Forms Tool.

### Tasks

- Fetch published templates by purpose.
- Filter templates by purpose and target respondent.
- Add template preview.
- Save selected template ID and version ID to policy.
- Prevent draft/archived templates from being selected.

### Acceptance Criteria

- State can select active accreditation template.
- State can select active re-accreditation template.
- Only valid published templates appear.
- Template preview works.

---

## Chunk 4: Validity Period Settings

### Goal

Implement accreditation validity configuration.

### Tasks

- Add validity period fields.
- Add unit selection.
- Add accreditation start date rule.
- Add expiry behaviour settings.
- Validate positive duration.

### Acceptance Criteria

- State can set validity period.
- Approval flow calculates expiry date correctly.
- Facility status changes to expired when applicable.

---

## Chunk 5: Review Timeline Settings

### Goal

Implement application SLA and review timeline settings.

### Tasks

- Add initial review SLA.
- Add SLA type: working days/calendar days.
- Add correction window.
- Add resubmission review SLA.
- Add final decision SLA.
- Add application auto-close window.
- Add escalation threshold.

### Acceptance Criteria

- Review due dates are calculated from policy.
- Correction due dates are calculated from policy.
- Overdue status works.
- Escalation threshold is stored.

---

## Chunk 6: Reminder Rules UI and Scheduler

### Goal

Implement configurable reminder rules.

### Tasks

- Add reminder rules table.
- Add create/edit/disable rule modal.
- Add trigger event options.
- Add offset options.
- Add recipient type options.
- Add notification channel options.
- Add scheduler integration.
- Add test reminder action.

### Acceptance Criteria

- State can configure reminder rules.
- Application review reminders are scheduled.
- Correction reminders are scheduled.
- Expiry reminders are scheduled.
- Re-accreditation reminders are scheduled.

---

## Chunk 7: Re-accreditation Rules

### Goal

Implement renewal policy settings.

### Tasks

- Add re-accreditation opening window.
- Add grace period.
- Add allow renewal after expiry setting.
- Add allow suspended facility renewal setting.
- Add auto-disable assessment setting.

### Acceptance Criteria

- Renewal window opens based on settings.
- Facility can start renewal when eligible.
- Expired/suspended rules are enforced.

---

## Chunk 8: Suspension & Expiry Rules

### Goal

Implement rules that control facility behaviour when expired or suspended.

### Tasks

- Add auto-expire rule.
- Add disable assessments when expired.
- Add disable assessments when suspended.
- Add reactivation approval rule.
- Add re-inspection before reactivation rule.
- Enforce in assessment workflow.

### Acceptance Criteria

- Expired facilities cannot create assessments if disabled.
- Suspended facilities cannot create assessments if disabled.
- Reactivation follows configured rules.

---

## Chunk 9: Accreditation Application Integration

### Goal

Make facility applications consume the active policy.

### Tasks

- On application start, load active state policy.
- Attach active template version to application.
- Render form response from template.
- Store policy snapshot on submission.
- Calculate review due date.
- Validate required documents through Forms Tool schema.

### Acceptance Criteria

- New applications use active template.
- Required documents block incomplete submission.
- Application stores template version and policy snapshot.
- Review due date is calculated correctly.

---

## Chunk 10: Approval, Expiry, and Reminder Integration

### Goal

Apply policy after approval.

### Tasks

- On approval, calculate start and expiry date.
- Update facility accreditation status.
- Schedule expiry reminders.
- Schedule renewal window.
- Apply auto-expiry job.
- Disable assessments if expired/suspended according to settings.

### Acceptance Criteria

- Approved facility receives expiry date.
- Expiry reminders are scheduled.
- Re-accreditation window opens correctly.
- Expired facility status updates automatically.

---

## Chunk 11: More Information / Resubmission Flow

### Goal

Use configured correction timelines.

### Tasks

- Add reviewer field-level comments.
- Allow reviewer to request more information.
- Calculate correction due date.
- Notify facility.
- Allow facility to update response/documents.
- Calculate resubmission review due date.

### Acceptance Criteria

- More Information Required status works.
- Facility can resubmit.
- Timelines and reminders work.
- Reviewer comments are visible to facility.

---

## Chunk 12: Audit Logs and History

### Goal

Track all setting changes and accreditation policy actions.

### Tasks

- Add policy audit log.
- Show audit history tab.
- Capture old/new values.
- Capture actor, date, IP, user agent.
- Audit template changes, validity changes, timeline changes, reminder changes.

### Acceptance Criteria

- Settings history is visible.
- All policy changes are traceable.
- Unauthorized users cannot view audit logs.

---

## Chunk 13: Permissions and Tests

### Goal

Secure settings and workflow.

### Tasks

- Implement permissions.
- Add API tests.
- Add UI permission tests.
- Add policy calculation tests.
- Add reminder scheduling tests.
- Add accreditation workflow tests.

### Acceptance Criteria

- Only authorized users can update settings.
- Policy calculations are correct.
- Template filtering works.
- Reminder rules work.
- Expiry behaviour works.

---

## Chunk 14: Final UI QA

### Goal

Confirm UI consolidation and workflow usability.

### QA Checklist

- Medical Facility Settings is under Account Settings.
- Required documents are managed through Forms Tool templates.
- Active templates are selected in Medical Facility Settings.
- Validity period is configurable.
- Review timelines are configurable.
- Reminders are configurable.
- Re-accreditation rules are configurable.
- Suspension/expiry rules are configurable.
- Medical Facilities module consumes these settings.
- No duplicate settings pages exist.

---

# 19. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Implement Medical Facility Settings under State Account Settings for FoodCert NG.

The goal is to consolidate accreditation document requirements, validity periods, review timelines, reminders, re-accreditation rules, and suspension/expiry rules under:

State Account Settings → Medical Facility Settings

Do not hardcode required accreditation documents inside the Medical Facilities module.
Required accreditation documents must be defined as required document upload fields inside Forms Tool templates.

Forms Tool responsibilities:
- Create accreditation and re-accreditation templates
- Add required document upload fields
- Add validation, skip logic, repeat groups, declarations, and evidence rules
- Publish template versions

Medical Facility Settings responsibilities:
- Select active accreditation template
- Select active re-accreditation template
- Set accreditation validity period
- Set review timelines and SLAs
- Set reminder and escalation rules
- Set re-accreditation opening window
- Set grace period and expiry behaviour
- Set suspension rules

Medical Facilities Module responsibilities:
- Load active template when facility starts accreditation/re-accreditation
- Validate required documents through the Forms Tool schema
- Store template version and policy snapshot on application
- Calculate review due dates
- Handle review, approval, rejection, and more information requests
- Calculate expiry date on approval
- Schedule expiry and renewal reminders
- Enforce expired/suspended facility rules

Build UI sections:
- Accreditation Templates
- Accreditation Validity
- Review Timelines
- Reminder Rules
- Re-accreditation Rules
- Suspension & Expiry Rules
- Audit History

Implement backend model:
MedicalFacilityAccreditationPolicy

Implement policy audit logs and permissions:
- state.medical_facility_settings.view
- state.medical_facility_settings.update
- state.medical_facility_settings.audit.view

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions and scoping remain the source of truth.
```

---

# 20. MVP Build Order

1. Account Settings navigation update
2. MedicalFacilityAccreditationPolicy model and API
3. Accreditation template selection
4. Validity period settings
5. Review timeline settings
6. Reminder rules UI and scheduler
7. Re-accreditation rules
8. Suspension and expiry rules
9. Accreditation application integration
10. Approval, expiry, and reminder integration
11. More information/resubmission flow
12. Audit logs and history
13. Permissions and tests
14. Final UI QA
