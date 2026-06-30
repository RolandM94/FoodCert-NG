# Updated PRD: Health Declaration Form Template Inheritance & Medical Assessment Workflow

**Application:** FoodCert / National Food Handlers Medical Test Platform  
**Module:** Food Handler Medical Test, Health Declaration, Facility Assessment, Certificate Workflow  
**Primary Users:** Federal Account, State Account, Medical Facility, Food Handler, Employer/Food Business, Medical Doctor, Lab Officer  
**Guideline Basis:** National Guidelines for Food Handlers’ Medical Test 2024. The guideline requires food handlers to complete and certify a declaration form disclosing recent illnesses that may pose food safety risks, and requires the medical doctor to validate the completed declaration questionnaire. It also requires medical assessment, lab investigations, doctor review, certificate generation, QR verification, and central storage of certificates.

---

## 1. Product Objective

Develop a configurable **Health Declaration Form Template System** and connect it to the full **Food Handler Medical Test Workflow**.

The key principle is:

```text
Federal Government creates the base declaration form.
State adopts the Federal form and may add extra requirements.
Medical Facility adopts Federal + State form and may add facility-specific requirements.
Food Handler fills the final merged declaration form.
Medical Doctor validates the declaration during the assessment.
```

Lower levels may add requirements, but they must not remove, weaken, hide, or override higher-level requirements.

---

## 2. Core Governance Logic

### 2.1 Form Ownership Hierarchy

```text
Federal Account
    ↓ creates
National Health Declaration Form Template
    ↓ adopted by
State Account
    ↓ adds State-specific fields
State Health Declaration Extension
    ↓ adopted by
Medical Facility
    ↓ adds facility-specific fields
Facility Health Declaration Extension
    ↓ completed by
Food Handler
```

### 2.2 Permissions by Level

| User Level | Can Create | Can Add Fields | Can Edit Own Fields | Can Delete Own Fields | Can Delete Parent Fields |
|---|---|---:|---:|---:|---:|
| Federal | National base template | Yes | Yes | Only through new version | N/A |
| State | State extension | Yes | Yes | Yes, before publish | No |
| Medical Facility | Facility extension | Yes | Yes | Yes, before publish | No |
| Food Handler | Response only | No | No | No | No |
| Medical Doctor | Validation only | No | No | No | No |

---

## 3. Form Builder Requirement

The existing **Forms Tool/Form Builder Engine** should be used, but it must be upgraded to support:

1. Template inheritance
2. Locked inherited fields
3. Field ownership
4. Versioning
5. Publishing workflow
6. Dynamic form merging
7. Response locking
8. Doctor validation
9. Audit logs

The Form Builder should no longer only create ordinary forms. It should also support regulated policy-backed forms.

---

## 4. Health Declaration Form Template Structure

### 4.1 Federal Base Template

The Federal Government account creates the **National Food Handler Health Declaration Form Template**.

This form should contain the minimum mandatory national fields.

#### Federal Base Sections

| Section | Example Fields |
|---|---|
| Identity Information | Full name, NIN, DOB, gender, passport photo |
| Food Handler Information | Food handler category, employer if applicable |
| Recent Illness Declaration | Fever, jaundice, diarrhoea, vomiting, cough/flu, sore throat |
| Communicable Disease History | Typhoid, cholera, hepatitis A, dysentery, gastrointestinal infection |
| Skin and Infection Declaration | Skin infection, boils, cuts, lesions, discharge from eyes/nose/ears/mouth |
| Vaccination History | Typhoid certificate, Hepatitis A certificate |
| Consent | Consent for medical assessment and certificate processing |
| Declaration Statement | Food handler confirms information is true |

The guideline specifically requires disclosure of recent illnesses that pose a food safety risk, including typhoid, cholera, hepatitis A, dysentery, gastrointestinal infections, and skin infections.

---

### 4.2 State Extension Template

A State account adopts the active Federal template and may add State-specific fields.

Examples:

| State Addition Type | Example |
|---|---|
| Local outbreak screening | “Have you recently been exposed to cholera in your LGA?” |
| State public health notice | “This state requires additional cholera screening during outbreak periods.” |
| State consent | Consent for state public health surveillance |
| State-specific health risk | “Have you worked in a market with a reported disease outbreak?” |
| State administrative field | State food handler registration number |

#### State Restrictions

The State cannot:

```text
Delete Federal fields
Hide Federal fields
Rename Federal fields
Make Federal required fields optional
Change Federal risk logic
Change Federal validation rules
Change Federal display meaning
```

---

### 4.3 Medical Facility Extension Template

A medical facility adopts the active Federal + State form and may add facility-specific fields.

Examples:

| Facility Addition Type | Example |
|---|---|
| Facility intake question | “Have you previously been tested at this facility?” |
| Clinical preparation | “Have you taken antibiotics recently?” |
| Operational preference | Preferred appointment time or unit |
| Facility consent | Consent for facility record handling |
| Internal triage | “Do you require special assistance at the facility?” |

#### Medical Facility Restrictions

The facility cannot:

```text
Delete Federal fields
Delete State fields
Hide inherited fields
Make inherited fields optional
Override inherited validation
Change inherited risk scoring
```

---

## 5. Final Form Generation Logic

When a food handler applies for a medical test and selects a facility, the system dynamically generates the final declaration form.

```text
Food Handler selects medical facility
    ↓
System identifies facility state
    ↓
System loads active Federal declaration template
    ↓
System loads active State extension template
    ↓
System loads active Facility extension template
    ↓
System merges all templates
    ↓
Food Handler completes final declaration form
```

Example:

```text
Final Form =
Federal mandatory questions
+ Lagos State additional questions
+ Facility A additional questions
```

---

## 6. Form Field Ownership Logic

Every field must carry an ownership level.

| Field Attribute | Description |
|---|---|
| `owner_level` | federal, state, facility |
| `owner_id` | Federal, State, or Facility ID |
| `locked` | True if inherited from parent level |
| `required` | Whether response is mandatory |
| `risk_flag` | Whether answer can trigger medical risk review |
| `inherited_from_field_id` | Parent field reference |
| `editable_by_child` | Default false for inherited fields |
| `deletable_by_child` | Always false for inherited fields |

---

## 7. Versioning Logic

Published templates must be immutable.

### Template Lifecycle

```text
Draft
    ↓
Submitted for Review
    ↓
Approved
    ↓
Published
    ↓
Active
    ↓
Superseded / Archived
```

### Version Rules

| Rule | Logic |
|---|---|
| Draft templates can be edited | Yes |
| Published templates can be edited directly | No |
| Editing a published template creates new version | Yes |
| Active assessments keep original form version | Yes |
| New assessments use latest active version | Yes |
| Child templates must be linked to active parent version | Yes |
| If Federal publishes new version, States are notified | Yes |
| States may adopt new Federal version | Yes |
| Facilities may adopt updated State version | Yes |

---

## 8. Food Handler Declaration Submission Flow

```text
Food Handler / Employer starts assessment request
    ↓
Food Handler selects or confirms approved medical facility
    ↓
System generates final declaration form
    ↓
Food Handler fills the declaration form
    ↓
Food Handler gives consent
    ↓
Food Handler submits declaration
    ↓
Declaration becomes locked
    ↓
Doctor/facility receives declaration for validation
```

### Submission Rules

| Rule | Logic |
|---|---|
| Only the food handler can complete the declaration | Yes |
| Employer cannot complete health declaration for food handler | Yes |
| Declaration required before appointment confirmation | Yes |
| Submitted declaration is locked | Yes |
| Corrections require reopen workflow | Yes |
| Every submission is audit logged | Yes |
| Doctor validates but does not alter original answers | Yes |

---

## 9. Doctor Validation Flow

```text
Medical Doctor opens assessment case
    ↓
Reviews submitted declaration
    ↓
Validates declaration
    ↓
Flags high-risk answers if applicable
    ↓
Continues to physical examination
```

### Doctor Validation Options

| Option | System Action |
|---|---|
| Validate declaration | Continue to physical examination |
| Request clarification | Reopen declaration for food handler correction |
| Reject declaration | Assessment paused |
| Mark high-risk | Requires further clinical review |

The guideline requires the medical doctor to validate the declaration questionnaire.

---

## 10. Integration With Medical Test Workflow

The health declaration form is the first required medical assessment step.

```text
Assessment Request Created
    ↓
Health Declaration Submitted
    ↓
Appointment Payment / Confirmation
    ↓
Facility Check-In
    ↓
Doctor Declaration Validation
    ↓
Physical Examination
    ↓
Lab Test Request
    ↓
Lab Result Entry
    ↓
System Recommendation
    ↓
Doctor Final Decision
    ↓
Certificate / Temporary Unfit Report
```

The system should not allow the assessment to proceed to doctor validation unless the declaration has been completed and submitted.

---

## 11. Medical Test Result Input Flow

After the doctor validates the declaration and completes the physical examination, required lab test requests are generated.

```text
Doctor completes physical exam
    ↓
System generates required lab test requests
    ↓
Lab officer enters structured test results
    ↓
Lab officer uploads supporting document
    ↓
Doctor reviews results
    ↓
System recommends Fit / Unfit / Further Review
    ↓
Doctor confirms final decision
```

### Required Lab Tests

The guideline identifies required laboratory investigations for food handlers, including stool microscopy, culture and sensitivity, and Hepatitis A Antigen.

| Test | Required |
|---|---|
| Stool microscopy, culture and sensitivity | Yes |
| Hepatitis A Antigen | Yes |
| Additional tests | Conditional, if clinically indicated |

---

## 12. Fitness Decision Logic

The system should recommend the decision, but the doctor must confirm the final outcome.

```text
System evaluates declaration + exam + lab results + vaccination review
    ↓
System recommends Fit / Temporarily Unfit / Further Review
    ↓
Doctor reviews recommendation
    ↓
Doctor confirms final decision
```

### Decision Rules

| Decision | Logic |
|---|---|
| Fit | All required steps complete, no unsafe findings |
| Temporarily Unfit | Unsafe symptom, abnormal result, or doctor-determined food safety risk |
| Further Review | Inconclusive result, missing information, or additional test required |

---

## 13. Certificate / Report Generation

### If Fit

```text
Doctor confirms Fit
    ↓
System generates Certificate of Fitness
    ↓
QR code is generated
    ↓
Certificate is stored in central database
    ↓
Dashboards update
```

### If Temporarily Unfit

```text
Doctor confirms Temporarily Unfit
    ↓
System blocks certificate
    ↓
System generates Temporary Unfit Report
    ↓
Food handler receives report
    ↓
Employer sees status only
    ↓
Dashboards update
```

The guideline requires generated fitness-to-work certificates to contain QR codes and unique identifiers for verification, and to be stored in formats verifiable in a central database administered by regulatory bodies.

---

## 14. Data Model Updates

### 14.1 `form_templates`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | String | Template name |
| form_type | Enum | `health_declaration`, etc. |
| owner_level | Enum | `federal`, `state`, `facility` |
| owner_id | UUID nullable | State/facility ID where applicable |
| parent_template_id | UUID nullable | For inheritance |
| base_template_id | UUID nullable | Federal base template |
| version | String | Example: v1.0 |
| status | Enum | draft, review, approved, published, active, archived |
| effective_date | Date | Activation date |
| superseded_by_id | UUID nullable | Newer version |
| created_by | UUID | User |
| approved_by | UUID nullable | User |
| published_at | Timestamp nullable | Publication date |
| created_at | Timestamp | Auto |
| updated_at | Timestamp | Auto |

---

### 14.2 `form_fields`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| template_id | UUID | Linked template |
| field_key | String | Unique key |
| label | Text | Question label |
| help_text | Text nullable | Instruction |
| field_type | Enum | yes_no, text, select, multi_select, date, file, consent |
| required | Boolean | Required field |
| owner_level | Enum | federal, state, facility |
| owner_id | UUID nullable | Owner ID |
| locked | Boolean | True if inherited |
| inherited_from_field_id | UUID nullable | Parent field |
| risk_flag | Boolean | Whether answer can trigger risk |
| risk_logic | JSON nullable | Example: yes = high risk |
| validation_rules | JSON nullable | Required formats |
| display_order | Integer | Order |
| section | String | Form section |
| is_active | Boolean | Field active |
| created_at | Timestamp | Auto |
| updated_at | Timestamp | Auto |

---

### 14.3 `form_template_adoptions`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| parent_template_id | UUID | Federal or State template |
| child_template_id | UUID | State or facility extension |
| adopted_by_level | Enum | state, facility |
| adopted_by_id | UUID | State/facility ID |
| adopted_at | Timestamp | Adoption date |
| status | Enum | active, superseded |

---

### 14.4 `form_responses`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| final_template_snapshot_id | UUID | Exact form version used |
| assessment_id | UUID | Medical assessment |
| food_handler_id | UUID | Respondent |
| response_payload | JSON | All answers |
| risk_summary | JSON nullable | Auto risk flags |
| status | Enum | draft, submitted, validated, reopened, rejected |
| submitted_at | Timestamp nullable | Submission date |
| validated_by_doctor_id | UUID nullable | Doctor |
| validated_at | Timestamp nullable | Validation date |
| created_at | Timestamp | Auto |
| updated_at | Timestamp | Auto |

---

### 14.5 `form_template_snapshots`

This preserves the exact merged form completed by the food handler.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| assessment_id | UUID | Assessment |
| federal_template_id | UUID | Federal source |
| state_template_id | UUID nullable | State source |
| facility_template_id | UUID nullable | Facility source |
| merged_schema | JSON | Final merged form |
| generated_at | Timestamp | Auto |

---

## 15. Updated Implementation Chunks for Codex

### Chunk 1: Extend Forms Tool With Template Ownership and Inheritance

**Goal:** Add form template hierarchy for Federal, State, and Facility-owned templates.

**Codex Prompt:**

```text
Extend the existing Forms Tool to support inherited form templates for regulated workflows.

Implement:
1. form_templates table/model with owner_level: federal, state, facility.
2. parent_template_id to allow State templates to inherit Federal templates and Facility templates to inherit State templates.
3. form_type enum with at least health_declaration.
4. version, status, effective_date, published_at, approved_by fields.
5. base_template_id to track the original Federal base template.
6. Template lifecycle statuses: draft, review, approved, published, active, archived, superseded.

Rules:
- Federal can create base templates.
- State can adopt active Federal templates and create State extension templates.
- Facility can adopt active State templates and create Facility extension templates.
- Published templates are immutable.
- Editing a published template must create a new draft version.
```

---

### Chunk 2: Add Field Ownership, Locking, and Inheritance Rules

**Goal:** Ensure lower-level users cannot delete or weaken parent fields.

**Codex Prompt:**

```text
Update form_fields to support field ownership and locking.

Add:
- owner_level: federal, state, facility
- owner_id
- locked boolean
- inherited_from_field_id
- risk_flag
- risk_logic JSON
- validation_rules JSON
- section
- display_order

Business rules:
1. Fields inherited from Federal must be locked for State and Facility users.
2. Fields inherited from State must be locked for Facility users.
3. Lower-level users cannot delete, hide, rename, reorder, or make optional inherited fields.
4. Lower-level users can only add their own fields.
5. Federal users can edit Federal draft fields.
6. State users can edit only State draft fields.
7. Facility users can edit only Facility draft fields.
8. Published field schemas cannot be edited directly.
9. Any attempted modification of inherited fields should return a permission error.
```

---

### Chunk 3: Federal Health Declaration Base Template Builder

**Goal:** Allow Federal users to create the national declaration form.

**Codex Prompt:**

```text
Build the Federal Health Declaration Form Template Builder.

Federal users should be able to create a National Food Handler Health Declaration Form Template using the Forms Tool.

Include default sections:
1. Identity Information
2. Food Handler Information
3. Recent Illness Declaration
4. Communicable Disease History
5. Skin and Infection Declaration
6. Vaccination History
7. Consent
8. Declaration Statement

Default Federal fields should include:
- fever
- jaundice
- diarrhoea
- vomiting
- cough or flu
- sore throat
- skin infection
- boils/cuts/lesions
- discharge from eyes/nose/ears/mouth
- known typhoid carrier history
- recent cholera/dysentery/gastrointestinal infection
- Hepatitis A history
- current medication
- Typhoid vaccination certificate upload/date
- Hepatitis A vaccination certificate upload/date
- consent checkbox
- declaration certification checkbox

Add UI for Federal users to:
- create template
- add/edit fields
- preview form
- submit for approval
- publish active version
```

---

### Chunk 4: State Template Adoption and Extension

**Goal:** Allow State users to adopt Federal template and add State-specific fields.

**Codex Prompt:**

```text
Implement State adoption and extension of Federal Health Declaration Form templates.

Requirements:
1. State users can view active Federal health declaration templates.
2. State users can click "Adopt Template".
3. System creates a State extension template linked to the Federal parent template.
4. Federal fields are visible but locked.
5. State users can add State-specific sections and fields.
6. State users cannot delete, edit, hide, reorder, rename, or make optional Federal fields.
7. State template must have draft, review, approved, active, archived statuses.
8. Publish State template only after validation confirms all inherited Federal fields are intact.
9. Notify facilities in the State when a State health declaration template is published or updated.
```

---

### Chunk 5: Medical Facility Template Adoption and Extension

**Goal:** Allow facilities to adopt Federal + State template and add facility-specific fields.

**Codex Prompt:**

```text
Implement Medical Facility adoption and extension of Health Declaration Forms.

Requirements:
1. Facility users can view active State health declaration templates for their mapped State.
2. Facility users can click "Adopt Template".
3. System creates a Facility extension template linked to the State template.
4. Federal and State inherited fields are visible but locked.
5. Facility users can add facility-specific fields in designated Facility Additional Questions section.
6. Facility cannot delete, edit, hide, reorder, rename, or make optional inherited Federal or State fields.
7. Facility template must be published before it can be used for food handler assessments.
8. If no facility extension exists, the system can use Federal + State template as default.
9. If no State extension exists, the system can use the Federal template as default, depending on State adoption policy.
```

---

### Chunk 6: Dynamic Final Declaration Form Merge

**Goal:** Generate the final form based on selected facility.

**Codex Prompt:**

```text
Implement dynamic form merging for food handler health declarations.

When a food handler selects a medical facility:
1. Identify the facility State.
2. Load active Federal health declaration template.
3. Load active State extension template if available.
4. Load active Facility extension template if available.
5. Merge fields in this order:
   - Federal sections and fields
   - State additional sections and fields
   - Facility additional sections and fields
   - Consent and Declaration section
6. Preserve field ownership metadata in the merged schema.
7. Create a form_template_snapshot for the assessment containing the exact merged schema.
8. Render the merged form for the food handler.
9. Ensure inherited locked fields cannot be removed from final schema.
```

---

### Chunk 7: Food Handler Declaration Submission

**Goal:** Let food handlers complete the final declaration form.

**Codex Prompt:**

```text
Implement food handler health declaration submission.

Requirements:
1. Only the food handler can complete the health declaration.
2. If an employer initiated the assessment, the food handler must still log in or verify identity to complete the declaration.
3. Render the merged form snapshot.
4. Validate all required fields.
5. Save responses as structured JSON in form_responses.
6. Generate risk_summary based on field risk_logic.
7. Lock response after submission.
8. Update medical_assessment declaration_status to submitted.
9. Move assessment status from Pending Declaration to Pending Payment or Appointment Confirmed depending on payment configuration.
10. Audit log the submission.
```

---

### Chunk 8: Declaration Reopen and Correction Workflow

**Goal:** Allow corrections without losing audit integrity.

**Codex Prompt:**

```text
Implement declaration reopen and correction workflow.

Requirements:
1. Submitted declarations are locked by default.
2. Doctor or authorized facility user can request clarification or correction.
3. System changes form_response status to reopened.
4. Food handler can edit only the response, not the form schema.
5. Previous submitted response must be preserved in response history.
6. New submission creates a new response version.
7. Audit log who reopened it, reason, old response, new response, and timestamp.
8. Assessment cannot proceed to final decision while declaration is reopened.
```

---

### Chunk 9: Doctor Declaration Validation

**Goal:** Doctor validates declaration before physical exam.

**Codex Prompt:**

```text
Implement doctor validation for health declarations.

Requirements:
1. Doctor can view submitted health declaration responses.
2. Doctor can see risk_summary generated from declaration answers.
3. Doctor can validate declaration, reject declaration, or request clarification.
4. Doctor cannot edit food handler answers.
5. If validated, set form_response status to validated.
6. If rejected, pause assessment and require facility/admin review.
7. If clarification is requested, trigger declaration reopen workflow.
8. Save doctor notes and validation timestamp.
9. Audit log all validation actions.
```

---

### Chunk 10: Integrate Declaration Status With Assessment Booking

**Goal:** Ensure declaration is required before appointment confirmation.

**Codex Prompt:**

```text
Integrate health declaration status with medical assessment booking.

Rules:
1. A medical assessment cannot proceed to confirmed appointment unless declaration_status = submitted or validated, depending on configured policy.
2. If payment is required, assessment moves:
   Pending Declaration -> Pending Payment -> Appointment Confirmed.
3. If pay-at-facility is enabled, assessment moves:
   Pending Declaration -> Appointment Confirmed.
4. Facility should see declaration status on appointment list.
5. Facility cannot check in a food handler if declaration is missing.
6. Doctor cannot start assessment if declaration is not submitted.
```

---

### Chunk 11: Lab Test Result Entry and Doctor Review Integration

**Goal:** Connect declaration to full medical assessment result flow.

**Codex Prompt:**

```text
Integrate health declaration with the existing medical test workflow.

After declaration validation:
1. Allow doctor to conduct physical examination.
2. Generate required lab test requests:
   - Stool microscopy, culture and sensitivity
   - Hepatitis A Antigen
3. Allow lab officer to enter structured results and upload supporting files.
4. Results must be reviewed by doctor.
5. System recommendation engine should consider:
   - declaration risk_summary
   - physical examination risk flags
   - lab result statuses
   - vaccination review status
6. Doctor must confirm final decision before certificate/report generation.
```

---

### Chunk 12: Certificate and Report Generation From Validated Assessment

**Goal:** Generate certificate/report only after complete workflow.

**Codex Prompt:**

```text
Update certificate/report generation rules.

Certificate of Fitness can only be generated when:
1. Assessment was conducted by approved facility.
2. Declaration was submitted and validated.
3. Physical examination was completed.
4. Required lab tests were completed.
5. Lab results were reviewed by doctor.
6. Doctor final decision = Fit.
7. Certificate template is active.
8. QR token is generated.

If doctor final decision = Temporarily Unfit:
1. Block certificate generation.
2. Generate Temporary Unfit Report.
3. Employer sees status only.
4. Food handler sees report based on privacy rules.
5. Dashboards update.
```

---

### Chunk 13: Dashboard Updates for Form Adoption and Assessment Status

**Goal:** Add visibility for Federal, State, Facility, Employer, and Food Handler.

**Codex Prompt:**

```text
Add dashboard widgets for health declaration templates and assessment status.

Federal dashboard:
- number of States that adopted Federal declaration template
- States using latest version
- States pending adoption
- total declarations submitted nationally
- risk flag trends by state

State dashboard:
- facilities that adopted State template
- facilities using latest template
- declarations submitted in State
- high-risk declaration trends
- pending facility adoption

Facility dashboard:
- active declaration template version
- pending declarations
- declarations requiring doctor validation
- declarations reopened for correction
- appointments blocked due to missing declaration

Employer dashboard:
- staff pending declaration
- staff pending test
- certified staff
- expired certificate staff
- temporarily unfit staff

Food handler dashboard:
- declaration status
- appointment status
- assessment status
- certificate/report status
```

---

### Chunk 14: Notifications

**Goal:** Notify users about template adoption and declaration workflow.

**Codex Prompt:**

```text
Implement notifications for health declaration template and workflow events.

Notify:
1. State users when Federal publishes new declaration template version.
2. Facility users when State publishes new declaration extension.
3. Facility users when they need to adopt latest State template.
4. Food handler when declaration is required.
5. Facility/doctor when declaration is submitted.
6. Food handler when declaration requires correction.
7. Food handler/employer when appointment is blocked due to missing declaration.
8. Doctor when high-risk declaration requires validation.
9. Employer when staff declaration is pending, without revealing medical details.
```

---

### Chunk 15: Audit Logging and Compliance Controls

**Goal:** Ensure full traceability.

**Codex Prompt:**

```text
Implement audit logging and compliance controls for inherited declaration forms.

Audit these events:
- Federal template created
- Federal template published
- State template adopted
- State field added
- State template published
- Facility template adopted
- Facility field added
- Facility template published
- Attempt to modify inherited locked field
- Final merged form generated
- Food handler declaration submitted
- Declaration reopened
- Declaration corrected
- Doctor validated declaration
- Doctor rejected declaration
- Assessment blocked due to missing declaration

Audit fields:
- actor_user_id
- actor_role
- owner_level
- entity_type
- entity_id
- action
- old_value
- new_value
- reason
- timestamp
```

---

## 16. Acceptance Criteria

### Federal Template

- Federal user can create health declaration base template.
- Federal fields can be marked mandatory and risk-triggering.
- Federal template can be published and versioned.
- Published Federal template is immutable.

### State Adoption

- State can adopt active Federal template.
- State sees Federal fields as locked.
- State can add additional fields.
- State cannot delete or weaken Federal fields.
- State can publish State extension.

### Facility Adoption

- Facility can adopt Federal + State template.
- Facility sees inherited fields as locked.
- Facility can add facility-specific fields.
- Facility cannot delete or weaken Federal/State fields.
- Facility can publish facility extension.

### Food Handler Submission

- Final declaration form is generated based on selected facility.
- Food handler completes the merged form.
- Employer cannot complete declaration on behalf of food handler.
- Submitted declaration is locked.
- Declaration is linked to medical assessment.

### Doctor Validation

- Doctor can validate, reject, or request clarification.
- Doctor cannot edit food handler answers.
- Declaration validation is audit logged.
- Assessment cannot proceed without declaration submission/validation according to policy.

### Medical Assessment

- Lab test flow remains connected to declaration.
- System recommendation considers declaration risk flags.
- Doctor confirms final decision.
- Certificate/report is generated only after full assessment completion.

---

## 17. Final Updated Workflow

```text
1. Federal creates National Health Declaration Form Template using Forms Tool.

2. Federal publishes active template version.

3. State receives notification and adopts Federal template.

4. State adds State-specific questions if needed.

5. State publishes State extension.

6. Medical facility receives notification and adopts Federal + State form.

7. Medical facility adds facility-specific questions if needed.

8. Facility publishes facility extension.

9. Food handler registers directly or is added by employer.

10. Food handler/employer starts medical assessment request.

11. Food handler/employer selects approved medical facility.

12. System generates final declaration form:
    Federal fields + State fields + Facility fields.

13. Food handler completes and submits declaration.

14. Declaration is locked and linked to assessment.

15. Doctor validates declaration.

16. Food handler pays and appointment is confirmed, or appointment confirms based on pay-at-facility setting.

17. Facility checks in food handler.

18. Doctor conducts physical examination.

19. Required lab tests are conducted.

20. Lab officer enters structured results and uploads evidence.

21. System evaluates declaration, exam, lab result, and vaccine review.

22. System recommends Fit, Temporarily Unfit, or Further Review.

23. Doctor confirms final decision.

24. If Fit, QR-coded Certificate of Fitness is generated.

25. If Unfit, Temporary Unfit Report is generated.

26. Certificate/report is stored in central database.

27. Food handler, employer, facility, State, and Federal dashboards update.
```

---

## 18. Final Recommendation

This update makes the Forms Tool a central part of the regulated medical assessment process while preserving Federal control, State flexibility, and facility-level operational customization.

The core rule for the platform is:

```text
Federal defines the national minimum standard.
State can add jurisdiction-specific requirements.
Medical Facility can add operational requirements.
Lower levels cannot delete, hide, or weaken higher-level requirements.
```
