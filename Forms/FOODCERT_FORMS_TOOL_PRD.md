# PRD: Forms Tool, Form Templates, Assignments & Module-Based Responses — FoodCert NG

## 1. Document Purpose

This PRD defines the **Forms Tool** for FoodCert NG.

The Forms Tool is the platform-wide engine for creating, managing, assigning, responding to, tracking, and reporting on forms and data collection templates.

The core product decision is:

> **Forms Tool creates and manages form templates and assignments. Operational modules consume assigned forms in the correct workflow context.**

This means the State Ministry can create form templates for inspections, employer data collection, medical facility reporting, accreditation checklists, compliance assessments, incident reports, and other data collection needs. Once assigned, the form should appear inside the relevant module for the assigned user to respond.

Example inspection flow:

```txt
State creates Inspection Template
→ State creates Inspection Assignment
→ State assigns Inspector and selects Inspection Template
→ Inspector opens Inspections module
→ Inspector sees assigned inspection form
→ Inspector completes form during inspection
→ Form response is linked to the Inspection record
→ State reviews the inspection response from Inspections and Forms Tool
```

Example employer data collection flow:

```txt
State creates Employer Data Collection Form
→ State assigns it to selected Employers
→ Employer users receive notification
→ Employer opens Assigned Forms or the relevant Employer module
→ Employer completes and submits response
→ State tracks response status and exports submissions
```

---

## 2. Product Decision

### 2.1 Forms Tool Is a Central Template and Assignment Engine

The Forms Tool should manage:

```txt
Form Templates
Form Versions
Form Purposes
Form Assignments
Recipients
Submission Rules
Response Tracking
Exports
Reports
Audit Logs
```

### 2.2 Operational Modules Consume Forms

Operational modules should not each build their own separate form builder.

They should consume forms assigned from the Forms Tool.

Examples:

```txt
Inspections Module consumes Inspection Checklist templates
Medical Facilities Module consumes Facility Reporting / Accreditation Checklist templates
Employer Portal consumes Employer Data Collection templates
Food Handler Portal consumes Food Handler Survey / Declaration templates where applicable
Reports Module consumes submitted response data
```

### 2.3 Assigned Forms Must Appear Where the User Works

Once a form is assigned, the respondent should not have to search inside the Forms Tool if the form belongs to a specific workflow.

The assigned form should appear inside the relevant module.

Examples:

```txt
Inspection form → appears in assigned Inspection record
Employer data form → appears in Employer portal Assigned Forms / Compliance section
Medical facility monthly form → appears in Medical Facility portal Assigned Forms / Reports section
Accreditation checklist → appears in Accreditation review workflow
Incident form → appears in Incident / Compliance / Inspection workflow
```

---

## 3. Core Product Principle

The Forms Tool should separate **form management** from **workflow execution**.

### 3.1 Form Management

Handled by Forms Tool:

```txt
Create template
Edit template
Publish template
Version template
Assign template
Set recipients
Set due date
Track responses
Export responses
View submissions
Archive template
```

### 3.2 Workflow Context

Handled by operational modules:

```txt
Why the form is being used
Who should respond
Which record the response belongs to
Where the response appears
What action happens after submission
```

Example:

```txt
Template = Inspection Checklist
Assignment Context = Inspection Record
Respondent = Inspector
Response Location = Inspection Module
Review Location = State Inspection Review + Forms Responses
```

---

## 4. Users and Actors

### 4.1 State Ministry Users

State Ministry users should be able to:

- Create form templates.
- Configure form purpose.
- Publish form templates.
- Version form templates.
- Assign forms to inspectors, employers, medical facilities, food handlers, or groups.
- Attach forms to operational records such as inspections or accreditation reviews.
- Track submissions.
- Review responses.
- Return submissions for correction.
- Export response data.
- Create reports from submitted forms.

### 4.2 Inspectors

Inspectors should be able to:

- View assigned inspection forms.
- Complete inspection templates/checklists during inspection.
- Save drafts where allowed.
- Upload evidence where required.
- Submit completed inspection responses.
- View submitted inspection forms.

### 4.3 Employers / Food Businesses

Employer users should be able to:

- View assigned forms from the State Ministry.
- Complete employer data collection forms.
- Complete compliance self-assessment forms.
- Complete branch/outlet-specific forms where assigned.
- Save drafts where allowed.
- Submit responses.
- View submitted forms.
- Respond to returned forms where more information is required.

### 4.4 Medical Facilities

Medical facility users should be able to:

- View assigned forms from State Ministry.
- Complete facility data collection forms.
- Complete monthly/periodic reporting forms.
- Complete accreditation-related forms where applicable.
- Submit responses.
- View submitted forms.
- Respond to returned forms.

### 4.5 Food Handlers

Food handlers may receive forms where needed, such as:

- Surveys.
- Self-declaration updates.
- Training feedback.
- Complaint/feedback forms.
- Follow-up forms.

Food handler forms should be simple, mobile-friendly, and privacy-aware.

### 4.6 Federal Ministry Users

Federal Ministry users should be able to:

- View national form templates where permitted.
- Create national-level templates where policy allows.
- View aggregate responses across states.
- Export national-level reports.
- Monitor adoption and response rates.

Federal users should not interfere with state-owned forms unless granted policy or admin permissions.

### 4.7 Platform Admin

Platform admin should be able to:

- Manage global form categories.
- Configure field types.
- Maintain system templates.
- Resolve template errors.
- Audit form changes.
- Manage form feature flags.

---

## 5. Forms Tool Navigation and UI Consolidation

### 5.1 Recommended Parent Module

Use one parent module:

```txt
Forms Tool
```

Inside it, use these main tabs:

```txt
Forms Tool
├── Overview
├── Templates
├── Assignments
├── Responses
├── Reports
└── Settings
```

Do not create separate top-level modules such as:

```txt
Inspection Templates
Employer Forms
Facility Forms
Survey Tool
Questionnaires
Data Collection
Form Responses
```

Those are all part of the Forms Tool.

### 5.2 Forms Tool Tab Definitions

#### Overview

Dashboard showing form usage, assignments, response rate, overdue forms, and recent activity.

#### Templates

Where authorized users create, edit, publish, version, archive, and manage form templates.

#### Assignments

Where authorized users assign templates to users, organizations, modules, groups, or records.

#### Responses

Where authorized users view submitted responses, pending responses, drafts, returned submissions, and reviewed responses.

#### Reports

Where users generate form-based analytics, response summaries, and exports.

#### Settings

Where admins manage form categories, purposes, field types, scoring rules, and default templates.

---

## 6. Form Template Purpose

Every form template must have a purpose.

Recommended purposes:

```txt
Inspection Checklist
Employer Data Collection
Employer Compliance Self-Assessment
Medical Facility Data Collection
Medical Facility Monthly Report
Accreditation Checklist
Re-accreditation Checklist
Food Handler Survey
Food Handler Declaration
Incident Report
Training Feedback
Public Health Follow-Up
General Data Collection
```

### 6.1 Purpose Drives Where the Form Appears

| Form Purpose | Primary Module | Respondent |
|---|---|---|
| Inspection Checklist | Inspections | Inspector |
| Employer Data Collection | Employer Portal / Forms | Employer Admin / Compliance Officer |
| Employer Compliance Self-Assessment | Employer Portal / Compliance | Employer Admin / Compliance Officer |
| Medical Facility Data Collection | Medical Facility Portal / Forms | Facility Admin |
| Medical Facility Monthly Report | Medical Facility Portal / Reports / Forms | Facility Admin / Medical Director |
| Accreditation Checklist | Medical Facilities / Accreditation | State Reviewer / Facility |
| Re-accreditation Checklist | Medical Facilities / Accreditation | State Reviewer / Facility |
| Food Handler Survey | Food Handler Portal | Food Handler |
| Food Handler Declaration | Food Handler / Medical Assessment | Food Handler |
| Incident Report | Inspections / Compliance | Inspector / Employer / State User |
| Training Feedback | Training / Forms | Training Participant |
| General Data Collection | Assigned Forms | Configured Recipient |

---

## 7. Template Lifecycle

### 7.1 Template Statuses

```txt
Draft
Published
Archived
Deprecated
```

### 7.2 Template Lifecycle Flow

```txt
Create Draft Template
→ Configure Sections and Questions
→ Preview Template
→ Publish Template
→ Assign Template
→ Collect Responses
→ Version Template if changes are needed
→ Archive or Deprecate Template when no longer used
```

### 7.3 Versioning Rules

- Published templates should not be edited directly if they already have responses.
- Editing a published template should create a new version.
- Existing assignments should remain linked to the version they were assigned.
- Responses should always show the template version used.
- Reports should be able to filter by template and version.

Example:

```txt
Inspection Checklist v1 assigned in March
Inspection Checklist v2 published in April
March inspection responses remain linked to v1
New assignments use v2 by default
```

---

## 8. Form Builder Requirements

### 8.1 Template Structure

A form template should support:

```txt
Template Title
Description
Purpose
Owner Organization
Target Respondent Type
Module Context
Sections
Questions
Validation Rules
Scoring Rules, where applicable
Evidence Requirements
Submission Rules
Visibility Rules
Version
Status
```

### 8.2 Sections

Templates can have multiple sections.

Example inspection template:

```txt
Section 1: Employer Information
Section 2: Facility Hygiene
Section 3: Food Handler Certification
Section 4: Storage and Handling
Section 5: Evidence Uploads
Section 6: Inspector Findings
```

### 8.3 Question Types

Supported question types should include:

```txt
Short Text
Long Text
Number
Decimal
Date
DateTime
Time
Single Choice
Multiple Choice
Dropdown
Yes / No
Checkbox
File Upload
Image Upload
Signature
Location / GPS
Rating
Score
Matrix
Repeating Group
Calculated Field
Instruction / Read-only Text
```

### 8.4 Validation Rules

Question validation should include:

```txt
Required
Minimum Length
Maximum Length
Minimum Value
Maximum Value
Date Range
File Type
Maximum File Size
Allowed Options
Regex Pattern
Conditional Required
```

### 8.5 Conditional Logic

Forms should support conditional display rules.

Example:

```txt
If “Are all food handlers certified?” = No
→ Show “List uncertified food handlers”
→ Require evidence upload
```

### 8.6 Scoring Rules

Some forms, especially inspection templates, may require scoring.

Scoring should support:

```txt
Question-level scores
Section-level scores
Overall score
Pass/fail threshold
Risk rating
Critical failure rules
Weighted scoring
```

Example:

```txt
If critical violation = Yes
→ Inspection outcome cannot be Passed
```

### 8.7 Evidence Uploads

Forms should support evidence capture:

```txt
Photo
Document
Video, optional
Signature
GPS location
Timestamp
```

Evidence should be linked to both:

```txt
Form Response
Operational Record, such as Inspection
```

---

## 9. Assignment Requirements

### 9.1 Assignment Types

Forms can be assigned to:

```txt
Specific User
Organization
Organization Unit / Branch / Department
Role
Group
Inspection Record
Accreditation Application
Medical Facility
Employer
Food Handler
State-wide cohort
```

### 9.2 Assignment Context

Each assignment should have context:

```txt
No Context / General Form
Inspection
Employer
Employer Branch / Outlet
Medical Facility
Accreditation Application
Food Handler
Incident
Training
Report Period
```

### 9.3 Assignment Fields

Recommended fields:

```txt
template_id
template_version_id
assignment_title
purpose
assigned_by
assigned_to_type
assigned_to_id
recipient_role
context_type
context_id
start_date
due_date
allow_late_submission
allow_draft
allow_multiple_submissions
requires_review
reviewer_role
status
created_at
updated_at
```

### 9.4 Assignment Statuses

Recommended statuses:

```txt
Draft
Scheduled
Active
In Progress
Submitted
Partially Submitted
Returned
Reviewed
Overdue
Cancelled
Closed
```

### 9.5 Recipient Rules

The assignment engine should determine recipients based on:

```txt
User ID
Organization ID
Organization type
State
LGA
Branch
Role
Permission
Facility accreditation status
Employer subscription status
Food handler certificate status
Inspection assignment
```

---

## 10. Module-Based Form Consumption

### 10.1 Inspections Module

The Inspections module must support assigning an inspector and assigning an inspection template.

#### Inspection Assignment Flow

```txt
State creates inspection
→ Select Employer / Food Business
→ Select Branch / Outlet, if applicable
→ Select Inspector
→ Select Inspection Template
→ Set date and due date
→ Notify Inspector
→ Inspector opens assigned inspection
→ Inspector completes assigned form
→ Inspector submits form
→ State reviews inspection response
```

#### Inspection Form UI

Inside an inspection record, show:

```txt
Inspection Details
Employer / Branch Details
Assigned Inspector
Assigned Form Template
Inspection Form Response
Evidence Uploads
Findings
Submit Inspection
```

#### Inspection Template Rules

- Inspection templates are created in Forms Tool.
- Inspection templates are assigned from the Inspections module when creating or editing an inspection.
- Inspector should not need to open Forms Tool to complete the inspection form.
- Inspection response must be linked to the inspection record.
- Inspection findings can be generated from form answers where configured.

#### Inspection Assignment Fields

```txt
inspection_id
inspector_id
employer_id
branch_id
form_template_id
template_version_id
scheduled_date
due_date
inspection_status
form_response_id
```

### 10.2 Employer Portal

Employer users should see forms assigned to their organization or branch.

#### Employer Form Locations

Forms assigned to employers may appear in:

```txt
Employer Dashboard
Assigned Forms
Compliance
Food Handlers, if food-handler-specific
Branches / Outlets, if branch-specific
Reports, if reporting-related
```

#### Employer Assigned Forms Page

Recommended filters:

```txt
All
Pending
In Progress
Submitted
Returned
Overdue
Reviewed
```

Recommended columns:

```txt
Form Title
Purpose
Assigned By
Context
Due Date
Status
Submitted By
Submitted Date
Actions
```

#### Employer Actions

```txt
Start Form
Continue Draft
Submit Response
View Submission
Respond to Returned Form
Download Submission
```

### 10.3 Medical Facility Portal

Medical facilities should see forms assigned to their facility.

#### Medical Facility Form Locations

Forms assigned to facilities may appear in:

```txt
Facility Dashboard
Assigned Forms
Accreditation
Reports
Assessments, if assessment-related
```

#### Facility Assigned Forms Examples

```txt
Monthly Assessment Volume Report
Facility Equipment Update Form
Accreditation Evidence Checklist
Re-accreditation Checklist
Staffing Update Form
```

#### Facility Actions

```txt
Start Form
Continue Draft
Submit Response
View Submission
Respond to Returned Form
Download Submission
```

### 10.4 Medical Facilities Accreditation Workflow

Accreditation checklists should use the Forms Tool.

Flow:

```txt
State creates Accreditation Checklist Template
→ Facility submits accreditation application
→ Checklist is attached to application
→ Facility completes facility-facing sections, if required
→ State reviewer completes review sections
→ Form response becomes part of accreditation record
```

Rule:

> The form template is managed in Forms Tool, but the response appears inside the accreditation application workflow.

### 10.5 Food Handler Portal

Food handler forms should be used where appropriate.

Examples:

```txt
Training Feedback
Health Declaration Update
Food Handler Survey
Public Health Follow-Up
```

Forms should be mobile-friendly and simple.

### 10.6 Reports Module

Submitted form responses should feed into reports.

Reports should allow filtering by:

```txt
Template
Template Version
Purpose
State
LGA
Organization Type
Respondent Type
Assignment Status
Submission Status
Date Range
```

---

## 11. Forms Tool User Interface

### 11.1 Overview Tab

KPI Cards:

```txt
Total Templates
Published Templates
Active Assignments
Pending Responses
Submitted Responses
Overdue Responses
Forms Due This Week
Average Response Rate
```

Widgets:

```txt
Recent Templates
Recent Assignments
Overdue Forms
Response Rate by Purpose
Top Assigned Templates
Recent Submissions
```

### 11.2 Templates Tab

Templates table columns:

```txt
Template Name
Purpose
Owner
Target Respondent
Version
Status
Last Updated
Created By
Actions
```

Template actions:

```txt
Create Template
Edit Draft
Preview
Publish
Duplicate
Create New Version
Archive
View Responses
Assign
```

Template filters:

```txt
All
Draft
Published
Archived
Purpose
Owner
Target Respondent
```

### 11.3 Form Builder UI

Recommended builder layout:

```txt
Left Panel: Sections
Center Panel: Form Canvas
Right Panel: Question Settings
Top Bar: Template name, save, preview, publish
```

Builder capabilities:

- Add section.
- Reorder section.
- Rename section.
- Add question.
- Reorder question.
- Duplicate question.
- Delete question.
- Configure required/optional.
- Configure validation.
- Configure conditional logic.
- Configure scoring.
- Configure evidence requirement.
- Preview form.
- Save draft.
- Publish template.

### 11.4 Assignments Tab

Assignments table columns:

```txt
Assignment Title
Template
Purpose
Recipient Type
Context
Due Date
Status
Response Progress
Created By
Actions
```

Assignment actions:

```txt
Create Assignment
View Assignment
Edit Assignment
Cancel Assignment
Send Reminder
View Responses
Export Responses
```

Assignment filters:

```txt
All
Active
Scheduled
In Progress
Submitted
Returned
Overdue
Closed
Purpose
Recipient Type
Context Type
```

### 11.5 Assignment Creation UI

Use a wizard:

```txt
Step 1: Select Template
Step 2: Select Purpose / Context
Step 3: Select Recipients
Step 4: Configure Submission Rules
Step 5: Review and Publish Assignment
```

Submission rules:

```txt
Due Date
Allow Draft
Allow Multiple Submissions
Allow Late Submission
Require Review
Reviewer Role
Reminder Schedule
```

### 11.6 Responses Tab

Responses table columns:

```txt
Form Title
Assignment
Purpose
Respondent
Organization
Context
Status
Submitted Date
Reviewed By
Actions
```

Response statuses:

```txt
Not Started
In Progress
Submitted
Returned
Reviewed
Overdue
Cancelled
```

Response actions:

```txt
View Response
Review Response
Return for Correction
Mark Reviewed
Export Response
Download Attachments
```

### 11.7 Reports Tab

Reports include:

```txt
Template Response Summary
Assignment Progress Report
Overdue Response Report
Inspection Form Response Report
Employer Data Collection Report
Medical Facility Data Collection Report
Accreditation Checklist Report
Response Rate by Organization
Response Rate by LGA
```

---

## 12. Data Model Requirements

### 12.1 FormTemplate

Suggested fields:

```txt
id
title
description
purpose
owner_organization
target_respondent_type
module_context
status
current_version
created_by
created_at
updated_at
archived_at
```

### 12.2 FormTemplateVersion

Suggested fields:

```txt
id
template
version_number
schema_json
scoring_json
conditional_logic_json
published_by
published_at
status
created_at
```

### 12.3 FormSection

May be embedded in schema JSON or stored relationally.

Fields if relational:

```txt
id
template_version
title
description
order
visibility_logic
```

### 12.4 FormQuestion

May be embedded in schema JSON or stored relationally.

Fields if relational:

```txt
id
section
label
description
question_type
required
order
options_json
validation_json
conditional_logic_json
scoring_json
evidence_rules_json
```

### 12.5 FormAssignment

Suggested fields:

```txt
id
title
template
template_version
purpose
assigned_by
assigned_to_type
assigned_to_id
recipient_role
context_type
context_id
start_date
due_date
allow_draft
allow_multiple_submissions
allow_late_submission
requires_review
reviewer_role
status
created_at
updated_at
closed_at
```

### 12.6 FormRecipient

For assignments with multiple recipients:

```txt
id
assignment
recipient_type
recipient_id
organization
role
status
notified_at
started_at
submitted_at
reviewed_at
```

### 12.7 FormResponse

Suggested fields:

```txt
id
assignment
template
template_version
respondent_user
respondent_organization
context_type
context_id
response_json
score
risk_rating
status
submitted_at
reviewed_by
reviewed_at
review_notes
returned_reason
created_at
updated_at
```

### 12.8 FormResponseAttachment

Suggested fields:

```txt
id
response
question_id
file_url
file_type
file_name
uploaded_by
uploaded_at
metadata_json
```

### 12.9 FormAuditLog

Suggested fields:

```txt
id
actor
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

## 13. API Requirements

### 13.1 Template APIs

```txt
GET    /api/forms/templates
POST   /api/forms/templates
GET    /api/forms/templates/:id
PATCH  /api/forms/templates/:id
POST   /api/forms/templates/:id/publish
POST   /api/forms/templates/:id/archive
POST   /api/forms/templates/:id/duplicate
POST   /api/forms/templates/:id/new-version
GET    /api/forms/templates/:id/versions
GET    /api/forms/templates/:id/preview
```

### 13.2 Assignment APIs

```txt
GET    /api/forms/assignments
POST   /api/forms/assignments
GET    /api/forms/assignments/:id
PATCH  /api/forms/assignments/:id
POST   /api/forms/assignments/:id/cancel
POST   /api/forms/assignments/:id/send-reminder
GET    /api/forms/assignments/:id/recipients
GET    /api/forms/assignments/:id/responses
```

### 13.3 Response APIs

```txt
GET    /api/forms/responses
POST   /api/forms/responses
GET    /api/forms/responses/:id
PATCH  /api/forms/responses/:id
POST   /api/forms/responses/:id/submit
POST   /api/forms/responses/:id/review
POST   /api/forms/responses/:id/return
POST   /api/forms/responses/:id/attachments
GET    /api/forms/responses/:id/export
```

### 13.4 Module Integration APIs

Inspections:

```txt
POST /api/inspections
PATCH /api/inspections/:id/assign-template
GET  /api/inspections/:id/form-response
POST /api/inspections/:id/form-response
```

Employer:

```txt
GET /api/employer/assigned-forms
GET /api/employer/assigned-forms/:id
POST /api/employer/assigned-forms/:id/response
```

Medical Facility:

```txt
GET /api/facility/assigned-forms
GET /api/facility/assigned-forms/:id
POST /api/facility/assigned-forms/:id/response
```

Food Handler:

```txt
GET /api/food-handler/assigned-forms
GET /api/food-handler/assigned-forms/:id
POST /api/food-handler/assigned-forms/:id/response
```

---

## 14. Permissions

### 14.1 Forms Tool Permissions

```txt
forms.template.view
forms.template.create
forms.template.update
forms.template.publish
forms.template.archive
forms.template.version

forms.assignment.view
forms.assignment.create
forms.assignment.update
forms.assignment.cancel
forms.assignment.send_reminder

forms.response.view
forms.response.submit
forms.response.review
forms.response.return
forms.response.export

forms.report.view
forms.report.export
forms.settings.manage
```

### 14.2 Module Permissions

Inspections:

```txt
inspection.create
inspection.assign_inspector
inspection.assign_form_template
inspection.respond_to_form
inspection.review_response
```

Employer:

```txt
employer.assigned_forms.view
employer.assigned_forms.submit
```

Medical Facility:

```txt
facility.assigned_forms.view
facility.assigned_forms.submit
```

Food Handler:

```txt
food_handler.assigned_forms.view
food_handler.assigned_forms.submit
```

### 14.3 Access Rules

- Only authorized State users can create and assign state-owned forms.
- Users can only respond to forms assigned to them, their organization, their role, or their operational context.
- Inspectors can only respond to inspection forms for inspections assigned to them.
- Employers can only respond to forms assigned to their organization or branch.
- Medical facilities can only respond to forms assigned to their facility.
- Food handlers can only respond to forms assigned to them.
- Backend permissions are the source of truth.

---

## 15. Notifications

### 15.1 Assignment Notifications

Notify recipients when:

```txt
Form assigned
Form due soon
Form overdue
Form returned for correction
Form reviewed
Assignment cancelled
```

### 15.2 Inspection-Specific Notifications

Notify inspector when:

```txt
Inspection assigned
Inspection template assigned
Inspection due soon
Inspection form returned for correction
```

Notify State reviewer when:

```txt
Inspection form submitted
Critical inspection response received
```

### 15.3 Employer / Facility Notifications

Notify organization admins when:

```txt
New form assigned
Due date approaching
Form overdue
Submission returned
Submission reviewed
```

---

## 16. Reporting and Analytics

### 16.1 Response Tracking

Track:

```txt
Total assigned
Not started
In progress
Submitted
Reviewed
Returned
Overdue
Response rate
Average completion time
```

### 16.2 Form Response Analytics

For structured questions, support analytics:

```txt
Choice distribution
Average score
Risk rating distribution
Section score
Pass/fail count
Compliance gaps
Common failed questions
Evidence submission rate
```

### 16.3 Inspection Template Analytics

For inspection forms:

```txt
Inspection pass rate
Critical violations
Average inspection score
Common non-compliance areas
Employer compliance score
Branch compliance score
Inspector submission rate
```

---

## 17. Privacy and Data Protection

### 17.1 Sensitive Forms

Some forms may collect sensitive data.

Examples:

```txt
Health declaration
Medical follow-up
Food handler illness report
Return-to-work form
```

Sensitive forms must have:

- Restricted visibility.
- Role-based access.
- Audit logging.
- Privacy notices.
- Purpose limitation.
- Export restrictions.

### 17.2 Employer Privacy

Employers should not see private medical information unless explicitly allowed by policy.

### 17.3 Inspector Privacy

Inspectors should see operational compliance fields, not private medical records.

### 17.4 Export Controls

Exports must respect:

```txt
Permission
Scope
Privacy classification
Purpose
Audit logging
```

---

## 18. UI Consolidation Rules

### 18.1 Do Not Duplicate Form Builders

Do not build separate form builders inside:

```txt
Inspections
Medical Facilities
Employers
Food Handlers
Reports
```

Use the Forms Tool builder.

### 18.2 Module Forms Are Contextual

Operational modules should display assigned forms contextually.

Examples:

```txt
Inspection record shows the assigned inspection template response.
Employer portal shows assigned employer forms.
Medical facility portal shows assigned facility forms.
Accreditation workflow shows checklist forms.
```

### 18.3 Forms Tool Owns Template and Assignment Management

Do not scatter template creation across modules.

### 18.4 Modules Own Workflow

Do not force users to leave their workflow to respond to assigned forms.

### 18.5 One Forms Tool, Many Use Cases

The system should support many form purposes without creating separate mini form products.

---

## 19. Acceptance Criteria

### 19.1 Forms Tool

- Authorized users can create form templates.
- Authorized users can publish templates.
- Published templates are versioned.
- Published templates with responses cannot be edited directly.
- Authorized users can assign forms to users, organizations, roles, modules, and records.
- Users can track response status.
- Users can export responses where permitted.

### 19.2 Inspections Integration

- State can assign an inspector.
- State can assign an inspection template to the inspection.
- Inspector sees the form inside the inspection assignment.
- Inspector can complete and submit the inspection form.
- Inspection response is linked to the inspection record.
- State can review inspection responses.

### 19.3 Employer Integration

- Employer can view assigned forms.
- Employer can submit assigned forms.
- Employer can view submitted forms.
- Branch-specific forms are visible only to authorized branch users.

### 19.4 Medical Facility Integration

- Facility can view assigned forms.
- Facility can submit assigned forms.
- Accreditation and reporting forms appear in the correct workflow context.

### 19.5 Reporting

- State can view pending, submitted, reviewed, returned, and overdue responses.
- State can export responses where permitted.
- Response analytics work for structured questions.

### 19.6 Privacy and Security

- Users only see assigned forms within their scope.
- Sensitive form responses are protected.
- Exports are permission-controlled.
- Template changes and response actions are audit logged.

---

## 20. Implementation Chunks for Codex

### Chunk 1: Forms Tool Navigation and Page Shell

**Goal:** Create the Forms Tool parent module with consolidated tabs.

Tasks:

- Add Forms Tool to navigation.
- Create `FormsToolPage`.
- Add tabs: Overview, Templates, Assignments, Responses, Reports, Settings.
- Add permission-based tab visibility.
- Remove or avoid separate top-level modules such as Inspection Templates, Surveys, Questionnaires, or Data Collection.

Acceptance Criteria:

- Forms Tool appears as one parent module.
- Tabs render correctly.
- Unauthorized tabs are hidden.
- No duplicate form-builder modules exist.

### Chunk 2: Form Template Data Model and APIs

**Goal:** Implement form template and versioning foundation.

Tasks:

- Create or update `FormTemplate`.
- Create or update `FormTemplateVersion`.
- Store schema JSON.
- Store purpose and target respondent type.
- Add template statuses.
- Add APIs for create, update, publish, archive, duplicate, and new version.

Acceptance Criteria:

- Draft templates can be created and edited.
- Templates can be published.
- Published templates are versioned.
- New version is created for published templates with responses.
- Archived templates cannot be assigned.

### Chunk 3: Form Builder UI

**Goal:** Create the template builder interface.

Tasks:

- Build section/question builder.
- Support required field, options, validation, conditional logic, scoring, and evidence rules.
- Add preview.
- Add save draft and publish actions.
- Add template purpose selection.

Acceptance Criteria:

- Users can create multi-section templates.
- Users can add supported question types.
- Users can preview forms.
- Users can publish templates.
- Template schema saves correctly.

### Chunk 4: Assignment Engine

**Goal:** Allow templates to be assigned to users, organizations, roles, groups, modules, and records.

Tasks:

- Create `FormAssignment`.
- Create `FormRecipient`.
- Add assignment wizard.
- Support context type and context ID.
- Support due dates, drafts, multiple submission rules, review requirement, reminders.
- Add recipient resolution logic.

Acceptance Criteria:

- Forms can be assigned to inspectors, employers, medical facilities, food handlers, and groups.
- Assignments can be tied to inspections, accreditation applications, branches, facilities, or general contexts.
- Recipients are resolved correctly.
- Assignments generate notifications.

### Chunk 5: Response Engine

**Goal:** Allow assigned recipients to submit responses.

Tasks:

- Create `FormResponse`.
- Create `FormResponseAttachment`.
- Implement response renderer from template schema.
- Support draft save.
- Support submit.
- Support attachment upload.
- Support scoring where configured.
- Support review and return.

Acceptance Criteria:

- Assigned users can respond.
- Drafts save where allowed.
- Required fields validate.
- Conditional logic works.
- Attachments upload.
- Submitted responses are immutable except through return/correction flow.
- Responses link to assignment and context.

### Chunk 6: Inspections Integration

**Goal:** Allow inspection templates to be assigned and completed inside the Inspections module.

Tasks:

- Update inspection creation/edit flow.
- Add inspector assignment.
- Add form template selection.
- Link inspection to form assignment.
- Render assigned inspection form inside inspection detail.
- Link submitted response to inspection record.
- Generate findings from configured critical answers where applicable.

Acceptance Criteria:

- State can assign inspector and inspection template.
- Inspector sees assigned form inside Inspections module.
- Inspector completes form without entering Forms Tool.
- Response is linked to inspection.
- State can review inspection form response.

### Chunk 7: Employer Portal Integration

**Goal:** Show assigned employer forms in the Employer portal.

Tasks:

- Add Employer Assigned Forms page or section.
- Show forms assigned to employer, branch, role, or user.
- Add filters for pending, submitted, returned, overdue.
- Render response form.
- Submit response.
- Show submitted forms.

Acceptance Criteria:

- Employer users see only assigned forms within scope.
- Branch users see branch-specific forms where permitted.
- Employer can submit and view responses.
- Returned forms can be corrected.

### Chunk 8: Medical Facility Portal Integration

**Goal:** Show assigned medical facility forms in the Facility portal.

Tasks:

- Add Facility Assigned Forms page or section.
- Integrate forms into Accreditation workflow where context type is accreditation.
- Integrate forms into Reports section where purpose is facility reporting.
- Render and submit responses.
- Show submission history.

Acceptance Criteria:

- Facility users see assigned forms.
- Accreditation forms appear in accreditation context.
- Reporting forms appear in reports/assigned forms context.
- Facility responses are scoped and permission-controlled.

### Chunk 9: Directory, Reports, and Analytics Integration

**Goal:** Expose submitted response data for reporting and review.

Tasks:

- Add response tables.
- Add response exports.
- Add analytics for structured responses.
- Add filters by template, version, purpose, state, LGA, organization, and status.
- Link responses to related operational records.

Acceptance Criteria:

- State can track response progress.
- State can export responses.
- Structured analytics are available.
- Reports respect permissions and privacy.

### Chunk 10: Notifications and Reminders

**Goal:** Notify users about assignments and deadlines.

Tasks:

- Add notification templates.
- Trigger assignment notifications.
- Trigger due soon reminders.
- Trigger overdue reminders.
- Trigger returned/reviewed notifications.
- Add notification preferences where applicable.

Acceptance Criteria:

- Recipients are notified when forms are assigned.
- Reminder notifications are sent.
- Review and return notifications work.
- Notification events are audit logged.

### Chunk 11: Permissions, Scope, and Privacy

**Goal:** Secure form access.

Tasks:

- Implement permissions listed in this PRD.
- Enforce respondent scoping.
- Enforce organization and state scoping.
- Enforce privacy classification on sensitive forms.
- Audit template, assignment, response, review, export actions.

Acceptance Criteria:

- Users cannot see forms outside their scope.
- Users cannot submit forms not assigned to them.
- Sensitive responses are protected.
- Exports are controlled.
- Audit logs capture critical actions.

### Chunk 12: Final UI QA and Route Consolidation

**Goal:** Confirm Forms Tool is consolidated and module consumption works.

QA Checklist:

- Forms Tool is one parent module.
- Template builder is only in Forms Tool.
- Inspection form appears inside Inspections.
- Employer forms appear inside Employer portal.
- Facility forms appear inside Medical Facility portal.
- Accreditation checklists appear in accreditation workflow.
- Responses appear in Forms Tool and relevant module.
- No duplicate form modules exist.
- Empty states work.
- Loading states work.
- Mobile responsiveness works.
- Permissions work.

---

## 21. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Build the FoodCert NG Forms Tool as a centralized form/template and assignment engine.

The Forms Tool should manage:
- Form Templates
- Template Versions
- Form Assignments
- Recipients
- Responses
- Reviews
- Exports
- Reports
- Settings

Use one parent module:
Forms Tool
- Overview
- Templates
- Assignments
- Responses
- Reports
- Settings

Do not create separate standalone form builders inside Inspections, Employers, Medical Facilities, Food Handlers, Reports, or Accreditation.

Operational modules should consume assigned forms contextually.

Inspections:
- State creates inspection.
- State assigns inspector.
- State selects inspection form template from Forms Tool.
- Inspector opens Inspections module and completes assigned form there.
- Response links to inspection record.

Employer:
- Forms assigned to employers or branches appear in Employer portal.
- Employer can complete assigned forms and view submitted forms.

Medical Facility:
- Forms assigned to facilities appear in Medical Facility portal.
- Accreditation checklist forms appear inside accreditation workflow.
- Facility reporting forms appear in assigned forms/reports context.

State:
- State can create templates, publish versions, assign forms, track responses, review submissions, and export responses.
- Forms can be assigned to users, organizations, roles, groups, inspections, accreditation applications, employers, branches, medical facilities, and food handlers.

Implement:
- FormTemplate
- FormTemplateVersion
- FormAssignment
- FormRecipient
- FormResponse
- FormResponseAttachment
- FormAuditLog

Support:
- Multi-section templates
- Question types
- Conditional logic
- Validation
- Evidence upload
- Scoring
- Drafts
- Reviews
- Returned submissions
- Reminders
- Exports
- Analytics

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions and scoping remain the source of truth.
```

---

## 22. MVP Build Order

1. Forms Tool navigation and page shell
2. Template data model and APIs
3. Form builder UI
4. Assignment engine
5. Response engine
6. Inspections integration
7. Employer portal integration
8. Medical facility portal integration
9. Directory/reports/analytics integration
10. Notifications and reminders
11. Permissions, scope, and privacy
12. Final UI QA and route consolidation
