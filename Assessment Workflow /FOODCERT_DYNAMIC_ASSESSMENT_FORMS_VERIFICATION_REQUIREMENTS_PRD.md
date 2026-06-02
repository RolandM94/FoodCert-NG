# PRD: Dynamic Assessment Forms & Verification Requirements Module — FoodCert NG

## 1. Module Name

**Dynamic Assessment Forms & Verification Requirements Module**

## 2. Product Context

FoodCert NG must separate **food handler registration** from **food handler medical verification**.

Food handler registration should remain stable because it captures identity and account information that should not change from facility to facility. However, verification requirements may change depending on:

- National health policy
- State Ministry requirements
- Food handler category
- Employer or establishment type
- Medical facility intake process
- Public health risks
- Medical assessment type
- Illness or return-to-work condition
- Updated clinical or regulatory requirements

This module introduces a configurable, versioned, policy-controlled form and requirements engine that allows the platform to manage changing verification questionnaires and assessment requirements without changing the core food handler registration process.

The guiding product principle is:

> Food Handler registration is fixed and identity-based. Medical verification requirements are configurable, versioned, and policy-controlled.

---

# 3. Product Goal

To provide a structured and controlled system for configuring, versioning, collecting, validating, and auditing medical assessment questionnaires and verification requirements while ensuring that all facilities collect data in the right format and comply with national and state rules.

---

# 4. Core Objectives

The module must allow the platform to:

1. Keep food handler registration fixed and separate from medical verification forms.
2. Define national mandatory verification requirements.
3. Allow State Ministries to add state-specific verification requirements.
4. Allow approved medical facilities to add supplementary intake questions where permitted.
5. Prevent facilities from removing or weakening mandatory national/state requirements.
6. Provide a controlled form builder with approved field types.
7. Version all form templates.
8. Preserve the exact form version used for every assessment.
9. Store responses in structured, exportable, and auditable formats.
10. Support questionnaire rules, conditional logic, validations, and required fields.
11. Protect questionnaire answers as sensitive medical data.
12. Ensure employers and public verifiers never see medical questionnaire answers.
13. Support reporting, dashboards, and audits without exposing sensitive details.
14. Support future changes to verification requirements without breaking old records.

---

# 5. Problem Statement

Food handler registration fields are relatively stable. They include identity fields such as name, date of birth, gender, NIN, passport photograph, contact information, employer, and branch.

However, medical verification is not static. A medical facility may need to collect additional intake information. A State Ministry may require extra disease exposure questions. The Federal Ministry may update national requirements. A food handler returning to work after illness may require a different questionnaire from a routine certificate renewal.

If these changing requirements are hardcoded into the registration form, the platform will become difficult to maintain and will not support policy changes. If facilities are allowed to collect information using arbitrary PDFs or free text, data quality will be poor and reporting will be unreliable.

The solution is a dynamic, structured, versioned form engine for verification requirements.

---

# 6. Key Product Principle

## 6.1 Registration Is Stable

Food handler registration should collect fixed identity and account data.

Examples:

- Full name
- Date of birth
- Gender
- NIN
- Passport photograph
- Phone number
- Email
- Employer linkage
- Branch linkage
- State and LGA

These should not be changed per facility.

## 6.2 Verification Is Configurable

Medical verification should use configurable form templates and requirement sets.

Examples:

- National health declaration
- State-specific public health questions
- Facility intake questionnaire
- Return-to-work questionnaire
- Illness reporting questionnaire
- Vaccination evidence requirements
- Lab test requirement checklist
- Doctor-only clinical review form

## 6.3 Facility Flexibility Must Be Controlled

Medical facilities may collect additional information only within permitted boundaries.

Facilities must not be allowed to:

- Remove national mandatory questions
- Remove state mandatory questions
- Change the meaning of official questions
- Make medical data visible to employers
- Use uncontrolled or unstructured form formats as the primary data source
- Ask questions outside approved medical/regulatory scope without approval

---

# 7. Key Actors

## 7.1 Federal Ministry Admin / Policy Officer

Can:

- Create national form templates.
- Configure national mandatory questions.
- Configure national verification requirement sets.
- Approve national field libraries.
- Publish national form versions.
- Retire old form versions.
- View national form usage analytics.
- Audit state and facility form configurations.

Cannot:

- Edit historical responses.
- See sensitive individual responses unless explicitly authorized.
- Delete assessment form history.

## 7.2 State Ministry Admin / Policy Officer

Can:

- Create state-specific form templates.
- Add state-specific questions to national form sets.
- Configure state verification requirements.
- Approve or reject facility-level supplementary questionnaires.
- View state form usage.
- Retire state form versions.

Cannot:

- Remove national mandatory questions.
- Weaken national validation rules.
- Edit historical form responses.

## 7.3 Medical Facility Admin

Can:

- Create facility supplementary intake forms, where permitted.
- Submit facility forms for State Ministry approval, where required.
- Configure facility department routing for forms.
- View facility form usage.
- Retire facility form versions.

Cannot:

- Change national mandatory questions.
- Change state mandatory questions.
- Publish forms that bypass approval where approval is required.
- Make medical answers visible to employers.

## 7.4 Doctor

Can:

- Review medical questionnaire responses for assigned assessments.
- Complete doctor-only forms.
- Validate declaration forms.
- Add clinical notes in restricted fields.
- Use responses to support medical decision-making.

Cannot:

- Modify locked food handler responses except through authorized correction/versioning workflow.
- Share sensitive responses with employers.
- Change published form template structure.

## 7.5 Lab Staff

Can:

- Complete lab-specific form sections where assigned.
- Enter structured lab result fields.
- Upload supporting lab documents.

Cannot:

- View unrelated clinical questionnaire sections unless authorized.
- Make final fitness decision.
- Edit food handler declaration answers.

## 7.6 Food Handler

Can:

- Complete assigned questionnaires.
- Save draft responses.
- Submit responses.
- View their submitted responses where policy allows.
- Correct responses before submission.

Cannot:

- Edit responses after doctor validation unless reopened.
- Access doctor-only notes.
- Change form requirements.

## 7.7 Employer

Can:

- View whether a food handler has completed required verification steps.
- View operational statuses such as declaration pending, assessment pending, vaccination due, fit, temporarily not fit, or certificate issued.

Cannot:

- View questionnaire answers.
- View health declaration details.
- View lab results.
- View doctor notes.
- View diagnosis.

## 7.8 Inspector

Can:

- View operational compliance status during inspection.
- Verify certificate status.
- See whether required verification was completed.

Cannot:

- View medical questionnaire answers.
- View lab results.
- View diagnosis.
- View doctor notes.

---

# 8. Module Scope

## 8.1 In Scope

This module includes:

- Dynamic form templates
- Form sections
- Form questions
- Question libraries
- Field type controls
- Conditional logic
- Validation rules
- Form versioning
- Requirement sets
- National forms
- State forms
- Facility supplementary forms
- Approval workflow for facility forms
- Form publishing
- Form retirement
- Response collection
- Response versioning
- Response locking
- Sensitive response access control
- Form usage tracking
- Form audit logs
- Structured export rules
- Integration with medical assessment workflow

## 8.2 Out of Scope for MVP

The following may be deferred:

- AI-assisted form creation
- Offline form collection
- Complex clinical scoring engine
- Natural language medical decision support
- External EMR integration
- Third-party form marketplace
- Multilingual dynamic form translation management
- Patient-facing mobile offline sync
- Advanced ontology mapping such as SNOMED/LOINC

---

# 9. Relationship With Food Handler Registration

## 9.1 Food Handler Registration Must Remain Fixed

The existing registration process should remain separate from dynamic assessment questionnaires.

Food handler registration should capture identity and account fields.

Recommended fixed registration fields:

- Full name
- Date of birth
- Gender
- NIN
- Passport photograph
- Phone number
- Email
- Password or account access method
- Employer linkage, where applicable
- Branch linkage, where applicable
- State
- LGA

## 9.2 Verification Requirements Must Be Dynamic

After registration, the platform determines what verification requirements apply to the food handler.

This may depend on:

- Assessment type
- State
- Facility
- Food handler category
- Employer category
- Previous certificate status
- Illness history
- Return-to-work status
- Vaccination status
- National/state policy

## 9.3 Separation Rule

Dynamic verification forms must never be implemented by adding random fields directly to the core `FoodHandlerProfile` table.

Instead:

- Registration data belongs to `FoodHandlerProfile`.
- Verification data belongs to `MedicalAssessment`, `AssessmentFormTemplate`, and `AssessmentFormResponse`.

---

# 10. Form Ownership Levels

The system must support multiple ownership levels.

| Level | Owner | Example |
|---|---|---|
| System | Platform/Super Admin | Built-in workflow fields |
| National | Federal Ministry | Mandatory national declaration questions |
| State | State Ministry | State-specific disease exposure questions |
| Facility | Medical Facility | Facility intake questionnaire |
| Assessment Type | Policy Engine | Return-to-work form, renewal form |

## 10.1 National Forms

National forms define the minimum mandatory requirements across the country.

Examples:

- National food handler health declaration
- National vaccination declaration
- National consent form
- National return-to-work screening form

National mandatory questions cannot be removed by states or facilities.

## 10.2 State Forms

State forms add state-specific requirements.

Examples:

- State outbreak exposure questions
- State-required public health declarations
- State-specific consent or attestation
- State-specific high-risk food sector questions

State questions apply only within that state.

## 10.3 Facility Forms

Facility forms are supplementary forms used by approved medical facilities.

Examples:

- Facility intake form
- Facility triage questionnaire
- Additional clinical screening questions
- Facility administrative intake questions

Facility forms must be controlled and may require State Ministry approval before use.

---

# 11. Form Types

The platform should support different form types.

## 11.1 Health Declaration Form

Completed by food handler and validated by doctor.

## 11.2 Facility Intake Form

Completed by food handler or facility staff before assessment.

## 11.3 Doctor Clinical Review Form

Completed by doctor during assessment.

## 11.4 Lab Result Form

Completed by laboratory staff.

## 11.5 Vaccination Review Form

Completed by doctor or authorized clinical staff.

## 11.6 Return-to-Work Form

Completed when a food handler is returning after illness or exclusion.

## 11.7 Illness Report Form

Completed by food handler, employer, doctor, or public health officer depending on workflow.

## 11.8 State Validation Checklist

Completed by State Ministry during certificate validation.

## 11.9 Inspection Support Form

Used by inspectors where a configurable checklist is needed. This should integrate with the Inspector & Enforcement Module but follow the same form engine principles.

---

# 12. Form Template Lifecycle

## 12.1 Form Template Statuses

Use the following statuses:

- Draft
- Pending Approval
- Approved
- Published
- Active
- Retired
- Rejected
- Archived

## 12.2 Form Template Flow

```txt
User creates form template
→ Adds sections and questions
→ Configures validation and logic
→ Saves as draft
→ Submits for approval, where required
→ Approver reviews
→ Form is approved or rejected
→ Approved form is published
→ Published version becomes available for assessments
→ Future edits create new version
→ Old version remains available for historical records
```

## 12.3 Form Versioning Rule

Once a form is published and used in an assessment, it must not be edited in place.

Any change must create a new version.

Example:

```txt
Facility Intake Form v1 used for Assessment A
Facility Intake Form v2 used for Assessment B
```

Assessment A must always show the exact v1 questions and answers used at the time.

---

# 13. Requirement Sets

## 13.1 Purpose

Requirement sets define which forms, documents, tests, and verification steps are required for a specific assessment context.

## 13.2 Requirement Set Examples

- Standard new food handler assessment
- Certificate renewal assessment
- Return-to-work assessment
- High-risk food handler assessment
- State-specific outbreak response assessment
- Facility-specific intake assessment

## 13.3 Requirement Set Fields

- Name
- Description
- Scope: national/state/facility/system
- State, if applicable
- Facility, if applicable
- Assessment type
- Food handler category
- Employer category
- Required forms
- Required documents
- Required lab tests
- Required vaccinations
- Required approvals
- Effective start date
- Effective end date
- Status
- Version

## 13.4 Requirement Set Resolution

When an assessment is created, the system should determine applicable requirements by evaluating:

1. National requirements
2. State requirements
3. Assessment type requirements
4. Food handler category requirements
5. Facility-approved supplementary requirements
6. Public health/illness-specific requirements

## 13.5 Conflict Rule

Where requirements conflict:

- National mandatory requirement wins over state/facility.
- State mandatory requirement wins over facility.
- Facility can only add supplementary requirements.
- Facility cannot remove or weaken mandatory requirements.

---

# 14. Form Builder Requirements

## 14.1 Form Builder Features

Authorized users should be able to:

- Create form template
- Add sections
- Add questions
- Select question type
- Mark question required/optional
- Add help text
- Add validation rules
- Add conditional logic
- Add scoring/risk flags, where permitted
- Preview form
- Save draft
- Submit for approval
- Publish approved version
- Retire old version
- Duplicate form as new version

## 14.2 Form Section Fields

- Section title
- Section description
- Sort order
- Visibility rules
- Required completion flag

## 14.3 Question Fields

- Question key
- Question label
- Question type
- Help text
- Placeholder
- Required flag
- Options, where applicable
- Validation rules
- Conditional visibility rules
- Risk flag mapping
- Privacy classification
- Respondent role
- Sort order

## 14.4 Question Key Rules

Question keys must be:

- Unique within form version
- Stable within the version
- Machine-readable
- Lowercase snake_case recommended
- Not reused for different meanings across versions

Example:

```txt
recent_diarrhoea_vomiting
cholera_contact_last_5_days
hepatitis_a_certificate_uploaded
```

---

# 15. Approved Field Types

Facilities and ministries must only use approved field types.

## 15.1 Basic Field Types

- Short text
- Long text
- Number
- Date
- Time
- Date/time
- Yes/No
- Single choice
- Multiple choice
- Checkbox confirmation
- Dropdown
- Phone number
- Email
- File upload

## 15.2 Medical Field Types

- Temperature
- Weight
- Height
- Blood pressure
- Pulse rate
- Symptom checklist
- Exposure history
- Vaccination date
- Vaccine dose
- Lab result status
- Clinical note, restricted
- Doctor-only note
- Lab-only note

## 15.3 Controlled Field Rules

Medical field types must carry privacy classification.

Examples:

| Field Type | Privacy Classification |
|---|---|
| Health declaration answer | Medical Sensitive |
| Doctor note | Restricted Medical |
| Lab result | Restricted Medical |
| Vaccination status | Employer Safe Summary |
| Certificate status | Public/Employer Safe |

---

# 16. Conditional Logic

## 16.1 Purpose

Conditional logic allows forms to show relevant questions based on previous answers or assessment context.

## 16.2 Examples

If food handler answers `Yes` to diarrhoea/vomiting:

```txt
Show: Date symptoms started
Show: Are symptoms still ongoing?
Show: Date symptoms stopped
Flag: Medical review required
```

If Hepatitis A certificate is missing:

```txt
Show: Has vaccine been administered today?
Show: Next dose date
Flag: Vaccination incomplete
```

If assessment type is Return-to-Work:

```txt
Show: Symptom end date
Show: Clearance test result
Show: Doctor clearance decision
```

## 16.3 Conditional Logic Rules

- Logic must be stored in structured JSON.
- Logic must be validated before publishing.
- Broken logic should prevent publishing.
- Logic must be versioned with the form.
- Frontend should render logic but backend must validate logic.

---

# 17. Validation Rules

## 17.1 Validation Types

The form engine should support:

- Required field
- Minimum length
- Maximum length
- Minimum value
- Maximum value
- Date before/after
- File type restriction
- File size restriction
- Regex pattern
- Allowed choices
- Conditional required fields
- Unique within assessment, where applicable

## 17.2 Backend Validation

Backend must validate all form responses.

Frontend validation improves user experience but must not be trusted as the source of truth.

## 17.3 Invalid Response Handling

If a response fails validation:

- Return field-level errors.
- Prevent submission.
- Preserve draft response.
- Show user-friendly error message.

---

# 18. Risk Flagging

## 18.1 Purpose

Certain answers should trigger risk flags for doctor review or public health follow-up.

## 18.2 Risk Flag Types

- Medical Review Required
- Lab Test Required
- Vaccination Required
- Temporary Exclusion Recommended
- Return-to-Work Required
- Public Health Clearance Required
- State Review Required

## 18.3 Risk Flag Rules

- Risk flags do not automatically equal final decision.
- Doctor reviews risk flags and makes clinical decision.
- Risk flags should appear in doctor dashboard.
- Employers should see only operational status, not specific medical risk answer.

---

# 19. Response Collection Workflow

## 19.1 Food Handler Response Flow

```txt
Assessment created
→ System resolves applicable requirement set
→ Food handler sees required forms
→ Food handler completes forms
→ Food handler saves draft or submits
→ System validates responses
→ Submitted responses are locked
→ Doctor reviews responses
```

## 19.2 Doctor Response Flow

```txt
Doctor opens assigned assessment
→ Reviews food handler forms
→ Completes clinical review form
→ Adds doctor-only notes
→ Validates declaration
→ Proceeds with assessment workflow
```

## 19.3 Lab Staff Response Flow

```txt
Lab request created
→ Lab staff opens lab form
→ Enters structured result fields
→ Uploads result document
→ Submits to doctor
→ Doctor reviews result
```

## 19.4 Facility Staff Response Flow

```txt
Facility staff opens intake form
→ Completes administrative or triage questions
→ Saves/submits response
→ Doctor sees approved relevant responses
```

---

# 20. Response Statuses

Use the following statuses:

- Not Started
- Draft
- Submitted
- Under Review
- Clarification Requested
- Reopened
- Resubmitted
- Validated
- Locked
- Superseded
- Archived

---

# 21. Response Versioning

## 21.1 Purpose

If a submitted response is corrected or reopened, the system must preserve previous response versions.

## 21.2 Rules

- Submitted responses are locked.
- Reopening a response creates a new version.
- Old responses remain viewable to authorized users.
- Audit trail must show who reopened and why.
- Assessment record should identify the final accepted response version.

## 21.3 Example

```txt
Health Declaration Response v1 submitted by food handler
Doctor requests clarification
Response reopened
Food handler submits Response v2
Doctor validates Response v2
Response v1 remains archived
```

---

# 22. Structured Data Format

## 22.1 Form Template JSON

Example:

```json
{
  "form_template_id": "uuid",
  "version": 3,
  "scope": "facility",
  "form_type": "facility_intake",
  "sections": [
    {
      "key": "facility_intake",
      "title": "Facility Intake Questions",
      "questions": [
        {
          "key": "recent_antibiotics",
          "label": "Have you used antibiotics in the last 14 days?",
          "type": "yes_no",
          "required": true,
          "privacy_classification": "medical_sensitive"
        }
      ]
    }
  ]
}
```

## 22.2 Response JSON

Example:

```json
{
  "form_template_id": "uuid",
  "form_version": 3,
  "assessment_id": "uuid",
  "responses": {
    "recent_antibiotics": true
  },
  "submitted_by": "uuid",
  "submitted_at": "2026-06-01T10:00:00Z"
}
```

## 22.3 Snapshot Rule

Every response must preserve:

- Form template ID
- Form version
- Question snapshot
- Response values
- Respondent role
- Submission timestamp

This prevents future template changes from altering historical assessment records.

---

# 23. Approval Workflow for Facility Forms

## 23.1 Purpose

Facility supplementary forms may need State Ministry approval before use.

## 23.2 Workflow

```txt
Facility creates supplementary form
→ Facility submits for State approval
→ State reviews questions and purpose
→ State approves, rejects, or requests changes
→ Approved form can be published
→ Published form is included in facility assessments
```

## 23.3 Review Criteria

State reviewer should check:

- Questions are relevant to medical assessment.
- Questions do not duplicate/conflict with national/state mandatory questions.
- Questions use approved field types.
- Questions have correct privacy classification.
- Questions do not request unnecessary sensitive data.
- Form has clear purpose.
- Validation rules are appropriate.

## 23.4 Facility Form Rejection Reasons

- Unnecessary sensitive data
- Unclear purpose
- Conflicts with national form
- Conflicts with state form
- Invalid field types
- Poorly structured questions
- Missing privacy classification
- Disallowed employer visibility

---

# 24. Requirement Resolution Engine

## 24.1 Purpose

The system must determine which forms and requirements apply to a specific assessment.

## 24.2 Inputs

The engine should consider:

- Assessment type
- State
- Facility
- Food handler category
- Employer category
- Certificate status
- Renewal status
- Illness status
- Return-to-work status
- Policy configuration
- Public health alerts, future

## 24.3 Output

The engine should return:

- Required forms
- Optional forms
- Required documents
- Required lab tests
- Required vaccination evidence
- Required approvals
- Blocking requirements
- Non-blocking advisory requirements

## 24.4 Example Output

```json
{
  "assessment_id": "uuid",
  "required_forms": [
    "national_health_declaration_v4",
    "state_lagos_public_health_addendum_v2",
    "facility_intake_form_v1"
  ],
  "required_lab_tests": [
    "stool_microscopy",
    "stool_culture_sensitivity",
    "hepatitis_a_antigen"
  ],
  "required_vaccinations": [
    "typhoid",
    "hepatitis_a"
  ],
  "blocking_requirements": [
    "national_health_declaration_v4",
    "payment_confirmed",
    "nin_verified"
  ]
}
```

---

# 25. Integration With Existing Modules

## 25.1 Medical Assessment Workflow Module

The assessment workflow must use this module to determine required forms and completion status.

Integration points:

- Assessment creation triggers requirement resolution.
- Declaration form is generated from active template.
- Doctor review uses form responses.
- Incomplete required forms block assessment progression.
- Risk flags feed into doctor dashboard.

## 25.2 Medical Facility Module

Facilities use this module to create supplementary forms.

Integration points:

- Facility admin creates facility intake form.
- Facility form requires State approval if policy requires.
- Approved facility form applies only to that facility.
- Facility staff may complete facility-assigned sections.

## 25.3 State Ministry Module

State Ministry uses this module to manage state-specific requirements.

Integration points:

- State policy officer creates state forms.
- State approves facility forms.
- State validation desk sees requirement completion checklist.
- State can audit forms used in assessments.

## 25.4 Federal Ministry Module

Federal Ministry uses this module to set national mandatory requirements.

Integration points:

- National form library
- National mandatory declaration questions
- National field type library
- National requirement sets
- National form usage analytics

## 25.5 Reports, Dashboards & M&E Module

The reporting module should consume aggregate form completion and risk flag data.

Integration points:

- Form completion rate
- Declaration risk flag count
- State-specific question analytics
- Facility form usage
- Return-to-work form completion
- Data quality checks

Reports must not expose sensitive individual responses unless authorized.

## 25.6 Notifications Module

Notifications should be sent for:

- Form assigned
- Form incomplete
- Form submitted
- Doctor clarification requested
- Facility form approved/rejected
- New form version published
- Required form overdue

---

# 26. Privacy and Data Protection

## 26.1 Privacy Classifications

Each form field must have a privacy classification.

Recommended classifications:

- Public Safe
- Employer Safe Summary
- Inspector Safe Summary
- Medical Sensitive
- Restricted Medical
- Internal Administrative
- Regulatory Restricted

## 26.2 Visibility Rules

Employers may see:

- Form completion status
- Operational compliance status
- Vaccination summary status
- Assessment readiness status

Employers must not see:

- Health declaration answers
- Facility intake medical answers
- Doctor notes
- Lab fields
- Diagnosis
- Restricted medical responses

Public users may see:

- Nothing from assessment forms

Inspectors may see:

- Operational compliance summary only

Doctors may see:

- Assigned assessment form responses relevant to medical review

State regulators may see:

- Assessment summary and required evidence according to permission

Federal users may see:

- Aggregates by default

## 26.3 Access Logging

Viewing sensitive responses must create audit logs.

---

# 27. Data Model Requirements

## 27.1 AssessmentFormTemplate

```python
class AssessmentFormTemplate(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=100)
    scope = models.CharField(max_length=50)  # system, national, state, facility
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    facility = models.ForeignKey("facilities.MedicalFacility", null=True, blank=True, on_delete=models.SET_NULL)
    owner_organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50)
    is_mandatory = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="approved_assessment_forms", on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey("accounts.User", null=True, related_name="created_assessment_forms", on_delete=models.SET_NULL)
    parent_template = models.ForeignKey("self", null=True, blank=True, related_name="versions", on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 27.2 AssessmentFormSection

```python
class AssessmentFormSection(models.Model):
    id = models.UUIDField(primary_key=True)
    template = models.ForeignKey("forms.AssessmentFormTemplate", on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    visibility_rules = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 27.3 AssessmentFormQuestion

```python
class AssessmentFormQuestion(models.Model):
    id = models.UUIDField(primary_key=True)
    section = models.ForeignKey("forms.AssessmentFormSection", on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    label = models.TextField()
    help_text = models.TextField(blank=True)
    question_type = models.CharField(max_length=80)
    required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)
    validation_rules = models.JSONField(default=dict, blank=True)
    conditional_logic = models.JSONField(default=dict, blank=True)
    risk_flag_rules = models.JSONField(default=dict, blank=True)
    privacy_classification = models.CharField(max_length=80)
    respondent_role = models.CharField(max_length=80)  # food_handler, doctor, lab_staff, facility_staff, state_user
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 27.4 AssessmentRequirementSet

```python
class AssessmentRequirementSet(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=50)  # national, state, facility, system
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    facility = models.ForeignKey("facilities.MedicalFacility", null=True, blank=True, on_delete=models.SET_NULL)
    assessment_type = models.CharField(max_length=100)
    food_handler_category = models.CharField(max_length=100, blank=True)
    employer_category = models.CharField(max_length=100, blank=True)
    required_forms = models.ManyToManyField("forms.AssessmentFormTemplate", blank=True)
    required_documents = models.JSONField(default=list, blank=True)
    required_lab_tests = models.JSONField(default=list, blank=True)
    required_vaccinations = models.JSONField(default=list, blank=True)
    required_approvals = models.JSONField(default=list, blank=True)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 27.5 AssessmentFormResponse

```python
class AssessmentFormResponse(models.Model):
    id = models.UUIDField(primary_key=True)
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE)
    template = models.ForeignKey("forms.AssessmentFormTemplate", on_delete=models.PROTECT)
    template_version = models.PositiveIntegerField()
    respondent = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    respondent_role = models.CharField(max_length=80)
    status = models.CharField(max_length=50)
    response_data = models.JSONField(default=dict)
    question_snapshot = models.JSONField(default=dict)
    risk_flags = models.JSONField(default=list, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="validated_form_responses", on_delete=models.SET_NULL)
    validated_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    previous_response = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 27.6 FormApprovalRequest

```python
class FormApprovalRequest(models.Model):
    id = models.UUIDField(primary_key=True)
    template = models.ForeignKey("forms.AssessmentFormTemplate", on_delete=models.CASCADE)
    submitted_by = models.ForeignKey("accounts.User", related_name="submitted_form_approvals", null=True, on_delete=models.SET_NULL)
    reviewed_by = models.ForeignKey("accounts.User", related_name="reviewed_form_approvals", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50)
    submission_note = models.TextField(blank=True)
    review_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
```

---

# 28. API Requirements

## 28.1 Form Templates

```txt
GET    /api/forms/templates
POST   /api/forms/templates
GET    /api/forms/templates/:id
PATCH  /api/forms/templates/:id
POST   /api/forms/templates/:id/duplicate
POST   /api/forms/templates/:id/submit-for-approval
POST   /api/forms/templates/:id/approve
POST   /api/forms/templates/:id/reject
POST   /api/forms/templates/:id/publish
POST   /api/forms/templates/:id/retire
GET    /api/forms/templates/:id/versions
```

## 28.2 Form Sections and Questions

```txt
GET    /api/forms/templates/:id/sections
POST   /api/forms/templates/:id/sections
PATCH  /api/forms/sections/:section_id
DELETE /api/forms/sections/:section_id

GET    /api/forms/sections/:section_id/questions
POST   /api/forms/sections/:section_id/questions
PATCH  /api/forms/questions/:question_id
DELETE /api/forms/questions/:question_id
```

## 28.3 Requirement Sets

```txt
GET    /api/forms/requirement-sets
POST   /api/forms/requirement-sets
GET    /api/forms/requirement-sets/:id
PATCH  /api/forms/requirement-sets/:id
POST   /api/forms/requirement-sets/:id/publish
POST   /api/forms/requirement-sets/:id/retire
POST   /api/forms/requirements/resolve
GET    /api/assessments/:assessment_id/requirements
```

## 28.4 Form Responses

```txt
GET    /api/assessments/:assessment_id/forms
GET    /api/assessments/:assessment_id/forms/:template_id
POST   /api/assessments/:assessment_id/forms/:template_id/responses
PATCH  /api/form-responses/:response_id
POST   /api/form-responses/:response_id/submit
POST   /api/form-responses/:response_id/validate
POST   /api/form-responses/:response_id/reopen
GET    /api/form-responses/:response_id/versions
```

## 28.5 Form Analytics and Audit

```txt
GET /api/forms/analytics/usage
GET /api/forms/analytics/completion
GET /api/forms/analytics/risk-flags
GET /api/forms/templates/:id/audit
GET /api/form-responses/:response_id/audit
```

---

# 29. Frontend Routes

## 29.1 Admin / Federal Routes

```txt
/app/admin/forms
/app/admin/forms/new
/app/admin/forms/[id]
/app/admin/forms/[id]/builder
/app/admin/forms/[id]/versions
/app/admin/forms/requirement-sets
/app/admin/forms/requirement-sets/[id]
/app/admin/forms/field-library
```

## 29.2 State Ministry Routes

```txt
/app/state/forms
/app/state/forms/new
/app/state/forms/[id]
/app/state/forms/[id]/builder
/app/state/forms/approval-requests
/app/state/forms/approval-requests/[id]
/app/state/requirement-sets
```

## 29.3 Facility Routes

```txt
/app/facility/forms
/app/facility/forms/new
/app/facility/forms/[id]
/app/facility/forms/[id]/builder
/app/facility/forms/[id]/submit-for-approval
/app/facility/forms/approval-status
```

## 29.4 Assessment Routes

```txt
/app/food-handler/assessment/[id]/forms
/app/food-handler/assessment/[id]/forms/[template_id]
/app/doctor/assessments/[id]/forms
/app/doctor/assessments/[id]/forms/[response_id]
/app/lab/assessments/[id]/forms/[template_id]
```

---

# 30. Core Frontend Components

- FormTemplateTable
- FormTemplateStatusBadge
- FormBuilderCanvas
- FormSectionEditor
- FormQuestionEditor
- QuestionTypeSelector
- FieldValidationEditor
- ConditionalLogicBuilder
- RiskFlagRuleBuilder
- PrivacyClassificationSelector
- FormPreviewPanel
- RequirementSetBuilder
- RequirementResolverPreview
- FormApprovalReviewPanel
- DynamicAssessmentFormRenderer
- FormResponseStatusBadge
- FormResponseReviewPanel
- FormVersionHistoryPanel
- FormAuditTimeline
- FormUsageAnalyticsCards

---

# 31. Permissions and Access Control

## 31.1 Federal Admin / Policy Officer

Can:

- Manage national forms.
- Manage national requirement sets.
- Manage field type library.
- Publish national templates.
- View national form analytics.

## 31.2 State Admin / Policy Officer

Can:

- Manage state forms.
- Manage state requirement sets.
- Approve/reject facility forms.
- View state form analytics.

## 31.3 Facility Admin

Can:

- Create facility supplementary forms.
- Submit forms for approval.
- Retire facility forms.
- View facility form analytics.

## 31.4 Doctor

Can:

- View assigned assessment responses.
- Validate declaration responses.
- Complete doctor-only forms.

## 31.5 Lab Staff

Can:

- Complete lab-specific forms.

## 31.6 Food Handler

Can:

- Complete assigned food-handler forms.
- View own submitted forms where allowed.

## 31.7 Employer

Can:

- View completion status only.

Cannot:

- View medical questionnaire answers.

---

# 32. Audit Logs

Create audit logs for:

- Form template created
- Form template edited
- Form template duplicated
- Section added/updated/deleted
- Question added/updated/deleted
- Form submitted for approval
- Form approved/rejected
- Form published
- Form retired
- Requirement set created/updated/published/retired
- Requirement resolution performed
- Form assigned to assessment
- Form response draft saved
- Form response submitted
- Form response validated
- Form response reopened
- Form response version created
- Sensitive response viewed
- Form export generated

---

# 33. Reports and Analytics

## 33.1 Operational Reports

- Form completion report
- Incomplete required forms report
- Facility form usage report
- State form usage report
- Form approval pending report
- Form version usage report

## 33.2 Data Quality Reports

- Missing required responses
- Invalid response patterns
- Duplicate facility questions
- Deprecated form still in use
- Forms with high clarification rates
- Forms with high risk flag rates

## 33.3 M&E Indicators

Suggested indicators:

- Percentage of assessments with completed mandatory declaration
- Average time to complete food handler questionnaire
- Percentage of facility forms approved/rejected
- Number of active form versions by state
- Number of risk flags by state/facility
- Number of clarification requests per form
- Percentage of assessments blocked by missing forms

---

# 34. Notifications

Send notifications for:

- Form assigned to food handler
- Form incomplete reminder
- Form submitted
- Doctor clarification requested
- Form reopened
- Facility form submitted for approval
- Facility form approved
- Facility form rejected
- New form version published
- Requirement set updated
- Required form overdue

---

# 35. Acceptance Criteria

## 35.1 Registration Separation

- Food handler registration remains fixed and separate from verification forms.
- Dynamic questionnaire fields are not added directly to food handler profile.
- Assessment-specific responses are linked to MedicalAssessment.

## 35.2 Form Builder

- Authorized users can create form templates.
- Users can add sections and questions.
- Users can select only approved field types.
- Users can configure validation rules.
- Users can configure conditional logic.
- Users can preview forms before publishing.

## 35.3 Versioning

- Published forms cannot be edited in place.
- Changes create new versions.
- Historical assessments show the exact form version used.
- Old responses remain valid and auditable.

## 35.4 Requirement Sets

- System can resolve applicable requirements for an assessment.
- National mandatory requirements cannot be removed by state/facility.
- State mandatory requirements cannot be removed by facility.
- Facility forms can only add supplementary requirements.

## 35.5 Response Collection

- Food handlers can complete assigned forms.
- Doctors can validate assigned responses.
- Lab staff can complete lab forms.
- Submitted responses are locked.
- Reopened responses create new versions.

## 35.6 Privacy

- Employers see only completion/operational status.
- Public users see no form responses.
- Inspectors see no medical questionnaire answers.
- Sensitive response access is audit logged.

## 35.7 Facility Form Approval

- Facility can submit supplementary form for approval.
- State can approve/reject/request changes.
- Facility form cannot be published until approved where policy requires.

## 35.8 Reporting

- Admin users can view form usage reports.
- Reports respect privacy settings.
- Risk flag analytics are aggregate unless authorized.

---

# 36. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Dynamic Assessment Forms & Verification Requirements Module for FoodCert NG.

The module must keep food handler registration fixed and separate from medical verification forms. It must support dynamic assessment form templates, sections, questions, approved field types, validation rules, conditional logic, risk flag rules, privacy classification, form versioning, requirement sets, requirement resolution, response collection, response locking, response versioning, approval workflow for facility forms, national/state/facility form scopes, audit logs, privacy-safe serializers, analytics, reports, and frontend form builder pages.

Important rules:
- Do not add changing questionnaire fields directly to FoodHandlerProfile.
- Registration captures fixed identity/account data only.
- Verification requirements are configured through form templates and requirement sets.
- National mandatory questions cannot be removed by states or facilities.
- State mandatory questions cannot be removed by facilities.
- Facility forms are supplementary and may require State approval.
- Published forms cannot be edited in place; edits create new versions.
- Every assessment response must preserve the form version and question snapshot used at the time.
- Employers must never see medical questionnaire answers.
- Public users must never see assessment form responses.
- Sensitive response access must be audit logged.
- Backend must validate form responses and requirement completion.

Build backend models, serializers, services, permissions, API endpoints, tests, frontend pages, and reusable form renderer components for the module.
```

---

# 37. MVP Build Order

1. AssessmentFormTemplate model
2. AssessmentFormSection model
3. AssessmentFormQuestion model
4. AssessmentRequirementSet model
5. AssessmentFormResponse model
6. Form builder API
7. Approved field type library
8. Validation rule engine
9. Conditional logic engine
10. Form versioning service
11. Requirement resolution service
12. Response collection API
13. Response locking/versioning workflow
14. Facility form approval workflow
15. Privacy-safe serializers
16. Form builder frontend
17. Dynamic form renderer frontend
18. Food handler form completion page
19. Doctor form review page
20. Requirement completion checklist
21. Form analytics dashboard
22. Audit logs
23. Permission tests
24. Versioning tests
25. Privacy tests
