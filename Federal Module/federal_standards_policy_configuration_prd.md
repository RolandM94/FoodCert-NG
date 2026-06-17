# PRD: Federal Module — Standards and Policy Configuration Feature

## Document Control

| Item | Details |
|---|---|
| Product | National Food Handlers Medical Test Management Platform |
| Module | Federal Module |
| Feature | Standards and Policy Configuration |
| Primary Owner | Federal Ministry of Health and Social Welfare |
| Intended Engineering Consumer | Codex / Development Team |
| Version | v1.0 |
| Status | Implementation PRD |

---

## 1. Executive Summary

The **Standards and Policy Configuration** feature is the policy engine of the Federal Module. It enables the Federal Ministry of Health and Social Welfare to define, version, approve, publish, monitor, and enforce the national rules that govern the implementation of the National Guidelines for Food Handlers' Medical Test.

The feature should allow Federal users to configure standards for food handler categories, food establishment categories, medical tests, vaccination requirements, certificate rules, QR verification, return-to-work rules, medical facility eligibility standards, reporting templates, M&E indicators, policy documents, SOPs, and circulars.

This feature must ensure that all States and the FCT implement a consistent national standard while allowing limited state-level configuration where the guideline assigns responsibility to State Ministries of Health.

The guiding product principle is:

> States implement. Medical facilities assess. Food businesses comply. Food handlers get certified. The Federal Ministry owns the standards, central portal, certificate archive, policy rules, reporting framework, and national oversight layer.

---

## 2. Background and Policy Context

The National Guidelines for Food Handlers' Medical Test establish a standardized framework for medical assessment and management of food handlers across Nigeria. The guideline requires implementation across all 36 States and the FCT, with key responsibilities shared between the Federal Ministry of Health and Social Welfare, State Ministries of Health, approved medical facilities, food business owners, and food handlers.

The Federal Ministry's role in the application is to provide the central policy, standards, digital certification, archiving, reporting, analytics, and oversight layer. The application must therefore support policy configuration as a first-class system feature instead of hardcoding the current guideline into the application.

The Standards and Policy Configuration feature exists because policy rules may evolve over time. The guideline itself anticipates continuous monitoring, evaluation, and updating as medical science, food safety practices, and public health risks evolve.

---

## 3. Problem Statement

Without a centralized Standards and Policy Configuration feature, the platform will face the following risks:

1. Different States may interpret and implement medical test rules inconsistently.
2. Approved medical facilities may issue certificates using different standards.
3. Certificate validity periods may become inconsistent.
4. Vaccination rules may not be uniformly applied.
5. Historical certificates may be difficult to verify against the policy rules active at issuance.
6. Policy updates may require developer intervention instead of administrative configuration.
7. Federal oversight dashboards may show inconsistent data because States are using different categories, rules, and reporting templates.
8. QR verification may become unreliable if certificate formats differ across jurisdictions.
9. The Federal Ministry may lack an auditable trail of policy changes, approvals, and implementation acknowledgements.

The system must therefore provide a robust, auditable, version-controlled policy configuration tool that drives downstream workflows across the application.

---

## 4. Product Goals

The feature must achieve the following goals:

1. Enable Federal users to configure national food handler medical assessment standards.
2. Enable Federal users to version, approve, publish, retire, and archive policy configurations.
3. Ensure that every certificate references the policy version used at issuance.
4. Ensure that States cannot reduce Federal minimum standards.
5. Allow limited state-specific configuration only where permitted.
6. Provide a single source of truth for medical tests, vaccinations, categories, certificate rules, and reporting templates.
7. Support periodic policy updates without requiring major engineering changes.
8. Maintain a full audit trail of every policy configuration action.
9. Notify States and relevant users when new policy versions or standards are published.
10. Support Federal M&E, compliance oversight, and public health policy analytics.

---

## 5. Non-Goals

This PRD does not cover implementation of the following features except where they consume configuration from this feature:

1. Food handler registration workflow.
2. Food business owner registration workflow.
3. Medical test result entry workflow.
4. Certificate issuance workflow.
5. Public QR verification portal.
6. State dashboard.
7. Payment or assessment pricing workflow.
8. Enforcement case management.
9. National Overview Dashboard.
10. Full medical records module.

These should be implemented as separate modules but must consume rules from this Standards and Policy Configuration feature.

---

## 6. Primary Users and Personas

### 6.1 Federal Super Admin

Full administrative authority over the Federal Module. Can create, edit, approve, publish, retire, and manage all standards and system configurations.

### 6.2 National Programme Manager

Responsible for national programme oversight. Reviews and approves policy versions, monitors implementation, and ensures alignment with national food safety goals.

### 6.3 Federal Policy Officer

Creates and maintains policy content, guidelines, SOPs, circulars, categories, and documentation.

### 6.4 Federal Medical Standards Officer

Configures clinical standards, required medical tests, physical examination rules, vaccination requirements, re-examination triggers, and return-to-work rules.

### 6.5 Federal Certification Officer

Configures certificate templates, validity rules, QR payloads, certificate statuses, revocation reasons, and public verification display fields.

### 6.6 Federal M&E Officer

Configures reporting templates, M&E indicators, reporting frequencies, compliance formulas, targets, thresholds, and data quality rules.

### 6.7 State Ministry of Health Admin

Views published Federal standards, acknowledges new policy versions, and configures limited state-level implementation settings where allowed.

### 6.8 Approved Medical Facility Admin

Views active standards applicable to medical assessments, medical test requirements, vaccination rules, documentation requirements, and certificate eligibility logic.

### 6.9 Auditor

Reviews policy history, approval trails, change logs, publication records, state acknowledgement logs, and user activity.

---

## 7. Permissions Matrix

| Capability | Super Admin | Programme Manager | Policy Officer | Medical Standards Officer | Certification Officer | M&E Officer | State Admin | Facility Admin | Auditor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| View active standards | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Create policy draft | Yes | Yes | Yes | Yes | Yes | Yes | No | No | No |
| Edit own draft | Yes | Yes | Yes | Yes | Yes | Yes | No | No | No |
| Submit draft for review | Yes | Yes | Yes | Yes | Yes | Yes | No | No | No |
| Review policy draft | Yes | Yes | Limited | Limited | Limited | Limited | No | No | View |
| Approve policy version | Yes | Yes | No | No | No | No | No | No | No |
| Publish policy version | Yes | Yes | No | No | No | No | No | No | No |
| Retire policy version | Yes | Yes | No | No | No | No | No | No | No |
| Configure categories | Yes | Yes | Yes | No | No | No | No | No | View |
| Configure medical tests | Yes | Yes | No | Yes | No | No | No | No | View |
| Configure vaccination rules | Yes | Yes | No | Yes | No | No | No | No | View |
| Configure certificate template | Yes | Yes | No | No | Yes | No | No | No | View |
| Configure QR rules | Yes | Yes | No | No | Yes | No | No | No | View |
| Configure reporting templates | Yes | Yes | No | No | No | Yes | No | No | View |
| Configure M&E indicators | Yes | Yes | No | No | No | Yes | No | No | View |
| Upload policy documents | Yes | Yes | Yes | Yes | Yes | Yes | No | No | View |
| Acknowledge policy version | No | No | No | No | No | No | Yes | No | View |
| View audit logs | Yes | Yes | No | No | No | No | No | No | Yes |

---

## 8. Information Architecture

The Federal Module sidebar should include the following high-level sections:

1. National Overview
2. States & FCT
3. Standards & Policy Configuration
4. Food Handlers
5. Food Businesses
6. Medical Facilities
7. Certificates
8. Reports & M&E
9. Compliance Oversight
10. Public Awareness
11. Administration
12. Audit Logs

Within **Standards & Policy Configuration**, create grouped sub-navigation. These are configuration and governance tools inside one Federal Standards module, not separate top-level product modules:

1. Overview
2. Policy Governance
   - Policy Versions
   - Approval Queue
   - Change History
   - Documents & Circulars
3. Assessment Standards
   - Food Handler Categories
   - Establishment Categories
   - Medical Test Rules
   - Physical Examination Rules
   - Vaccination Rules
   - Return-to-Work Rules
4. Certification & Facility Rules
   - Certificate Standards
   - Certificate Validity & Expiry Rules
   - Medical Facility Requirements
   - State Configuration Controls
5. Reporting & M&E
   - Reporting Templates
   - M&E Indicators

---

## 9. Feature Architecture

The Standards and Policy Configuration feature should behave as a policy engine that exposes active standards to other modules through APIs/services.

### 9.1 Core Capability Areas

The following are capability areas within the single Standards and Policy Configuration feature. They should not be interpreted as separate top-level application modules or as mandatory one-to-one navigation tabs. The visible UI should group these capabilities into a smaller number of configuration areas, while preserving direct routes where useful.

1. Standards Overview Dashboard
2. Policy Version Management
3. Food Handler Category Configuration
4. Food Establishment Category Configuration
5. Medical Test Rule Configuration
6. Physical Examination Rule Configuration
7. Vaccination Rule Configuration
8. Certificate Standards Configuration
9. Certificate Validity and Expiry Configuration
10. Return-to-Work and Exclusion Rule Configuration
11. Medical Facility Eligibility and Documentation Configuration
12. State-Specific Configuration Controls
13. Reporting Template Configuration
14. M&E Indicator Configuration
15. Policy Document and Circular Management
16. Approval Workflow
17. Notification Engine Integration
18. Audit Log and Change History

The Notification Engine Integration is an internal/shared service capability. Standards and Policy Configuration should emit or trigger notification events when policy versions, approvals, publications, retirements, or acknowledgements require communication, but it should not appear as a separate Standards tab.

### 9.2 Downstream Consumers

The following modules must consume rules from this feature:

| Consuming Module | Rules Consumed |
|---|---|
| Food Handler Registration | Handler categories, required fields, NIN/passport requirements |
| Food Business Registration | Establishment categories, linked handler category requirements |
| Medical Assessment | Medical tests, examination checklist, re-examination triggers |
| Vaccination Management | Vaccine rules, dose schedules, validity calculations |
| Certificate Issuance | Certificate template, QR rules, validity, status logic |
| QR Verification | Public verification fields, certificate status rules |
| State Reporting | Reporting templates, deadlines, indicators |
| National Dashboard | M&E indicators, compliance formulas, reporting rules |
| Facility Accreditation | Facility requirements, documentation checklist |

---

## 10. Core Business Rules

1. Only authorized Federal users can create or modify national standards.
2. Published policy versions cannot be edited directly.
3. Changes to published standards must be made through a new policy version or amendment version.
4. All active standards must be linked to a policy version.
5. Only one national policy version should be active at a time, unless a transition window is explicitly enabled.
6. Certificates must store the policy version used at issuance.
7. States cannot reduce Federal minimum requirements.
8. States can only add stricter or localized requirements if the Federal configuration allows it.
9. Mandatory medical tests must be completed before a certificate can be issued.
10. Blocking medical results must prevent certificate issuance.
11. Missing or expired mandatory vaccinations must trigger a certification flag based on the active vaccination rule.
12. QR code configuration must be active before certificates can be generated.
13. Public QR verification must not expose detailed medical records.
14. State reporting templates must have a frequency, deadline, indicators, and submission structure.
15. All configuration changes must be logged.
16. Any high-impact change must go through approval.
17. Emergency rules must have a review date or expiry date.
18. Deleted standards should be soft-deleted or retired, not physically removed.
19. Policy documents should be versioned and archived.
20. States must be notified when a new policy version becomes active.

---

## 11. Detailed Functional Requirements

## 11.1 Standards Overview Dashboard

### Description

This is the landing page for the Standards and Policy Configuration section. It gives Federal users a quick operational view of policy configuration status.

### UI Components

1. Header: `Standards & Policy Configuration`
2. Active Policy Version card
3. Policy Status cards
4. Pending Approvals panel
5. Upcoming Effective Changes panel
6. State Acknowledgement summary
7. Configuration Completeness checklist
8. Recent Changes feed
9. Quick Actions panel

### Dashboard Cards

| Card | Data |
|---|---|
| Active Policy Version | Version code, title, effective date, status |
| Draft Versions | Count of policy versions in draft |
| Pending Approval | Count of drafts awaiting approval |
| Published Documents | Count of active documents/SOPs/circulars |
| States Acknowledged | Number of States/FCT that acknowledged latest policy |
| Active Medical Test Rules | Count of active mandatory and conditional rules |
| Active Vaccination Rules | Count of active vaccine rules |
| Certificate Template | Active template name and version |
| Reporting Template | Active template and reporting frequency |

### Quick Actions

1. Create New Policy Version
2. Clone Active Policy
3. Add Medical Test Rule
4. Add Vaccination Rule
5. Upload Circular
6. View Approval Queue
7. View Change History

### Acceptance Criteria

1. Users see only quick actions permitted by their role.
2. Dashboard loads using active policy version by default.
3. If no active certificate template exists, show a high-priority warning.
4. If policy version is pending state acknowledgement, show count and list.
5. If any high-impact rule is in draft, show it in pending changes.

---

## 11.2 Policy Version Management

### Description

Federal users must be able to create, clone, review, approve, publish, retire, and archive policy versions.

### Status Lifecycle

Draft → Under Review → Returned or Approved → Scheduled or Active → Retired → Archived

### Functional Requirements

The system must allow authorized users to:

1. Create a policy version.
2. Clone an existing policy version.
3. Edit a draft version.
4. Attach supporting documents.
5. Submit a draft for review.
6. Assign reviewers.
7. Return a draft with comments.
8. Approve a draft.
9. Schedule publication for a future date.
10. Publish immediately.
11. Retire an active version.
12. Archive old versions.
13. Compare two versions.
14. View all rules attached to a version.
15. Track state acknowledgements.
16. Export policy version summary.

### Required Fields

| Field | Type | Required |
|---|---|---:|
| Version Code | Text | Yes |
| Version Title | Text | Yes |
| Description | Long Text | Yes |
| Major/Minor Type | Enum | Yes |
| Effective Start Date | Date | Yes |
| Effective End Date | Date | No |
| Review Deadline | Date | No |
| Requires State Acknowledgement | Boolean | Yes |
| Change Summary | Long Text | Yes |
| Supporting Documents | File Attachments | No |
| Status | Enum | System-generated |

### Version Code Format

Use this format:

`NG-FHMT-YYYY-vMajor.Minor`

Example:

`NG-FHMT-2024-v1.0`

### Validation Rules

1. Version code must be unique.
2. Effective start date must not overlap with another active version unless transition mode is enabled.
3. A policy version cannot be published without at least:
   - One certificate standard.
   - One medical test rule group.
   - One certificate validity rule.
   - One reporting template.
4. Published versions cannot be edited.
5. Retired versions cannot be used for new certificates.
6. Certificates issued under retired versions remain verifiable historically.

### UI/UX Flow: Create Policy Version

1. User opens `Standards & Policy Configuration > Policy Versions`.
2. User clicks `Create Policy Version`.
3. System opens a multi-step modal/page:
   - Step 1: Basic Information
   - Step 2: Effective Dates
   - Step 3: Clone Existing Rules? Yes/No
   - Step 4: Attach Documents
   - Step 5: Review Summary
4. User saves as draft.
5. System redirects to Policy Version Detail page.
6. User configures or edits rules under that version.
7. User clicks `Submit for Review`.
8. System validates completeness.
9. If validation passes, status becomes `Under Review`.
10. Reviewers receive notification.

### UI/UX Flow: Publish Policy Version

1. Programme Manager opens `Approval Queue`.
2. Selects policy version.
3. Reviews change summary and configuration completeness.
4. Clicks `Approve`.
5. System requests approval comment.
6. After approval, user clicks `Publish`.
7. System asks whether to publish immediately or schedule.
8. User selects effective date.
9. System validates no conflicting active version.
10. System publishes or schedules the version.
11. States receive notification.
12. State acknowledgement records are created.

---

## 11.3 Food Handler Category Configuration

### Description

Federal users must define the food handler categories covered by the national guideline.

### Default Seed Categories

Seed the following categories from the guideline:

1. Kitchen Staff
2. Food Preparers
3. Serving and Catering Staff
4. Food Packers
5. Bakery Workers
6. Food Processing Operators
7. Bartenders
8. Dishwashers
9. Food Delivery Personnel
10. Food Stall and Street Food Vendors
11. Food Storage Handlers
12. Concession Stand Workers
13. Airline Catering Vendors
14. Train Catering Vendors
15. Cruise Ship / Sea Vessel Catering Vendors
16. Livestock Farmers
17. Emergency Situation Workers

### Functional Requirements

The system must allow users to:

1. Create categories.
2. Edit draft categories.
3. Activate or deactivate categories.
4. Assign category code.
5. Add description.
6. Assign risk level.
7. Link category to medical test rule group.
8. Link category to vaccination rule group.
9. Link category to certificate requirements.
10. Define whether certificate is mandatory.
11. Define whether category is nationally locked.
12. Define whether States may add subcategories.
13. Bulk upload categories.
14. Export categories.

### Data Fields

| Field | Type |
|---|---|
| Category ID | UUID |
| Category Name | Text |
| Category Code | Text |
| Description | Long Text |
| Risk Level | Low / Medium / High |
| Certificate Required | Boolean |
| Medical Test Rule Group | Relationship |
| Vaccination Rule Group | Relationship |
| Nationally Locked | Boolean |
| Allow State Subcategories | Boolean |
| Status | Draft / Active / Inactive / Retired |
| Policy Version ID | UUID |

### UI/UX Flow: Add Food Handler Category

1. User opens `Food Handler Categories`.
2. User sees searchable table with columns:
   - Category
   - Code
   - Risk Level
   - Certificate Required
   - Status
   - Policy Version
   - Last Updated
   - Actions
3. User clicks `Add Category`.
4. Form opens in side drawer.
5. User enters name, code, description, risk level.
6. User selects certificate requirement.
7. User links medical and vaccination rule groups.
8. User saves as draft.
9. User submits for approval or keeps draft.
10. After policy version publication, category becomes active.

---

## 11.4 Food Establishment Category Configuration

### Description

Federal users must define the types of food establishments affected by the guideline.

### Default Seed Categories

1. Restaurants and Cafes
2. Bakeries and Pastry Shops
3. Abattoirs, Slaughter Slabs, and Butcher Shops
4. Grocery Stores and Supermarkets
5. Food Trucks and Street Vendors
6. Catering Services
7. School Cafeterias
8. Hospital Kitchens
9. Bars and Pubs
10. Food Processing Plants
11. Hotels and Resorts
12. Corporate Dining Facilities
13. Food Markets and Stalls
14. Airports and Train Stations
15. Farms and Livestock Feed Processing Plants
16. Daycare Centres

### Functional Requirements

The system must allow users to:

1. Create establishment categories.
2. Assign risk level.
3. Link establishment categories to required food handler categories.
4. Define minimum compliance requirements.
5. Define whether inspection is required.
6. Define required business documentation.
7. Allow or disallow state-specific subcategories.
8. Activate, deactivate, or retire categories.
9. Bulk upload categories.
10. Export list.

### UI/UX Flow: Configure Establishment Category

1. User opens `Establishment Categories`.
2. User clicks `Add Establishment Type`.
3. User enters name, code, description.
4. User selects risk level.
5. User selects food handler categories normally associated with the establishment.
6. User defines compliance requirements.
7. User saves.
8. System links category to selected policy version.

---

## 11.5 Medical Test Rule Configuration

### Description

This module defines required, conditional, optional, and emergency medical tests.

### Default Seed Medical Tests

1. Stool Microscopy, Culture and Sensitivity
2. Hepatitis A Antigen
3. Additional doctor-requested tests where clinically indicated

### Functional Requirements

The system must allow authorized users to:

1. Create medical test rule.
2. Define whether test is mandatory, conditional, optional, or emergency.
3. Define applicable handler categories.
4. Define applicable establishment risk levels.
5. Define result type.
6. Define accepted values.
7. Define whether positive/abnormal result blocks certification.
8. Define validity duration.
9. Define whether attachment is required.
10. Define whether doctor validation is required.
11. Define whether lab validation is required.
12. Define re-test rule.
13. Define if test is activated during outbreak or emergency.
14. Deactivate or retire old tests.

### Data Fields

| Field | Type |
|---|---|
| Test Rule ID | UUID |
| Test Name | Text |
| Test Code | Text |
| Test Type | Lab / Clinical / Physical / Other |
| Rule Type | Mandatory / Conditional / Optional / Emergency |
| Result Type | Positive-Negative / Normal-Abnormal / Numeric / Text / File |
| Accepted Result Values | JSON |
| Blocks Certification | Boolean |
| Requires Attachment | Boolean |
| Requires Doctor Validation | Boolean |
| Requires Lab Validation | Boolean |
| Validity Days | Integer |
| Applicable Categories | JSON / Relationship |
| Applicable Establishment Risk Levels | JSON |
| Policy Version ID | UUID |
| Status | Draft / Active / Retired |

### Validation Rules

1. Mandatory test must have result type.
2. Mandatory test must define certification impact.
3. A blocking test must define which result blocks certification.
4. A test cannot be active without a policy version.
5. A certificate cannot be issued if mandatory active tests are missing.

### UI/UX Flow: Add Medical Test Rule

1. User opens `Medical Test Rules`.
2. User clicks `Add Test Rule`.
3. Side drawer or full page opens.
4. User enters test name and code.
5. User selects rule type.
6. User selects applicable categories.
7. User defines result type.
8. User defines blocking result logic.
9. User defines attachment/validation requirements.
10. User previews rule impact.
11. User saves as draft.
12. User submits for review.

### UI/UX Flow: Medical Facility Consumes Rule

1. Facility user begins assessment.
2. Facility selects food handler category.
3. System calls active policy rule API.
4. System displays mandatory tests for that handler.
5. Facility cannot complete assessment until mandatory fields are filled.
6. If blocking result is entered, system marks handler as not fit or under review.

---

## 11.6 Physical Examination Rule Configuration

### Description

Defines physical examination checklist items and symptom triggers that require deeper examination, exclusion, or re-examination.

### Default Seed Indicators

1. Fever
2. Jaundice
3. Skin infections on hands, arms, or face
4. Boils, styes, or sepsis on fingers
5. Discharge from eyes, nose, ears, or mouth
6. Diarrhoea and/or vomiting
7. Known history of being a typhoid carrier
8. Sore throat
9. Cough or flu

### Functional Requirements

The system must allow users to:

1. Create examination checklist item.
2. Define whether item is mandatory.
3. Define whether finding blocks certification.
4. Define whether finding requires doctor notes.
5. Define whether finding requires re-examination.
6. Define whether finding requires exclusion from food handling.
7. Define return-to-work condition.
8. Define severity level.
9. Define public health escalation flag.
10. Activate or retire indicators.

### UI/UX Flow

1. User opens `Physical Examination Rules`.
2. System shows checklist items with status and impact.
3. User clicks `Add Indicator` or edits a draft indicator.
4. User defines finding, severity, certification impact, and return-to-work rule.
5. User saves.
6. Rule becomes active after policy version publication.

---

## 11.7 Vaccination Rule Configuration

### Description

Defines vaccine requirements, schedules, validity periods, dose rules, evidence requirements, and certification impact.

### Default Seed Vaccines

1. Typhoid Fever Vaccine
2. Hepatitis A Vaccine
3. Other vaccines as may be required by competent authority

### Default Seed Rules

| Vaccine | Default Rule |
|---|---|
| Typhoid | One dose every three years |
| Hepatitis A | Two doses at 0 and 6 months for full protection |

### Functional Requirements

The system must allow users to:

1. Create vaccine rule.
2. Define vaccine name and code.
3. Define required status.
4. Define dose schedule.
5. Define validity period.
6. Define evidence requirements.
7. Define whether missing vaccine blocks certification.
8. Define whether expired vaccine blocks certification.
9. Define whether doctor prescription is required when absent or expired.
10. Auto-calculate expiry and next visit date.
11. Configure booster rules.
12. Link vaccines to handler categories.
13. Configure grace period.
14. Activate, deactivate, or retire rules.

### Data Fields

| Field | Type |
|---|---|
| Vaccine Rule ID | UUID |
| Vaccine Name | Text |
| Vaccine Code | Text |
| Required | Boolean |
| Dose Schedule | JSON |
| Validity Months | Integer |
| Grace Period Days | Integer |
| Evidence Required | Boolean |
| Evidence Fields | JSON |
| Blocks Certification If Missing | Boolean |
| Blocks Certification If Expired | Boolean |
| Requires Doctor Prescription If Missing | Boolean |
| Applicable Categories | JSON / Relationship |
| Policy Version ID | UUID |
| Status | Draft / Active / Retired |

### UI/UX Flow: Add Vaccine Rule

1. User opens `Vaccination Rules`.
2. User clicks `Add Vaccine Rule`.
3. User enters vaccine name and code.
4. User selects whether required.
5. User builds dose schedule using a schedule builder.
6. User defines validity duration.
7. User defines evidence fields: vaccination date, brand, batch number, vaccinator, facility, next visit.
8. User defines certification impact.
9. User saves as draft.
10. Rule enters approval workflow.

### Acceptance Criteria

1. Typhoid expiry must auto-calculate as vaccination date plus 3 years by default.
2. Hepatitis A must support multi-dose tracking.
3. Missing required vaccine must trigger a visible flag in the assessment workflow.
4. Vaccination rules must feed dashboards and certificate eligibility logic.

---

## 11.8 Certificate Standards Configuration

### Description

Defines certificate templates, required fields, certificate number format, QR payload, public verification display fields, digital signatures, and certificate statuses.

### Functional Requirements

The system must allow users to:

1. Create certificate template.
2. Clone existing template.
3. Define certificate layout sections.
4. Define required identity fields.
5. Define medical summary fields.
6. Define issuing authority fields.
7. Define certificate number format.
8. Define QR payload.
9. Define public verification display fields.
10. Define certificate statuses.
11. Define revocation reasons.
12. Define suspension reasons.
13. Add digital seal/signature.
14. Preview certificate.
15. Publish template with policy version.

### Required Certificate Fields

1. Certificate ID
2. QR code
3. Full name
4. Date of birth
5. Gender
6. Passport photograph
7. NIN
8. State of domicile
9. Employer or food business name
10. Medical facility name
11. Doctor name or registration/reference number
12. Assessment date
13. Issue date
14. Expiry date
15. Fitness status
16. Vaccination summary
17. Policy version
18. Issuing authority
19. Digital signature or seal

### QR Payload Recommendation

The QR code should not expose medical data directly. It should include:

1. Certificate ID
2. Verification token
3. Issuing authority
4. Policy version
5. Verification URL
6. Cryptographic checksum/signature

### Public Verification Display Fields

1. Certificate status
2. Handler name
3. Passport photograph
4. Certificate ID
5. Issue date
6. Expiry date
7. State
8. Medical facility
9. Fit/not fit status
10. Verification timestamp

### Certificate Statuses

| Status | Meaning |
|---|---|
| Draft | Not issued |
| Valid | Active and verifiable |
| Expired | Past expiry date |
| Revoked | Withdrawn by authority |
| Suspended | Temporarily blocked |
| Not Fit | Handler not cleared |
| Cleared to Return | Previously unfit handler cleared |
| Under Review | Pending review |

### UI/UX Flow: Configure Certificate Template

1. User opens `Certificate Standards`.
2. User sees active template preview and status.
3. User clicks `Create Template` or `Clone Active Template`.
4. Template builder opens with sections:
   - Header
   - Identity Details
   - Assessment Summary
   - Vaccination Summary
   - Issuing Authority
   - QR Code
   - Footer
5. User selects required fields.
6. User configures certificate number format.
7. User configures QR payload.
8. User configures public verification fields.
9. User previews certificate.
10. User saves as draft.
11. User submits for approval.
12. Approved template becomes active when policy version is published.

---

## 11.9 Certificate Validity and Expiry Configuration

### Description

Defines certificate validity duration, routine assessment intervals, renewal windows, expiry reminders, grace periods, and revalidation rules.

### Important Product Note

The guideline references food handler assessment every six months and also references certificate validity of one year in another section. To avoid hardcoding a potentially contested interpretation, the platform should make assessment interval and certificate validity duration configurable.

### Functional Requirements

The system must allow users to configure:

1. Routine assessment interval.
2. Certificate validity duration.
3. Renewal window.
4. Grace period.
5. Expiry reminder schedule.
6. Re-examination triggers.
7. Illness-triggered suspension rules.
8. Emergency revalidation rule.
9. Return-to-work clearance requirement.

### Default Recommended Settings

| Setting | Default |
|---|---|
| Routine Assessment Interval | 6 months |
| Certificate Validity Duration | Configurable by active policy |
| Typhoid Vaccination Validity | 3 years |
| Hepatitis A Schedule | 0 and 6 months |
| Expiry Reminders | 30, 14, and 7 days before expiry |
| Re-examination Trigger | Immediate when symptoms are reported |

### UI/UX Flow

1. User opens `Certificate Validity & Expiry Rules`.
2. User selects active or draft policy version.
3. User configures interval and validity rules.
4. User configures reminder schedule.
5. User configures grace period.
6. User previews impact: number of existing certificates affected, if any.
7. User saves as draft.
8. High-impact change requires approval.

---

## 11.10 Return-to-Work and Exclusion Rule Configuration

### Description

Defines rules for excluding food handlers from food handling duties and clearing them to return to work after illness or suspected infection.

### Functional Requirements

The system must allow users to:

1. Define exclusion triggers.
2. Define default exclusion period.
3. Define condition-specific clearance rules.
4. Define whether medical clearance is required.
5. Define whether laboratory clearance is required.
6. Define number of negative samples required.
7. Define whether health authority approval is required.
8. Define return-to-work certificate/report format.
9. Define employer acknowledgement requirement.
10. Define state/public health escalation requirement.

### Default Rule Examples

| Condition | Default Rule |
|---|---|
| Diarrhoea/Vomiting | Exclude until 48 hours after symptoms stop |
| Cholera | Require medical clearance and negative stool samples |
| Hepatitis A | Exclude and require clearance based on policy rule |
| Infected Skin Lesion | Allow only if covered or medically cleared |
| Lassa Fever | Require documentation, clearance, and health authority approval |

### UI/UX Flow

1. User opens `Return-to-Work Rules`.
2. User views condition rules table.
3. User clicks `Add Condition Rule`.
4. User defines condition, exclusion period, clearance requirements, and evidence.
5. User defines whether rule blocks certificate or suspends active certificate.
6. User saves.
7. Rule is routed for approval if high impact.

---

## 11.11 Medical Facility Eligibility and Documentation Standards

### Description

Defines the minimum requirements for medical facilities that can conduct food handler assessments.

### Functional Requirements

The system must allow Federal users to configure:

1. Facility eligibility criteria.
2. Required documentation.
3. Required staffing capacity.
4. Required equipment.
5. Medical records requirements.
6. Computer and internet access requirements.
7. QR certificate capability requirements.
8. Annual re-accreditation rules.
9. Facility audit checklist.
10. Facility suspension criteria.
11. Facility reporting requirements.
12. Facility data quality requirements.

### Default Facility Requirements

1. Written reporting and documentation policy.
2. Computers and computer operators in medical records unit.
3. Pre-defined health declaration, laboratory, and investigation request forms.
4. Patient files for doctor notes.
5. Certificate formats containing QR codes.
6. Internet access.
7. Trained clinical, non-clinical, and medical records staff.
8. Standard medical record management process.
9. Confidentiality and safe storage policy.
10. Annual re-accreditation.

### UI/UX Flow

1. User opens `Medical Facility Requirements`.
2. User sees checklist categories:
   - Documentation
   - Staffing
   - Equipment
   - Digital Infrastructure
   - Records Management
   - Certificate Capability
   - Re-accreditation
3. User adds or edits checklist item.
4. User marks requirement as mandatory or optional.
5. User defines evidence type.
6. User saves and submits.

---

## 11.12 State Configuration Controls

### Description

Defines which implementation settings States can configure and which Federal rules are locked.

### Functional Requirements

The system must allow Federal users to:

1. Mark rules as Federal locked.
2. Mark rules as State configurable.
3. Define whether States can add stricter rules.
4. Define whether States can add subcategories.
5. Define whether Federal review is required for state-specific changes.
6. View all state-specific configurations.
7. Revoke or reject state-specific configurations if non-compliant.

### Recommended Control Matrix

| Configuration Item | Federal Control | State Control |
|---|---|---|
| Medical test minimums | Locked | Cannot reduce |
| Vaccination minimums | Locked | Cannot reduce |
| Handler categories | Defines national list | May add subcategories if allowed |
| Establishment categories | Defines national list | May add subcategories if allowed |
| Facility approval | Sets criteria | Approves facilities within state |
| Assessment prices | Sets framework | Sets state price |
| Reporting templates | Defines structure | Submits data |
| Enforcement actions | Monitors | Executes |

### UI/UX Flow

1. Federal user opens `State Configuration Controls`.
2. User sees table of configurable domains.
3. User toggles each item as:
   - Federal Locked
   - State Editable
   - State Editable with Federal Approval
4. User saves changes as draft.
5. Changes require approval if they affect state powers.

---

## 11.13 Reporting Template Configuration

### Description

Allows Federal M&E users to configure templates that States use to submit periodic reports.

### Functional Requirements

The system must allow users to:

1. Create reporting template.
2. Define reporting frequency.
3. Define reporting period.
4. Define required indicators.
5. Define required narrative sections.
6. Define file upload requirements.
7. Define validation rules.
8. Define deadline rules.
9. Define late submission flags.
10. Define completeness scoring.
11. Define approval workflow.
12. Publish template.

### Default Report Sections

1. State summary
2. Total food handlers registered
3. Total certified food handlers
4. Total expired certificates
5. Total unfit handlers
6. Total approved medical facilities
7. Facility re-accreditation status
8. Vaccination coverage
9. Illness and exclusion reports
10. Enforcement actions
11. Public awareness activities
12. Challenges
13. Recommendations
14. Data quality issues

### UI/UX Flow: Create Reporting Template

1. User opens `Reporting Templates`.
2. User clicks `Create Template`.
3. Template builder opens.
4. User enters template name and frequency.
5. User adds indicator sections.
6. User adds narrative sections.
7. User defines required uploads.
8. User defines deadline rule.
9. User defines scoring rules.
10. User previews state submission form.
11. User saves as draft.
12. User submits for approval.

---

## 11.14 M&E Indicator Configuration

### Description

Allows Federal M&E users to configure indicators used in reporting, dashboards, and policy analysis.

### Functional Requirements

The system must allow users to:

1. Create indicator.
2. Define formula.
3. Define numerator and denominator.
4. Define data source.
5. Define reporting frequency.
6. Define target.
7. Define thresholds.
8. Define visualization type.
9. Define dashboard visibility.
10. Define state visibility.
11. Define whether indicator is mandatory.
12. Version indicators with policy versions.

### Recommended Indicators

| Indicator | Formula |
|---|---|
| Food Handler Certification Rate | Certified handlers / Registered handlers × 100 |
| Vaccination Compliance Rate | Handlers with valid vaccination / Registered handlers × 100 |
| Expired Certificate Rate | Expired certificates / Total issued certificates × 100 |
| Facility Accreditation Compliance | Re-accredited facilities / Approved facilities × 100 |
| State Reporting Compliance | Submitted reports / Expected reports × 100 |
| QR Verification Failure Rate | Failed QR checks / Total QR checks × 100 |
| Unfit Detection Rate | Unfit handlers / Total assessed handlers × 100 |
| Return-to-Work Clearance Rate | Cleared handlers / Excluded handlers × 100 |
| Data Completeness Score | Completed required fields / Total required fields × 100 |

### UI/UX Flow

1. User opens `M&E Indicators`.
2. User clicks `Add Indicator`.
3. User enters name, code, description.
4. User selects data source.
5. User builds formula using formula builder.
6. User defines target and thresholds.
7. User selects visualization type.
8. User selects dashboard visibility.
9. User saves and submits.

---

## 11.15 Policy Documents and Circular Management

### Description

Allows Federal users to upload, publish, distribute, archive, and track acknowledgement of policy documents, circulars, SOPs, templates, and FAQs.

### Functional Requirements

The system must allow users to:

1. Upload documents.
2. Classify document type.
3. Link document to policy version.
4. Add description and tags.
5. Publish document.
6. Retire or archive document.
7. Require state acknowledgement.
8. Track downloads.
9. Track acknowledgements.
10. Notify target users.
11. Replace document with new version.
12. Maintain document version history.

### Document Types

1. National Guideline
2. SOP
3. Circular
4. Form Template
5. Reporting Template
6. FAQ
7. Training Material
8. Public Awareness Material
9. Technical Memo

### UI/UX Flow

1. User opens `Documents & Circulars`.
2. User clicks `Upload Document`.
3. User selects document type.
4. User uploads file.
5. User links document to policy version.
6. User selects target audience:
   - Federal users
   - State users
   - Medical facilities
   - Food businesses
   - Public
7. User selects whether acknowledgement is required.
8. User saves as draft or publishes.

---

## 11.16 Approval Queue

### Description

Central place for authorized reviewers and approvers to process pending configuration changes.

### Functional Requirements

The system must allow users to:

1. View pending approvals.
2. Filter by entity type.
3. Filter by impact level.
4. Review old vs new values.
5. Add comments.
6. Approve.
7. Return for correction.
8. Reject.
9. Escalate.
10. View approval history.

### Impact Levels

| Impact | Examples |
|---|---|
| Low | Document typo, category description |
| Medium | New category, reporting field update |
| High | Medical test rule, vaccination rule, certificate validity, QR rule |
| Emergency | Outbreak-related temporary rule |

### UI/UX Flow: Approve Change

1. Reviewer opens `Approval Queue`.
2. Selects an item.
3. System displays:
   - Summary
   - Change diff
   - Affected modules
   - Affected states
   - Effective date
   - Requesting user
4. Reviewer enters comment.
5. Reviewer clicks approve, return, or reject.
6. System logs action.
7. Requesting user receives notification.

---

## 11.17 Change History and Audit Logs

### Description

All configuration changes must be traceable and auditable.

### Functional Requirements

The system must log:

1. Entity type.
2. Entity ID.
3. Action performed.
4. Old value.
5. New value.
6. User who performed action.
7. Date/time.
8. Reason for change.
9. Approval comments.
10. IP address and device metadata where available.
11. Affected policy version.
12. Affected downstream modules.

### Audit Views

1. Policy version history
2. Medical test rule history
3. Vaccination rule history
4. Certificate template history
5. Reporting template history
6. M&E indicator history
7. Document publication history
8. State acknowledgement history
9. User activity history

### UI/UX Flow

1. Auditor opens `Change History`.
2. Auditor filters by entity type, date range, user, status, or policy version.
3. Auditor opens an audit record.
4. System shows old value, new value, approval trail, and affected modules.
5. Auditor exports audit report if permitted.

---

## 12. Data Model Specification

## 12.1 policy_versions

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| version_code | String | Unique |
| title | String | Required |
| description | Text | Required |
| version_type | Enum | major, minor, emergency |
| status | Enum | draft, under_review, returned, approved, scheduled, active, retired, archived |
| effective_start_date | DateTime | Required before publish |
| effective_end_date | DateTime | Nullable |
| requires_state_acknowledgement | Boolean | Default true |
| change_summary | Text | Required |
| created_by | UUID | User FK |
| submitted_by | UUID | User FK nullable |
| approved_by | UUID | User FK nullable |
| published_by | UUID | User FK nullable |
| retired_by | UUID | User FK nullable |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |
| submitted_at | Timestamp |  |
| approved_at | Timestamp |  |
| published_at | Timestamp |  |
| retired_at | Timestamp |  |

## 12.2 food_handler_categories

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| name | String | Required |
| code | String | Unique within policy version |
| description | Text |  |
| risk_level | Enum | low, medium, high |
| certificate_required | Boolean | Default true |
| medical_test_rule_group_id | UUID | Nullable |
| vaccination_rule_group_id | UUID | Nullable |
| nationally_locked | Boolean | Default true |
| allow_state_subcategories | Boolean | Default false |
| status | Enum | draft, active, inactive, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.3 establishment_categories

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| name | String | Required |
| code | String | Unique within policy version |
| description | Text |  |
| risk_level | Enum | low, medium, high |
| required_handler_categories | JSON | Category IDs |
| compliance_requirements | JSON | Configurable checklist |
| inspection_required | Boolean | Default false |
| required_documents | JSON |  |
| allow_state_subcategories | Boolean | Default false |
| status | Enum | draft, active, inactive, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.4 medical_test_rules

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| name | String | Required |
| code | String | Unique within policy version |
| test_type | Enum | laboratory, clinical, physical, other |
| rule_type | Enum | mandatory, conditional, optional, emergency |
| result_type | Enum | positive_negative, normal_abnormal, numeric, text, file |
| accepted_values | JSON |  |
| blocking_values | JSON | Values that block certification |
| blocks_certification | Boolean | Default false |
| requires_attachment | Boolean | Default false |
| requires_doctor_validation | Boolean | Default true |
| requires_lab_validation | Boolean | Default false |
| validity_days | Integer | Nullable |
| applicable_categories | JSON | Category IDs |
| applicable_establishment_risk_levels | JSON |  |
| emergency_activation_rule | JSON | Nullable |
| status | Enum | draft, active, inactive, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.5 physical_examination_rules

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| indicator_name | String | Required |
| code | String | Unique within policy version |
| description | Text |  |
| severity | Enum | low, medium, high, critical |
| requires_doctor_notes | Boolean | Default true |
| blocks_certification | Boolean | Default false |
| requires_reexamination | Boolean | Default false |
| requires_exclusion | Boolean | Default false |
| return_to_work_rule_id | UUID | Nullable |
| public_health_escalation | Boolean | Default false |
| status | Enum | draft, active, inactive, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.6 vaccination_rules

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| vaccine_name | String | Required |
| vaccine_code | String | Unique within policy version |
| required | Boolean | Default true |
| dose_schedule | JSON | Dose schedule config |
| validity_months | Integer | Nullable |
| grace_period_days | Integer | Default 0 |
| evidence_required | Boolean | Default true |
| evidence_fields | JSON | Required evidence fields |
| blocks_certification_if_missing | Boolean | Default false |
| blocks_certification_if_expired | Boolean | Default false |
| requires_doctor_prescription_if_missing | Boolean | Default true |
| applicable_categories | JSON | Category IDs |
| status | Enum | draft, active, inactive, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.7 certificate_templates

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| template_name | String | Required |
| template_version | String | Required |
| layout_config | JSON | Sections and display config |
| required_fields | JSON | Required fields |
| certificate_number_format | String | Example FHMT-{STATE}-{YYYY}-{SEQ} |
| qr_payload_config | JSON | QR payload fields |
| public_verification_fields | JSON | Safe public fields |
| status_rules | JSON | Certificate status logic |
| revocation_reasons | JSON |  |
| digital_signature_config | JSON |  |
| status | Enum | draft, active, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.8 certificate_validity_rules

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| routine_assessment_interval_days | Integer | Example 180 |
| certificate_validity_days | Integer | Configurable |
| renewal_window_days | Integer | Example 30 |
| grace_period_days | Integer | Example 0 |
| expiry_reminder_days | JSON | Example [30,14,7] |
| illness_suspension_enabled | Boolean | Default true |
| emergency_revalidation_enabled | Boolean | Default false |
| status | Enum | draft, active, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.9 return_to_work_rules

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| condition_name | String | Required |
| condition_code | String | Unique within policy version |
| default_exclusion_hours | Integer | Example 48 |
| requires_medical_clearance | Boolean |  |
| requires_lab_clearance | Boolean |  |
| negative_samples_required | Integer | Nullable |
| sample_interval_hours | Integer | Nullable |
| requires_health_authority_approval | Boolean |  |
| employer_acknowledgement_required | Boolean |  |
| clearance_document_required | Boolean |  |
| status | Enum | draft, active, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.10 facility_requirement_rules

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| requirement_name | String | Required |
| requirement_code | String | Unique within policy version |
| category | Enum | documentation, staffing, equipment, digital_infrastructure, records, certification, reaccreditation |
| mandatory | Boolean | Default true |
| evidence_type | Enum | text, file, checklist, url, inspection |
| renewal_required | Boolean | Default false |
| renewal_interval_days | Integer | Nullable |
| suspension_trigger | Boolean | Default false |
| status | Enum | draft, active, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.11 reporting_templates

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| template_name | String | Required |
| template_code | String | Unique within policy version |
| reporting_frequency | Enum | monthly, quarterly, biannual, annual, ad_hoc |
| deadline_rule | JSON | Submission deadline logic |
| required_sections | JSON |  |
| required_indicators | JSON | Indicator IDs |
| required_uploads | JSON |  |
| scoring_config | JSON | Completeness scoring |
| approval_required | Boolean | Default true |
| status | Enum | draft, active, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.12 me_indicators

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| indicator_name | String | Required |
| indicator_code | String | Unique within policy version |
| description | Text |  |
| formula_config | JSON | Numerator, denominator, expression |
| data_source | Enum | certificate, assessment, facility, state_report, verification, manual |
| reporting_frequency | Enum | monthly, quarterly, annual, ad_hoc |
| target_value | Decimal | Nullable |
| threshold_config | JSON | Red/amber/green rules |
| visualization_type | Enum | card, line, bar, map, table, pie |
| federal_dashboard_visible | Boolean |  |
| state_dashboard_visible | Boolean |  |
| mandatory | Boolean |  |
| status | Enum | draft, active, retired |
| created_by | UUID | User FK |
| created_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.13 policy_documents

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK nullable |
| title | String | Required |
| document_type | Enum | guideline, sop, circular, form_template, reporting_template, faq, training, awareness, memo |
| description | Text |  |
| file_url | String | Required |
| version_label | String | Required |
| target_audience | JSON | User groups |
| requires_acknowledgement | Boolean | Default false |
| status | Enum | draft, published, retired, archived |
| uploaded_by | UUID | User FK |
| published_by | UUID | User FK nullable |
| created_at | Timestamp |  |
| published_at | Timestamp |  |
| updated_at | Timestamp |  |

## 12.14 approvals

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| entity_type | String | PolicyVersion, MedicalTestRule, etc. |
| entity_id | UUID |  |
| requested_by | UUID | User FK |
| reviewer_id | UUID | User FK nullable |
| approver_id | UUID | User FK nullable |
| status | Enum | pending, returned, rejected, approved |
| impact_level | Enum | low, medium, high, emergency |
| request_comment | Text |  |
| review_comment | Text |  |
| approval_comment | Text |  |
| created_at | Timestamp |  |
| reviewed_at | Timestamp |  |
| approved_at | Timestamp |  |

## 12.15 state_acknowledgements

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| policy_version_id | UUID | FK |
| state_id | UUID | FK |
| acknowledged_by | UUID | User FK |
| acknowledgement_comment | Text | Nullable |
| acknowledged_at | Timestamp |  |
| status | Enum | pending, acknowledged, overdue |

## 12.16 audit_logs

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| entity_type | String |  |
| entity_id | UUID |  |
| action | String | create, update, delete, publish, approve, reject, etc. |
| old_value | JSON | Nullable |
| new_value | JSON | Nullable |
| performed_by | UUID | User FK |
| reason | Text | Nullable |
| ip_address | String | Nullable |
| user_agent | String | Nullable |
| performed_at | Timestamp |  |

---

## 13. API Specification

Use REST or equivalent service endpoints. All endpoints must enforce RBAC and audit logging where applicable.

## 13.1 Policy Versions

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/federal/standards/policy-versions | List policy versions |
| POST | /api/federal/standards/policy-versions | Create policy version |
| GET | /api/federal/standards/policy-versions/{id} | Get policy version detail |
| PATCH | /api/federal/standards/policy-versions/{id} | Update draft policy version |
| POST | /api/federal/standards/policy-versions/{id}/clone | Clone policy version |
| POST | /api/federal/standards/policy-versions/{id}/submit | Submit for review |
| POST | /api/federal/standards/policy-versions/{id}/approve | Approve policy version |
| POST | /api/federal/standards/policy-versions/{id}/return | Return for correction |
| POST | /api/federal/standards/policy-versions/{id}/publish | Publish policy version |
| POST | /api/federal/standards/policy-versions/{id}/retire | Retire policy version |
| GET | /api/federal/standards/policy-versions/{id}/compare/{otherId} | Compare versions |

## 13.2 Configuration Resources

Use the following resource pattern:

| Resource | Base Endpoint |
|---|---|
| Food Handler Categories | /api/federal/standards/food-handler-categories |
| Establishment Categories | /api/federal/standards/establishment-categories |
| Medical Test Rules | /api/federal/standards/medical-test-rules |
| Physical Examination Rules | /api/federal/standards/physical-examination-rules |
| Vaccination Rules | /api/federal/standards/vaccination-rules |
| Certificate Templates | /api/federal/standards/certificate-templates |
| Certificate Validity Rules | /api/federal/standards/certificate-validity-rules |
| Return-to-Work Rules | /api/federal/standards/return-to-work-rules |
| Facility Requirements | /api/federal/standards/facility-requirements |
| Reporting Templates | /api/federal/standards/reporting-templates |
| M&E Indicators | /api/federal/standards/me-indicators |
| Policy Documents | /api/federal/standards/documents |

For each resource implement:

| Method | Purpose |
|---|---|
| GET | List records with filters |
| POST | Create record |
| GET /{id} | View record |
| PATCH /{id} | Update draft record |
| POST /{id}/submit | Submit for review |
| POST /{id}/approve | Approve record |
| POST /{id}/retire | Retire record |
| DELETE /{id} | Soft-delete only if draft |

## 13.3 Active Policy API for Downstream Modules

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/standards/active-policy | Get currently active policy |
| GET | /api/standards/active/handler-categories | Get active handler categories |
| GET | /api/standards/active/establishment-categories | Get active establishment categories |
| GET | /api/standards/active/medical-tests?category_id= | Get applicable medical tests |
| GET | /api/standards/active/vaccination-rules?category_id= | Get applicable vaccine rules |
| GET | /api/standards/active/certificate-template | Get active certificate template |
| GET | /api/standards/active/reporting-template?state_id= | Get active reporting template |
| GET | /api/standards/active/me-indicators | Get active indicators |

## 13.4 Audit and Approval APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/federal/standards/approval-queue | List approvals |
| GET | /api/federal/standards/approval-queue/{id} | View approval detail |
| POST | /api/federal/standards/approval-queue/{id}/approve | Approve item |
| POST | /api/federal/standards/approval-queue/{id}/return | Return item |
| POST | /api/federal/standards/approval-queue/{id}/reject | Reject item |
| GET | /api/federal/standards/audit-logs | List audit logs |
| GET | /api/federal/standards/audit-logs/{id} | View audit detail |

---

## 14. UI/UX Specification

## 14.1 Global Layout

### Page Shell

Use a consistent Federal Module layout:

1. Left sidebar navigation.
2. Top header with page title, active policy version, user profile, notifications.
3. Main content area.
4. Breadcrumb trail.
5. Contextual action buttons.
6. Right-side slide-out drawer for create/edit where appropriate.

### Global Header Elements

1. Active Policy Version badge.
2. Environment indicator if staging/dev.
3. Notification bell.
4. User role badge.
5. Help/documentation link.

### Status Badge Colors

Use consistent status badges:

| Status | Badge Label |
|---|---|
| Draft | Draft |
| Under Review | Under Review |
| Returned | Returned |
| Approved | Approved |
| Scheduled | Scheduled |
| Active | Active |
| Retired | Retired |
| Archived | Archived |
| Emergency | Emergency |

## 14.2 Table Design Pattern

All configuration list pages should include:

1. Search bar.
2. Policy version filter.
3. Status filter.
4. Category/type filter where applicable.
5. Date range filter.
6. Export button.
7. Create button if permitted.
8. Row actions menu.
9. Pagination.
10. Empty state.

### Standard Row Actions

1. View
2. Edit Draft
3. Clone
4. Submit for Review
5. Retire
6. View Change History

## 14.3 Form Design Pattern

All create/edit forms should include:

1. Clear title.
2. Policy version selector.
3. Required field indicators.
4. Inline validation.
5. Save as Draft button.
6. Submit for Review button.
7. Cancel button.
8. Change reason field for edits.
9. Preview section where applicable.

## 14.4 Empty States

Examples:

- No policy versions yet: “Create your first policy version to begin configuring national standards.”
- No medical test rules: “No medical test rules have been configured for this policy version.”
- No approvals: “There are no pending approvals.”

## 14.5 Error States

Examples:

- “This policy version cannot be published because no active certificate template is attached.”
- “This rule cannot be edited because it belongs to a published policy version. Clone or create an amendment instead.”
- “State-level configuration cannot reduce Federal minimum standards.”

## 14.6 Confirmation Modals

Require confirmation for:

1. Publish policy version.
2. Retire policy version.
3. Activate high-impact rule.
4. Approve emergency rule.
5. Change certificate validity duration.
6. Change QR payload.
7. Retire certificate template.

---

## 15. Detailed UI/UX Flows

## 15.1 Flow: Federal User Creates New Policy Version

### Actor

Federal Policy Officer or Programme Manager

### Steps

1. User logs into Federal Module.
2. User selects `Standards & Policy Configuration` from sidebar.
3. User lands on Overview page.
4. User clicks `Create Policy Version`.
5. System opens full-page wizard.
6. Step 1: User enters:
   - Version title
   - Version code
   - Version type
   - Description
   - Change summary
7. Step 2: User sets:
   - Effective start date
   - Effective end date if applicable
   - State acknowledgement requirement
8. Step 3: User chooses:
   - Start blank
   - Clone active policy version
   - Clone previous draft
9. Step 4: User uploads supporting documents.
10. Step 5: User reviews summary.
11. User clicks `Save Draft`.
12. System creates draft policy version and logs action.
13. User is redirected to policy detail page.

### Success Message

“Policy version created successfully. You can now configure standards under this draft.”

## 15.2 Flow: Federal User Configures Medical Test Rule

### Actor

Federal Medical Standards Officer

### Steps

1. User opens `Medical Test Rules`.
2. User selects draft policy version.
3. User clicks `Add Test Rule`.
4. System opens side drawer.
5. User enters test name and code.
6. User selects rule type: mandatory, conditional, optional, or emergency.
7. User selects test type: laboratory, clinical, physical, other.
8. User selects result type.
9. User defines accepted values.
10. User defines blocking values.
11. User chooses whether attachment is required.
12. User chooses whether doctor validation is required.
13. User selects applicable handler categories.
14. User saves as draft.
15. System validates and saves.
16. User submits for review.
17. Rule appears in approval queue.

### Validation Failure Example

If user marks rule as mandatory but does not define result type, show:

“Mandatory test rules must include a result type before they can be saved.”

## 15.3 Flow: Configure Vaccine Rule

### Actor

Federal Medical Standards Officer

### Steps

1. User opens `Vaccination Rules`.
2. User clicks `Add Vaccine Rule`.
3. User enters vaccine name and code.
4. User marks vaccine as required.
5. User builds dose schedule:
   - Number of doses
   - Interval between doses
   - Validity period
6. User selects evidence fields required:
   - Vaccination date
   - Brand
   - Batch number
   - Vaccinator
   - Facility
   - Next visit
7. User sets whether missing/expired vaccine blocks certification.
8. User selects applicable handler categories.
9. User previews rule output.
10. User saves as draft.

## 15.4 Flow: Configure Certificate Template

### Actor

Federal Certification Officer

### Steps

1. User opens `Certificate Standards`.
2. User clicks `Create Certificate Template`.
3. User selects draft policy version.
4. User opens template builder.
5. User configures layout sections:
   - Header
   - Handler identity
   - Assessment summary
   - Vaccination summary
   - Facility/doctor details
   - QR verification
   - Footer
6. User selects required fields.
7. User configures certificate number format.
8. User configures QR payload.
9. User configures public verification fields.
10. User uploads digital seal or selects configured seal.
11. User clicks `Preview Certificate`.
12. System renders sample certificate.
13. User saves as draft.
14. User submits for approval.

## 15.5 Flow: Approve and Publish Policy Version

### Actor

Programme Manager or Super Admin

### Steps

1. User opens `Approval Queue`.
2. User filters by `Policy Version`.
3. User opens submitted policy version.
4. System shows:
   - Change summary
   - Configured categories
   - Medical rules
   - Vaccination rules
   - Certificate rules
   - Reporting templates
   - Missing configuration warnings
5. User clicks `Approve`.
6. System requires approval comment.
7. Status becomes `Approved`.
8. User clicks `Publish`.
9. System asks:
   - Publish now
   - Schedule for later
10. User selects effective date.
11. System checks conflicts.
12. System publishes or schedules policy version.
13. System notifies States.
14. State acknowledgement tasks are created.
15. System logs all actions.

## 15.6 Flow: State Admin Acknowledges Policy Version

### Actor

State Ministry of Health Admin

### Steps

1. State Admin logs into State Module.
2. Notification appears: “New Federal policy version requires acknowledgement.”
3. User clicks notification.
4. System opens policy summary page.
5. User reviews change summary, effective date, documents, and affected workflows.
6. User clicks `Acknowledge`.
7. System requires acknowledgement checkbox:
   - “I confirm that this State Ministry has reviewed the updated standards.”
8. User submits.
9. System records acknowledgement timestamp and user.
10. Federal dashboard updates acknowledgement count.

## 15.7 Flow: Auditor Reviews Change History

### Actor

Auditor

### Steps

1. Auditor opens `Change History`.
2. Auditor filters by:
   - Entity type: Vaccination Rule
   - Date range
   - Policy version
3. Auditor opens record.
4. System displays:
   - Old value
   - New value
   - Requesting user
   - Reviewer/approver
   - Comments
   - Timestamp
   - IP/device metadata
5. Auditor exports report.

---

## 16. Notification Requirements

### Notification Events

1. New policy draft created.
2. Policy submitted for review.
3. Policy returned for correction.
4. Policy approved.
5. Policy published.
6. Policy scheduled to become active.
7. State acknowledgement required.
8. State acknowledgement overdue.
9. Medical test rule changed.
10. Vaccination rule changed.
11. Certificate template changed.
12. QR configuration changed.
13. Reporting template changed.
14. Emergency rule activated.
15. Policy document published.

### Notification Channels

1. In-app notification.
2. Email notification.
3. Dashboard alert.
4. Optional SMS for urgent emergency rules.

### Notification Template Example

Subject: New Federal Food Handler Policy Version Published

Body:

A new policy version, `{version_code}`, has been published and will become active on `{effective_date}`. Please review and acknowledge the updated standards in your State dashboard.

---

## 17. Security Requirements

1. Enforce role-based access control for all configuration endpoints.
2. Require elevated permissions for policy publication.
3. Require approval workflow for high-impact changes.
4. Prevent direct editing of published standards.
5. Use soft-delete or retire actions, not hard delete, for policy records.
6. Audit all create, update, submit, approve, publish, retire, and delete actions.
7. Protect policy document uploads from unauthorized access.
8. Public QR verification must not expose sensitive medical records.
9. Use secure file storage for documents and digital seals.
10. Enforce session timeout for Federal admin users.
11. Consider two-factor authentication for Super Admin and Programme Manager roles.
12. Validate all JSON configuration payloads against schemas.
13. Prevent malicious file uploads by restricting file types and scanning uploads.
14. Use signed verification tokens for QR payloads.
15. Ensure state users cannot edit Federal-locked rules.

---

## 18. Validation Requirements

| Area | Validation Rule |
|---|---|
| Policy Version | Version code must be unique |
| Policy Version | Cannot publish without effective date |
| Policy Version | Cannot publish if required configuration is missing |
| Categories | Category code must be unique within policy version |
| Medical Test | Mandatory test must have result type |
| Medical Test | Blocking rule must define blocking value |
| Vaccination | Required vaccine must have schedule or validity rule |
| Certificate Template | Must include certificate ID and QR code |
| QR Payload | Must include verification token and certificate ID |
| Reporting Template | Must include frequency and deadline rule |
| M&E Indicator | Formula must reference valid data fields |
| Approval | Rejection or return must include comments |
| State Acknowledgement | Must record state, user, timestamp |
| Document Upload | Must have document type and version label |

---

## 19. Reporting Requirements

The feature must support the following reports:

1. Active Standards Report
2. Policy Version Summary Report
3. Policy Change Comparison Report
4. State Acknowledgement Report
5. Medical Test Rule Report
6. Vaccination Rule Report
7. Certificate Template Configuration Report
8. QR Verification Configuration Report
9. Reporting Template Report
10. M&E Indicator Configuration Report
11. Facility Requirement Standards Report
12. Approval Trail Report
13. Audit Log Report
14. Published Documents Report

Each report should be exportable in CSV and PDF where applicable.

---

## 20. Implementation Chunks for Codex

## Chunk 1: Foundation, Routing, Permissions, and Navigation

### Objective

Create the base Federal Standards and Policy Configuration module structure.

### Tasks

1. Add route group for Federal Standards module.
2. Add sidebar navigation item: `Standards & Policy Configuration`.
3. Add sub-navigation pages:
   - Overview
   - Policy Versions
   - Food Handler Categories
   - Establishment Categories
   - Medical Test Rules
   - Physical Examination Rules
   - Vaccination Rules
   - Certificate Standards
   - Certificate Validity & Expiry Rules
   - Return-to-Work Rules
   - Medical Facility Requirements
   - State Configuration Controls
   - Reporting Templates
   - M&E Indicators
   - Documents & Circulars
   - Approval Queue
   - Change History
4. Implement permissions constants.
5. Add route guards based on role.
6. Add active policy version badge to Standards pages.
7. Build empty page shells for each sub-page.

### Acceptance Criteria

1. Federal users can navigate to the Standards module.
2. Users only see actions allowed by their role.
3. All sub-pages render without errors.
4. Active policy version badge appears globally in the module.

---

## Chunk 2: Database Migrations and Core Models

### Objective

Create database tables and model relationships.

### Tasks

1. Create migrations for:
   - policy_versions
   - food_handler_categories
   - establishment_categories
   - medical_test_rules
   - physical_examination_rules
   - vaccination_rules
   - certificate_templates
   - certificate_validity_rules
   - return_to_work_rules
   - facility_requirement_rules
   - reporting_templates
   - me_indicators
   - policy_documents
   - approvals
   - state_acknowledgements
   - audit_logs
2. Define enums.
3. Define model relationships.
4. Add soft delete or retired status handling where appropriate.
5. Add created_by and updated_by tracking.
6. Add policy_version_id foreign keys.

### Acceptance Criteria

1. Migrations run successfully.
2. Models can be created and queried.
3. Relationships between policy versions and rules work.
4. Database prevents duplicate codes within a policy version.

---

## Chunk 3: Seed Default 2024 Guideline Standards

### Objective

Seed the application with the baseline national guideline configuration.

### Tasks

1. Create seed policy version: `NG-FHMT-2024-v1.0`.
2. Seed food handler categories.
3. Seed establishment categories.
4. Seed medical test rules:
   - Stool microscopy, culture and sensitivity
   - Hepatitis A Antigen
   - Additional clinically indicated tests
5. Seed physical examination indicators.
6. Seed vaccination rules:
   - Typhoid
   - Hepatitis A
7. Seed certificate statuses.
8. Seed facility requirement checklist.
9. Seed basic reporting template.
10. Seed M&E indicators.

### Acceptance Criteria

1. Fresh installation has a complete draft or active baseline policy.
2. Seeded categories match the guideline categories.
3. Seeded rules are linked to the baseline policy version.
4. Seed data can be edited only through draft/amendment workflow.

---

## Chunk 4: Policy Version Management Backend

### Objective

Implement APIs and services for policy version lifecycle.

### Tasks

1. Implement create policy version endpoint.
2. Implement list policy versions endpoint.
3. Implement view policy version endpoint.
4. Implement update draft policy version endpoint.
5. Implement clone policy version service.
6. Implement submit for review endpoint.
7. Implement approve/return/reject endpoints.
8. Implement publish endpoint.
9. Implement schedule publication logic.
10. Implement retire endpoint.
11. Implement policy comparison service.
12. Add audit logging for all actions.

### Acceptance Criteria

1. Draft versions can be created and updated.
2. Published versions cannot be edited.
3. Clone function copies rules into a new draft version.
4. Publish validates required configuration.
5. Retired versions remain readable but not usable for new certificates.

---

## Chunk 5: Policy Version Management UI

### Objective

Build the user interface for managing policy versions.

### Tasks

1. Build policy versions table.
2. Add filters: status, effective date, version type.
3. Build create policy version wizard.
4. Build policy detail page.
5. Add rule summary tabs to policy detail page.
6. Add submit for review button.
7. Add approve/publish actions based on permission.
8. Add comparison UI.
9. Add state acknowledgement tab.

### Acceptance Criteria

1. Users can create policy versions through the UI.
2. Users can clone active policy into new draft.
3. Users can submit for review.
4. Approvers can approve and publish.
5. Users can compare versions visually.

---

## Chunk 6: Category Configuration Backend and UI

### Objective

Implement food handler and establishment category management.

### Tasks

1. Implement CRUD endpoints for food handler categories.
2. Implement CRUD endpoints for establishment categories.
3. Add category risk level logic.
4. Add linking to medical and vaccination rule groups.
5. Add state subcategory control fields.
6. Build food handler category table and form.
7. Build establishment category table and form.
8. Add bulk upload endpoint and UI.
9. Add export functionality.
10. Add audit logging.

### Acceptance Criteria

1. Categories can be created under draft policy versions.
2. Categories cannot be edited after publication.
3. Category codes are unique within a policy version.
4. Establishments can be linked to handler categories.

---

## Chunk 7: Medical Test and Physical Examination Rule Engine

### Objective

Implement medical test rule and physical examination configuration.

### Tasks

1. Implement medical test rule CRUD APIs.
2. Implement physical examination rule CRUD APIs.
3. Implement validation schema for result types.
4. Implement blocking result logic.
5. Implement applicable category filtering.
6. Build Medical Test Rules table and form.
7. Build Physical Examination Rules table and form.
8. Build rule preview panel.
9. Build downstream API to get applicable tests by category.
10. Add audit logging.

### Acceptance Criteria

1. Mandatory test rules require result type.
2. Blocking results can be configured.
3. Assessment module can fetch active applicable rules.
4. UI clearly shows certification impact.

---

## Chunk 8: Vaccination Rule Engine

### Objective

Implement vaccination rule configuration and schedule logic.

### Tasks

1. Implement vaccination rule CRUD APIs.
2. Implement dose schedule JSON schema.
3. Implement validity calculation utility.
4. Implement next visit calculation utility.
5. Implement missing/expired vaccine flag logic.
6. Build Vaccination Rules table.
7. Build vaccine rule form with schedule builder.
8. Add preview for calculated expiry and next visit.
9. Add downstream API for applicable vaccination rules.
10. Add audit logging.

### Acceptance Criteria

1. Typhoid defaults to 3-year validity.
2. Hepatitis A supports 0 and 6-month dose schedule.
3. Expiry calculation works from vaccination date.
4. Rules can define whether missing/expired vaccine blocks certification.

---

## Chunk 9: Certificate Standards and QR Configuration

### Objective

Implement certificate template and QR configuration.

### Tasks

1. Implement certificate template CRUD APIs.
2. Implement certificate required fields schema.
3. Implement certificate number format configuration.
4. Implement QR payload schema.
5. Implement public verification field schema.
6. Build certificate template builder UI.
7. Build QR payload configuration UI.
8. Build certificate preview page.
9. Add validation to ensure QR and required identifiers exist.
10. Add downstream API for active certificate template.
11. Add audit logging.

### Acceptance Criteria

1. Certificate template cannot be published without QR config.
2. QR payload cannot include restricted medical fields unless explicitly permitted by admin policy.
3. Certificate preview renders with sample data.
4. Certificate issuance module can fetch active template.

---

## Chunk 10: Certificate Validity, Expiry, and Return-to-Work Rules

### Objective

Implement validity, expiry, re-examination, exclusion, and return-to-work configuration.

### Tasks

1. Implement certificate validity rule CRUD APIs.
2. Implement expiry reminder configuration.
3. Implement return-to-work rule CRUD APIs.
4. Implement exclusion period logic.
5. Implement clearance requirement schema.
6. Build Certificate Validity & Expiry UI.
7. Build Return-to-Work Rules UI.
8. Add impact preview for changes.
9. Add downstream API for validity and return-to-work rules.
10. Add audit logging.

### Acceptance Criteria

1. Validity rules are configurable, not hardcoded.
2. Expiry reminders can be stored as list of days.
3. Return-to-work rules can require medical/lab/authority clearance.
4. High-impact changes require approval.

---

## Chunk 11: Facility Requirements Configuration

### Objective

Implement medical facility eligibility and documentation standards.

### Tasks

1. Implement facility requirement CRUD APIs.
2. Implement requirement categories.
3. Implement evidence type schema.
4. Implement mandatory/optional checklist logic.
5. Implement annual re-accreditation interval settings.
6. Build Facility Requirements table.
7. Build requirement form.
8. Build checklist preview.
9. Add downstream API for State facility accreditation module.
10. Add audit logging.

### Acceptance Criteria

1. Federal users can configure facility eligibility checklist.
2. State accreditation module can fetch active facility requirements.
3. Requirements can define evidence type.
4. Annual re-accreditation can be configured.

---

## Chunk 12: State Configuration Controls

### Objective

Implement Federal control over what States can configure.

### Tasks

1. Create state configuration control model if not included as generic StandardRule.
2. Implement APIs to set state configurability.
3. Define controls for categories, tests, vaccines, facility approvals, pricing, reporting, awareness, and enforcement.
4. Build State Configuration Controls UI.
5. Add guard logic to prevent States from reducing Federal minimums.
6. Add Federal view of state-specific settings.
7. Add audit logging.

### Acceptance Criteria

1. Federal users can mark rules as locked or state-configurable.
2. State users cannot override locked Federal rules.
3. State-added rules reference Federal policy version.
4. Federal users can view all state-level configurations.

---

## Chunk 13: Reporting Templates and M&E Indicators

### Objective

Implement reporting template and M&E indicator configuration.

### Tasks

1. Implement reporting template CRUD APIs.
2. Implement reporting frequency and deadline schema.
3. Implement required sections schema.
4. Implement required uploads schema.
5. Implement M&E indicator CRUD APIs.
6. Implement formula builder schema.
7. Implement threshold configuration.
8. Build Reporting Template Builder UI.
9. Build M&E Indicator Builder UI.
10. Add downstream APIs for State reporting and dashboards.
11. Add audit logging.

### Acceptance Criteria

1. Reporting templates can be created and published.
2. State reporting module can fetch active template.
3. M&E indicators can define formulas and thresholds.
4. Indicators can be marked visible on Federal or State dashboards.

---

## Chunk 14: Policy Documents and Circulars

### Objective

Implement document management and acknowledgement tracking.

### Tasks

1. Implement secure file upload.
2. Implement policy document CRUD APIs.
3. Implement document type classification.
4. Implement document versioning.
5. Implement publish/retire/archive workflow.
6. Implement target audience selection.
7. Implement state acknowledgement tracking.
8. Build Documents & Circulars UI.
9. Build acknowledgement dashboard.
10. Add download tracking.
11. Add audit logging.

### Acceptance Criteria

1. Federal users can upload and publish documents.
2. Documents can be linked to policy versions.
3. States can acknowledge required documents.
4. Federal users can track acknowledgements and downloads.

---

## Chunk 15: Approval Workflow and Notifications

### Objective

Implement approval queue and notification system.

### Tasks

1. Implement approvals table and service.
2. Implement submit-for-review for each entity.
3. Implement approve, return, and reject actions.
4. Implement impact level classification.
5. Build Approval Queue UI.
6. Build approval detail diff view.
7. Implement in-app notifications.
8. Implement email notifications.
9. Implement state acknowledgement notification.
10. Add audit logging.

### Acceptance Criteria

1. Config changes can be routed for approval.
2. Approvers can see old vs new values.
3. Returned/rejected items require comments.
4. Notifications are sent for key workflow events.

---

## Chunk 16: Audit Logs, Change History, and Export

### Objective

Implement audit logging and change history views.

### Tasks

1. Create centralized audit log service.
2. Track create, update, submit, approve, publish, retire, archive actions.
3. Store old and new values.
4. Build Change History UI.
5. Build entity-level history panel.
6. Add filters by entity, user, policy version, date range, action.
7. Implement CSV export.
8. Implement PDF export if supported.
9. Add permission restrictions.

### Acceptance Criteria

1. Every configuration action has an audit log.
2. Auditors can filter and inspect logs.
3. Entity detail pages show change history.
4. Export respects permissions.

---

## Chunk 17: Integration with Downstream Modules

### Objective

Expose active standards to other modules.

### Tasks

1. Build active policy service.
2. Build active handler category service.
3. Build active establishment category service.
4. Build applicable medical test service.
5. Build applicable vaccination rule service.
6. Build active certificate template service.
7. Build active reporting template service.
8. Build active M&E indicator service.
9. Add caching for active policy rules.
10. Add tests for downstream APIs.

### Acceptance Criteria

1. Other modules can fetch active rules without querying drafts.
2. APIs return only active, published rules.
3. Cached rules refresh when new policy becomes active.
4. Historical certificates can still reference retired policy versions.

---

## Chunk 18: Testing, QA, and Hardening

### Objective

Ensure the feature is stable, secure, and production-ready.

### Tasks

1. Unit tests for models.
2. Unit tests for policy lifecycle.
3. Unit tests for validation schemas.
4. Integration tests for APIs.
5. Permission tests for each role.
6. Approval workflow tests.
7. Audit log tests.
8. UI tests for major flows.
9. Security tests for unauthorized edits.
10. Regression tests for downstream active standards APIs.

### Acceptance Criteria

1. Published rules cannot be edited directly.
2. Unauthorized users cannot access restricted actions.
3. Policy publication fails if required configurations are missing.
4. All high-impact changes require approval.
5. Audit logs are generated for every important action.

---

## 21. MVP Scope

The first release should include:

1. Policy version management.
2. Food handler category configuration.
3. Establishment category configuration.
4. Medical test rule configuration.
5. Physical examination rule configuration.
6. Vaccination rule configuration.
7. Certificate template and QR configuration.
8. Certificate validity configuration.
9. Return-to-work rules.
10. Facility requirements.
11. Reporting templates.
12. M&E indicators.
13. Policy documents and circulars.
14. Approval queue.
15. Audit logs.
16. Active standards APIs for downstream modules.

---

## 22. Post-MVP Enhancements

1. Advanced visual certificate template designer.
2. Emergency outbreak rule activation console.
3. Policy impact simulation.
4. Advanced policy comparison tool.
5. Public changelog.
6. Multi-language policy document support.
7. Integration with NIN verification.
8. Integration with disease surveillance systems.
9. Advanced data quality scoring.
10. AI-assisted policy summary generation.
11. State policy localization tools.
12. Advanced dashboard widgets for policy adoption.

---

## 23. Success Metrics

| Metric | Target |
|---|---|
| Core standards configurable without developer changes | 100% |
| Certificates linked to policy version | 100% |
| Published policy versions auditable | 100% |
| State acknowledgement within required period | 90%+ |
| Mandatory test rule enforcement accuracy | 98%+ |
| Unauthorized policy edits blocked | 100% |
| High-impact changes routed through approval | 100% |
| Active standards API uptime | 99.5%+ |
| Audit coverage for configuration actions | 100% |
| State reporting template adoption | 100% of States/FCT |

---

## 24. Open Questions for Product Owner

1. Should the routine certificate validity be six months or one year?
2. Should States be able to add additional medical tests beyond the Federal minimum?
3. Should Federal approval be required before a State activates a medical facility?
4. Should assessment pricing be configured here or in a separate payment/pricing module?
5. Should QR verification be fully public or role-tiered?
6. Should policy changes take effect immediately or only after State acknowledgement?
7. Should emergency outbreak rules override active certificates?
8. Should the platform integrate with NIN verification from MVP?
9. Should certificate templates support multiple languages?
10. Should medical facilities be able to see historical versions or only active standards?
11. Should food businesses receive policy circulars directly or only through State communication?
12. Should the Federal Ministry have the power to suspend state-specific rules?

---

## 25. Recommended Engineering Notes

1. Treat policy configuration as versioned data, not static code.
2. Never hardcode medical tests, vaccine validity, or certificate validity directly into workflows.
3. All downstream modules should request rules from the active standards service.
4. Store policy version ID on every assessment and certificate.
5. Use JSON schema validation for flexible rule configs.
6. Cache active policy rules for performance, but invalidate cache on publication.
7. Published versions should be immutable.
8. Use audit logs for every configuration mutation.
9. Keep medical data out of public QR verification payloads.
10. Build the MVP with simple forms first; advanced visual builders can come later.

---

## 26. Recommended Default Seed Codes

### Food Handler Category Codes

| Category | Code |
|---|---|
| Kitchen Staff | FH-KITCHEN |
| Food Preparers | FH-PREPARER |
| Serving and Catering Staff | FH-SERVICE-CATERING |
| Food Packers | FH-PACKER |
| Bakery Workers | FH-BAKERY |
| Food Processing Operators | FH-PROCESSING |
| Bartenders | FH-BARTENDER |
| Dishwashers | FH-DISHWASHER |
| Food Delivery Personnel | FH-DELIVERY |
| Food Stall and Street Food Vendors | FH-STREET-VENDOR |
| Food Storage Handlers | FH-STORAGE |
| Concession Stand Workers | FH-CONCESSION |
| Airline Catering Vendors | FH-AIRLINE-CATERING |
| Train Catering Vendors | FH-TRAIN-CATERING |
| Cruise Ship / Sea Vessel Catering Vendors | FH-SEA-CATERING |
| Livestock Farmers | FH-LIVESTOCK |
| Emergency Situation Workers | FH-EMERGENCY |

### Medical Test Codes

| Test | Code |
|---|---|
| Stool Microscopy, Culture and Sensitivity | LAB-STOOL-MCS |
| Hepatitis A Antigen | LAB-HEPA-AG |
| Additional Clinically Indicated Test | LAB-CLINICAL-ADDITIONAL |

### Vaccine Codes

| Vaccine | Code |
|---|---|
| Typhoid | VAC-TYPHOID |
| Hepatitis A | VAC-HEPA |
| Other Required Vaccine | VAC-OTHER |

### Certificate Status Codes

| Status | Code |
|---|---|
| Valid | CERT-VALID |
| Expired | CERT-EXPIRED |
| Revoked | CERT-REVOKED |
| Suspended | CERT-SUSPENDED |
| Not Fit | CERT-NOT-FIT |
| Cleared to Return | CERT-CLEARED-RETURN |
| Under Review | CERT-UNDER-REVIEW |

---

## 27. Final Product Direction

The Standards and Policy Configuration feature should be implemented as the foundational policy engine of the entire Food Handlers Medical Test Management Platform.

The application should not treat food handler categories, test requirements, vaccination validity, certificate layout, QR rules, reporting templates, and M&E indicators as hardcoded values. These should all be configurable, versioned, approved, auditable, and publishable by authorized Federal users.

This design will allow the Federal Ministry of Health and Social Welfare to maintain national control and oversight while supporting state-level implementation across all 36 States and the FCT.
