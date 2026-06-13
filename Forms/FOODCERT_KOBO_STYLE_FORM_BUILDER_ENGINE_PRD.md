# PRD: KoboToolbox-Style Form Builder Engine — FoodCert NG

## 1. Document Purpose

This PRD defines the enhanced **FoodCert NG Form Builder Engine**, inspired by the practical strengths of tools like KoboToolbox, but designed specifically for FoodCert NG workflows.

The Forms Tool must support:

```txt
Form Builder
Question Types
Skip Logic
Required Fields
Repeat Groups
Offline Response Support
Media Uploads
Submission Tracking
Exports
```

The goal is to allow State Ministries and authorized platform users to create flexible data collection tools that can be used across FoodCert NG modules such as:

```txt
Inspections
Employers / Food Businesses
Medical Facilities
Accreditation
Food Handlers
Reports
Compliance Monitoring
Training / Feedback
Incident Reporting
```

The Forms Tool should function as a reusable form engine, while the operational modules determine how each form is used.

---

# 2. Product Vision

The FoodCert NG Form Builder should be a flexible, workflow-aware data collection engine.

It should allow a State Ministry user to create a form template once and use it across different contexts.

Examples:

```txt
Inspection checklist for food business inspection
Medical facility monthly report form
Employer compliance self-assessment form
Food handler survey
Accreditation checklist
Re-accreditation checklist
Incident report form
Training feedback form
```

The platform should support both:

```txt
Online submission
Offline data collection with later sync
```

This is especially important for inspectors working in areas with poor internet connectivity.

---

# 3. Core Product Decision

The Form Builder Engine should behave like a professional data collection platform, but embedded inside FoodCert NG.

It should provide:

```txt
Template creation
Dynamic form design
Question configuration
Conditional logic
Repeatable sections
Draft saving
Offline response capture
Media evidence upload
Submission tracking
Export and reporting
Module-based assignment
```

However, unlike a general-purpose external survey platform, FoodCert NG forms must be tied to platform records.

Examples:

```txt
Inspection form response → linked to Inspection record
Employer form response → linked to Employer / Branch record
Medical facility form response → linked to Medical Facility record
Accreditation checklist → linked to Accreditation Application
Food handler survey → linked to Food Handler profile
```

---

# 4. Scope

## 4.1 In Scope

This PRD covers:

```txt
Form template builder
Question types
Required fields
Validation rules
Skip logic / conditional logic
Repeat groups
Media uploads
GPS / location capture
Signature capture
Offline response support
Draft responses
Submission tracking
Response review
Data exports
Form analytics
Module integration
Permissions and privacy
Implementation chunks
```

## 4.2 Out of Scope

This PRD does not cover:

```txt
Full external public survey hosting outside FoodCert NG
Anonymous mass public polling
Replacing the medical assessment workflow
Replacing certificate issuance
Replacing payment workflows
```

Forms may support medical or certification workflows, but they should not replace core verified workflows unless explicitly configured.

---

# 5. User Roles

## 5.1 Form Creator

Usually State Ministry, Federal Ministry, or Platform Admin users.

Can:

```txt
Create form templates
Edit draft templates
Preview forms
Publish templates
Create new versions
Archive templates
Assign forms
View responses
Export responses
```

## 5.2 Form Assigner

Can assign published forms to:

```txt
Inspectors
Employers
Employer branches/outlets
Medical facilities
Food handlers
State users
Groups
Operational records
```

## 5.3 Form Respondent

Can complete and submit forms assigned to them.

Respondents may include:

```txt
Inspector
Employer Admin
Employer Compliance Officer
Branch Manager
Medical Facility Admin
Medical Director
Food Handler
State Officer
```

## 5.4 Form Reviewer

Can review submitted responses, return forms for correction, approve, mark reviewed, or escalate.

## 5.5 Form Analyst

Can view reports, export response data, and analyze submissions.

---

# 6. Forms Tool UI Consolidation

## 6.1 Parent Module

Use one parent module:

```txt
Forms Tool
```

Tabs:

```txt
Forms Tool
├── Overview
├── Templates
├── Assignments
├── Responses
├── Exports
├── Reports
└── Settings
```

Do not create separate top-level menus for:

```txt
Surveys
Questionnaires
Inspection Templates
Data Collection
Form Responses
Offline Forms
```

They should all be part of the Forms Tool.

## 6.2 Operational Module Consumption

Operational modules should consume assigned forms.

Examples:

```txt
Inspections Module → displays inspection checklist assigned to inspector
Employer Portal → displays assigned employer data collection form
Medical Facility Portal → displays assigned facility monthly report
Accreditation Workflow → displays assigned accreditation checklist
Food Handler Portal → displays assigned survey or declaration update
```

## 6.3 Key Rule

```txt
Forms Tool owns templates, assignments, responses, exports, and reporting.
Operational modules own context and workflow.
```

---

# 7. Form Template Builder

## 7.1 Builder Layout

Recommended layout:

```txt
Top Bar
├── Template Name
├── Save Draft
├── Preview
├── Publish
└── More Actions

Left Panel
├── Sections
├── Repeat Groups
└── Question Navigator

Center Panel
├── Form Canvas
├── Section Content
└── Question Blocks

Right Panel
├── Question Settings
├── Validation
├── Skip Logic
├── Calculation / Scoring
├── Media Rules
└── Advanced Settings
```

## 7.2 Template Metadata

Each template should include:

```txt
Template Name
Description
Purpose
Owner Organization
Target Respondent Type
Primary Module
Default Context Type
Language
Status
Version
Created By
Created Date
Last Updated
```

## 7.3 Template Purposes

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

---

# 8. Supported Question Types

The Form Builder must support the following question types.

## 8.1 Basic Text Fields

```txt
Short Text
Long Text
Email
Phone Number
URL
```

## 8.2 Numeric Fields

```txt
Number
Decimal
Currency
Percentage
Calculated Number
```

## 8.3 Date and Time Fields

```txt
Date
Time
Date and Time
Month / Year
```

## 8.4 Choice Fields

```txt
Single Choice
Multiple Choice
Dropdown
Yes / No
Likert Scale
Rating Scale
Matrix Question
```

## 8.5 Media and Evidence Fields

```txt
Image Upload
File Upload
Video Upload, optional
Audio Upload, optional
Signature Capture
GPS Location
Barcode / QR Scan
```

## 8.6 Advanced Fields

```txt
Repeat Group
Calculated Field
Read-only Instruction
Section Header
Consent / Declaration
Hidden Field
Auto-filled Platform Field
```

## 8.7 FoodCert-Specific Fields

Recommended FoodCert-specific field types:

```txt
Food Handler Selector
Employer Selector
Branch / Outlet Selector
Medical Facility Selector
Inspector Selector
Certificate QR Scan
Accreditation Application Selector
Inspection Record Selector
Risk Rating
Compliance Score
```

These fields should pull from FoodCert NG platform records.

---

# 9. Required Fields and Validation

## 9.1 Required Fields

Each question should have a required/optional setting.

Required questions must be completed before submission.

## 9.2 Validation Rules

Supported validation rules:

```txt
Minimum length
Maximum length
Minimum value
Maximum value
Date before / after
Allowed date range
Allowed file type
Maximum file size
Minimum selected options
Maximum selected options
Email format
Phone number format
Regex pattern
GPS required
Signature required
Media required
Conditional required
```

## 9.3 Custom Error Messages

Form creators should be able to set custom validation messages.

Example:

```txt
Please upload at least one photo of the food preparation area.
```

## 9.4 Submission Blocking

If validation fails:

```txt
User cannot submit
Invalid fields are highlighted
Error summary is shown
User is taken to first invalid question
```

---

# 10. Skip Logic and Conditional Logic

## 10.1 Purpose

Skip logic allows the form to show or hide questions, sections, or repeat groups based on earlier answers.

## 10.2 Supported Logic Types

```txt
Show question if condition is true
Hide question if condition is true
Require question if condition is true
Skip to section
End form early
Show warning
Trigger critical finding
Calculate score
```

## 10.3 Condition Operators

```txt
Equals
Does not equal
Contains
Does not contain
Greater than
Less than
Greater than or equal to
Less than or equal to
Is empty
Is not empty
Is selected
Is not selected
Between
Not between
```

## 10.4 Multiple Conditions

Support:

```txt
AND
OR
Nested conditions
Condition groups
```

## 10.5 Example Inspection Logic

```txt
Question: Are all food handlers certified?
Answer: No
Action:
- Show question: List uncertified food handlers
- Require evidence upload
- Trigger compliance warning
```

## 10.6 Example Medical Facility Logic

```txt
Question: Does facility have a functional laboratory?
Answer: No
Action:
- Show question: Explain laboratory referral arrangement
- Require supporting document
```

---

# 11. Repeat Groups

## 11.1 Purpose

Repeat groups allow users to enter the same set of questions multiple times.

This is important for inspections and field data collection.

Examples:

```txt
List all food handlers observed on site
List all branches inspected
List all equipment items checked
List all violations found
List all facility staff members
List all uploaded evidence items
```

## 11.2 Repeat Group Configuration

A repeat group should support:

```txt
Group name
Description
Minimum repeats
Maximum repeats
Allow add/remove repeat
Required repeat group
Summary label
Nested questions
Conditional display
```

## 11.3 Repeat Group UX

User should be able to:

```txt
Add item
Remove item
Edit item
Collapse item
Expand item
Duplicate item
View repeat summary
```

Example:

```txt
Food Handlers Observed
+ Add Food Handler
```

Each repeated item can contain:

```txt
Name
Certificate QR Scan
Fitness Status
Was handler actively working?
Evidence photo
Comment
```

## 11.4 Nested Repeat Groups

Support nested repeat groups only if technically feasible in the MVP.

Recommended approach:

```txt
MVP: One-level repeat groups
Phase 2: Nested repeat groups
```

---

# 12. Offline Response Support

## 12.1 Why Offline Support Matters

Inspectors may conduct inspections in locations with poor or no internet connection. The platform must allow them to complete assigned forms offline and sync later.

## 12.2 Offline-Capable Users

Offline support is most important for:

```txt
Inspectors
State field officers
Medical facility field teams, if applicable
```

It may also be useful for employers and facilities, but inspection use case should be prioritized.

## 12.3 Offline Capabilities

The application should support:

```txt
Download assigned forms for offline use
Cache form template schema
Cache required assignment context
Save draft responses locally
Capture media locally
Capture GPS where device allows
Validate required fields offline
Submit/sync when connection returns
Show sync status
Handle sync errors
Prevent duplicate submissions
```

## 12.4 Offline Storage

Use secure local storage technology appropriate for the frontend.

Recommended for web/PWA:

```txt
IndexedDB for form schemas, drafts, responses, and media metadata
Service Worker for offline app shell
Background Sync where available
Local encrypted storage for sensitive data where feasible
```

## 12.5 Offline Sync Statuses

Recommended statuses:

```txt
Not Downloaded
Available Offline
Draft Saved Locally
Ready to Sync
Syncing
Synced
Sync Failed
Conflict Detected
```

## 12.6 Conflict Handling

Possible conflicts:

```txt
Assignment cancelled while offline
Template version changed
Respondent submitted same form on another device
Due date passed while offline
Media upload failed
```

Conflict handling rules:

```txt
Keep local response safe
Notify user
Allow retry
Show conflict reason
Allow authorized reviewer to resolve conflict
Never silently discard data
```

## 12.7 Offline Limitations

Offline mode should clearly warn users that:

```txt
Some platform lookups may be unavailable offline
Large media uploads may sync slowly
GPS capture depends on device permission
QR scan validation may be limited if certificate data is not cached
```

---

# 13. Media Uploads

## 13.1 Supported Media

The form engine should support:

```txt
Images
Documents
PDFs
Videos, optional
Audio, optional
Signatures
GPS coordinates
QR/barcode scan data
```

## 13.2 Media Capture Sources

Users should be able to:

```txt
Take photo using device camera
Upload existing file
Record signature
Capture GPS location
Scan QR code
```

## 13.3 Media Rules

Each media question should support:

```txt
Required / optional
Allowed file types
Maximum file size
Minimum number of files
Maximum number of files
Capture-only mode, optional
Gallery upload allowed, optional
GPS metadata required, optional
Timestamp required
```

## 13.4 Media Compression

For photos and videos, support compression before upload where appropriate.

Suggested requirements:

```txt
Compress image before upload
Preserve enough quality for inspection evidence
Keep original metadata where policy allows
Show upload progress
Allow retry failed uploads
```

## 13.5 Media Security

Media uploads may contain sensitive information.

Requirements:

```txt
Access-controlled storage
Signed/private URLs
Virus/malware scanning where available
Audit log for download/view
Permission-based access
Export restrictions
```

---

# 14. Drafts and Autosave

## 14.1 Draft Support

Forms should support drafts if the assignment allows it.

Drafts may be:

```txt
Server drafts
Offline local drafts
Hybrid local + server drafts
```

## 14.2 Autosave

Autosave should save:

```txt
Text answers
Choice answers
Repeat group entries
Media metadata
Location data
Progress state
```

## 14.3 Autosave Frequency

Recommended:

```txt
Autosave every 15–30 seconds
Autosave on section change
Autosave before navigation away
Autosave when connectivity changes
```

## 14.4 Draft Recovery

If the app closes unexpectedly:

```txt
User can reopen the form
Draft is restored
User can continue from last saved section
```

---

# 15. Submission Tracking

## 15.1 Assignment-Level Tracking

Track:

```txt
Total recipients
Not started
In progress
Submitted
Reviewed
Returned
Overdue
Cancelled
Response rate
Completion rate
Average completion time
```

## 15.2 Response-Level Tracking

Track:

```txt
Respondent
Organization
Context
Started at
Last saved at
Submitted at
Reviewed at
Returned at
Sync status
Device/source
```

## 15.3 Statuses

Recommended response statuses:

```txt
Not Started
Draft
In Progress
Submitted
Returned for Correction
Reviewed
Approved, optional
Rejected, optional
Overdue
Cancelled
Sync Pending
Sync Failed
```

## 15.4 Response Activity Log

Each response should have an activity log:

```txt
Assigned
Opened
Draft saved
Media uploaded
Submitted
Returned
Resubmitted
Reviewed
Exported
```

---

# 16. Exports

## 16.1 Export Formats

Support:

```txt
CSV
Excel
JSON
PDF Summary
ZIP Attachments
```

## 16.2 Export Scope

Exports should support:

```txt
Single response
All responses for assignment
All responses for template
Filtered response set
Response data with attachments
Response data without attachments
```

## 16.3 Export Filters

```txt
Template
Template Version
Purpose
Assignment
Respondent Type
Organization
State
LGA
Date Range
Response Status
Review Status
Sync Status
Risk Rating
Score Range
```

## 16.4 Export Flattening

Repeat groups should be exportable in useful formats.

Recommended options:

```txt
One row per response
One row per repeat item
Separate sheets per repeat group
JSON nested export
```

For Excel:

```txt
Sheet 1: Responses
Sheet 2: Repeat Group - Food Handlers Observed
Sheet 3: Repeat Group - Violations
Sheet 4: Attachments Index
```

## 16.5 Export Privacy

Exports must respect:

```txt
User permission
Organization scope
State scope
Field sensitivity
Medical privacy
Attachment visibility
```

Export events must be audit logged.

---

# 17. Form Scoring and Risk Ratings

## 17.1 Purpose

Some forms, especially inspections and compliance assessments, may require scoring.

## 17.2 Scoring Features

Support:

```txt
Question scores
Section scores
Weighted scores
Overall score
Critical failure rules
Risk rating
Pass/fail outcome
```

## 17.3 Risk Ratings

Recommended ratings:

```txt
Low Risk
Medium Risk
High Risk
Critical Risk
```

## 17.4 Critical Rule Example

```txt
If “Evidence of food contamination?” = Yes
→ Risk Rating = Critical
→ Inspection cannot be marked passed
→ Create critical finding
```

---

# 18. Languages and Accessibility

## 18.1 Language Support

The builder should allow multilingual form labels over time.

MVP can start with English, but data model should support future translations.

Possible fields:

```txt
label_translations
description_translations
option_translations
```

## 18.2 Accessibility Requirements

Forms should support:

```txt
Keyboard navigation
Screen reader labels
Clear validation messages
Large tap targets
Mobile-first layouts
High contrast states
Error summaries
```

---

# 19. Data Model Requirements

## 19.1 FormTemplate

```txt
id
title
description
purpose
owner_organization_id
target_respondent_type
primary_module
default_context_type
status
current_version_id
created_by
created_at
updated_at
archived_at
```

## 19.2 FormTemplateVersion

```txt
id
template_id
version_number
schema_json
logic_json
scoring_json
settings_json
published_by
published_at
status
created_at
```

## 19.3 FormAssignment

```txt
id
title
template_id
template_version_id
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
allow_offline
allow_multiple_submissions
allow_late_submission
requires_review
reviewer_role
status
created_at
updated_at
closed_at
```

## 19.4 FormRecipient

```txt
id
assignment_id
recipient_type
recipient_id
organization_id
role_id
status
notified_at
started_at
submitted_at
reviewed_at
```

## 19.5 FormResponse

```txt
id
assignment_id
template_id
template_version_id
recipient_id
respondent_user_id
respondent_organization_id
context_type
context_id
response_json
score
risk_rating
status
sync_status
device_id
offline_created_at
started_at
last_saved_at
submitted_at
reviewed_by
reviewed_at
review_notes
returned_reason
created_at
updated_at
```

## 19.6 FormResponseAttachment

```txt
id
response_id
question_key
repeat_group_key
repeat_item_id
file_url
file_type
file_name
file_size
mime_type
uploaded_by
uploaded_at
captured_at
gps_latitude
gps_longitude
metadata_json
sync_status
```

## 19.7 FormResponseActivityLog

```txt
id
response_id
actor_id
action
details_json
created_at
ip_address
device_id
```

## 19.8 OfflineSyncQueue

```txt
id
user_id
assignment_id
response_id
local_response_id
operation_type
payload_json
media_payload_ref
status
attempt_count
last_attempt_at
error_message
created_at
updated_at
```

---

# 20. API Requirements

## 20.1 Template APIs

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

## 20.2 Assignment APIs

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

## 20.3 Response APIs

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

## 20.4 Offline APIs

```txt
GET  /api/forms/offline/assignments
GET  /api/forms/offline/assignments/:id/package
POST /api/forms/offline/sync
POST /api/forms/offline/sync/media
GET  /api/forms/offline/sync/:syncJobId/status
```

## 20.5 Export APIs

```txt
POST /api/forms/exports
GET  /api/forms/exports
GET  /api/forms/exports/:id
GET  /api/forms/exports/:id/download
```

## 20.6 Module Integration APIs

### Inspections

```txt
PATCH /api/inspections/:id/assign-template
GET   /api/inspections/:id/form-response
POST  /api/inspections/:id/form-response
```

### Employer

```txt
GET  /api/employer/assigned-forms
GET  /api/employer/assigned-forms/:id
POST /api/employer/assigned-forms/:id/response
```

### Medical Facility

```txt
GET  /api/facility/assigned-forms
GET  /api/facility/assigned-forms/:id
POST /api/facility/assigned-forms/:id/response
```

### Food Handler

```txt
GET  /api/food-handler/assigned-forms
GET  /api/food-handler/assigned-forms/:id
POST /api/food-handler/assigned-forms/:id/response
```

---

# 21. Frontend Components

## 21.1 Forms Tool Components

```txt
FormsToolPage
FormsOverview
TemplatesTable
TemplateBuilder
TemplatePreview
TemplatePublishModal
TemplateVersionHistory
AssignmentsTable
AssignmentWizard
ResponsesTable
ResponseViewer
ResponseReviewPanel
FormExportsPage
FormsReportsPage
FormsSettingsPage
```

## 21.2 Builder Components

```txt
FormCanvas
SectionEditor
QuestionBlock
QuestionTypePicker
QuestionSettingsPanel
ValidationSettings
SkipLogicBuilder
RepeatGroupBuilder
ScoringSettings
MediaRulesSettings
PreviewRenderer
```

## 21.3 Response Components

```txt
DynamicFormRenderer
RepeatGroupRenderer
MediaUploadField
SignatureField
GpsCaptureField
QrScanField
OfflineStatusBanner
AutosaveIndicator
SubmissionProgress
ValidationErrorSummary
```

## 21.4 Offline Components

```txt
OfflineFormsPage
DownloadForOfflineButton
SyncQueuePanel
SyncStatusBadge
ConflictResolutionModal
OfflineDraftRecovery
```

---

# 22. Permissions

## 22.1 Template Permissions

```txt
forms.template.view
forms.template.create
forms.template.update
forms.template.publish
forms.template.archive
forms.template.version
```

## 22.2 Assignment Permissions

```txt
forms.assignment.view
forms.assignment.create
forms.assignment.update
forms.assignment.cancel
forms.assignment.send_reminder
```

## 22.3 Response Permissions

```txt
forms.response.view
forms.response.submit
forms.response.review
forms.response.return
forms.response.export
```

## 22.4 Offline Permissions

```txt
forms.offline.download
forms.offline.sync
```

## 22.5 Export Permissions

```txt
forms.export.create
forms.export.download
```

## 22.6 Permission Rules

- Form creators cannot assign forms unless they have assignment permission.
- Respondents can only submit forms assigned to them or their organization/role/context.
- Inspectors can only complete inspection forms assigned to their inspections.
- Employers can only respond to employer/branch forms within their scope.
- Medical facilities can only respond to facility forms assigned to them.
- Food handlers can only respond to forms assigned to them.
- Exports must respect field sensitivity and user scope.
- Backend remains the source of truth.

---

# 23. Privacy and Security

## 23.1 Sensitive Data Classification

Form questions should support sensitivity labels:

```txt
Public
Internal
Confidential
Medical
Personal Identifiable Information
Financial
```

## 23.2 Field-Level Privacy

Sensitive questions should support:

```txt
Role-based visibility
Export restriction
Masked display
Audit-on-view
Medical-only visibility
```

## 23.3 Offline Security

Offline storage requirements:

```txt
Do not store unnecessary sensitive data
Encrypt local responses where feasible
Clear synced local data based on retention policy
Require authenticated session to access offline forms
Protect media attachments
```

## 23.4 Audit Logging

Audit these actions:

```txt
Template created
Template edited
Template published
Template versioned
Assignment created
Assignment sent
Form opened
Draft saved
Response submitted
Response reviewed
Response returned
Export generated
Export downloaded
Offline sync completed
Sensitive response viewed
```

---

# 24. Acceptance Criteria

## 24.1 Form Builder

- User can create a form template.
- User can add sections.
- User can add supported question types.
- User can set required fields.
- User can configure validation rules.
- User can configure skip logic.
- User can configure repeat groups.
- User can configure media upload questions.
- User can preview the form.
- User can publish the form.

## 24.2 Skip Logic

- Questions can show/hide based on previous answers.
- Sections can show/hide based on previous answers.
- Required rules can be conditional.
- Logic works during form preview and response mode.
- Logic works offline.

## 24.3 Repeat Groups

- User can create repeat groups.
- Respondent can add multiple repeated items.
- Validation applies to repeated items.
- Repeat group data exports correctly.

## 24.4 Offline Support

- User can download assigned form for offline use.
- User can complete form offline.
- User can save draft locally.
- User can capture media offline.
- User can sync when online.
- Sync failures are visible.
- Data is not silently lost.

## 24.5 Media Uploads

- User can upload or capture images.
- User can upload documents.
- User can capture signature.
- User can capture GPS.
- Media uploads can be required.
- Media sync status is visible.
- Media access is permission-controlled.

## 24.6 Submission Tracking

- Assigners can see not started, draft, submitted, reviewed, returned, overdue.
- Response progress is visible.
- Activity logs are visible to authorized users.
- Reminders can be sent.

## 24.7 Exports

- Responses can be exported to CSV.
- Responses can be exported to Excel.
- Responses can be exported to JSON.
- Repeat groups are exported cleanly.
- Attachments can be exported as a ZIP.
- Exports respect permissions and privacy.

---

# 25. Implementation Chunks for Codex

## Chunk 1: Forms Engine Foundation

### Goal

Create the core form engine models, schema structure, and base APIs.

### Tasks

- Implement `FormTemplate`.
- Implement `FormTemplateVersion`.
- Implement `FormAssignment`.
- Implement `FormRecipient`.
- Implement `FormResponse`.
- Implement `FormResponseAttachment`.
- Implement `FormResponseActivityLog`.
- Define form schema JSON format.
- Add basic template APIs.

### Acceptance Criteria

- Templates can be created.
- Template versions can be stored.
- Assignments can reference a specific template version.
- Responses can store JSON answers.
- Activity logging works.

---

## Chunk 2: Form Builder UI

### Goal

Build the form template creation interface.

### Tasks

- Create builder page.
- Add section creation.
- Add question creation.
- Add question type picker.
- Add question settings panel.
- Add preview mode.
- Add save draft.
- Add publish action.

### Acceptance Criteria

- User can build a multi-section form.
- User can preview the form.
- Template schema saves successfully.
- Published template is locked/versioned.

---

## Chunk 3: Question Types

### Goal

Implement supported question types.

### Tasks

- Add text, number, date/time, choice, media, GPS, signature, QR scan, repeat group, calculated field, and instruction types.
- Add FoodCert-specific selector fields.
- Add renderer for each question type.
- Add builder settings for each question type.

### Acceptance Criteria

- Each question type renders in builder.
- Each question type renders in response mode.
- Each question type saves and validates answers correctly.

---

## Chunk 4: Required Fields and Validation

### Goal

Implement validation engine.

### Tasks

- Add required rules.
- Add field-specific validation.
- Add custom validation messages.
- Add error summary.
- Prevent invalid submission.
- Support validation in repeat groups.
- Support offline validation.

### Acceptance Criteria

- Required fields block submission.
- Invalid fields show clear messages.
- Validation works online and offline.
- Repeat group validation works.

---

## Chunk 5: Skip Logic Engine

### Goal

Implement conditional logic.

### Tasks

- Build skip logic UI.
- Implement condition operators.
- Support show/hide questions.
- Support show/hide sections.
- Support conditional required fields.
- Support critical warning triggers.
- Ensure logic works in preview, online response, and offline response.

### Acceptance Criteria

- Form creator can configure skip logic.
- Respondent sees correct dynamic questions.
- Hidden required questions do not block submission.
- Logic works offline.

---

## Chunk 6: Repeat Groups

### Goal

Implement repeatable form sections.

### Tasks

- Add repeat group builder.
- Add min/max repeat settings.
- Add repeat item UI.
- Add validation for repeated items.
- Add repeat summary labels.
- Add export handling for repeat groups.

### Acceptance Criteria

- Respondent can add multiple repeat items.
- Repeat items can be edited and removed.
- Required repeat groups validate.
- Repeat groups export correctly.

---

## Chunk 7: Media Uploads and Evidence Capture

### Goal

Implement media and evidence support.

### Tasks

- Add image upload/capture.
- Add document upload.
- Add signature capture.
- Add GPS capture.
- Add QR/barcode scan field.
- Add media validation rules.
- Add upload progress and retry.
- Add secure storage handling.

### Acceptance Criteria

- Media can be uploaded.
- Media can be captured on device where supported.
- Required media blocks submission if missing.
- Upload status is visible.
- Media access is permission-controlled.

---

## Chunk 8: Offline Response Support

### Goal

Allow assigned forms to be completed offline and synced later.

### Tasks

- Add offline app shell support.
- Cache assigned form templates.
- Cache assignment context.
- Store local drafts in IndexedDB.
- Store media metadata and local file references.
- Add offline validation.
- Add sync queue.
- Add sync retry.
- Add conflict handling UI.
- Add offline status indicators.

### Acceptance Criteria

- Assigned form can be downloaded offline.
- Respondent can complete form offline.
- Draft persists after reload.
- Media can be captured offline.
- Response syncs when online.
- Sync failure is visible and retryable.
- No data is silently lost.

---

## Chunk 9: Submission Tracking

### Goal

Track response progress and status.

### Tasks

- Add assignment dashboard.
- Add response statuses.
- Add response activity log.
- Add response progress summary.
- Add overdue detection.
- Add reminder actions.
- Add review/return workflow.

### Acceptance Criteria

- Assigners can see submission progress.
- Response statuses update correctly.
- Overdue responses are flagged.
- Reviewer can return or mark reviewed.
- Activity log is available.

---

## Chunk 10: Export Engine

### Goal

Export response data and attachments.

### Tasks

- Add export request flow.
- Support CSV export.
- Support Excel export.
- Support JSON export.
- Support PDF summary export.
- Support attachment ZIP export.
- Flatten repeat groups.
- Add export audit logs.
- Enforce export permissions.

### Acceptance Criteria

- Users can export responses.
- Repeat groups export in usable structure.
- Attachments can be downloaded where permitted.
- Exports respect privacy and scope.
- Export generation is audit logged.

---

## Chunk 11: Inspections Integration

### Goal

Use form templates as inspection checklists.

### Tasks

- Allow State to select inspection template when creating inspection.
- Assign inspector and form template together.
- Render form inside inspection record.
- Link response to inspection.
- Generate findings from critical responses where configured.
- Support offline inspection forms.

### Acceptance Criteria

- Inspector receives assigned inspection form.
- Inspector completes form in Inspections module.
- Response is linked to inspection.
- Offline inspection response works.
- State can review submitted inspection form.

---

## Chunk 12: Employer and Medical Facility Integration

### Goal

Show assigned forms inside Employer and Medical Facility portals.

### Tasks

- Add assigned forms views.
- Add pending/submitted/returned filters.
- Render dynamic forms.
- Submit responses.
- Show response history.
- Respect organization and branch/facility scope.

### Acceptance Criteria

- Employers see assigned employer/branch forms.
- Facilities see assigned facility/accreditation/reporting forms.
- Users respond from their own portal.
- Responses link to correct organization/context.

---

## Chunk 13: Reports and Analytics

### Goal

Add form analytics and reporting.

### Tasks

- Add response rate reports.
- Add structured response analytics.
- Add inspection score analytics.
- Add risk rating reports.
- Add LGA/state filters.
- Add module context filters.

### Acceptance Criteria

- Users can analyze form responses.
- Reports can filter by template, assignment, status, date, location, and organization.
- Analytics respect permissions and privacy.

---

## Chunk 14: Permissions, Privacy, and Audit

### Goal

Secure the Forms Tool.

### Tasks

- Implement permissions.
- Implement field sensitivity.
- Implement scope checks.
- Add audit logging.
- Add export controls.
- Add sensitive field masking.

### Acceptance Criteria

- Users only see forms within scope.
- Sensitive fields are protected.
- Exports are controlled.
- Audits are recorded.

---

## Chunk 15: Final UI QA

### Goal

Confirm KoboToolbox-style functionality and FoodCert workflow integration.

### QA Checklist

- Form builder works.
- Question types work.
- Required fields work.
- Skip logic works.
- Repeat groups work.
- Offline response works.
- Media uploads work.
- Submission tracking works.
- Exports work.
- Inspection integration works.
- Employer/facility integration works.
- Permissions work.
- Mobile layout works.

---

# 26. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Build the FoodCert NG Form Builder Engine with KoboToolbox-style capabilities, integrated into FoodCert workflows.

Required capabilities:
- Form builder
- Multiple question types
- Required fields
- Validation rules
- Skip logic / conditional logic
- Repeat groups
- Offline response support
- Media uploads
- Submission tracking
- Exports

The Forms Tool should remain one parent module:
Forms Tool
- Overview
- Templates
- Assignments
- Responses
- Exports
- Reports
- Settings

Do not create separate form builders inside Inspections, Employers, Medical Facilities, Accreditation, Food Handlers, or Reports.

Implement templates, versions, assignments, recipients, responses, attachments, offline sync queue, exports, and audit logs.

Forms must be workflow-aware:
- Inspection templates appear inside assigned inspection records.
- Employer forms appear inside Employer portal.
- Medical facility forms appear inside Facility portal.
- Accreditation checklists appear inside accreditation workflow.
- Food handler forms appear inside Food Handler portal.

Support:
- Text, number, date, choice, media, GPS, signature, QR scan, repeat group, calculated field, and instruction question types.
- Skip logic with conditions.
- Required fields and validation.
- Repeat groups with min/max repeats.
- Offline form download, local draft save, media capture, sync, retry, and conflict handling.
- Exports to CSV, Excel, JSON, PDF summary, and ZIP attachments.
- Submission statuses and activity logs.
- Permissions, privacy, field sensitivity, and audit logs.

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system.
Backend permissions and scoping remain the source of truth.
```

---

# 27. MVP Build Order

1. Forms engine foundation
2. Form builder UI
3. Question types
4. Required fields and validation
5. Skip logic engine
6. Repeat groups
7. Media uploads and evidence capture
8. Offline response support
9. Submission tracking
10. Export engine
11. Inspections integration
12. Employer and medical facility integration
13. Reports and analytics
14. Permissions, privacy, and audit
15. Final UI QA
